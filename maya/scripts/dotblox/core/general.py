import pymel.core as pm
from dotblox.core.constant import AXIS, DIRECTION


def pivot_to_bb(axis=AXIS.Y, direction=DIRECTION.NEGATIVE, center=False, *nodes):
    """Move the pivot of the given objects to the given direction

    Args:
        axis (str): x, y, z
        direction (int): +:0 |  1 == negative
        center (bool): center the pivot in the given axis
        *nodes:

    Notes:
        Operates on the given nodes individually not as a group

    """
    if not nodes:
        nodes = pm.ls(selection=True, long=True)

    for node in nodes:
        # Determine the min and max of the given axis
        max_value = float("-inf")
        min_value = float("inf")
        for child in node.listRelatives(allDescendents=True):
            # Make sure we are not including intermediate shapes
            try:
                if child.intermediateObject.get():
                    continue
            except:
                pass

            # Safeguard against any unsupported nodes
            try:
                bb = child.boundingBox()
            except:
                continue

            max_value = max(max_value, getattr(bb.max(), axis))
            min_value = min(min_value, getattr(bb.min(), axis))

        # Determine the offset value to use
        value = min_value if direction else max_value
        if center:
            mid_distance = (max_value - min_value) / 2.0
            value = abs(max_value - mid_distance)

        # Create a relative offset from the current pivot
        pivot = node.getRotatePivot(space="preTransform")
        offset = pm.dt.Vector()

        pivot_axis = getattr(pivot, axis)
        # Inverse the value
        if center and pivot_axis < 0:
            value *= -1

        setattr(offset,
                axis,
                value - pivot_axis)

        pm.move(offset.x,
                offset.y,
                offset.z,
                node.rotatePivot,
                node.scalePivot,
                objectSpace=True,
                relative=True)

def get_tool_pivot_position():
    """Get the current pivot from the move tool
    The current tool context is kept
    """
    current_tool = pm.currentCtx()
    pm.setToolTo("Move")
    position = pm.manipMoveContext('Move', query=True, position=True)
    pm.setToolTo(current_tool)
    return position

def get_face_rotation(face, up_axis=AXIS.Y, direction=DIRECTION.POSITIVE):
    """Get the world space rotation of the given face
    Args:
        face: the shape and face to use
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
    normal_vector = face.getNormal(space="world")

    # Calculate the edge vector and normalize it
    p0 = face.getPoint(0, space="world")
    p1 = face.getPoint(1, space="world")
    edge_vector = (p1 - p0).normal()

    tangent_vector = edge_vector.cross(normal_vector)

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

    matrix = pm.datatypes.Matrix(*order)
    transform_matrix = pm.datatypes.TransformationMatrix(matrix)
    return pm.datatypes.Vector(map(pm.util.degrees, transform_matrix.eulerRotation()))


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

    closest_point, closest_face = mesh.getClosestPoint(point, space="world")

    if rotate:
        rotation = get_face_rotation(mesh.f[closest_face], up_axis=up_axis, direction=direction)
        pm.rotate(driven, rotation, absolute=True, worldSpace=True)

    if translate:
        pm.move(driven, closest_point, absolute=True, worldSpaceDistance=True)
