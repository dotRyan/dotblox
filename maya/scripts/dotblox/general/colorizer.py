"""
"""

from maya import cmds
from PySide2 import QtWidgets, QtCore, QtGui
from dotblox.core.mutil import OptionVar

from dotblox.core.mutil import OptionVar
from dotblox.core.ui import dockwindow

from dotbloxlib import color as colorlib
from dotblox.core import color as colorm
from dotbloxlib.color import mdc


class PALETTE_MODES():
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXTREME = "extreme"

    WEIGHTS = {
        BASIC: [mdc.Weight500],
        STANDARD: [
            mdc.Weight200,
            mdc.Weight500,
            mdc.Weight800,
        ],
        ADVANCED: [
            mdc.Weight50,
            mdc.Weight100,
            mdc.Weight200,
            mdc.Weight300,
            mdc.Weight400,
            mdc.Weight500,
            mdc.Weight600,
            mdc.Weight700,
            mdc.Weight800,
            mdc.Weight900,
        ]
    }

    @classmethod
    def get_weights(cls, color, mode):
        weights = mdc.get_weights(color).keys()
        if mode == cls.EXTREME:
            return sorted(
                    weights,
                    key=lambda key: (
                        float("inf") if "a" in key else int(key),
                        int(key.replace("a", ""))))
        return [weight if weight in weights else None for weight in cls.WEIGHTS[mode]]


class APPLY_MODES():
    OBJECT = "object"
    OUTLINER = "outliner"
    LAYER = "layer"


class ColorizerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.tool_name = "colorizer"

        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name.capitalize())

        self.option_var = OptionVar(self.tool_name)

        self.ui = ColorizeUI()
        self.ui.setup_ui(self)

        self._palette_mode_option_key = "palette_mode"
        self._apply_mode_option_key = "apply_mode"

        # Connections
        self.ui.palette_mode_grp.triggered.connect(self.on_palette_option_changed)
        self.ui.layer_chkbx.changed.connect(lambda *x: self.on_apply_option_changed(APPLY_MODES.LAYER))
        self.ui.outliner_chkbx.changed.connect(lambda *x: self.on_apply_option_changed(APPLY_MODES.OUTLINER))
        self.ui.object_chkbx.changed.connect(lambda *x: self.on_apply_option_changed(APPLY_MODES.OBJECT))
        self.ui.clear_menu.triggered.connect(self.clear_selection)

        self.startup_settings()

    @property
    def is_layer(self):
        return self.ui.layer_chkbx.isChecked()

    @is_layer.setter
    def is_layer(self, value):
        self.ui.layer_chkbx.setChecked(value)

    @property
    def is_object(self):
        return self.ui.object_chkbx.isChecked()

    @is_object.setter
    def is_object(self, value):
        self.ui.object_chkbx.setChecked(value)

    @property
    def is_outliner(self):
        return self.ui.outliner_chkbx.isChecked()

    @is_outliner.setter
    def is_outliner(self, value):
        self.ui.outliner_chkbx.setChecked(value)

    def startup_settings(self):
        palette_mode = self.option_var.get(self._palette_mode_option_key, PALETTE_MODES.BASIC)
        action = self.ui.palette_mode_actions[palette_mode]
        action.setChecked(True)
        self.ui.palette_mode_grp.triggered.emit(action)

        apply_mode = self.option_var.get(self._apply_mode_option_key, APPLY_MODES.LAYER)
        if APPLY_MODES.LAYER in apply_mode:
            self.ui.layer_chkbx.setChecked(True)

        if APPLY_MODES.OBJECT in apply_mode:
            self.ui.object_chkbx.setChecked(True)

        if APPLY_MODES.OUTLINER in apply_mode:
            self.ui.outliner_chkbx.setChecked(True)

    def on_palette_option_changed(self, action):
        palette_mode = action.data()

        self.ui.palette_mode_menu.setTitle(
                "Palette: {mode}".format(
                        mode=palette_mode.capitalize()))
        self.build_palette(palette_mode)

        self.option_var.set(self._palette_mode_option_key, palette_mode)

    def on_apply_option_changed(self, mode):
        if mode == APPLY_MODES.LAYER:
            if self.is_layer:
                self.ui.outliner_chkbx.setChecked(False)
                self.ui.object_chkbx.setChecked(False)
            else:
                self.ui.object_chkbx.setChecked(True)
        else:
            if not self.is_object and not self.is_outliner:
                self.ui.layer_chkbx.setChecked(True)
            else:
                self.ui.layer_chkbx.setChecked(False)

        if self.is_layer:
            mode = APPLY_MODES.LAYER.capitalize()

        elif self.is_outliner and self.is_object:
            mode = APPLY_MODES.OBJECT.capitalize() + " + " + APPLY_MODES.OUTLINER.capitalize()
        elif self.is_object:
            mode = APPLY_MODES.OBJECT.capitalize()
        elif self.is_outliner:
            mode = APPLY_MODES.OUTLINER.capitalize()

        self.option_var.set(self._apply_mode_option_key, mode.lower())
        self.ui.clear_menu.setText("Clear: " + mode)
        self.ui.apply_menu.setTitle("Apply to: " + mode)

    def clear_selection(self):
        if self.is_layer:
            display_layers = self.get_selected_display_layers()

            if not len(display_layers):
                cmds.inViewMessage(
                        message="No Display Late",
                        pos='midCenter',
                        fade=True,
                        fadeOutTime=1500,
                        fontSize=12,
                        fadeStayTime=1250)

            for display_layer in display_layers:
                cmds.setAttr(display_layer + ".color", True)
                cmds.setAttr(display_layer + ".overrideRGBColors", False)
            return

        selection = cmds.ls(selection=True, long=True)

        for item in selection:
            if self.is_object and cmds.objExists(item + ".overrideEnabled"):
                # TODO: do we turn this off?
                #       how do we know the only change was made to the color
                #       would be really helful to add a custom attribute
                # cmds.setAttr(item + ".overrideEnabled", True)
                cmds.setAttr(item + ".overrideRGBColors", False)

            if self.is_outliner and cmds.objExists(item + ".useOutlinerColor"):
                cmds.setAttr(item + ".useOutlinerColor", False)

    def get_selected_display_layers(self):
        # Note: we could get all displayLayer nodes but there is no way
        #       to select them without going through the UI so we do it this way
        display_layers = cmds.layout("LayerEditorDisplayLayerLayout",
                                   query=True,
                                   childArray=True) or []
        return [display_layer
                for display_layer in display_layers
                if cmds.layerButton(display_layer, query=True, select=True)]

    def build_palette(self, mode):
        columns = self.ui.palette_grid.columnCount()
        rows = self.ui.palette_grid.rowCount()
        for column in range(columns):
            for row in range(rows):
                widget_item = self.ui.palette_grid.itemAtPosition(row, column)
                if not widget_item:
                    continue
                w = widget_item.widget()
                self.ui.palette_grid.removeWidget(w)
                w.deleteLater()

        column = 0
        for color in mdc.get_colors():
            row = -1

            for weight in PALETTE_MODES.get_weights(color, mode):
                row += 1
                if not weight:
                    continue

                btn = ColorButton(color, weight)
                btn.pressed.connect(lambda btn=btn: self.on_color_btn_presss(btn))

                self.ui.palette_grid.addWidget(btn, row, column)

            column += 1

        def resize():
            self.adjustSize()
            current = self.size()
            min = self.minimumSizeHint()

            if hasattr(self, "_dock_win"):
                self._dock_win.resize_workspace(current.width(), min.height())

        QtCore.QTimer.singleShot(100, resize)

    def on_color_btn_presss(self, btn):
        raw_color = colorlib.color_hex_to_rgbf(btn.hex_value)
        color = colorm.color_managed_convert(raw_color)

        is_layer = self.ui.layer_chkbx.isChecked()
        is_object = self.ui.object_chkbx.isChecked()
        is_outliner = self.ui.outliner_chkbx.isChecked()

        if is_layer:

            for display_layer in self.get_selected_display_layers():
                # This is on by default but just in case
                cmds.setAttr(display_layer + ".enabled", True)
                cmds.setAttr(display_layer + ".overrideColorRGB", *color)
                cmds.setAttr(display_layer + ".color", False)
                cmds.setAttr(display_layer + ".overrideRGBColors", True)

        if is_object or is_outliner:

            selection = cmds.ls(selection=True, long=True)

            for item in selection:
                if is_object and cmds.objExists(item + ".overrideEnabled"):
                    cmds.setAttr(item + ".overrideEnabled", True)
                    cmds.setAttr(item + ".overrideRGBColors", True)
                    cmds.setAttr(item + ".overrideColorRGB", *color)

                if is_outliner and cmds.objExists(item + ".useOutlinerColor"):
                    cmds.setAttr(item + ".useOutlinerColor", True)
                    cmds.setAttr(item + ".outlinerColor", *raw_color)


class ColorizeUI(object):

    def setup_ui(self, widget):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.build_menus(main_layout)

        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setAlignment(QtCore.Qt.AlignTop)

        self.palette_grid = QtWidgets.QGridLayout()
        self.palette_grid.setSpacing(0)
        content_layout.addLayout(self.palette_grid)

        main_layout.addLayout(content_layout)

        widget.setLayout(main_layout)

    def build_menus(self, layout):
        self.menu_bar = QtWidgets.QMenuBar()

        # Palette Size
        self.apply_menu = QtWidgets.QMenu("Apply to: ", None)  # type: QtWidgets.QMenu
        self.apply_menu.setTearOffEnabled(True)
        self.menu_bar.addMenu(self.apply_menu)

        self.palette_mode_menu = QtWidgets.QMenu("Palette:")  # type: QtWidgets.QMenu
        self.menu_bar.addMenu(self.palette_mode_menu)

        self.util_menu = self.menu_bar.addMenu("Util")  # type: QtWidgets.QMenu

        # Mode Menu Items
        self.palette_mode_grp = QtWidgets.QActionGroup(self.palette_mode_menu)
        self.palette_mode_actions = {}
        palette_modes = [PALETTE_MODES.BASIC,
                         PALETTE_MODES.STANDARD,
                         PALETTE_MODES.ADVANCED,
                         PALETTE_MODES.EXTREME]
        for palette_mode in palette_modes:
            action = QtWidgets.QAction(palette_mode.capitalize(), None)
            action.setData(palette_mode)
            action.setCheckable(True)
            self.palette_mode_actions[palette_mode] = action
            self.palette_mode_menu.addAction(action)
            self.palette_mode_grp.addAction(action)

        # Type Menu Actions
        self.layer_chkbx = QtWidgets.QAction(APPLY_MODES.LAYER.capitalize(), None)  # type: QtWidgets.QAction
        self.layer_chkbx.setCheckable(True)
        self.apply_menu.addAction(self.layer_chkbx)

        self.object_chkbx = QtWidgets.QAction(APPLY_MODES.OBJECT.capitalize(), None)
        self.object_chkbx.setCheckable(True)
        self.apply_menu.addAction(self.object_chkbx)

        self.outliner_chkbx = QtWidgets.QAction(APPLY_MODES.OUTLINER.capitalize(), None)
        self.outliner_chkbx.setCheckable(True)
        self.apply_menu.addAction(self.outliner_chkbx)

        self.clear_menu = QtWidgets.QAction("Clear", None)  # type: QtWidgets.QAction
        self.util_menu.addAction(self.clear_menu)

        layout.addWidget(self.menu_bar)


class ColorButton(QtWidgets.QPushButton):
    def __init__(self, color, weight, parent=None):
        QtWidgets.QPushButton.__init__(self, parent=parent)

        self.color = color
        self.weight = weight

        # self.setFixedHeight(20)

        self.hex_value = mdc.get_color(color, weight)
        self.setToolTip("{color} {weight}".format(color=self.color,
                                                  weight=self.weight))

        self.set_style()

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(0, 20)

    def set_style(self):
        i = QtGui.QColor(self.hex_value)
        darker = i.darker(125)
        darker = darker.name()

        lighter = i.lighter(110)
        lighter = lighter.name()

        self.setStyleSheet("""
            QPushButton{{
                background-color:{base};
                                border: 1px solid black;

            }}
            
            QPushButton:hover{{
                background-color:{lighter};
            }}
            
            
            QPushButton:pressed{{
                background-color:{darker};
                border: 1px solid black;
            }}
        """.format(base=self.hex_value, lighter=lighter, darker=darker))

dock = dockwindow.DockWindowManager(ColorizerWidget)