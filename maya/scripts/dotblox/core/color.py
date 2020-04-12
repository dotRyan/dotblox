from pymel import core as pm


def color_managed_convert(rgbf):
    """Convert the given color to the current workspace"""
    cm_enabled = pm.colorManagementPrefs(query=True, cmEnabled=True)
    if not cm_enabled:
        return rgbf

    # Note: maybe one day autodesk will provide us with the builtin libraries
    #       currently this requires third party libraries
    cm_ocio_enabled = pm.colorManagementPrefs(query=True, cmConfigFileEnabled=True)
    if cm_ocio_enabled:
        pm.warning("OCIO config enabled. 2.2 Gamma is being used for color conversion")

    srgb_to_linear = lambda x: x / 12.92 if x < 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    return [srgb_to_linear(i) for i in rgbf]
