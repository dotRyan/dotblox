from collections import defaultdict

import pymel.core as pm

from dotblox.core.constant import AXIS, DIRECTION
from dotblox.core.mutil import Undoable


class MIRROR_AXIS():
    [BOUNDING_BOX,
     OBJECT,
     WORLD
     ] = [x for x in range(3)]


def poly_mirror(axis=AXIS.X,
                direction=DIRECTION.NEGATIVE,
                mirror_axis=MIRROR_AXIS.OBJECT,
                *nodes):
    """Mirror geometry across an axis

    This method doesnt do anything fancy other than keep some
    settings consistent

    Args:
        axi(str): x, y, z
        direction: +:0, -:1
        mirror_axis: {
                        0: "Bounding Box",
                        1: "Object",
                        2: "World"
                    }
    """
    if not nodes:
        nodes = pm.ls(selection=True, long=True)

    axis_map = {
        AXIS.X: 0,
        AXIS.Y: 1,
        AXIS.Z: 2,
    }

    if axis not in axis_map:
        if axis not in axis_map.values():
            raise RuntimeError("Axis \"%s\" not valid" % axis)

    for node in nodes:
        pm.polyMirrorFace(node,
                          cutMesh=True,
                          axis=axis_map[axis],
                          axisDirection=direction,
                          mergeMode=1,  # Merge Border Vertices
                          mirrorAxis=mirror_axis,
                          mirrorPosition=0,
                          mergeThresholdType=1,  # Merge Threshold custom
                          mergeThreshold=0.001,
                          flipUVs=False,
                          smoothingAngle=30,
                          constructionHistory=True,
                          )


class BevelEditor():
    """Class that gives you the ability to modify an existing bevel

    Definitions:
        vis_node: the node that is created when show_bevel is run
        src_node: the mesh that the bevels were found on
        bevel_node: the bevel node that is currently being shown

    Selection Supported Methods:
        - add_to_bevel
        - remove_from_bevel

    Usage:
        pass


    """
    BEVEL_ATTR = "bevel_editor_bevel"
    NODE_ATTR = "bevel_editor_node"

    @classmethod
    def get_bevel_nodes(cls, node):
        """
        Get a list of all the bevel nodes on the given node

        Args:
            node: mesh transform to operate on

        Returns: list of bevel nodes in order of last created

        """

        src_node = cls.get_src_node(node)
        if src_node:
            node = src_node

        history = node.listHistory()

        return filter(lambda node: node.type().startswith("polyBevel"), history)

    @classmethod
    def show_bevel(cls, bevel_node):
        """
        Show the given bevel
        Args:
            bevel_node: the bevel node to show

        Returns: vis_node

        """
        # Make sure the bevel node is hooked up to something
        history = bevel_node.listHistory()
        if not history:
            raise RuntimeError("Bevel node has no history")

        # Last item in the history seems to be the active mesh
        last_item = history[-1]
        if last_item.type() != "mesh":
            raise RuntimeError("Unable to determine endpoint of bevel")

        # Always operate on the transform
        src_node = last_item.getParent()

        # Find the input mesh of the bevel node. This is the mesh we want
        #   to display
        input_mesh_connections = bevel_node.inputPolymesh.listConnections(plugs=True)
        if not input_mesh_connections:
            raise RuntimeError("Unable to find input mesh on bevel")
        # Should only be 1 connection since maya does not allow multiple
        input_connection = input_mesh_connections[0]

        # Format name of the vis_node
        vis_node_name = "{mesh}_bevel_vis".format(
                mesh=src_node.name(),
                bevel=bevel_node.name())

        # Offset the mesh only on creation
        offset = False
        if not pm.objExists(vis_node_name):
            vis_node = pm.createNode("transform", name=vis_node_name)
            vis_mesh = pm.createNode("mesh",
                                     parent=vis_node,
                                     name=vis_node_name + "Shape")
            # Add custom attributes so we can find all the nodes
            #   associated with the current vis_node
            vis_node.addAttr(cls.BEVEL_ATTR, type="message")
            vis_node.addAttr(cls.NODE_ATTR, type="message")
            # Match the current transforms to the vis_node
            vis_node.setMatrix(src_node.getMatrix(worldSpace=True))
            pm.move(vis_node, [0, 0, 0], relative=True)
            # Assign default shader
            pm.sets("initialShadingGroup", vis_mesh, forceElement=True)
            offset = True
        else:
            vis_node = pm.PyNode(vis_node_name)
            vis_mesh = vis_node.getShape()

        bevel_attr = vis_node.attr(cls.BEVEL_ATTR)
        node_attr = vis_node.attr(cls.NODE_ATTR)

        # Connect everything up so we can link back
        if not src_node.message.isConnectedTo(node_attr):
            src_node.message >> node_attr
        if not src_node.message.isConnectedTo(bevel_attr):
            bevel_node.message >> bevel_attr

        # Copy the bevel input mesh to the vis_mesh
        input_connection >> vis_mesh.inMesh
        # TODO: figure out how to force a dgeval
        #       for now doing a refresh works.
        #       This may run like shit on a large scene
        pm.refresh()
        input_connection // vis_mesh.inMesh

        # Offset the node from the src node
        if offset:
            width = src_node.getBoundingBox().width()
            pm.move(vis_node, [width * 1.25, 0, 0], relative=True)

        # Select the new node.
        vis_node.select()

        cls._colorize(vis_node)
        return vis_node

    @classmethod
    def get_bevel_edges(cls, bevel_node, flatten=False):
        """Get a list of edges of the bevel_node in context of the vis_node

        Args:
            bevel_node: bevel node of edge to use.
            flatten: return the list as individual items rather than mayas grouping

        Returns:
            list of edges
        """
        vis_node = cls.get_vis_node(bevel_node)
        if not vis_node:
            return []
        # Result is a list of indices [3, 0, 1, 4]
        # The first index is the length of edges in the array
        current_edges = bevel_node.inputComponents.get() or []
        if current_edges:
            # Remap to a pynode mesh edge
            current_edges = [pm.MeshEdge(vis_node.getShape() + "." + edge)
                             for edge in current_edges]
            if flatten:
                current_edges = pm.ls(current_edges, flatten=True)

        return current_edges

    @classmethod
    def _eval_components(cls, *components):
        """Get a map of each object's edges from the select components


            Faces are converted to the edge perimeter
            Verts are converted to the connected edges

            Returns:
                dict of each node associated with a set of each edge rather than .e[2:5]
        """
        if not components:
            components = pm.ls(selection=True, flatten=True, long=True)
        else:
            components = pm.ls(components, flatten=True)

        face_map = defaultdict(set)
        edge_map = defaultdict(set)

        for component in components:
            if isinstance(component, pm.MeshFace):
                key = component.node().getParent()
                face_map[key].add(component)
            elif isinstance(component, pm.MeshEdge):
                key = component.node().getParent()
                edge_map[key].add(component)
            elif isinstance(component, pm.MeshVertex):
                key = component.node().getParent()
                for edge in component.connectedEdges():
                    edge_map[key].add(edge)
            else:
                pm.displayWarning("Component not supported %s" % component)

        # Get the edge perimeter of all the faces at once
        for node, face_map in face_map.iteritems():
            edge_perimeter = pm.polyListComponentConversion(face_map,
                                                            toEdge=True,
                                                            border=True)
            for edge in pm.ls(edge_perimeter, flatten=True):
                edge_map[node].add(edge)

        return edge_map

    @classmethod
    @Undoable()
    def add_to_bevel(cls, *components):
        """Add the selected/given components to the vis bevel
            Args:
                components: can be of type vertex, edge and face

            Raises:
                non blocking; Warning's are displayed for unsupported nodes
        """
        edge_map = cls._eval_components(*components)

        for vis_node, selected_edges in edge_map.iteritems():
            # Make sure the node is a vis node
            if vis_node != cls.get_vis_node(vis_node):
                pm.displayWarning("Node %s is not a vis node"
                                  % vis_node.name(long=True))
                continue
            # Make sure there is a bevel node
            bevel_node = cls.get_vis_bevel(vis_node)
            if bevel_node is None:
                pm.displayWarning("Node %s not supported"
                                  % vis_node.name(long=True))
                continue

            current_edges = cls.get_bevel_edges(bevel_node)

            cls._set_edges(bevel_node, selected_edges, current_edges)
            cls._colorize(vis_node)

    @classmethod
    @Undoable()
    def remove_from_bevel(cls, *components):
        """Remove the selected/given components to the vis bevel
            Args:
                components: can be of type vertex, edge and face

            Raises:
                non blocking; Warning's are displayed for unsupported nodes

        """
        edge_map = cls._eval_components(*components)

        for vis_node, selected_edges in edge_map.iteritems():
            # Make sure the node is a vis node
            if vis_node != cls.get_vis_node(vis_node):
                pm.displayWarning("Node %s is not a vis node"
                                  % vis_node.name(long=True))
                continue
            # Make sure there is a bevel node
            bevel_node = cls.get_vis_bevel(vis_node)
            if bevel_node is None:
                pm.displayWarning("Node %s not supported"
                                  % vis_node.name(long=True))
                continue
            # get a flattened list so we can remove individual edges
            current_edges = cls.get_bevel_edges(bevel_node, flatten=True)

            # Remove the selected edges if they are in the bevel
            for edge in selected_edges:
                if edge in current_edges:
                    current_edges.remove(edge)

            cls._set_edges(bevel_node, current_edges)
            cls._colorize(vis_node)

    @classmethod
    def _set_edges(cls, bevel_node, *edges):
        """Set the edges on the selected bevel

            `inputComponents` is set to an array with the first index
            being the length of edges in the array
            [num_edges, 0, 2, 4]
        """
        with PreserveSelection():
            # Note: To optimize the list of edges let maya do its selection thing
            #   Edges are represented as .e[3:6]
            #  Maybe there is a better way to do this?
            pm.select(*edges)
            compressed_edges = []
            for edge in pm.ls(selection=True):
                compressed_edges.append(edge.name().split(".")[-1])

        bevel_node.inputComponents.set([len(compressed_edges)] + compressed_edges)

    @classmethod
    def _colorize(cls, node):
        """"Colorize the mesh by using the crease functionality

        Args:
            node: can be the vis_node, bevel_node or src_node

        """
        bevel_node = cls.get_vis_bevel(node)
        if bevel_node is None:
            raise RuntimeError("Bevel not found on %s" % node.name(long=True))

        edges = cls.get_bevel_edges(bevel_node)
        vis_node = cls.get_vis_node(node)
        # Remove the crease from all the edges
        pm.polyCrease(vis_node.e, createHistory=False, value=0)
        # Set the crease of all the edges
        # value does not bolden the display in the viewport
        pm.polyCrease(edges, createHistory=False, value=5)

    @classmethod
    def get_vis_bevel(cls, node):
        """Get the bevel currently being shown

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            bevel node
        """
        # Given the vis_node get the connection to the bevel attribute
        if node.hasAttr(cls.NODE_ATTR) and node.hasAttr(cls.BEVEL_ATTR):
            connections = node.attr(cls.BEVEL_ATTR).listConnections()
            return connections[0]

        # Loop through the attributes on both sides of the message connection
        connections = node.message.listConnections(plugs=True)
        for connection in connections:
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            if connection.attrName() in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                # Recurse back knowing we have the vis node but it will
                #   check but it will make sure it has both attributes
                return cls.get_vis_bevel(connection.node())

    @classmethod
    def get_vis_node(cls, node):
        """Get the vis_node

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            vis node
        """
        # If we have both attributes then it is the vis_node
        if node.hasAttr(cls.NODE_ATTR) and node.hasAttr(cls.BEVEL_ATTR):
            return node

        # Loop through the attributes on both sides of the message connection
        connections = node.message.listConnections(plugs=True)
        for connection in connections:
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            if connection.attrName() in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                # Recurse back knowing we have the vis node but it will
                #   check but it will make sure it has both attributes
                return cls.get_vis_node(connection.node())

    @classmethod
    def get_src_node(cls, node):
        """Get the src_node

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            src node
        """
        # Given the vis_node get the connection to the bevel attribute
        if node.hasAttr(cls.NODE_ATTR) and node.hasAttr(cls.BEVEL_ATTR):
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            connections = node.attr(cls.NODE_ATTR).listConnections()
            return connections[0]

        # Loop through the attributes on both sides of the message connection
        connections = node.message.listConnections(plugs=True)
        for connection in connections:
            # Recurse back knowing we have the vis node but it will
            #   check but it will make sure it has both attributes
            if connection.attrName() in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                return cls.get_src_node(connection.node())

    @classmethod
    def remove_vis_bevel(cls, src_node):
        """Given the src_node remove the vis bevel nodes

            If the vis_node is currently in the selection the src_node
            will be selected instead
        """
        vis_node = cls.get_vis_node(src_node)
        if vis_node:
            if vis_node in pm.ls(sl=True, long=True):
                pm.select(src_node, add=True)
            pm.delete(vis_node)
