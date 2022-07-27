import os


class Bootstrap():
    """Install a templated file to a given location"""
    def __init__(self):
        pass

    def install(self, force=False):
        """Install the file

        Args:
            force(bool): force the file to be reinstalled

        """
        install_path = self.install_path()

        if self.is_installed():
            if not force:
                return
            print("Module {path} will be overwritten".format(path=install_path))


        with open(self.template_path(), "r") as f:
            template_contents = f.read()

        parent_dir = os.path.dirname(install_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)


        contents = self.parse(template_contents)

        with open(install_path, "w") as f:
            f.write(contents)

    def uninstall(self):
        """Uninstall this file"""
        if not self.is_installed():
            raise IOError("File not installed " + self.install_path())
        os.remove(self.install_path())

    def is_installed(self):
        """Check to see if the file already exists in the install path"""
        return os.path.exists(self.install_path())

    def template_path(self):
        """Return the path to where the template file lives"""
        raise NotImplementedError("Method not implemented")

    def install_path(self):
        """Return the full path of the installation"""
        raise NotImplementedError("Method not implemented")

    def parse(self, contents):
        """Parse the contents of the file and return the results."""
        raise NotImplementedError("Method not implemented")
