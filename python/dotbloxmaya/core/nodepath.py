from maya import cmds


def __underworld_filter(node):
    """Removes the underworld notation from the string

    Makes sure the give node does not end with ->

    Args:
        node (str): node path

    Returns:
        str: node path
    """
    if node.endswith("->"):
        return node[:-2]
    return node


def name(node):
    """Return the name of a node path

    Args:
        node (str): node path

    Returns:
        str: last item of the path
    """
    return node.rsplit("|", 1)[-1]


def leafname(node):
    """Return the name of a node without the namespace

    Args:
        node (str): node path

    Returns:
        str: node name without namespace
    """
    return name(node).rsplit(":", 1)[-1]


def namespace(node):
    """Get the namespace of a node

    Args:
        node (str): node path

    Returns:
        str: namespace of the given node
    """
    return name(node).split(":")[0]


def parent(node):
    """Get the nodes parent

    Args:
        node (str): node path

    Returns:
        str: node path
    """
    result = __underworld_filter(node.rsplit("|", 1)[0])
    if not result and node.startswith("|"):
        return "|"
    return result


def node(node):
    """Remove the attribute/component part of a path

    Args:
        node (str): node path

    Returns:
        str: node path
    """
    return node.split(".")[0]


def attr(node, strip=False):
    """Get the attr component of a node string

    Args:
        node (str): node string
        strip (bool): return only the attribute name

    Usage:
        attr("node.e[3:4]") == "e[3:4]"
        attr("node.e[3:4]", strip=True) == "e"
    Returns:
        str: node attr part
    """
    if "." in node:
        attr = node.split(".")[-1]
        if strip:
            return attr.split("[")[0]
        return attr


def join(*nodes):
    """Join the given nodes into a |node|path

    Args:
        *nodes (str): node path

    Returns:
        str: node path
    """
    return "|".join(nodes)


def ancestors(node):
    """

    Args:
        node (str): node path

    Returns:
        list[str]: list of the given nodes ancestors
    """
    return [__underworld_filter(node.rsplit("|", i)[0]) for i in range(1, node.count("|"))]


def full_path(node):
    """Attempts to retrieve the full path name of the given node

    Args:
        node (str): node path

    Returns:
        str: node path

    Raises:
        RuntimeError: node does not exist or is not unique
    """
    nodes = cmds.ls(node, long=True)
    if len(nodes) != 1:
        raise RuntimeError("Node \"%s\" does not exist or is not unique" % node)
    return nodes[0]
