from maya import cmds


def name(node):
    """Return the name of a node path"""
    return node.rsplit("|", 1)[-1]

def leafname(node):
    """Return the name of a node without the namespace"""
    return name(node).rsplit(":", 1)[-1]

def namespace(node):
    """Get the namespace of a node"""
    return name(node).split(":")

def parent(node):
    """Get the nodes parent"""
    return node.rsplit("|", 1)[0]

def node(node):
    """Remove the component part of a path"""
    return node.split(".")[0]

def attr(node):
    if "." in node:
        return node.split(".")[-1]

def join(*nodes):
    return "|".join(nodes)

def ancestors(node):
    return [node.rsplit("|", i)[0] for i in range(1, node.count("|"))]


def full_path(node):
    nodes = cmds.ls(node, long=True)
    if len(nodes) != 1:
        raise RuntimeError("Node \"%s\" does not exist or is not unique" % node)
    return nodes[0]
