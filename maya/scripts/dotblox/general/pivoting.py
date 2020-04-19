from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm
import maya.OpenMayaUI as omui

win = None

class COLORS():
    LIGHT_GREEN = "#5fad88"
    LIGHT_RED = "#db5953"
    LIGHT_BLUE = "#58a5cc"
    RED = "#c83539"
    GREEN = "#66ad17"
    BLUE = "#366fd9"


class PivotingWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        MayaQWidgetDockableMixin.__init__(self, parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        # create a frame that other windows can dock into
        self.docking_frame = QtWidgets.QMainWindow(self)
        self.docking_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.docking_frame.setWindowFlags(QtCore.Qt.Widget)
        self.docking_frame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.central_widget = PivotingWidget()
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
                uiScript=ui_script,
                closeCallback=close_callback)

    @property
    def workspace_control(self):
        return self.objectName() + "WorkspaceControl"

    def show(self, *args, **kwargs):
        super(PivotingWindow, self).show(*args, **kwargs)


class PivotingWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.tool_name = "pivoting"
        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name.capitalize())


        self.ui = PivotingWidgetUI()
        self.ui.setup_ui(self)

        self.ui.center_btn.clicked.connect(
                lambda : pm.xform(centerPivotsOnComponents=True))
        
        self.ui.pos_x_btn.clicked.connect(lambda: self.pivot_to_bb("x", 0))
        self.ui.cntr_x_btn.clicked.connect(
                lambda: self.pivot_to_bb("x", center=True))
        self.ui.neg_x_btn.clicked.connect(lambda: self.pivot_to_bb("x", 1))

        self.ui.pos_y_btn.clicked.connect(lambda: self.pivot_to_bb("y", 0))
        self.ui.cntr_y_btn.clicked.connect(
                lambda: self.pivot_to_bb("y", center=True))
        self.ui.neg_y_btn.clicked.connect(lambda: self.pivot_to_bb("y", 1))

        self.ui.pos_z_btn.clicked.connect(lambda: self.pivot_to_bb("z", 0))
        self.ui.cntr_z_btn.clicked.connect(
                lambda: self.pivot_to_bb("z", center=True))
        self.ui.neg_z_btn.clicked.connect(lambda: self.pivot_to_bb("z", 1))


    def pivot_to_bb(self, axis="y", direction=1, center=False, *nodes):
        """Move the pivot of the given objects to the given direction

        Args:
            axis: x, y, z
            direction: 0 == positive |  1 == negative
            center: center the pivot in the given axis
            *nodes:

        Notes:
            Operates on the given nodes individually not as a group

        """
        if not nodes:
            nodes = pm.ls(selection=True, long=True)

        for node in nodes:
            # Determine the min and max of the given axis
            max_value = float("-inf")
            min_value = float("inf")
            for child in node.listRelatives(allDescendents=True):
                # Safeguard against any unsupported nodes
                if not hasattr(child, "boundingBox"):
                    continue
                bb = child.boundingBox()
                max_value = max(max_value, getattr(bb.max(), axis))
                min_value = min(min_value, getattr(bb.min(), axis))

            # Determine the offset value to use
            value = min_value if direction else max_value
            if center:
                mid_distance = (max_value - min_value) / 2.0
                value = abs(max_value - mid_distance)

            # Create a relative offset from the current pivot
            pivot = node.getRotatePivot(space="preTransform")
            offset = pm.dt.Vector()
            setattr(offset,
                    axis,
                    (getattr(pivot, axis) - value) * -1)

            pm.move(offset.x,
                    offset.y,
                    offset.z,
                    node.rotatePivot,
                    node.scalePivot,
                    objectSpace=True,
                    relative=True)


class PivotingWidgetUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QHBoxLayout()
        self.center_btn = PivotPushButton("Center")
        layout.addWidget(self.center_btn)
        content_layout.addLayout(layout)

        # Direction Button Grid
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(0)

        self.pos_x_btn = PivotPushButton("+X")
        self.cntr_x_btn = PivotPushButton("=X")
        self.neg_x_btn = PivotPushButton("-X")
        self.pos_y_btn = PivotPushButton("+Y")
        self.cntr_y_btn = PivotPushButton("=Y")
        self.neg_y_btn = PivotPushButton("-Y")
        self.pos_z_btn = PivotPushButton("+Z")
        self.cntr_z_btn = PivotPushButton("=Z")
        self.neg_z_btn = PivotPushButton("-Z")

        grid_layout.addWidget(self.neg_x_btn, 0, 0, 1, 2)
        grid_layout.addWidget(self.cntr_x_btn, 0, 2, 1, 1)
        grid_layout.addWidget(self.pos_x_btn, 0, 3, 1, 2)
        grid_layout.addWidget(self.neg_y_btn, 1, 0, 1, 2)
        grid_layout.addWidget(self.cntr_y_btn, 1, 2, 1, 1)
        grid_layout.addWidget(self.pos_y_btn, 1, 3, 1, 2)
        grid_layout.addWidget(self.neg_z_btn, 2, 0, 1, 2)
        grid_layout.addWidget(self.cntr_z_btn, 2, 2, 1, 1)
        grid_layout.addWidget(self.pos_z_btn, 2, 3, 1, 2)

        content_layout.addLayout(grid_layout)

        main_layout.addLayout(content_layout)
        parent.setLayout(main_layout)


class PivotPushButton(QtWidgets.QPushButton):
    dark_factor = 110

    COLORS = {
        "+X": COLORS.RED,
        "=X": QtGui.QColor(COLORS.RED).darker(dark_factor).name(),
        "-X": QtGui.QColor(COLORS.RED).darker(dark_factor + 15).name(),
        "+Y": COLORS.GREEN,
        "=Y": QtGui.QColor(COLORS.GREEN).darker(dark_factor).name(),
        "-Y": QtGui.QColor(COLORS.GREEN).darker(dark_factor + 15).name(),
        "+Z": COLORS.BLUE,
        "=Z": QtGui.QColor(COLORS.BLUE).darker(dark_factor).name(),
        "-Z": QtGui.QColor(COLORS.BLUE).darker(dark_factor + 15).name(),
        "All": COLORS.LIGHT_BLUE,
        "Center": COLORS.LIGHT_GREEN,
        "T":COLORS.RED,
        "R":COLORS.GREEN,
        "S":COLORS.BLUE,
    }

    def __init__(self, label, parent=None):
        QtWidgets.QPushButton.__init__(self, label, parent=parent)

        if label in self.COLORS:
            self.setStyleSheet("""
            font-size: 12px;
            background-color:{color};""".format(
                    color=self.COLORS[label]
            ))

        if "=" in label:
            self.setText("=")


def closed():
    global win
    win.deleteLater()
    win = None


def run(restore=False):
    global win

    if win == None:
        win = PivotingWindow()

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
