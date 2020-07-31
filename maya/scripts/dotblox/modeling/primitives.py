from dotblox.core.constant import AXIS, DIRECTION
from dotbloxlib.icon import get_icon
from maya import cmds
from PySide2 import QtWidgets, QtCore, QtGui

from dotblox.core import general
from dotblox.core.mutil import OptionVar, Undoable
from dotblox.core.ui import dockwindow

__author__ = "Ryan Robinson"

from dotbloxlib.qt.flattoolbutton import FlatToolButton

class PRIMITIVE():
    PLANE = "plane"
    CUBE = "cube"
    CYLINDER = "cylinder"
    SPHERE = "sphere"

option_var = OptionVar(__name__)


class PrimitivesWidget(QtWidgets.QWidget):
    """Widget to create primitives.

    """

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.tool_name = "primitives"
        self.setObjectName(self.tool_name)
        self.setWindowTitle(self.tool_name.capitalize())

        self.ui = PrimitivesWidgetUI()
        self.ui.setup_ui(self)

        self.ui.sphere_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.SPHERE,
                                             self.ui.sphere_btn.activeOption()))
        self.ui.cube_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.CUBE,
                                             self.ui.cube_btn.activeOption()))
        self.ui.cylinder_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.CYLINDER,
                                             self.ui.cylinder_btn.activeOption()))
        self.ui.plane_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.PLANE,
                                             self.ui.plane_btn.activeOption()))

        self.ui.snap_btn.clicked.connect(self._snap_selection)

    @Undoable()
    def _make_primitive(self, primitive, divisions):

        selection = cmds.ls(selection=True, long=True)
        components = cmds.filterExpand(selection, sm=(31, 32, 34, 35), fullPath=True)
        component_objects = list(set(cmds.ls(components, objectsOnly=True, long=True)))

        # Only snap if the len of nodes is 1 and the selection is a component
        snap = len(component_objects) == 1 and components
        if snap:
            # Get the tool position before node creation since maya
            # selects new nodes
            tool_position = general.get_tool_pivot_position()

        if primitive == PRIMITIVE.SPHERE:
            node, _ = cmds.polySphere(subdivisionsAxis=divisions,
                                    subdivisionsHeight=divisions)
        elif primitive == PRIMITIVE.CUBE:
            node, _ = cmds.polyCube(subdivisionsWidth=divisions,
                                  subdivisionsHeight=divisions,
                                  subdivisionsDepth=divisions)
        elif primitive == PRIMITIVE.CYLINDER:
            node, _ = cmds.polyCylinder(subdivisionsAxis=divisions,
                                      subdivisionsHeight=1,
                                      subdivisionsCaps=1)
        elif primitive == PRIMITIVE.PLANE:
            node, _ = cmds.polyPlane(subdivisionsWidth=divisions,
                                   subdivisionsHeight=divisions)
        else:
            raise RuntimeError("Primative not supported")

        if snap:
            general.snap_to_mesh_face(component_objects[0], node, tool_position)

    @Undoable()
    def _snap_selection(self):
        option = self.ui.snap_btn.activeOption()

        direction = DIRECTION.NEGATIVE if "-" in option else DIRECTION.POSITIVE
        axis = getattr(AXIS, option.strip("-").upper())


        selection = cmds.ls(selection=True, long=True)
        components = cmds.filterExpand(selection, sm=(31, 32, 34, 35), fullPath=True)
        component_objects = list(set(cmds.ls(components, objectsOnly=True, long=True)))

        # Only snap if the len of nodes is 1 and the selection is a component
        if len(component_objects) != 1:
            cmds.warning("Too many objects with components selected. "
                            "Please Select only 1 objects components")
            return

        cmds.select(components)
        tool_position = general.get_tool_pivot_position()
        nodes = cmds.ls(list(set(selection) - set(components)), type="transform")
        for node in nodes:
            general.snap_to_mesh_face(component_objects[0],
                                      node,
                                      point=tool_position,
                                      up_axis=axis,
                                      direction=direction)
        cmds.select(nodes)


class PrimitivesWidgetUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.sphere_btn = ToolButton(PRIMITIVE.SPHERE , get_icon("dblx_polySphere"))
        self.sphere_btn.setOptions([8, 16, 24, 32, 64],
                                   default=16,
                                   label="Divisions")
        main_layout.addWidget(self.sphere_btn)

        self.cube_btn = ToolButton(PRIMITIVE.CUBE , get_icon("dblx_polyCube"))
        self.cube_btn.setOptions([1, 2, 3, 4], label="Divisions")
        main_layout.addWidget(self.cube_btn)

        self.cylinder_btn = ToolButton(PRIMITIVE.CYLINDER , get_icon("dblx_polyCylinder"))
        self.cylinder_btn.setOptions([8, 16, 24, 32, 64],
                                     default=16,
                                     label="Divisions")
        main_layout.addWidget(self.cylinder_btn)

        self.plane_btn = ToolButton(PRIMITIVE.PLANE, get_icon("dblx_polyMesh"))
        self.plane_btn.setOptions([1, 2, 3, 4], label="Divisions")
        main_layout.addWidget(self.plane_btn)

        self.snap_btn = ToolButton("Snap", get_icon("dblx_snap"))
        self.snap_btn.setOptions(["x", "y", "z", "-x", "-y", "-z"],
                                 default="y",
                                 label="Direction")

        main_layout.addWidget(self.snap_btn)

        parent.setLayout(main_layout)


class ToolButton(FlatToolButton):
    def __init__(self, label, icon=None, parent=None):
        """

        Args:
            widget (QtWidgets.QWidget): widget to be used for the popup
            icon (str): path of icon to be set
        """
        FlatToolButton.__init__(self, icon=icon, parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._context_menu = QtWidgets.QMenu()
        # The if the first item in a menu is a separator it seems not
        # wanna draw. But setting collapsible false seems to fix
        self._context_menu.setSeparatorsCollapsible(False)

        self._label = label
        self._options = {}
        self._active_option = None

    def setOptions(self, options, default=None, label=None):
        if default is None:
            default = options[0]

        if label is not None:
            self._context_menu.addSeparator().setText(label)

        options = list(options)
        for option in options:
            self._options[option] = self._context_menu.addAction(
                    str(option),
                    lambda x=option: self._on_option_selected(x))
        value = option_var.get(self._label, default)
        self.setActiveOption(value)

    def setActiveOption(self, option):
        self._active_option = option
        option_var.set(self._label, option)
        self.repaint()

    def activeOption(self):
        return self._active_option

    def _on_option_selected(self, division):
        self.setActiveOption(division)
        self.clicked.emit()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self._context_menu.exec_(event.globalPos())
        else:
            FlatToolButton.mousePressEvent(self, event)

    def paintEvent(self, event):
        FlatToolButton.paintEvent(self, event)

        rect = event.rect()
        painter = QtGui.QPainter(self)
        painter.drawText(rect.adjusted(0, 0, -4, -4), QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,
                         str(self._active_option) or "")


dock = dockwindow.DockWindowManager(PrimitivesWidget)
