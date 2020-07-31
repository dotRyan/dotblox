from PySide2 import QtCore, QtWidgets
from dotblox.core.ui import dockwindow
from dotblox.general.pivoting import PivotingWidget
from dotblox.modeling.mirrorer import MirrorerWidget
from dotblox.modeling.primitives import PrimitivesWidget
from dotbloxlib.icon import get_icon
from dotbloxlib.qt.framewidget import FrameWidget
from dotbloxlib.qt.widgettoolbutton import WidgetToolButton

__author__ = "Ryan Robinson"

class DotModelingWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.tool_name = "dotModeling"
        self.setObjectName(self.tool_name)
        self.setWindowTitle(".Modeling")

        self.ui = DotModelingWidgetUI()
        self.ui.setup_ui(self)


class DotModelingWidgetUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.primitives_frame = FrameWidget("Primitives")
        self.primitives_frame.addWidget(PrimitivesWidget())
        main_layout.addWidget(self.primitives_frame)


        self.tool_frame = FrameWidget("Tools")
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        self.pivot_tool_btn = WidgetToolButton(PivotingWidget(), icon=get_icon("dblx_pivot"))
        self.mirror_tool_btn = WidgetToolButton(MirrorerWidget(), icon=get_icon("dblx_polyMirror"))

        layout.addWidget(self.mirror_tool_btn)
        layout.addWidget(self.pivot_tool_btn)
        self.tool_frame.addLayout(layout)

        main_layout.addWidget(self.tool_frame)

        parent.setLayout(main_layout)


dock = dockwindow.DockWindowManager(DotModelingWidget)
