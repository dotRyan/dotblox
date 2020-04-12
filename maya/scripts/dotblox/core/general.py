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