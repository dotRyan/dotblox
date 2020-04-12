class AXIS():
    """This may be redundant but some tools map the values to 0,1,2

    Notes:
        If the maya cmd uses another way of defining an axis, those values
        should be mapped within your function

            def your_function(axis):
                axis_map = {
                    AXIS.X:0,
                    AXIS.Y:1,
                    AXIS.Z:2,
                }[axis]
    """
    X = "x"
    Y = "y"
    Z = "z"

class DIRECTION():
    """Most Maya tools use this as the settings which gets confusing.
    To keep consistency and sanity map these to a term.
    """
    POSITIVE = 0
    NEGATIVE = 1