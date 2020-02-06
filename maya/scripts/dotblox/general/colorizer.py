"""
"""

from PySide2 import QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm

win = None


class MaterialColors():
    RED = "red"
    PINK = "pink"
    PURPLE = "purple"
    DEEPPURPLE = "deeppurple"
    INDIGO = "indigo"
    BLUE = "blue"
    LIGHTBLUE = "lightblue"
    CYAN = "cyan"
    TEAL = "teal"
    GREEN = "green"
    LIGHTGREEN = "lightgreen"
    LIME = "lime"
    YELLOW = "yellow"
    AMBER = "amber"
    ORANGE = "orange"
    DEEPORANGE = "deeporange"
    BROWN = "brown"
    GREY = "grey"
    BLUEGREY = "bluegrey"
    COLORS = {
        RED: {
            "50": "#ffebee",
            "100": "#ffcdd2",
            "200": "#ef9a9a",
            "300": "#e57373",
            "400": "#ef5350",
            "500": "#f44336",
            "600": "#e53935",
            "700": "#d32f2f",
            "800": "#c62828",
            "900": "#b71c1c",
            "a100": "#ff8a80",
            "a200": "#ff5252",
            "a400": "#ff1744",
            "a700": "#d50000"
        },
        PINK: {
            "50": "#fce4ec",
            "100": "#f8bbd0",
            "200": "#f48fb1",
            "300": "#f06292",
            "400": "#ec407a",
            "500": "#e91e63",
            "600": "#d81b60",
            "700": "#c2185b",
            "800": "#ad1457",
            "900": "#880e4f",
            "a100": "#ff80ab",
            "a200": "#ff4081",
            "a400": "#f50057",
            "a700": "#c51162"
        },
        PURPLE: {
            "50": "#f3e5f5",
            "100": "#e1bee7",
            "200": "#ce93d8",
            "300": "#ba68c8",
            "400": "#ab47bc",
            "500": "#9c27b0",
            "600": "#8e24aa",
            "700": "#7b1fa2",
            "800": "#6a1b9a",
            "900": "#4a148c",
            "a100": "#ea80fc",
            "a200": "#e040fb",
            "a400": "#d500f9",
            "a700": "#aa00ff"
        },
        DEEPPURPLE: {
            "50": "#ede7f6",
            "100": "#d1c4e9",
            "200": "#b39ddb",
            "300": "#9575cd",
            "400": "#7e57c2",
            "500": "#673ab7",
            "600": "#5e35b1",
            "700": "#512da8",
            "800": "#4527a0",
            "900": "#311b92",
            "a100": "#b388ff",
            "a200": "#7c4dff",
            "a400": "#651fff",
            "a700": "#6200ea"
        },
        INDIGO: {
            "50": "#e8eaf6",
            "100": "#c5cae9",
            "200": "#9fa8da",
            "300": "#7986cb",
            "400": "#5c6bc0",
            "500": "#3f51b5",
            "600": "#3949ab",
            "700": "#303f9f",
            "800": "#283593",
            "900": "#1a237e",
            "a100": "#8c9eff",
            "a200": "#536dfe",
            "a400": "#3d5afe",
            "a700": "#304ffe"
        },
        BLUE: {
            "50": "#e3f2fd",
            "100": "#bbdefb",
            "200": "#90caf9",
            "300": "#64b5f6",
            "400": "#42a5f5",
            "500": "#2196f3",
            "600": "#1e88e5",
            "700": "#1976d2",
            "800": "#1565c0",
            "900": "#0d47a1",
            "a100": "#82b1ff",
            "a200": "#448aff",
            "a400": "#2979ff",
            "a700": "#2962ff"
        },
        LIGHTBLUE: {
            "50": "#e1f5fe",
            "100": "#b3e5fc",
            "200": "#81d4fa",
            "300": "#4fc3f7",
            "400": "#29b6f6",
            "500": "#03a9f4",
            "600": "#039be5",
            "700": "#0288d1",
            "800": "#0277bd",
            "900": "#01579b",
            "a100": "#80d8ff",
            "a200": "#40c4ff",
            "a400": "#00b0ff",
            "a700": "#0091ea"
        },
        CYAN: {
            "50": "#e0f7fa",
            "100": "#b2ebf2",
            "200": "#80deea",
            "300": "#4dd0e1",
            "400": "#26c6da",
            "500": "#00bcd4",
            "600": "#00acc1",
            "700": "#0097a7",
            "800": "#00838f",
            "900": "#006064",
            "a100": "#84ffff",
            "a200": "#18ffff",
            "a400": "#00e5ff",
            "a700": "#00b8d4"
        },
        TEAL: {
            "50": "#e0f2f1",
            "100": "#b2dfdb",
            "200": "#80cbc4",
            "300": "#4db6ac",
            "400": "#26a69a",
            "500": "#009688",
            "600": "#00897b",
            "700": "#00796b",
            "800": "#00695c",
            "900": "#004d40",
            "a100": "#a7ffeb",
            "a200": "#64ffda",
            "a400": "#1de9b6",
            "a700": "#00bfa5"
        },
        GREEN: {
            "50": "#e8f5e9",
            "100": "#c8e6c9",
            "200": "#a5d6a7",
            "300": "#81c784",
            "400": "#66bb6a",
            "500": "#4caf50",
            "600": "#43a047",
            "700": "#388e3c",
            "800": "#2e7d32",
            "900": "#1b5e20",
            "a100": "#b9f6ca",
            "a200": "#69f0ae",
            "a400": "#00e676",
            "a700": "#00c853"
        },
        LIGHTGREEN: {
            "50": "#f1f8e9",
            "100": "#dcedc8",
            "200": "#c5e1a5",
            "300": "#aed581",
            "400": "#9ccc65",
            "500": "#8bc34a",
            "600": "#7cb342",
            "700": "#689f38",
            "800": "#558b2f",
            "900": "#33691e",
            "a100": "#ccff90",
            "a200": "#b2ff59",
            "a400": "#76ff03",
            "a700": "#64dd17"
        },
        LIME: {
            "50": "#f9fbe7",
            "100": "#f0f4c3",
            "200": "#e6ee9c",
            "300": "#dce775",
            "400": "#d4e157",
            "500": "#cddc39",
            "600": "#c0ca33",
            "700": "#afb42b",
            "800": "#9e9d24",
            "900": "#827717",
            "a100": "#f4ff81",
            "a200": "#eeff41",
            "a400": "#c6ff00",
            "a700": "#aeea00"
        },
        YELLOW: {
            "50": "#fffde7",
            "100": "#fff9c4",
            "200": "#fff59d",
            "300": "#fff176",
            "400": "#ffee58",
            "500": "#ffeb3b",
            "600": "#fdd835",
            "700": "#fbc02d",
            "800": "#f9a825",
            "900": "#f57f17",
            "a100": "#ffff8d",
            "a200": "#ffff00",
            "a400": "#ffea00",
            "a700": "#ffd600"
        },
        AMBER: {
            "50": "#fff8e1",
            "100": "#ffecb3",
            "200": "#ffe082",
            "300": "#ffd54f",
            "400": "#ffca28",
            "500": "#ffc107",
            "600": "#ffb300",
            "700": "#ffa000",
            "800": "#ff8f00",
            "900": "#ff6f00",
            "a100": "#ffe57f",
            "a200": "#ffd740",
            "a400": "#ffc400",
            "a700": "#ffab00"
        },
        ORANGE: {
            "50": "#fff3e0",
            "100": "#ffe0b2",
            "200": "#ffcc80",
            "300": "#ffb74d",
            "400": "#ffa726",
            "500": "#ff9800",
            "600": "#fb8c00",
            "700": "#f57c00",
            "800": "#ef6c00",
            "900": "#e65100",
            "a100": "#ffd180",
            "a200": "#ffab40",
            "a400": "#ff9100",
            "a700": "#ff6d00"
        },
        DEEPORANGE: {
            "50": "#fbe9e7",
            "100": "#ffccbc",
            "200": "#ffab91",
            "300": "#ff8a65",
            "400": "#ff7043",
            "500": "#ff5722",
            "600": "#f4511e",
            "700": "#e64a19",
            "800": "#d84315",
            "900": "#bf360c",
            "a100": "#ff9e80",
            "a200": "#ff6e40",
            "a400": "#ff3d00",
            "a700": "#dd2c00"
        },
        BROWN: {
            "50": "#efebe9",
            "100": "#d7ccc8",
            "200": "#bcaaa4",
            "300": "#a1887f",
            "400": "#8d6e63",
            "500": "#795548",
            "600": "#6d4c41",
            "700": "#5d4037",
            "800": "#4e342e",
            "900": "#3e2723"
        },
        GREY: {
            "50": "#fafafa",
            "100": "#f5f5f5",
            "200": "#eeeeee",
            "300": "#e0e0e0",
            "400": "#bdbdbd",
            "500": "#9e9e9e",
            "600": "#757575",
            "700": "#616161",
            "800": "#424242",
            "900": "#212121"
        },
        BLUEGREY: {
            "50": "#eceff1",
            "100": "#cfd8dc",
            "200": "#b0bec5",
            "300": "#90a4ae",
            "400": "#78909c",
            "500": "#607d8b",
            "600": "#546e7a",
            "700": "#455a64",
            "800": "#37474f",
            "900": "#263238"
        }
    }

    WEIGHTS = ["50",
               "100",
               "200",
               "300",
               "400",
               "500",
               "600",
               "700",
               "800",
               "900",
               "a100",
               "a200",
               "a400",
               "a700"]

    ITEMS = [RED,
             PINK,
             PURPLE,
             DEEPPURPLE,
             INDIGO,
             BLUE,
             LIGHTBLUE,
             CYAN,
             TEAL,
             GREEN,
             LIGHTGREEN,
             LIME,
             YELLOW,
             AMBER,
             ORANGE,
             DEEPORANGE,
             BROWN,
             GREY,
             BLUEGREY]

    @classmethod
    def get_weights(cls, color):
        return sorted(MaterialColors.COLORS[color],
                      key=lambda x: cls.WEIGHTS.index(x))

    @classmethod
    def get_color(cls, color, weight="500"):
        return MaterialColors.COLORS[color][weight]


class PALETTE_MODES():
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXTREME = "extreme"

    WEIGHT_MAPS = {
        BASIC: ["500"],
        STANDARD: ["200", "500", "800"],
        ADVANCED: [
            "50",
            "100",
            "200",
            "300",
            "400",
            "500",
            "600",
            "700",
            "800",
            "900"
        ]
    }

    @classmethod
    def get_weights(cls, color, mode):
        weights = MaterialColors.get_weights(color)
        if mode == cls.EXTREME:
            return weights
        weight_map = cls.WEIGHT_MAPS[mode]
        return [None if weight not in weights else weight for weight in weight_map]


class APPLY_MODES():
    OBJECT = "object"
    OUTLINER = "outliner"
    LAYER = "layer"


def get_maya_win():
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QMainWindow)


class ColorizerWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        MayaQWidgetDockableMixin.__init__(self, parent)

        # create a frame that other windows can dock into
        self.docking_frame = QtWidgets.QMainWindow(self)
        self.docking_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.docking_frame.setWindowFlags(QtCore.Qt.Widget)
        self.docking_frame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.central_widget = ColorizerWidget(self)
        self.setWindowTitle(self.central_widget.windowTitle())
        self.setObjectName(self.central_widget.objectName() + "Window")

        self.docking_frame.setCentralWidget(self.central_widget)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self.docking_frame)
        self.setLayout(layout)

        self.minimum_size = self.central_widget.minimumSizeHint()
        self.preferred_size = QtCore.QSize(self.minimum_size.width(),
                                           self.minimum_size.height())

    def create_workspace_control(self):
        ui_script = "import {name}; {name}.run(restore=True)".format(name=__name__)
        close_callback = "import {name}; {name}.closed()".format(name=__name__)

        self.setDockableParameters(
                dockable=True,
                # retain deletes the workspace once the
                # Window is deleted. You will have to delete
                # the workspace for every call otherwise
                # when done set to true
                retain=False,
                minWidth=self.preferred_size.width(),
                width=self.preferred_size.width(),
                height=self.preferred_size.height(),
                widthSizingProperty="preferred",
                # heightSizingProperty="fixed",
                uiScript=ui_script,
                closeCallback=close_callback,
        )

    def show(self, *args, **kwargs):
        # Override MayaQWidgetDockableMixin.show() method
        # to resolve menu parenting issues for templates
        # MAYA-73418
        super(ColorizerWindow, self).show(*args, **kwargs)

    @property
    def workspace_control(self):
        return self.objectName() + "WorkspaceControl"

    def sizeHint(self):
        size = self.central_widget.minimumSizeHint()
        return QtCore.QSize(
                size.width(),
                size.height())

    def minimumSizeHint(self):
        return self.central_widget.minimumSizeHint()

    def resize_workspace(self, width, height):
        if pm.workspaceControl(self.workspace_control, query=True, exists=True):
            pm.workspaceControl(self.workspace_control, edit=True,
                                # width=width,
                                height=height,
                                # resizeWidth=width,
                                resizeHeight=height,
                                )
        self.resize(self.width(), height)


class ColorizerWidget(QtWidgets.QWidget):
    def __init__(self, window, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.window = window
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
        palette_mode = self.get_maya_option(self._palette_mode_option_key, PALETTE_MODES.BASIC)
        action = self.ui.palette_mode_actions[palette_mode]
        action.setChecked(True)
        self.ui.palette_mode_grp.triggered.emit(action)

        apply_mode = self.get_maya_option(self._apply_mode_option_key, APPLY_MODES.LAYER)
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
                pm.inViewMessage(
                        message="No Display Late",
                        pos='midCenter',
                        fade=True,
                        fadeOutTime=1500,
                        fontSize=12,
                        fadeStayTime=1250)

            for display_layer in display_layers:
                display_layer.color.set(True)
                display_layer.overrideRGBColors.set(False)
            return

        selection = pm.ls(selection=True)

        for item in selection:  # type: pm.PyNode
            if self.is_object and item.hasAttr("overrideEnabled"):
                # TODO: do we turn this off?
                #       how do we know the only change was made to the color
                #       would be really helful to add a custom attribute
                # item.overrideEnabled.set(True)
                item.overrideRGBColors.set(False)

            if self.is_outliner and item.hasAttr("useOutlinerColor"):
                item.useOutlinerColor.set(False)

    def get_selected_display_layers(self):
        # Note: we could get all displayLayer nodes but there is no way
        #       to select them without going through the UI so we do it this way
        display_layers = pm.layout("LayerEditorDisplayLayerLayout",
                                   query=True,
                                   childArray=True) or []
        return [pm.PyNode(display_layer)
                for display_layer in display_layers
                if pm.layerButton(display_layer, query=True, select=True)]

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
        for color in MaterialColors.ITEMS:
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

            size = self.minimumSizeHint()
            self.window.resize_workspace(size.width(), size.height())

        QtCore.QTimer.singleShot(100, resize)

    def on_color_btn_presss(self, btn):

        color = self._color_convert(btn.hex_value)

        is_layer = self.ui.layer_chkbx.isChecked()
        is_object = self.ui.object_chkbx.isChecked()
        is_outliner = self.ui.outliner_chkbx.isChecked()

        if is_layer:

            for display_layer in self.get_selected_display_layers():
                # This is on by default but just in case
                display_layer.enabled.set(True)
                display_layer.overrideColorRGB.set(color)
                display_layer.color.set(False)
                display_layer.overrideRGBColors.set(True)

        if is_object or is_outliner:

            selection = pm.ls(selection=True)

            for item in selection:  # type: pm.PyNode
                if is_object and item.hasAttr("overrideEnabled"):
                    item.overrideEnabled.set(True)
                    item.overrideRGBColors.set(True)
                    item.overrideColorRGB.set(color)

                if is_outliner and item.hasAttr("useOutlinerColor"):
                    item.useOutlinerColor.set(True)
                    item.outlinerColor.set(color)

    def _color_convert(self, hex_value):
        # Macro
        srgb_to_linear = lambda x: x / 12.92 if x < 0.04045 else ((x + 0.055) / 1.055) ** 2.4

        # 0-255
        rgb = [int(hex_value[i: i + 2], 16) for i in [1, 3, 5]]

        # 0-1
        rgbf = [i / 255.0 for i in rgb]

        cm_enabled = pm.colorManagementPrefs(query=True, cmEnabled=True)
        # Note: maybe one day autodesk will provide us with the fucking libraries
        cm_ocio_enabled = pm.colorManagementPrefs(query=True, cmConfigFileEnabled=True)

        color = rgbf
        if cm_enabled:
            if cm_ocio_enabled:
                pm.warning("OCIO config enabled. 2.2 Gamma is being used")

            return [srgb_to_linear(i) for i in color]

        return color

    def set_maya_option(self, key, value):

        if isinstance(value, (str, unicode)):
            kwarg = "stringValue"
        elif isinstance(value, float):
            kwarg = "floatValue"
        elif isinstance(value, int):
            kwarg = "intValue"

        pm.optionVar(**{kwarg: [
            "{tool_name}_{key}".format(tool_name=self.tool_name, key=key),
            value]})

    def get_maya_option(self, key, default):
        real_key = "{tool_name}_{key}".format(tool_name=self.tool_name, key=key)
        if not pm.optionVar(exists=real_key):
            return default
        return pm.optionVar(query=real_key)


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

        self.hex_value = MaterialColors.get_color(color, weight)
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


class OptionVar(object):
    def __init__(self, tool_name=None):
        if tool_name is None:
            tool_name = ""
        if len(tool_name):
            tool_name += "_"

        self.tool_name = tool_name

    def set(self, key, value):
        if isinstance(value, (str, unicode)):
            kwarg = "stringValue"
        elif isinstance(value, float):
            kwarg = "floatValue"
        elif isinstance(value, int):
            kwarg = "intValue"
        else:
            raise RuntimeError("Unsupported type: " + type(value))

        pm.optionVar(**{kwarg: [self._format_key(key), value]})

    def get(self, key, default):
        option_key = self._format_key(key)
        if not pm.optionVar(exists=option_key):
            return default
        return pm.optionVar(query=option_key)

    def _format_key(self, key):
        return "{tool_name}{key}".format(tool_name=self.tool_name, key=key)


def closed():
    global win
    win.deleteLater()
    win = None


def run(restore=False):
    """

    Args:
        restore: used only when maya is starting up and the workspace control
                 is being created by maya

    """
    global win, count

    if win == None:
        win = ColorizerWindow()
        if restore:
            parent = omui.MQtUtil.getCurrentParent()
            win_ptr = omui.MQtUtil.findControl(win.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(long(win_ptr), long(parent))
        else:
            win.create_workspace_control()

    if not restore:
        win.show()
