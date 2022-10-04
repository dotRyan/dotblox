import os
import subprocess

from PySide2 import QtWidgets, QtCore, QtGui

from dotblox import config
from dotblox.tools.codewall.ui.configdialog import ConfigDialog
from dotblox.tools.codewall.ui.fileviewwidget import FileViewWidget
from dotblox.icon import get_icon
from dotblox.tools.codewall.api import Config, StateConfig


class CodeWallWidget(QtWidgets.QWidget):
    def __init__(self, hook=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        widget_title = "Code Wall"
        self.setObjectName(widget_title.lower().replace(" ", "_"))
        self.setWindowTitle(widget_title)

        self.hook = hook if hook else Hook()
        self.state_config = StateConfig(self.hook.APP)

        self.ui = CodeWallUI()
        self.ui.setup_ui(self)

        self.ui.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        tab_bar = self.ui.tab_widget.tabBar()  # type: QtWidgets.QTabBar
        tab_bar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self.tab_bar_context_menu)
        self.ui.config_menu.aboutToShow.connect(self._build_config_menu)
        self.ui.tab_widget.currentChanged.connect(self._on_tab_change)
        self.ui.refresh_menu.triggered.connect(self._rebuild_tabs)
        self.ui.read_only_menu.triggered[bool].connect(self._on_read_only)

        self.ui.read_only_menu.setChecked(self.state_config.get_read_only())

        self._rebuild_tabs()

    def _rebuild_tabs(self):
        """Re update all the configs and rebuild the tabs"""
        last_tab = self.state_config.get_current_tab()
        matched_tab = None

        self.ui.tab_widget.blockSignals(True)
        self.ui.tab_widget.clear()

        configs = config.find_all("codewall.dblx")
        self.configs = [Config(x) for x in configs] # python 3 compatible

        tab_order = self.state_config.get_tab_order()
        for cfg in self.configs:
            for root in sorted(
                    cfg.get_roots(),
                    key=lambda x: (tab_order.index(x) if x in tab_order else float("inf"),
                                   cfg.get_label(x))):
                tab = FileViewWidget(root, cfg, self.state_config, self.hook)
                self.ui.tab_widget.addTab(tab, tab.tab_name())
                if last_tab == root:
                    matched_tab = tab
        if matched_tab:
            self.ui.tab_widget.setCurrentWidget(matched_tab)

        self.ui.tab_widget.blockSignals(False)
        self._update_read_only()

        tab_bar = self.ui.tab_widget.tabBar()
        for index in range(self.ui.tab_widget.count()):
            widget = self.ui.tab_widget.widget(index)
            if widget.can_edit_path:
                continue

            right = tab_bar.tabButton(index, QtWidgets.QTabBar.RightSide)
            left = tab_bar.tabButton(index, QtWidgets.QTabBar.LeftSide)
            if right:
                right.hide()
            if left:
                left.hide()

    def _update_tab_order(self):
        """When the tab order changes update the state config"""
        tabs = []
        for index in range(self.ui.tab_widget.count()):
            widget = self.ui.tab_widget.widget(index)
            tabs.append(widget.config_path)
        self.state_config.set_tab_order(tabs)

    def _build_config_menu(self):
        """Build the config menu based on the current configs"""
        self.ui.config_menu.clear()
        for config in self.configs:
            action = self.ui.config_menu.addAction(
                config.path,
                lambda x=config: self._show_config_dialog(config))
            if config.config_is_locked():
                action.setEnabled(False)
                action.setText("Locked: " + action.text())

    def _show_config_dialog(self, config):
        """Launch a dialog to modify a config

        Args:
            config(Config: config to operate on

        """
        dialog = ConfigDialog(config.path, parent=self)
        if not dialog.exec_():
            return

        label, path, as_relative = dialog.result()
        if as_relative:
            path = config.get_relative_path(path)

        config.add_root(path, label)
        self._rebuild_tabs()

    def _on_read_only(self, checked):
        """Save to the config and set the tabs to the current read only state

        Args:
            checked(bool):

        """
        self.state_config.set_read_only(checked)
        self._update_read_only()

    def _update_read_only(self):
        """Update the tabs with the current state read only value"""
        state = self.state_config.get_read_only()
        for index in range(self.ui.tab_widget.count()):
            widget = self.ui.tab_widget.widget(index)
            if not widget.can_edit_contents:
                # Force to False just in case were in some weird state
                widget.set_read_only(False)
                continue
            widget.set_read_only(state)

    def _on_update_config(self, widget):
        """ Update the given widgets config

        Args:
            widget(FileViewWidget): widget to grab the config from

        """
        old_path = widget.config_path
        old_label = widget.config.get_label(old_path)
        dialog = ConfigDialog(widget.config.path,
                              path=old_path,
                              label=old_label, parent=self)
        if not dialog.exec_():
            return

        label, path, relative = dialog.result()

        updates = False

        if label != old_label:
            updates = True
            widget.config.update_label(old_path, label)

        if relative:
            path = widget.config.get_relative_path(path)

        if path != old_path:
            updates = True
            widget.config.update_root(old_path, path)

        if updates:
            self._rebuild_tabs()

    def _on_tab_change(self, index):
        """Update the current tab when changed to it

        Args:
            index(int): index of the current tab

        """
        file_view = self.ui.tab_widget.widget(index)
        self.state_config.set_current_tab(file_view.config_path)
        self._update_tab_order()

    def _on_tab_close_requested(self, index):
        """Remove the root path from the config when tab is closed

        Args:
            index(int): index of current tab

        """
        widget = self.ui.tab_widget.widget(index)
        config = widget.config
        result = QtWidgets.QMessageBox.question(
            None,
            "Code Wall: Close Tab",
            "Are you sure you want to close {}.\n"
            "This will permanently remove it from the settings.".format(
                widget.root_path))
        if result == QtWidgets.QMessageBox.No:
            return

        config.remove_root(widget.config_path)
        self.ui.tab_widget.removeTab(index)

    def tab_bar_context_menu(self, pos):
        """Menu when right-clicking on tab bar

        Args:
            pos(QtCore.QPos): position for menu

        """
        tab_bar = self.ui.tab_widget.tabBar()  # type: QtWidgets.QTabBar

        index = tab_bar.tabAt(pos)
        widget = self.ui.tab_widget.widget(index)

        def open_in_system(file_path):
            if hasattr(os, "startfile"):
                os.startfile(file_path.replace("/", "\\"))
            else:
                subprocess.call(["open", file_path])

        menu = QtWidgets.QMenu()
        menu.addAction("Show In Explorer", lambda *x: open_in_system(widget.root_path))
        if widget.can_edit_path:
            menu.addAction("Update Settings", lambda *x: self._on_update_config(widget))
        menu.exec_(QtGui.QCursor.pos())


class CodeWallUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(2)

        self.menu_bar = QtWidgets.QMenuBar(parent)
        main_layout.setMenuBar(self.menu_bar)

        self.menu_btn = QtWidgets.QPushButton()
        self.menu_btn.setIcon(QtGui.QIcon(get_icon("dblx_menu.png")))
        self.menu_btn.setStyleSheet("""
           QPushButton{
               background-color: transparent;
               outline:none;
               border:none;
           }

           QPushButton::menu-indicator {
               image: none;
               }
           """)

        self.menu_bar.setCornerWidget(self.menu_btn, QtCore.Qt.TopRightCorner)
        self.menu_bar.setNativeMenuBar(False)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)

        self.tab_widget.setMovable(True)
        main_layout.addWidget(self.tab_widget)

        self.settings_menu = QtWidgets.QMenu("Settings Menu")
        self.read_only_menu = self.settings_menu.addAction("Read Only")
        self.read_only_menu.setCheckable(True)
        self.config_menu = self.settings_menu.addMenu("Config")
        self.refresh_menu = self.settings_menu.addAction("Refresh")

        self.menu_btn.setMenu(self.settings_menu)

        parent.setLayout(main_layout)


class Hook():
    """Hooks for external dccs to remap certain functions"""
    APP = "shell"

    def run_file(self, file_path):
        with open(file_path) as f:
            exec (compile(f.read(), file_path, "exec"))

    def get_supported_extensions(self):
        return [".py"]

    def execute_text(self, text, file_name):
        if file_name is None or file_name.endswith(".py"):
            exec (compile(text, "codewall_interactive", "exec"), globals(), locals())
