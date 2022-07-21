import datetime
import os
import shutil
from PySide2 import QtWidgets
from dotblox import config
from dotblox.tools.codewall.ui.codeeditor import CodeEditor

DEBUG = False
ARCHIVE_FOLDER_NAME = "__archive"


def create_new_folder_dialog(path):
    """Dialog for creating a new folder under the given path
    Args:
        path: path to create the folder under

    Returns:
        bool: success
    """
    new_folder, accepted = QtWidgets.QInputDialog.getText(
        None,
        "Code Wall: New Folder",
        "Folder Name:")

    if not accepted:
        return False

    if new_folder == "":
        QtWidgets.QMessageBox.information(None,
                                          "Code Wall: Invalid",
                                          "No name Specified.")
        return create_new_folder_dialog(path)

    new_path = os.path.join(path, new_folder)

    if os.path.exists(new_path):
        QtWidgets.QMessageBox.information(None,
                                          "Code Wall: Invalid",
                                          "Folder already exists!")
        return create_new_folder_dialog(path)

    if DEBUG:
        print("Creating new folder " + new_path)
        return True

    os.mkdir(new_path)
    return True


def code_editor(path, parent):
    """Create a code editor dialog with the given path

    Args:
        path: path to file or directory
        parent: file view widget

    """
    win = CodeEditor(parent.hook, path, parent)
    win.show()


def rename_dialog(path):
    """

    Args:
        path: path to rename

    Returns:
        bool: success
    """
    parent_dir = os.path.dirname(path)
    name = os.path.basename(path)

    while True:
        new_name, accepted = QtWidgets.QInputDialog.getText(
            None,
            "Code Wall: Rename {name}".format(
                name=name),
            "New Name:",
            QtWidgets.QLineEdit.Normal,
            name)

        if not accepted:
            return False

        if new_name == "":
            QtWidgets.QMessageBox.information(None,
                                              "Code Wall: Rename",
                                              "No Name specified")
            name = new_name
            continue

        new_path = os.path.join(parent_dir, new_name)

        if os.path.exists(new_path):
            QtWidgets.QMessageBox.critical(None,
                                           "Code Wall: Invalid",
                                           "Path already exists!")

            name = new_name
            continue

        if DEBUG:
            print("Renaming {src} to {dst}".format(src=path, dst=new_path))
            return True
        os.rename(path, new_path)
        return True


def remove(path, archive_root=None):
    """

    Args:
        path: path to remove
        archive_root: optionally include an archive root to instead move
                        rather than delete

    Returns:
        bool: success
    """
    dialog = QtWidgets.QMessageBox(None, "", "")
    # Bug where the text is not showing up
    dialog.setWindowTitle("Code Wall: Delete")
    dialog.setText("Are you sure you want to delete {name}?".format(
        name=os.path.basename(path)))
    if archive_root is not None:
        archive = dialog.addButton("Archive", QtWidgets.QMessageBox.AcceptRole)
    delete = dialog.addButton("Delete", QtWidgets.QMessageBox.DestructiveRole)
    cancel = dialog.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
    dialog.exec_()

    clicked_button = dialog.clickedButton()

    if clicked_button == cancel:
        return False

    if archive_root is not None and clicked_button == archive:
        archive_path = os.path.join(archive_root, ARCHIVE_FOLDER_NAME)

        if DEBUG:
            print ("Archiving {path} to {archive_path}".format(
                path=path,
                archive_path=archive_path))
            return True

        if not os.path.exists(archive_path):
            os.mkdir(archive_path)

        name, ext = os.path.splitext(os.path.basename(path))
        shutil.move(path, os.path.join(
            archive_path,
            "{name}.{time}{ext}".format(
                name=name,
                time=datetime.datetime.now().strftime("%Y%m%d.%H%M"),
                ext=ext
            )))

    if clicked_button == delete:
        if DEBUG:
            print ("Deleting {path}".format(path=path))
            return True

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    return False


class Config(config.ConfigJSON):
    """Handles the read/write of the config files"""
    PATH = "path"
    LABEL = "label"

    def __init__(self, path):
        config.ConfigJSON.__init__(self, path)
        self.roots = {}

    def get_roots(self):
        """Get all the root paths

        Returns:
            list: list of all paths
        """
        result = []
        with self.io as data:
            for path in data:
                result.append(path)
        return result

    def expand_path(self, root):
        """Expand the given root path of environment variables,
        home directory and relative paths.

        Args:
            root (str): root path

        Returns:
            str: resolved path
        """
        root = os.path.expandvars(root)
        root = os.path.expanduser(root)

        cwd = os.getcwd()
        os.chdir(os.path.dirname(self.path))
        abs_path = os.path.abspath(root)
        os.chdir(cwd)
        return abs_path

    def get_relative_path(self, path):
        """
        Try to get a relative path to the config

        Args:
            path (str): path to operate on

        Returns:
            str: relative path
        """
        try:
            return os.path.relpath(
                path,
                os.path.dirname(self.path)).replace("\\", "/")
        except:
            return path

    def get_label(self, root):
        """Get the label of a root path

        Args:
            root (str): root path

        Returns:
            str|None: label or None if not found
        """
        with self.io as data:
            return data[root].get(self.LABEL)

    def get_order(self, root, default=None):
        """Get the tab order of the root path

        Args:
            root (str): root path
            default (any): if no order is given

        Returns:
            int|float: order number
        """
        with self.io as data:
            return data[root].get(self.ORDER, default)

    def set_order(self, root, order):
        """Set the order number of the root path

        Args:
            root (str): root path
            order (int): order number

        """
        with self.io as data:
            data[root][self.ORDER] = order

    def remove_root(self, root):
        """Remove the given root path

        Args:
            root (str): root path to remove

        """
        with self.io.write() as data:
            del data[root]

    def add_root(self, path, label=None):
        """Add a new root path

        Args:
            path(str): path to add
            label(str): display label for the tab

        """
        with self.io.write() as data:
            item = data.get(path, {})
            if label:
                item.update({self.LABEL: label})
            data[path] = item

    def update_label(self, root, label):
        """Update the label of the given root path

        Args:
            root(str): root path
            label(str): label to update to. Set to any falsey value to remove
        """
        with self.io.write() as data:
            del data[root][self.LABEL]
            if label:
                data[root][self.LABEL] = label

    def update_root(self, old, new):
        """Update a root path to a new path

        Args:
            old(str): old root path
            new(str): new root path

        """
        with self.io.write() as data:
            data[new] = data[old]
            del data[old]


class StateConfig(config.ConfigJSON):
    """Save the current state of the interface"""
    EXPANDED_STATES = "states"
    CURRENT_TAB = "current_tab"
    READ_ONLY = "read_only"
    TAB_ORDER = "tab_order"

    def __init__(self, app):
        self.app = app
        config.ConfigJSON.__init__(self, config.get_global_settings_file("codewall-state.dblx", create=False),
                                   default={})
        with self.io.write() as data:
            if self.app not in data:
                data[self.app] = {self.EXPANDED_STATES: {}}

    def set_read_only(self, value):
        with self.io.write() as data:
            data[self.app][self.READ_ONLY] = value

    def get_read_only(self, default=True):
        with self.io as data:
            return data[self.app].get(self.READ_ONLY, default)

    def set_state(self, root_path, item_path):
        """Set the expanded state

        Args:
            root_path(str): root path from config
            item_path(str): relative path

        """
        with self.io.write() as data:
            link = data[self.app][self.EXPANDED_STATES]
            if root_path not in link:
                link[root_path] = [item_path]
            elif item_path not in link[root_path]:
                link[root_path].append(item_path)

    def remove_state(self, root_path, item_path):
        """Remove the expanded state

        Args:
            root_path(str): root path from config
            item_path(str): relative path

        """
        with self.io.write() as data:
            link = data[self.app][self.EXPANDED_STATES]
            if root_path in link:
                if item_path in link[root_path]:
                    link[root_path].remove(item_path)

    def get_states(self, root_path):
        """

        Args:
            root_path(str): root path from config

        Returns:
            list: list of files with all states
        """
        with self.io as data:
            if root_path in data[self.app][self.EXPANDED_STATES]:
                return data[self.app][self.EXPANDED_STATES][root_path]
        return []

    def set_current_tab(self, root_path):
        """Set the current tab

        Args:
            root_path(str): root path from config

        """
        with self.io.write() as data:
            data[self.app][self.CURRENT_TAB] = root_path

    def get_current_tab(self):
        """Get the current tab

        Returns:
            str: root path of config
        """
        with self.io as data:
            return data[self.app].get(self.CURRENT_TAB)

    def get_tab_order(self):
        """Get the order of the tabs

        Returns:
            list: list of root paths
        """
        with self.io.write() as data:
            return data[self.app].get(self.TAB_ORDER, [])

    def set_tab_order(self, paths):
        """Set the current tab order with the given paths

        Args:
            paths (list[str]): tab paths in order
        """
        with self.io.write() as data:
            data[self.app][self.TAB_ORDER] = paths
