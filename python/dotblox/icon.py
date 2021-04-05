import os
import glob

__ICON_CACHE = {}
def get_icon(name):
    """Get icon path of a dotblox icon"""
    cache = __ICON_CACHE.get(name)
    if cache:
        return cache

    directory = __file__.rsplit(os.sep, 3)[0]
    icon_directory = os.path.join(directory, "icons")

    files = glob.glob(os.path.join(icon_directory,  "%s*" % name))
    if files:
        __ICON_CACHE[name] = files[0]
        return files[0]

