from dotblox.core.ui import dockwindow
from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm

from dotblox.core.general import pivot_to_bb
from dotblox.core.constant import AXIS, DIRECTION


class COLORS():
    LIGHT_GREEN = "#5fad88"
    LIGHT_RED = "#db5953"
    LIGHT_BLUE = "#58a5cc"
    RED = "#c83539"
    GREEN = "#66ad17"
    BLUE = "#366fd9"


class PivotingWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.tool_name = "pivoting"
        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name.capitalize())

        self.ui = PivotingWidgetUI()
        self.ui.setup_ui(self)

        self.ui.center_btn.clicked.connect(
                lambda: pm.xform(centerPivotsOnComponents=True))
        self.ui.bake_btn.clicked.connect(
                lambda: pm.runtime.BakeCustomPivot()
        )

        self.ui.pos_x_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.X, direction=DIRECTION.POSITIVE))
        self.ui.cntr_x_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.X, center=True))
        self.ui.neg_x_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.X, direction=DIRECTION.NEGATIVE))

        self.ui.pos_y_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Y, direction=DIRECTION.POSITIVE))
        self.ui.cntr_y_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Y, center=True))
        self.ui.neg_y_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Y, direction=DIRECTION.NEGATIVE))

        self.ui.pos_z_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Z, direction=DIRECTION.POSITIVE))
        self.ui.cntr_z_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Z, center=True))
        self.ui.neg_z_btn.clicked.connect(
                lambda: pivot_to_bb(axis=AXIS.Z, direction=DIRECTION.NEGATIVE))

    def minimumSizeHint(self):
        initial = QtWidgets.QWidget.sizeHint(self)
        return QtCore.QSize(150, initial.height())


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

        self.bake_btn = PivotPushButton("Bake")
        layout.addWidget(self.bake_btn)
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
        "Center": COLORS.LIGHT_GREEN,
        "Bake": COLORS.LIGHT_BLUE
    }

    def __init__(self, label, parent=None):
        QtWidgets.QPushButton.__init__(self, label, parent=parent)

        if label in self.COLORS:
            self.setStyleSheet("""background-color:{color};""".format(
                    color=self.COLORS[label]))
        if "=" in label:
            self.setText("=")


dock = dockwindow.DockWindowManager(PivotingWidget)
