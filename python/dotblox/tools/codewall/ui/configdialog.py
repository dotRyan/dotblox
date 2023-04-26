import os.path

from PySide2 import QtWidgets

import dotblox.config
from dotblox.tools.codewall.api import Config


class ConfigDialog(QtWidgets.QDialog):
    """Dialog for editing/creating a new root path in a config

    Depending on the arguments passed in; the operational mode changes.

    Create:
        ConfigDialog(config=None, path=None)
    Add:
        ConfigDialog(config=config, path=None)
    Update:
        ConfigDialog(config=config, path=path)

    """

    class MODE():
        [UPDATE, ADD, CREATE] = range(3)

    def __init__(self,hook, config=None, path=None, parent=None):
        """
        Args:
            hook (Hook): Codewall Hook object initialized from the widget.
            config (Config): Optional config to work on.
            path (str):
            parent (QtWidgets.QWidget): parent widget inherited from Qt
        """

        QtWidgets.QDialog.__init__(self, parent=parent)

        self.setWindowTitle("Code Wall: Config Editor")

        self.hook = hook
        self.config = config
        self.root = path

        self.mode = self.MODE.CREATE
        if self.config and path:
            self.mode = self.MODE.UPDATE
        elif self.config:
            self.mode = self.MODE.ADD


        self.ui = ConfigDialogUI()
        self.ui.setup_ui(self)

        self.ui.root_explore_btn.clicked.connect(lambda: self._on_path_choose(self.ui.root_field))
        self.ui.root_default_btn.clicked.connect(self._on_set_root_default)
        self.ui.buttons.accepted.connect(self._on_accept)
        self.ui.buttons.rejected.connect(self.reject)

        _, default_root_path = self.hook.get_default_root_path()

        self.ui.root_default_btn.setVisible(bool(default_root_path and self.config and default_root_path not in self.config.get_roots()))

        # Update the interface based on the current mode
        if self.mode == self.MODE.UPDATE :
            message = "Update Config:"
        elif self.mode == self.MODE.ADD :
            message = "Add to Config:"
        else:
            message = "Config Path:"

        is_create = self.mode == self.MODE.CREATE
        self.ui.message.setText(message)

        self._build_config_combo(is_create)
        if is_create:
            default_config_path = self.hook.get_default_config_path()
            if default_config_path:
                self.ui.config_combo.setCurrentText(default_config_path)
        else:
            parent_dir = os.path.dirname(config.path)
            self.ui.config_combo.setCurrentText(parent_dir)
            if self.ui.config_combo.currentText() != parent_dir:
                raise RuntimeError("Unable to set config dialog to %s" % parent_dir)
            if self.root:
                self.ui.opt_removeable.setChecked(
                    self.config.get_root_option(
                        self.root,
                        self.config.ROOT_OPT_REMOVABLE,
                        True))

        self.ui.config_combo.setDisabled(not is_create)

        if self.root:
            self.ui.root_field.setText(self.root)
            self.ui.label_field.setText(config.get_label(path))

        self.ui.opt_removeable.setChecked(True)

    def _on_accept(self):
        label = self.ui.label_field.text()
        root = self.ui.root_field.text()
        make_relative = self.ui.relative_chkbx.isChecked()
        opt_removable = self.ui.opt_removeable.isChecked()

        if not root:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "No root given."
            )
            return

        if self.mode == self.MODE.CREATE:
            config_dir = self.ui.config_combo.currentText()

            if not os.path.exists(config_dir):
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Config folder does not exist."
                )
                return


            if not os.path.isdir(config_dir):
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Config root given is not a directory."
                )
                return

            config_path = os.path.join(config_dir, self.hook.get_config_file_name())
            new_config = Config(config_path)
            new_config.add_root(root, label, relative=make_relative)
            new_config.set_root_option(root,
                                       new_config.ROOT_OPT_REMOVABLE,
                                       opt_removable)
            self.accept()
            return
        elif self.mode == self.MODE.ADD:
            if root in self.config.get_roots():
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Root already added to config."
                )
                return

            self.config.add_root(root, label, relative=make_relative)
            self.config.set_root_option(root,
                                        self.config.ROOT_OPT_REMOVABLE,
                                        opt_removable)

            self.accept()
            return

        elif self.mode == self.MODE.UPDATE:

            updated = False

            if make_relative:
                root = self.config.get_relative_path(root)

            if label != self.config.get_label(self.root):
                updated = True
                self.config.set_label(self.root, label)

            if root != self.root:
                updated = True
                self.config.update_root(self.root, root)

            if opt_removable != self.config.get_root_option(root, Config.ROOT_OPT_REMOVABLE, True):
                updated = True
                self.config.set_root_option(root, Config.ROOT_OPT_REMOVABLE, opt_removable)

            if updated:
                self.accept()
            else:
                self.reject()
            return

    def _on_path_choose(self, field):
        """Open up the file choose dialog"""
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(dialog.DirectoryOnly)
        if dialog.exec_():
            field.setText(dialog.selectedFiles()[0].replace("\\", "/"))

    def _on_set_root_default(self):
        label, path = self.hook.get_default_root_path()
        self.ui.label_field.setText(label)
        self.ui.root_field.setText(path)
        self.ui.relative_chkbx.setChecked(False)

    def _build_config_combo(self, skip_existing=True):
        """Build the config menu based on PYTHONPATH"""
        self.ui.config_combo.clear()
        for path in dotblox.config.get_config_paths(include_global=True, global_priority=True):
            if not os.access(path, os.W_OK):
                continue
            if skip_existing and os.path.exists(os.path.join(path, self.hook.get_config_file_name())):
                continue
            self.ui.config_combo.addItem(path)


class ConfigDialogUI():
    def setup_ui(self, widget):
        self.message = QtWidgets.QLabel()
        self.expanded_label = QtWidgets.QLabel()
        self.config_combo = QtWidgets.QComboBox()
        self.root_field = QtWidgets.QLineEdit()
        self.root_default_btn = QtWidgets.QPushButton("Set to Default")
        self.root_explore_btn = QtWidgets.QPushButton("Browse")
        self.label_field = QtWidgets.QLineEdit()
        self.relative_chkbx = QtWidgets.QCheckBox("Make Relative")
        self.opt_removeable = QtWidgets.QCheckBox("Removable")

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save
            | QtWidgets.QDialogButtonBox.Close)

        root_layout = QtWidgets.QHBoxLayout()
        root_layout.addWidget(self.root_field)
        root_layout.addWidget(self.relative_chkbx)
        root_layout.addWidget(self.root_explore_btn)

        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addWidget(self.label_field)
        label_layout.addWidget(self.root_default_btn)

        option_layout_1 = QtWidgets.QHBoxLayout()
        option_layout_1.addWidget(self.opt_removeable)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.message, self.config_combo)
        form_layout.addRow("Display Name:", label_layout)
        form_layout.addRow("Library Root:", root_layout)
        form_layout.addRow("Options:", option_layout_1)


        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.buttons)
        widget.setLayout(main_layout)
