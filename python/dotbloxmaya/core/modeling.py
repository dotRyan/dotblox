from collections import defaultdict

from maya import cmds
import maya.api.OpenMaya as om

from dotbloxmaya.core import nodepath, mapi
from dotbloxmaya.core.constant import AXIS, DIRECTION
from dotbloxmaya.core.mutil import PreserveSelection, Undoable


class MIRROR_AXIS():
    [BOUNDING_BOX,
     OBJECT,
     WORLD
     ] = [x for x in range(3)]


def poly_mirror(nodes=None,
                axis=AXIS.X,
                direction=DIRECTION.NEGATIVE,
                mirror_axis=MIRROR_AXIS.OBJECT):
    """Mirror geometry across an axis

    This method doesnt do anything fancy other than keep some
    settings consistent

    Args:
        axis(str): x, y, z
        direction: +:0, -:1
        mirror_axis: {
                        0: "Bounding Box",
                        1: "Object",
                        2: "World"
                    }
    """
    if nodes is None:
        nodes = cmds.ls(selection=True, long=True)

    axis_map = {
        AXIS.X: 0,
        AXIS.Y: 1,
        AXIS.Z: 2,
    }

    if axis not in axis_map:
        if axis not in axis_map.values():
            raise RuntimeError("Axis \"%s\" not valid" % axis)

    for node in nodes:
        cmds.polyMirrorFace(node,
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

        history = map(nodepath.full_path, cmds.listHistory(node) or [])

        return filter(lambda node: cmds.nodeType(node).startswith("polyBevel"), history)

    @classmethod
    def show_bevel(cls, bevel_node):
        """
        Show the given bevel
        Args:
            bevel_node: the bevel node to show

        Returns: vis_node

        """
        # Make sure the bevel node is hooked up to something
        history = cmds.listHistory(bevel_node)
        if not history:
            raise RuntimeError("Bevel node has no history")

        # Last item in the history seems to be the active mesh
        last_item = history[-1]
        if cmds.nodeType(last_item) != "mesh":
            raise RuntimeError("Unable to determine endpoint of bevel")

        # Always operate on the transform
        src_node = nodepath.parent(nodepath.full_path(last_item))

        # Find the input mesh of the bevel node. This is the mesh we want
        #   to display
        input_mesh_connections = cmds.listConnections(bevel_node + ".inputPolymesh", plugs=True) or []
        if not input_mesh_connections:
            raise RuntimeError("Unable to find input mesh on bevel")
        # Should only be 1 connection since maya does not allow multiple
        input_connection = input_mesh_connections[0]

        # Format name of the vis_node
        vis_node = "{mesh}_bevel_vis".format(
                mesh=nodepath.leafname(src_node))

        # Offset the mesh only on creation
        offset = False
        if not cmds.objExists(vis_node):
            vis_node = cmds.createNode("transform", name=vis_node)
            vis_mesh = cmds.createNode("mesh",
                                       parent=vis_node,
                                       name=vis_node + "Shape")
            # Add custom attributes so we can find all the nodes
            #   associated with the current vis_node
            cmds.addAttr(vis_node, longName=cls.BEVEL_ATTR, attributeType="message")
            cmds.addAttr(vis_node, longName=cls.NODE_ATTR, attributeType="message")
            # Match the current transforms to the vis_node
            src_matrix = cmds.xform(src_node, query=True, matrix=True, worldSpace=True)
            cmds.xform(vis_node, matrix=src_matrix, worldSpace=True)
            # Assign default shader
            cmds.sets(vis_mesh, forceElement="initialShadingGroup")
            offset = True
        else:
            vis_mesh = mapi.get_shape(vis_node)

        node_attr = vis_node + "." + cls.NODE_ATTR
        src_msg_attr = src_node + ".message"
        # Connect everything up so we can link back
        if not cmds.isConnected(src_msg_attr, node_attr):
            cmds.connectAttr(src_msg_attr, node_attr, force=True)

        bevel_attr = vis_node + "." + cls.BEVEL_ATTR
        bevel_msg_attr = bevel_node + ".message"
        if not cmds.isConnected(bevel_msg_attr, bevel_attr):
            cmds.connectAttr(bevel_msg_attr, bevel_attr, force=True)

        # Copy the bevel input mesh to the vis_mesh
        cmds.connectAttr(input_connection, vis_mesh + ".inMesh")
        # TODO: figure out how to force a dgeval
        #       for now doing a refresh works.
        #       This may run like shit on a large scene
        cmds.refresh()
        cmds.disconnectAttr(input_connection, vis_mesh + ".inMesh")

        # Offset the node from the src node
        if offset:
            bb = om.MFnDagNode(mapi.get_mobject(src_node)).boundingBox
            cmds.move(bb.width * 1.25, 0, 0, vis_node, relative=True)

        # Select the new node.
        cmds.select(vis_node)

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
        current_edges = cmds.getAttr(bevel_node + ".inputComponents") or []
        if current_edges:
            # Remap to a pynode mesh edge
            current_edges = [vis_node + "." + edge
                             for edge in current_edges]
            if flatten:
                current_edges = cmds.ls(current_edges, flatten=True, long=True)

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
            components = cmds.ls(selection=True, flatten=True, long=True)
        else:
            components = cmds.ls(components, flatten=True)

        face_map = defaultdict(set)
        edge_map = defaultdict(set)

        for component in components:
            key = nodepath.node(component)
            # Faces
            if cmds.filterExpand(component, sm=34):
                face_map[key].add(component)
            # Edge
            elif cmds.filterExpand(component, sm=32):
                edge_map[key].add(component)
            # Vertex
            elif cmds.filterExpand(component, sm=31):
                edges = cmds.polyListComponentConversion(component,
                                                         toEdge=True)
                for edge in cmds.ls(edges, flatten=True, long=True):
                    edge_map[key].add(edge)
            else:
                cmds.warning("Component not supported %s" % component)

        # Get the edge perimeter of all the faces at once
        for node, face_map in face_map.iteritems():
            edge_perimeter = cmds.polyListComponentConversion(face_map,
                                                              toEdge=True,
                                                              border=True)
            for edge in cmds.ls(edge_perimeter, flatten=True, long=True):
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
                cmds.warning("Node %s is not a vis node" % vis_node)
                continue
            # Make sure there is a bevel node
            bevel_node = cls.get_vis_bevel(vis_node)
            if bevel_node is None:
                cmds.warning("Node %s not supported" % vis_node)
                continue

            current_edges = cls.get_bevel_edges(bevel_node)

            cls._set_edges(bevel_node, list(selected_edges), current_edges)
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
                cmds.warning("Node %s is not a vis node" % vis_node)
                continue
            # Make sure there is a bevel node
            bevel_node = cls.get_vis_bevel(vis_node)
            if bevel_node is None:
                cmds.warning("Node %s not supported" % vis_node)
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
            cmds.select(*edges)
            compressed_edges = []
            for edge in cmds.ls(selection=True, long=True):
                compressed_edges.append(edge.split(".")[-1])

        cmds.setAttr(bevel_node + ".inputComponents",
                     *[len(compressed_edges)] + compressed_edges,
                     type="componentList")

    @classmethod
    def _colorize(cls, node):
        """"Colorize the mesh by using the crease functionality

        Args:
            node: can be the vis_node, bevel_node or src_node

        """
        bevel_node = cls.get_vis_bevel(node)
        if bevel_node is None:
            raise RuntimeError("Bevel not found on %s" % node)

        edges = cls.get_bevel_edges(bevel_node)
        vis_node = cls.get_vis_node(node)
        # Remove the crease from all the edges
        cmds.polyCrease(vis_node + ".e[:]", createHistory=False, value=0)
        # Set the crease of all the edges
        # value does not bolden the display in the viewport
        cmds.polyCrease(edges, createHistory=False, value=5)

    @classmethod
    def get_vis_bevel(cls, node):
        """Get the bevel currently being shown

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            bevel node
        """
        # Given the vis_node get the connection to the bevel attribute
        if len(cmds.ls(node + "." + cls.NODE_ATTR, node + "." + cls.NODE_ATTR)) == 2:
            connections = cmds.listConnections(node + "." + cls.BEVEL_ATTR) or []
            return nodepath.full_path(connections[0])

        # Loop through the attributes on both sides of the message connection
        connections = cmds.listConnections(node + ".message", plugs=True) or []
        for connection in connections:
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            if nodepath.attr(connection) in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                # Recurse back knowing we have the vis node but it will
                #   check but it will make sure it has both attributes
                return cls.get_vis_bevel(nodepath.full_path(nodepath.node(connection)))

    @classmethod
    def get_vis_node(cls, node):
        """Get the vis_node

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            vis node
        """
        # If we have both attributes then it is the vis_node
        if len(cmds.ls(node + "." + cls.NODE_ATTR, node + "." + cls.NODE_ATTR)) == 2:
            return node

        # Loop through the attributes on both sides of the message connection
        connections = cmds.listConnections(node + ".message", plugs=True) or []
        for connection in connections:
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            if nodepath.attr(connection) in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                # Recurse back knowing we have the vis node but it will
                #   check but it will make sure it has both attributes
                return cls.get_vis_node(nodepath.full_path(nodepath.node(connection)))

    @classmethod
    def get_src_node(cls, node):
        """Get the src_node

        Args:
            node: can be the vis_node, bevel_node or src_node

        Returns:
            src node
        """
        # Given the vis_node get the connection to the bevel attribute
        if len(cmds.ls(node + "." + cls.NODE_ATTR, node + "." + cls.NODE_ATTR)) == 2:
            # Find the vis_node by checking if the connection has one of
            #   the custom attributes
            connections = cmds.listConnections(node + "." + cls.NODE_ATTR) or []
            return nodepath.full_path(connections[0])

        # Loop through the attributes on both sides of the message connection
        connections = cmds.listConnections(node + ".message", plugs=True) or []
        for connection in connections:
            # Recurse back knowing we have the vis node but it will
            #   check but it will make sure it has both attributes
            if nodepath.attr(connection) in [cls.BEVEL_ATTR, cls.NODE_ATTR]:
                return cls.get_src_node(nodepath.full_path(nodepath.node(connection)))

    @classmethod
    def remove_vis_bevel(cls, src_node):
        """Given the src_node remove the vis bevel nodes

            If the vis_node is currently in the selection the src_node
            will be selected instead
        """
        vis_node = cls.get_vis_node(src_node)
        if vis_node:
            if vis_node in cmds.ls(selection=True, long=True):
                cmds.select(src_node, add=True)
            cmds.delete(vis_node)
