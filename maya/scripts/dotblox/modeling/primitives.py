from dotblox.core import general
from dotblox.core.mutil import OptionVar, Undoable
from dotblox.core.ui import dockwindow
from PySide2 import QtWidgets, QtCore, QtGui
import pymel.core as pm

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
                                             self.ui.sphere_btn.activeDivision()))
        self.ui.cube_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.CUBE,
                                             self.ui.cube_btn.activeDivision()))
        self.ui.cylinder_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.CYLINDER,
                                             self.ui.cylinder_btn.activeDivision()))
        self.ui.plane_btn.clicked.connect(
                lambda: self._make_primitive(PRIMITIVE.PLANE,
                                             self.ui.plane_btn.activeDivision()))
        self.ui.snap_btn.clicked.connect(self._snap_selection)

    @Undoable()
    def _make_primitive(self, primitive, divisions):

        selection = pm.ls(selection=True)
        components = pm.filterExpand(selection, sm=(31, 32, 34, 35))
        component_objects = list(set(pm.ls(components, objectsOnly=True)))

        # Only snap if the len of nodes is 1 and the selection is a component
        snap = len(component_objects) == 1 and components
        if snap:
            # Get the tool position before node creation since maya
            # selects new nodes
            tool_position = general.get_tool_pivot_position()

        if primitive == PRIMITIVE.SPHERE:
            node, _ = pm.polySphere(subdivisionsAxis=divisions,
                                    subdivisionsHeight=divisions)
        elif primitive == PRIMITIVE.CUBE:
            node, _ = pm.polyCube(subdivisionsWidth=divisions,
                                  subdivisionsHeight=divisions,
                                  subdivisionsDepth=divisions)
        elif primitive == PRIMITIVE.CYLINDER:
            node, _ = pm.polyCylinder(subdivisionsAxis=divisions,
                                      subdivisionsHeight=1,
                                      subdivisionsCaps=1)
        elif primitive == PRIMITIVE.PLANE:
            node, _ = pm.polyPlane(subdivisionsWidth=divisions,
                                   subdivisionsHeight=divisions)
        else:
            raise RuntimeError("Primative not supported")

        if snap:
            general.snap_to_mesh_face(component_objects[0], node, tool_position)

    @Undoable()
    def _snap_selection(self):
        selection = pm.ls(selection=True, long=True)
        components = pm.ls(pm.filterExpand(selection, sm=(31, 32, 34, 35)))
        component_objects = list(set(pm.ls(components, objectsOnly=True)))

        # Only snap if the len of nodes is 1 and the selection is a component

        # Only snap if the len of nodes is 1 abd the selection is a component

        if len(component_objects) != 1:
            pm.displayError("Too many objects with components selected. "
                            "Please Select only 1 objects components")
            return

        pm.select(components)
        tool_position = general.get_tool_pivot_position()
        nodes = pm.ls(set(selection) - set(components), type="transform")
        for node in nodes:
            general.snap_to_mesh_face(component_objects[0], node, point=tool_position)
        pm.select(nodes)


class PrimitivesWidgetUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.sphere_btn = ToolButton(PRIMITIVE.SPHERE , ":polySphere.png")
        self.sphere_btn.setDivisions([8, 16, 24, 32, 64], 16)
        main_layout.addWidget(self.sphere_btn)

        self.cube_btn = ToolButton(PRIMITIVE.CUBE , ":polyCube.png")
        self.cube_btn.setDivisions([1, 2, 3, 4])
        main_layout.addWidget(self.cube_btn)

        self.cylinder_btn = ToolButton(PRIMITIVE.CYLINDER , ":polyCylinder.png")
        self.cylinder_btn.setDivisions([8, 16, 24, 32, 64], 16)
        main_layout.addWidget(self.cylinder_btn)

        self.plane_btn = ToolButton(PRIMITIVE.PLANE, ":polyMesh.png")
        self.plane_btn.setDivisions([1, 2, 3, 4])
        main_layout.addWidget(self.plane_btn)

        self.snap_btn = FlatToolButton(":snapPlane_200.png")
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
        self._context_menu.addSeparator().setText("Divisions")
        self._label = label
        self._divisions = {}
        self._active_division = None

    def setDivisions(self, divisions, default=None):
        if default is None:
            default = divisions[0]

        divisions = list(divisions)
        for div in sorted(divisions):
            self._divisions[div] = self._context_menu.addAction(
                    str(div),
                    lambda x=div: self._on_division_selected(x))
        value = option_var.get(self._label, default)
        self.setActiveDivision(value)

    def setActiveDivision(self, div):
        self._active_division = div
        option_var.set(self._label, div)
        self.repaint()

    def activeDivision(self):
        return self._active_division

    def _on_division_selected(self, division):
        self.setActiveDivision(division)
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
                         str(self._active_division) or "")


dock = dockwindow.DockWindowManager(PrimitivesWidget)
