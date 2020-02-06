from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm
import maya.OpenMayaUI as omui

from dotblox.common import Undoable

__author__ = "Ryan Robinson"

win = None
class COLORS():
    LIGHT_GREEN = "#5fad88"
    LIGHT_RED = "#db5953"
    LIGHT_BLUE = "#58a5cc"
    RED = "#c83539"
    GREEN = "#66ad17"
    BLUE = "#366fd9"


class MirrorerWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        MayaQWidgetDockableMixin.__init__(self, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        # create a frame that other windows can dock into
        self.docking_frame = QtWidgets.QMainWindow(self)
        self.docking_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.docking_frame.setWindowFlags(QtCore.Qt.Widget)
        self.docking_frame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.central_widget = MirrorerWidget()
        self.setObjectName(self.central_widget.objectName() + "Window")
        self.setWindowTitle(self.central_widget.windowTitle())

        self.docking_frame.setCentralWidget(self.central_widget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.docking_frame)
        self.setLayout(layout)

        self.minimum_size = self.central_widget.minimumSizeHint()
        self.preferred_size = QtCore.QSize(self.minimum_size.width(),
                                           self.minimum_size.height())

    def setSizeHint(self, size):
        self.preferred_size = size

    def sizeHint(self):
        return self.preferred_size

    def minimumSizeHint(self):
        return self.minimum_size

    def create_workspace_control(self):
        """Creates the workspace control and its defaults"""

        ui_script = "import {name}; {name}.run(restore=True)".format(name=__name__)
        close_callback = "import {name}; {name}.closed()".format(name=__name__)

        self.setDockableParameters(
                dockable=True,
                retain=False,
                minWidth=self.preferred_size.width(),
                width=self.preferred_size.width(),
                height=self.preferred_size.height(),
                widthSizingProperty="preferred",
                # heightSizingProperty="fixed",
                uiScript=ui_script,
                closeCallback=close_callback)

    @property
    def workspace_control(self):
        return self.objectName() + "WorkspaceControl"

    def show(self, *args, **kwargs):
        super(MirrorerWindow, self).show(*args, **kwargs)


class MirrorerWidget(QtWidgets.QWidget):
    SPACE_OPTION_KEY = "space"

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.tool_name = "mirrorer"
        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name.capitalize())

        self.option_var = OptionVar(self.tool_name)

        self.ui = MirrorerWidgetUI()
        self.ui.setup_ui(self)


        self.ui.space_combo.currentIndexChanged.connect(self.on_space_change)

        button_mapping = {
            self.ui.pos_x_btn: [0, 0],
            self.ui.neg_x_btn: [0, 1],
            self.ui.pos_y_btn: [1, 0],
            self.ui.neg_y_btn: [1, 1],
            self.ui.pos_z_btn: [2, 0],
            self.ui.neg_z_btn: [2, 1],
        }

        for button, args in button_mapping.iteritems():
            button.clicked.connect(Undoable()(lambda args=args: self.doMirror(*args)))

        self.start_up_settings()

    def start_up_settings(self):
        space = self.option_var.get(self.SPACE_OPTION_KEY, 1)
        self.ui.space_combo.setCurrentIndex(space)

    def doMirror(self, axis, direction):
        """
        Args:
            axis: 0:X, 1:Y, 2:Z
            direction: +:0, -:1
            mirror_axis: {
                            0: "Bounding Box",
                            1: "Object",
                            2: "World"
                        }
        """
        mirror_axis = self.ui.space_combo.currentIndex()
        self.poly_mirror(axis=axis,
                         direction=direction,
                         mirror_axis=mirror_axis)

    @Undoable()
    def poly_mirror(self, axis=2, direction=1, mirror_axis=1 ,*nodes):
        """
        Args:
            axis: 0:X, 1:Y, 2:Z
            direction: +:0, -:1
            mirror_axis: {
                            0: "Bounding Box",
                            1: "Object",
                            2: "World"
                        }
        """
        if not nodes:
            nodes = pm.ls(selection=True, long=True)

        for node in nodes:
            pm.polyMirrorFace(node,
                              cutMesh=True,
                              axis=axis,
                              axisDirection=direction,
                              mergeMode=1,  # Merge Border Vertices
                              mirrorAxis=mirror_axis,
                              mirrorPosition=0,
                              mergeThresholdType=1,  # Merge Threshold custom
                              mergeThreshold=0.001,
                              flipUVs=False,
                              smoothingAngle=30,
                              constructionHistory=True,
                              )

    def on_space_change(self, index):
        self.option_var.set(self.SPACE_OPTION_KEY, index)


class MirrorerWidgetUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Space:"))
        self.space_combo = QtWidgets.QComboBox()
        self.space_combo.addItems(["Bounding Box", "Object", "World"])
        layout.addWidget(self.space_combo)
        layout.setStretch(1, 3)
        content_layout.addLayout(layout)
        # Direction Button Grid
        grid_layout = QtWidgets.QGridLayout()

        self.pos_x_btn = MirrorPushButton("+X")
        self.neg_x_btn = MirrorPushButton("-X")
        self.pos_y_btn = MirrorPushButton("+Y")
        self.neg_y_btn = MirrorPushButton("-Y")
        self.pos_z_btn = MirrorPushButton("+Z")
        self.neg_z_btn = MirrorPushButton("-Z")

        grid_layout.addWidget(self.neg_x_btn, 0, 0)
        grid_layout.addWidget(self.pos_x_btn, 0, 1)
        grid_layout.addWidget(self.neg_y_btn, 1, 0)
        grid_layout.addWidget(self.pos_y_btn, 1, 1)
        grid_layout.addWidget(self.neg_z_btn, 2, 0)
        grid_layout.addWidget(self.pos_z_btn, 2, 1)

        grid_layout.setSpacing(0)

        content_layout.addLayout(grid_layout)

        main_layout.addLayout(content_layout)
        parent.setLayout(main_layout)


class MirrorPushButton(QtWidgets.QPushButton):
    dark_factor = 110
    COLORS = {
        "+X": COLORS.RED,
        "-X": QtGui.QColor(COLORS.RED).darker(dark_factor).name(),
        "+Y": COLORS.GREEN,
        "-Y": QtGui.QColor(COLORS.GREEN).darker(dark_factor).name(),
        "+Z": COLORS.BLUE,
        "-Z": QtGui.QColor(COLORS.BLUE).darker(dark_factor).name(),
    }

    def __init__(self, label, parent=None):
        QtWidgets.QPushButton.__init__(self, label, parent=parent)

        if label in self.COLORS:
            self.setStyleSheet("""
            font-size: 12px;
            background-color:{color};""".format(
                    color=self.COLORS[label]
            ))


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
        print
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
    global win

    if win == None:
        win = MirrorerWindow()

        if restore:
            # The current parent is the workspace control created by maya
            parent = omui.MQtUtil.getCurrentParent()
            win_ptr = omui.MQtUtil.findControl(win.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(long(win_ptr), long(parent))
        else:
            # get the state before the workspace control is created
            win.create_workspace_control()

    # Maya handles the visibility
    if not restore:
        if not win.isVisible():
            win.show()
