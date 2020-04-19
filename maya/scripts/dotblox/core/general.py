import math

from maya import cmds
import maya.api.OpenMaya as om

from dotblox.core import mapi, nodepath
from dotblox.core.constant import AXIS, DIRECTION


def pivot_to_bb(nodes=None, axis=AXIS.Y, direction=DIRECTION.NEGATIVE, center=False):
    """Move the pivot of the given objects to the given direction

    Args:
        axis (str): x, y, z
        direction (int): +:0 |  1 == negative
        center (bool): center the pivot in the given axis
        *nodes:

    Notes:
        Operates on the given nodes individually not as a group

    """
    if isinstance(nodes, (str, unicode)):
        nodes = [nodes]

    if nodes is None:
        nodes = cmds.ls(selection=True, long=True)

    for node in nodes:
        # Determine the min and max of the given axis
        max_value = float("-inf")
        min_value = float("inf")
        for child in cmds.listRelatives(node, allDescendents=True, fullPath=True) or []:
            # Make sure we are not including intermediate shapes
            try:
                if cmds.getAttr(child + ".intermediateObject"):
                    continue
            except:
                pass
            # Safeguard against any unsupported nodes
            try:
                bb = om.MFnDagNode(mapi.get_mobject(child)).boundingBox
            except:
                continue

            max_value = max(max_value, getattr(bb.max, axis))
            min_value = min(min_value, getattr(bb.min, axis))

        # Determine the offset value to use
        value = min_value if direction else max_value
        if center:
            mid_distance = (max_value - min_value) / 2.0
            value = abs(max_value - mid_distance)

        # Create a relative offset from the current pivot
        pivot = om.MVector(
                cmds.xform(node + ".rotatePivot",
                           query=True,
                           translation=True,
                           objectSpace=True))
        offset = om.MVector()

        pivot_axis = getattr(pivot, axis)
        # Inverse the value
        if center and pivot_axis < 0:
            value *= -1

        setattr(offset,
                axis,
                value - pivot_axis)

        cmds.move(offset.x,
                  offset.y,
                  offset.z,
                  node + ".rotatePivot",
                  node + ".scalePivot",
                  objectSpace=True,
                  relative=True)

def get_tool_pivot_position():
    """Get the current pivot from the move tool
    The current tool context is kept
    """
    current_tool = cmds.currentCtx()
    cmds.setToolTo("Move")
    position = cmds.manipMoveContext('Move', query=True, position=True)
    cmds.setToolTo(current_tool)
    return position

def get_face_rotation(mesh_face, up_axis=AXIS.Y, direction=DIRECTION.POSITIVE):
    """Get the world space rotation of the given face
    Args:
        mesh_face: the shape and face to use `node.face[index]`
        up_axis (AXIS): the axis that matches the normal of the given face
        direction (DIRECTION): positive or negative

    Notes:
               normal
              3__|____2
              /  |___/___ edge
            0/__/___/1
               /
            tangent
    """
    if not cmds.filterExpand(mesh_face, sm=34):
        raise RuntimeError("Given mesh_face is not \"node.f[index]\" got \"%s\"" % mesh_face)
    if len(cmds.ls(mesh_face, flatten=True)) != 1:
        raise RuntimeError("Given mesh_face must be a single index got \"%s\"" % mesh_face)

    mobj = mapi.get_mobject(mesh_face)
    component = mapi.get_component_mobject(mesh_face)

    comp_fn = om.MFnSingleIndexedComponent(component)
    face_id = comp_fn.element(0)

    mdag_path = om.MDagPath.getAPathTo(mobj)
    face_it = om.MItMeshPolygon(mdag_path)
    face_it.setIndex(face_id)
    mesh_fn = om.MFnMesh(mdag_path)

    space = om.MSpace.kWorld
    normal_vector = face_it.getNormal(space=space)

    f_vertices = face_it.getVertices()
    p0 = mesh_fn.getPoint(f_vertices[0], space=space)
    p1 = mesh_fn.getPoint(f_vertices[1], space=space)

    edge_vector = (p1 - p0).normal()

    tangent_vector = edge_vector ^ normal_vector

    inverse = lambda x: x * -1

    # Swap the axes to set the normal as the up axis
    if up_axis == AXIS.X and direction == DIRECTION.POSITIVE:
        order = [normal_vector, edge_vector, tangent_vector]  # +x
    elif up_axis == AXIS.X and direction == DIRECTION.NEGATIVE:
        order = [inverse(normal_vector), edge_vector, tangent_vector]  # -x
    elif up_axis == AXIS.Y and direction == DIRECTION.POSITIVE:
        order = [inverse(edge_vector), normal_vector, tangent_vector]  # +y
    elif up_axis == AXIS.Y and direction == DIRECTION.NEGATIVE:
        order = [edge_vector, inverse(normal_vector), inverse(tangent_vector)]  # -y
    elif up_axis == AXIS.Z and direction == DIRECTION.POSITIVE:
        order = [tangent_vector, edge_vector, normal_vector]  # +z
    elif up_axis == AXIS.Z and direction == DIRECTION.NEGATIVE:
        order = [tangent_vector, inverse(edge_vector), inverse(normal_vector)]  # -z

    matrix_arr = [[0] * 4 for i in range(4)]

    for i, v in enumerate(order):
        for j, k in enumerate(v):
            matrix_arr[i][j] = k

    matrix = om.MMatrix(matrix_arr)
    transform_matrix = om.MTransformationMatrix(matrix)

    return [math.degrees(angle) for angle in transform_matrix.rotation()]


def snap_to_mesh_face(mesh, driven , point, up_axis=AXIS.Y, direction=DIRECTION.POSITIVE, translate=True, rotate=True):
    """Find the closest point on the given mesh and snap and rotate the given object
    to it

    Args:
        mesh: the mesh to find the closest normal to the given point
        driven: the object to move and rotate
        point: the point to find the closest
                                          point on the mesh
        up_axis (AXIS): the axis that matches the normal of the given face
        direction (DIRECTION): positive or negative

    """

    mesh_mobj = mapi.get_mobject(mesh)
    mesh_fn = om.MFnMesh(om.MDagPath.getAPathTo(mesh_mobj))

    closest_point, closest_face = mesh_fn.getClosestPoint(om.MPoint(point), space=om.MSpace.kWorld)

    if rotate:
        rotation = get_face_rotation(mesh + ".f[%d]" % closest_face,
                                     up_axis=up_axis,
                                     direction=direction)
        cmds.rotate(rotation[0],
                    rotation[1],
                    rotation[2],
                    driven,
                    absolute=True,
                    worldSpace=True)

    if translate:
        cmds.move(closest_point.x,
                  closest_point.y,
                  closest_point.z,
                  driven,
                  rotatePivotRelative=True)
