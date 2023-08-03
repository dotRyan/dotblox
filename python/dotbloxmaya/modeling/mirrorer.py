from dotbloxmaya.core.constant import AXIS, DIRECTION
from dotbloxmaya.core.ui import dockwindow
from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial


from dotbloxmaya.core.mutil import Repeatable, Undoable, OptionVar
from dotbloxmaya.core.modeling import poly_mirror

__author__ = "Ryan Robinson"

win = None
class COLORS():
    LIGHT_GREEN = "#5fad88"
    LIGHT_RED = "#db5953"
    LIGHT_BLUE = "#58a5cc"
    RED = "#c83539"
    GREEN = "#66ad17"
    BLUE = "#366fd9"


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
            self.ui.pos_x_btn: [AXIS.X, DIRECTION.POSITIVE],
            self.ui.neg_x_btn: [AXIS.X, DIRECTION.NEGATIVE],
            self.ui.pos_y_btn: [AXIS.Y, DIRECTION.POSITIVE],
            self.ui.neg_y_btn: [AXIS.Y, DIRECTION.NEGATIVE],
            self.ui.pos_z_btn: [AXIS.Z, DIRECTION.POSITIVE],
            self.ui.neg_z_btn: [AXIS.Z, DIRECTION.NEGATIVE],
        }

        for button, args in button_mapping.items():
            button.clicked.connect(partial(self.do_mirror, *args))

        self.start_up_settings()

    def start_up_settings(self):
        space = self.option_var.get(self.SPACE_OPTION_KEY, 1)
        self.ui.space_combo.setCurrentIndex(space)

    @Repeatable()
    @Undoable()
    def do_mirror(self, axis, direction):
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
        poly_mirror(axis=axis,
                    direction=direction,
                    mirror_axis=mirror_axis)



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


dock = dockwindow.DockWindowManager(MirrorerWidget)