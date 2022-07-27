import os

from dotblox import bootstrap


class HoudiniPackage(bootstrap.Bootstrap):
    """Base class for installing a houdini package"""
    def __init__(self):
        bootstrap.Bootstrap.__init__(self)
        self.hou_package_dir = os.path.join(self._get_houdini_path(), "packages")

    def _get_houdini_path(self):
        """Determine the houdini user pref directory

        Returns:
            str

        Raises:
            EnvironmentError
        """
        key = "HOUDINI_USER_PREF_DIR"
        if key in os.environ:
            return os.environ[key]

        raise EnvironmentError("{key} not set".format(key=key))

    def install_path(self):
        return os.path.join(self.hou_package_dir, os.path.basename(self.template_path()))


class DotBloxPackage(HoudiniPackage):
    """DotBlox Package bootstrap for houdini"""

    def __init__(self):
        HoudiniPackage.__init__(self)

        self.package_dir = __file__
        for i in range(3):
            self.package_dir = os.path.dirname(self.package_dir)

    def parse(self, contents):
        return contents.replace("{path}", self.package_dir.replace("\\", "/"))

    def template_path(self):
        return os.path.join(
            self.package_dir,
            "houdini",
            "dotblox.json"
        )

# Expose these as this are part of this repository
def install(force=False):
    """Install the dotblox package for houdini

    Args:
        force(bool): force the installation file to be overwritten

    """
    DotBloxPackage().install(force=force)


def uninstall():
    """Uninstall the dotblox package for houdini"""
    DotBloxPackage().uninstall()
