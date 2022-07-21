from PySide2 import QtWidgets


class ConfigDialog(QtWidgets.QDialog):
    """Dialog for editing/creating a new root path in a config"""
    def __init__(self, config_path, path=None, label=None, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)

        self.setWindowTitle("Code Wall: Config Editor")

        self.ui = ConfigDialogUI()
        self.ui.setup_ui(self)

        self.ui.explore_btn.clicked.connect(self._on_path_choose)
        self.ui.buttons.accepted.connect(self.accept)
        self.ui.buttons.rejected.connect(self.reject)

        self.ui.message.setText("Add path to config %s" % config_path)
        if path:
            self.ui.path_field.setText(path)
            self.ui.message.setText("Updating config %s" % config_path)

        if label:
            self.ui.label_field.setText(label)

    def _on_path_choose(self):
        """Open up the dile choose dialog"""
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(dialog.DirectoryOnly)
        if dialog.exec_():
            self.ui.path_field.setText(dialog.selectedFiles()[0].replace("\\", "/"))

    def result(self):
        """ Get the result of the dialog

        Returns:
            tuple: contains the label, path and relative option
        """
        return self.ui.label_field.text(), self.ui.path_field.text(), self.ui.relative_chkbx.isChecked()


class ConfigDialogUI():
    def setup_ui(self, widget):
        self.message = QtWidgets.QLabel()
        self.path_field = QtWidgets.QLineEdit()
        self.label_field = QtWidgets.QLineEdit()
        self.explore_btn = QtWidgets.QPushButton("...")
        self.relative_chkbx = QtWidgets.QCheckBox()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save
            | QtWidgets.QDialogButtonBox.Close)

        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.path_field)
        path_layout.addWidget(self.explore_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Label:", self.label_field)
        form_layout.addRow("Path:", path_layout)
        form_layout.addRow("Relative Path:", self.relative_chkbx)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.message)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.buttons)
        # QtWidgets.QDialogButtonBox()
        widget.setLayout(main_layout)
