import os.path
import traceback

from PySide2 import QtCore, QtGui, QtWidgets

from dotblox.qt import pythonsyntax
from dotblox.qt.texteditorwidget import TextEditorWidget


class CodeEditor(QtWidgets.QWidget):
    """Dialog to edit/create script files"""

    def __init__(self, hook, path, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("Code Wall: Code Editor ~ " + path)

        self.setWindowFlags(QtCore.Qt.Window)
        self.ui = CodeEditorUI()
        self.ui.setup_ui(self)

        bg_color = "#272822"

        self.hook = hook
        pythonsyntax.PythonHighlighter(self.ui.editor.document())
        palette = self.ui.editor.palette()
        palette.setColor(palette.Base, QtGui.QColor(bg_color))
        palette.setColor(palette.Text, QtGui.QColor("#FFFFFF"))
        # Fix for houdini which cannot be set by a palette
        self.ui.editor.setStyleSheet("background-color: %s;" % bg_color)
        self.ui.editor.setPalette(palette)
        self.ui.reload_btn.clicked.connect(self._on_reload)
        self.ui.save_btn.clicked.connect(self._on_save)
        self.ui.editor.on_execute_selected.connect(self._execute_text)
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.execute_selection_btn.clicked.connect(self._on_execute_selected)
        self.ui.execute_btn.clicked.connect(self._on_execute)

        self.load(path)

    def _execute_text(self, text):
        """Execute the selected text

        Args:
            text(str): text to execute

        """
        try:
            self.hook.execute_text(self._sanitize_text(text),
                                   self.ui.name_field.text() or None)
        except Exception as e:
            traceback.print_exc(e)

    def _on_execute_selected(self):
        """Execute the selected text"""
        self._execute_text(self.ui.editor.get_all_selected_text())

    def _on_execute(self):
        """Execute all the text"""
        self._execute_text(self.ui.editor.get_text())

    def load(self, path):
        """Set up the dialog based on the given path

        Args:
            path(str): path on disk

        """
        self.orig_path = path
        self.initial_string = None

        if os.path.isdir(path):
            self.ui.folder_field.setText(path)
            self.create = True
            self.initial_string = ""
        elif os.path.isfile(path):
            self.create = False
            self.ui.folder_field.setText(os.path.dirname(path))
            self.ui.name_field.setText(os.path.basename(path))
            cursor = self.ui.editor.textCursor()
            with open(self.orig_path, "r") as f:
                self.ui.editor.setPlainText(f.read())
            self.ui.editor.setTextCursor(cursor)
            self.initial_string = self.ui.editor.toPlainText()
        elif not os.path.exists(path):
            self.ui.folder_field.setText(os.path.dirname(path))
            self.ui.name_field.setText(os.path.basename(path))
            self.create = True
            self.initial_string = ""
        self.ui.reload_btn.setVisible(not self.create)

    def _on_reload(self):
        """Reload the current script"""
        if not self._is_modified():
            return

        self.load(self.orig_path)

    def _on_save(self):
        """Save the current script"""
        title = "Code Wall: Saving Error"

        new_name = self.ui.name_field.text()
        old_name = os.path.basename(self.orig_path)
        if not new_name:
            QtWidgets.QMessageBox.critical(
                None,
                title,
                "No file name specified."
            )
            return False

        _, ext = os.path.splitext(new_name)
        supported = self.hook.get_supported_extensions()
        if ext not in supported:
            QtWidgets.QMessageBox.critical(
                self,
                title,
                "File extension {current} is not supported. Supported"
                " extensions are {supported}".format(
                    current=ext,
                    supported = " , ".join(supported)
                ))
            return False

        if not self.create:
            if old_name != new_name:
                result = QtWidgets.QMessageBox.question(
                    self,
                    title,
                    "File name has been changed from {old} to {new}. Save changes?".format(
                        old=old_name,
                        new=new_name
                    )
                )
                if result != QtWidgets.QMessageBox.Yes:
                    return False

        path = os.path.join(self.ui.folder_field.text(), new_name)
        self.initial_string = self._sanitize_text(self.ui.editor.get_text())
        with open(path, "w") as f:
            f.write(self.initial_string)
        return True

    def _sanitize_text(self, text):
        """Replace tabs with 4 spaces"""
        return text.replace("\t", " " * 4)

    def show(self):
        """Override s=to set focus on editor"""
        QtWidgets.QWidget.show(self)
        self.ui.editor.setFocus()

    def _is_modified(self):
        """Check if the text has been modified"""
        if self.initial_string is None:
            return False
        return self.initial_string != self._sanitize_text(self.ui.editor.get_text())

    def close(self):
        """Prevent closing if a file is modified"""
        if self._is_modified():
            file_name = self.ui.name_field.text()
            result = QtWidgets.QMessageBox.question(
                None,
                "Code Wall: Editor Close",
                "Save changes to %s?" % file_name if file_name else "untitled",
                QtWidgets.QMessageBox.Save
                | QtWidgets.QMessageBox.Discard
                |  QtWidgets.QMessageBox.Cancel
            )
            if result == QtWidgets.QMessageBox.Save:
                if not self._on_save():
                    return
            elif result == QtWidgets.QMessageBox.Cancel:
                return

        QtWidgets.QWidget.close(self)

class EditorWidget(TextEditorWidget):
    """Reimplement for adding convenience functions"""
    on_execute_selected = QtCore.Signal(str)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return \
                and event.modifiers() == QtCore.Qt.ControlModifier:
            self.on_execute_selected.emit(self.get_all_selected_text())
            return
        TextEditorWidget.keyPressEvent(self, event)

    def get_text(self):
        """Get all the text"""
        return self.toPlainText()

    def get_all_selected_text(self):
        """Get the full lines of selected text"""
        cursor = self.textCursor()
        min_pos = min(cursor.anchor(), cursor.position())
        max_pos = max(cursor.anchor(), cursor.position())
        cursor.setPosition(min_pos)
        cursor.select(cursor.SelectionType.LineUnderCursor)
        cursor.setPosition(max_pos, cursor.KeepAnchor)
        cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
        return cursor.selection().toPlainText()


class CodeEditorUI():
    def setup_ui(self, widget):
        main_layout = QtWidgets.QVBoxLayout()

        self.folder_field = QtWidgets.QLabel()
        self.name_field = QtWidgets.QLineEdit()
        self.reload_btn = QtWidgets.QPushButton("Reload")
        self.editor = EditorWidget()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.close_btn = QtWidgets.QPushButton("Close")
        self.execute_btn = QtWidgets.QPushButton("Execute")
        self.execute_selection_btn = QtWidgets.QPushButton("Execute Selection")
        bottom_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.folder_field)
        header_layout.addWidget(self.name_field)
        header_layout.addWidget(self.reload_btn)
        header_layout.setStretch(0, 4)
        header_layout.setStretch(1, 1)
        header_layout.setStretch(2, 0)

        toolbar_layout = QtWidgets.QHBoxLayout()
        toolbar_layout.addWidget(self.execute_btn)
        toolbar_layout.addWidget(self.execute_selection_btn)
        toolbar_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addSpacerItem(bottom_spacer)
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addWidget(self.close_btn)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.editor)
        main_layout.addLayout(bottom_layout)

        widget.setLayout(main_layout)
