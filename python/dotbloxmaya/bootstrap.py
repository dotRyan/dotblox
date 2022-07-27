from dotblox import bootstrap
import os


class MayaModule(bootstrap.Bootstrap):
    """Base class for installing a maya module"""

    def __init__(self):
        bootstrap.Bootstrap.__init__(self)

        self.maya_app_dir = self._get_maya_app_dir()
        self.maya_module_path = os.path.join(self.maya_app_dir, "modules")

    def _get_maya_app_dir(self):
        """Determine the maya app directory

        Maya will not run if it does not exist anyway

        Returns:
            str

        Raises:
            EnvironmentError
        """
        key = "MAYA_APP_DIR"
        if key in os.environ:
            return os.environ[key]

        raise EnvironmentError("{key} not set".format(key=key))

    def install_path(self):
        return os.path.join(
            self.maya_module_path,
            os.path.basename(self.template_path()))


class DotBloxModule(MayaModule):
    """DotBlox Package bootstrap maya houdini"""

    def __init__(self):
        MayaModule.__init__(self)

        self.package_dir = __file__
        for i in range(3):
            self.package_dir = os.path.dirname(self.package_dir)

    def template_path(self):
        return os.path.join(
            self.package_dir,
            "maya",
            "dotblox.mod")

    def parse(self, contents):
        return contents.format(
            path=self.package_dir
        )


def install(force=False):
    """Install the dotblox package for maya

    Args:
        force(bool): force the installation file to be overwritten

    """
    DotBloxModule().install(force=force)


def uninstall():
    """Uninstall the dotblox package for houdini"""
    DotBloxModule().uninstall()
