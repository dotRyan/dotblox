import os
import traceback

from PySide2 import QtWidgets, QtCore, QtGui
from dotblox.tools.codewall import api
from dotblox.icon import get_icon


class FileViewWidget(QtWidgets.QWidget):
    """Widget for viewing a script directory"""
    def __init__(self, root_path, config, state_config, hook, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.hook = hook
        self.state_config = state_config

        self.config = config
        self.config_path = root_path

        self.config_writable = self.config.is_writable()

        self.is_removable = self.config_writable and \
                            self.config.get_root_option(
                                self.config_path,
                                self.config.ROOT_OPT_REMOVABLE,
                                True)

        self.ui = FileViewWidgetUI()
        self.ui.setup_ui(self)

        self.file_system = FileSystemModel()
        name_filters = list("*" + x for x in self.hook.get_supported_extensions())
        self.file_system.setNameFilters(name_filters)
        self.ui.tree_view.setModel(self.file_system)

        self.ui.tree_view.customContextMenuRequested.connect(self._tree_view_context_menu)
        self.ui.tree_view.doubleClicked.connect(self._on_tree_view_double_click)

        self.ui.create_folder_btn.clicked.connect(lambda *x: self._on_create_folder())
        self.ui.create_script_btn.clicked.connect(lambda *x: self._on_create_script())

        self.ui.tree_view.expanded.connect(self._store_state)
        self.ui.tree_view.collapsed.connect(self._store_state)

        if root_path:
            self.set_root_path(self.config_path)
            self._restore_states()

    def set_root_path(self, path):
        """Set the root path of the widget

        Args:
            path(str): path to use

        """
        self.root_path = self.config.expand_path(path).replace("\\", "/")
        self.root_writable = os.access(self.root_path, os.W_OK)

        self.ui.actions_widget.setVisible(self.root_writable)

        layout = self.layout()
        layout.removeItem(self.ui.view_layout)
        layout.removeItem(self.ui.invalid_layout)

        if not os.path.exists(self.root_path):
            layout.addLayout(self.ui.invalid_layout)
            return

        layout.addLayout(self.ui.view_layout)
        self.file_system.setRootPath(self.root_path)
        self.ui.tree_view.setRootIndex(self.file_system.index(self.root_path))

    def _on_create_folder(self, folder_path=None):
        """Action for creating a folder

        Args:
            folder_path(str): parent directory to create the folder in

        """
        if folder_path is None:
            folder_path = self._get_selected_item_folder()

        api.create_new_folder_dialog(folder_path)

    def set_read_only(self, value):
        """Enable/Disable drag and drop within the interface"""
        self.file_system.setReadOnly(value)

    def _on_create_script(self, folder_path=None):
        """Action for creating a script

        Args:
            folder_path(str): folder path to create the script in

        """
        if folder_path is None:
            folder_path = self._get_selected_item_folder()
        api.code_editor(folder_path, self)

    def _get_selected_item_folder(self):
        """Get the path of the selected item"""
        path = self.root_path
        selected = self.ui.tree_view.selectedIndexes()
        if selected:
            file_info = self.file_system.fileInfo(selected[0])  # type: QtCore.QFileInfo
            if file_info.isFile():
                path = file_info.path()
            else:
                path = file_info.filePath()

        return path

    def _tree_view_context_menu(self, pos):
        """Context menu for the tree view

        Args:
            pos(QtCore.QPos):

        """
        index = self.ui.tree_view.indexAt(pos)  # type: QtCore.QModelIndex
        file_info = self.file_system.fileInfo(index)  # type: QtCore.QFileInfo
        file_path = file_info.filePath()  # type: str
        folder_path = file_path
        if file_info.isFile():
            folder_path = file_info.path()

        if not folder_path:
            folder_path = None

        menu = QtWidgets.QMenu(self)

        if file_info.isFile():
            menu.addAction("Run", lambda *x: self._run_file(file_path))

        if not self.root_writable:
            if menu.children():
                menu.exec_(QtGui.QCursor.pos())
            return

        menu.addSection("Create")
        action = menu.addAction(
                "New Folder",
                lambda *x: self._on_create_folder(folder_path=folder_path))
        action.setIcon(QtGui.QIcon(get_icon("dblx_folder.png")))
        action = menu.addAction(
                "New Script",
                lambda *x: self._on_create_script(folder_path=folder_path))
        action.setIcon(QtGui.QIcon(get_icon("dblx_file.png")))

        if index.isValid():
            menu.addSection("Edit")
            if not file_info.isDir():
                menu.addAction("Modify", lambda *x: self._on_modify_script(file_path))
            menu.addAction("Rename", lambda *x: api.rename_dialog(file_path))
            menu.addAction("Delete", lambda *x: api.remove(file_path, archive_root=self.root_path))

        menu.exec_(QtGui.QCursor.pos())

    def _on_tree_view_double_click(self, index):
        """Run the file on double click

        Args:Qt
            index(QtCore.QModelIndex): index of clicked item

        """
        file_info = self.file_system.fileInfo(index)
        if file_info.isDir():
            return
        self._run_file(file_info.filePath())

    def _run_file(self, file_path):
        """Run the given file

        Args:
            file_path(str): file to run

        """
        try:
            self.hook.run_file(file_path)
        except Exception as e:
            traceback.print_exc(e)

    def _on_modify_script(self, file_path):
        """Create/Edit the given file

        Args:
            file_path(str): file to modify

        """
        api.code_editor(file_path, self)

    def tab_name(self, depth=1):
        label = self.config.get_label(self.config_path)
        if label:
            return label

        return "/".join(self.root_path.split("/")[-depth:])

    def _store_state(self, index):
        """Store the state of the given index

        Args:
            index(QtCore.QModelIndex): index from the interface

        """

        path = self.file_system.fileInfo(index).filePath()
        item_path = path.replace(self.root_path, "").lstrip("/")
        if os.path.isdir(path):
            if self.ui.tree_view.isExpanded(index):
                self.state_config.set_state(self.config_path, item_path)
            else:
                self.state_config.remove_state(self.config_path, item_path)

    def _restore_states(self):
        """Restore the expanded state of the view"""
        for path in self.state_config.get_states(self.config_path):
            path = "{}/{}".format(self.root_path, path)
            if os.path.exists(path):
                self.ui.tree_view.setExpanded(self.file_system.index(path), True)


class FileViewWidgetUI():
    def setup_ui(self, widget):


        action_button_layout = QtWidgets.QHBoxLayout()
        action_button_layout.setContentsMargins(0, 0, 0, 0)
        # action_button_layout.setSpacing(2)

        self.create_folder_btn = QtWidgets.QPushButton()
        self.create_folder_btn.setIcon(QtGui.QIcon(get_icon("dblx_folder.png")))
        self.create_folder_btn.setStyleSheet("background-color: transparent;outline:none;border:none;")
        action_button_layout.addWidget(self.create_folder_btn)

        self.create_script_btn = QtWidgets.QPushButton()
        self.create_script_btn.setIcon(QtGui.QIcon(get_icon("dblx_file.png")))
        self.create_script_btn.setStyleSheet("background-color: transparent;outline:none;border:none;")
        action_button_layout.addWidget(self.create_script_btn)

        self.actions_widget = QtWidgets.QWidget()
        self.actions_widget.setContentsMargins(0,0,0,0)
        self.actions_widget.setLayout(action_button_layout)

        self.tree_view = _TreeView()
        self.tree_view.setHeaderHidden(True)

        self.invalid_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Invalid Path")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.invalid_layout.addWidget(label)

        self.view_layout = QtWidgets.QVBoxLayout()
        self.view_layout.setContentsMargins(2, 2, 2, 2)
        self.view_layout.addWidget(self.actions_widget)
        self.view_layout.addWidget(self.tree_view)


        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(self.view_layout)

        widget.setLayout(main_layout)


class FileSystemModel(QtWidgets.QFileSystemModel):
    """Reimplemented"""
    def __init__(self):
        QtWidgets.QFileSystemModel.__init__(self)
        self.icon_provider = FileIconProvider()
        self.setIconProvider(self.icon_provider)
        self.setNameFilterDisables(False)

    def supportedDropActions(self):

        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def flags(self, index):
        """Reimplemeneted

        Args:
            index (QtCore.QModelIndex):

        """

        flags = QtWidgets.QFileSystemModel.flags(self, index)
        if self.isReadOnly():
            return flags

        flags |= QtCore.Qt.ItemIsDropEnabled

        if not index.isValid():
            return flags

        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsDragEnabled

        return flags

    def columnCount(self, index):
        """
            Set column count to 1

        Args:
            index (QtCore.QModelIndex):

        Returns:
            int

        """
        return 1

    def hasChildren(self, index):
        """
        Reimplemented:
            Remove arrow indicator on empty folders

        Args:
            index (QtCore.QModelIndex):
        """
        file_info = self.fileInfo(index)
        if file_info.exists():
            if file_info.isDir():
                files = file_info.absoluteDir().entryList(self.nameFilters(),
                                      QtCore.QDir.AllDirs |
                                      QtCore.QDir.NoDotAndDotDot)
                return bool(files)
        return False

    def dropMimeData(self, data, action, row, column, parent):
        """

        Args:
            data (QtCore.QMimeData):
            action (QtCore.Qt.DropAction):
            row (int):
            column (int):
            parent (QtCore.QModelIndex):

        Returns:
            bool: accepted state
        """
        if not data.hasUrls() \
                or (action & self.supportedDropActions()) == QtCore.Qt.IgnoreAction \
                or not parent.isValid() \
                or self.isReadOnly():
            return False


        parent_info = self.fileInfo(parent)  # type: QtCore.QFileInfo

        # filePath does some path resolving so use that to get the path
        dst_root = self.filePath(parent)
        if parent_info.isFile():
            dst_root = parent_info.path()
        dst_root += QtCore.QDir.separator()

        for url in data.urls():
            src_path = url.toLocalFile()
            dst_path = dst_root + QtCore.QFileInfo(src_path).fileName()
            if action == QtCore.Qt.CopyAction:
                QtCore.QFile.copy(src_path, dst_path)
            elif action == QtCore.Qt.MoveAction:
                QtCore.QFile.rename(src_path, dst_path)
        return True


class _TreeView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        QtWidgets.QTreeView.__init__(self, parent)

        self.setIconSize(QtCore.QSize(20, 20))
        self.setEditTriggers(self.SelectedClicked | self.EditKeyPressed)

        self._last_pos = None

        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

        # Drag and Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDragDropMode(self.InternalMove)


    def mousePressEvent(self, event):
        """
        Reimplemented:
            Show the context menu on mouse down instead of mouse up
            Clear the selection if a click occurs out side of the list of items
        Args:
            event (QtGui.QMouseEvent):
        """

        if event.button() == QtCore.Qt.RightButton:
            QtWidgets.QTreeView.mousePressEvent(self, event)
            self.customContextMenuRequested.emit(event.pos())
        elif event.button() == QtCore.Qt.MidButton \
                and event.modifiers() == QtCore.Qt.AltModifier:
            # Ensures that this is only enacted when the mouse is clicked
            self._last_pos = event.globalPos()
            return
        else:
            QtWidgets.QTreeView.mousePressEvent(self, event)

            index_under_mouse = self.indexAt(event.pos())
            if not index_under_mouse.isValid():
                self.clearSelection()
                return

    def mouseReleaseEvent(self, event):
        if self._last_pos:
            self._last_pos = None
            self.setCursor(QtCore.Qt.ArrowCursor)
            return

        QtWidgets.QTreeView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        if self._last_pos:
            current_pos = event.globalPos()
            delta = self._last_pos - current_pos
            h = self.horizontalScrollBar()
            h.setSliderPosition(h.sliderPosition() + (delta.x()))
            v = self.verticalScrollBar()
            v.setSliderPosition(v.sliderPosition() + (delta.y()))
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self._last_pos = current_pos
            return

        QtWidgets.QTreeView.mouseMoveEvent(self, event)


class FileIconProvider(QtWidgets.QFileIconProvider):
    PIXMAP_CACHE = {}
    def __init__(self):
        QtWidgets.QFileIconProvider.__init__(self)

        self.default_file = self.get_pixmap(get_icon("dblx_file.png"))
        self.default_folder = self.get_pixmap(get_icon("dblx_folder.png"))

    def icon(self, file_info, *args):

        if isinstance(file_info, QtCore.QFileInfo):

            if file_info.isFile():
                icon_path = get_icon("dblx_file_{ext}.png".format(
                        ext=file_info.suffix()))
                if icon_path:
                    if icon_path not in self.PIXMAP_CACHE:
                        self.PIXMAP_CACHE[icon_path] = self.get_pixmap(icon_path)
                    return self.PIXMAP_CACHE[icon_path]
                return self.default_file
            else:
                return self.default_folder

        return QtWidgets.QFileIconProvider.icon(self, file_info)

    def _is_python_module(self, path):
        return bool(QtCore.QDir(path).entryList(["__init__.*"]))

    def get_pixmap(self, path):
        if path:
            return QtGui.QPixmap(path)
        return QtGui.QPixmap()
