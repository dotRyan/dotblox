import maya.api.OpenMaya as om
from maya import cmds


def get_mobject(node):
    """

    Args:
        node (str):

    Returns:
        om.MObject:
    """
    if isinstance(node, om.MObject):
        return node
    selection = om.MSelectionList()
    selection.add(node)
    if selection.length():
        return selection.getDependNode(0)

def get_component_mobject(component):
    """

    Args:
        component:

    Returns:
        om.MObject:
    """
    if isinstance(component, om.MObject):
        return component
    selection = om.MSelectionList()
    selection.add(component)
    if selection.length():
        _, comp = selection.getComponent(0)
        return comp


def get_shape(node):
    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
    if shapes:
        return shapes[0]
