from dotbloxlib.color import materialdesigncolors as mdc


def color_hex_to_rgbf(hex_color):
    # 0-255
    rgb = [int(hex_color[i: i + 2], 16) for i in [1, 3, 5]]

    # 0-1
    rgbf = color_rgb_to_rgbf(*rgb)

    return rgbf


def color_rgb_to_rgbf(*rgb):
    # 0-1
    return [i / 255.0 for i in rgb]