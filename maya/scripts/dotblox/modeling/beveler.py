import random
from PySide2 import QtCore, QtWidgets

from dotblox.core import nodepath
from dotblox.core.modeling import BevelEditor
from dotblox.core.ui import dockwindow
from maya import cmds

from dotblox.core.mutil import Repeatable


class BevelEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        widget_title = "Bevel Editor"
        self.setObjectName(widget_title.lower().replace(" ", "_"))
        self.setWindowTitle(widget_title)
        self.ui = BevelEditorUI()
        self.ui.setup_ui(self)

        cmds.scriptJob(event=["SelectionChanged", self.on_selection_changed],
                     parent=self.ui.bevel_combo.objectName())
        self.ui.bevel_combo.currentIndexChanged.connect(self.on_bevel_changed)

        self.ui.add_btn.clicked.connect(self.on_add_clicked)
        self.ui.remove_btn.clicked.connect(self.on_remove_click)
        self.ui.select_edges_btn.clicked.connect(self.on_select_edges_click)
        self.ui.remove_selected_action.triggered.connect(self.remove_from_selected)
        self.ui.remove_all_vis_action.triggered.connect(self.remove_from_all)

        self.on_selection_changed()

    def on_selection_changed(self):
        # If there is a large selection and since we only care about
        # the last object. Use maya cmds so pymel doesnt wrap everything
        # and then wrap it ourselves
        selection = cmds.ls(selection=True, long=True, objectsOnly=True, type=("transform", "mesh"))

        if not selection:
            self.set_bevel_nodes()
            return

        node = selection[-1]

        if cmds.nodeType(node) == "mesh":
            node = nodepath.parent(node)

        self.set_bevel_nodes(node)

    def set_bevel_nodes(self, node=None):
        self.ui.bevel_combo.blockSignals(True)
        self.ui.bevel_combo.setEnabled(True)

        self.ui.bevel_combo.clear()

        if node is None:
            self.ui.bevel_combo.addItem("Nothing Selected")
            self.ui.bevel_combo.setEnabled(False)
            return

        src_node = BevelEditor.get_src_node(node)
        if src_node:
            node = src_node

        bevel_nodes = BevelEditor.get_bevel_nodes(node)

        if not bevel_nodes:
            self.ui.bevel_combo.addItem("No bevels found on " + nodepath.leafname(node))
            self.ui.bevel_combo.setEnabled(False)
            return

        current_bevel_index = 0
        self.ui.bevel_combo.addItem("None", self.ui.ComboData(src_node, None))

        current_vis_bevel = BevelEditor.get_vis_bevel(node)

        for index, bevel_node in enumerate(bevel_nodes, 1):
            if current_vis_bevel == bevel_node:
                current_bevel_index = index
            self.ui.bevel_combo.addItem(nodepath.name(bevel_node),
                                        self.ui.ComboData(src_node, bevel_node))
        self.ui.bevel_combo.setCurrentIndex(current_bevel_index)
        self.ui.bevel_combo.blockSignals(False)

    def on_bevel_changed(self, index):
        data = self.ui.bevel_combo.currentData()
        if data.bevel_node:
            BevelEditor.show_bevel(data.bevel_node)
        else:
            BevelEditor.remove_vis_bevel(data.node)

    @Repeatable()
    def on_add_clicked(self):
        BevelEditor.add_to_bevel()

    @Repeatable()
    def on_remove_click(self):
        BevelEditor.remove_from_bevel()

    @Repeatable()
    def on_select_edges_click(self):
        selection = cmds.ls(selection=True, objectsOnly=True, long=True)
        edges = []
        for node in selection:
            bevel_node = BevelEditor.get_vis_bevel(node)
            if bevel_node:
                edges.append(BevelEditor.get_bevel_edges(bevel_node))

        if edges:
            cmds.select(clear=True)
            cmds.select(cmds.ls(*edges, objectsOnly=True))
            cmds.SelectEdgeMask()
            cmds.select(*edges)

    @Repeatable()
    def remove_from_selected(self):
        selection = cmds.ls(selection=True, long=True)
        for node in selection:
            src_node = BevelEditor.get_src_node(node)
            if src_node:
                BevelEditor.remove_vis_bevel(src_node)

    def remove_from_all(self):
        nodes = cmds.ls("*." + BevelEditor.BEVEL_ATTR, objectsOnly=True, type="transform")
        for node in nodes:
            src_node = BevelEditor.get_src_node(node)
            if src_node:
                BevelEditor.remove_vis_bevel(src_node)


class BevelEditorUI(object):
    def setup_ui(self, parent):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setContentsMargins(4, 0, 4, 4)
        content_layout.setAlignment(QtCore.Qt.AlignTop)

        self.menu_bar = QtWidgets.QMenuBar()
        main_layout.addWidget(self.menu_bar)

        self.util_menu = self.menu_bar.addMenu("Util")
        self.remove_selected_action = QtWidgets.QAction("Remove vis node from selected", None)
        self.util_menu.addAction(self.remove_selected_action)
        self.remove_all_vis_action = QtWidgets.QAction("Remove all vis nodes", None)
        self.util_menu.addAction(self.remove_all_vis_action)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Bevel:"))
        self.bevel_combo = QtWidgets.QComboBox()
        self.bevel_combo.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.bevel_combo.setObjectName("bevel_combo_{0}".format([random.randint(0, 9) for x in range(5)]))
        layout.addWidget(self.bevel_combo)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        content_layout.addLayout(layout)

        action_layout = QtWidgets.QGridLayout()

        self.add_btn = QtWidgets.QPushButton("Add")
        self.remove_btn = QtWidgets.QPushButton("Remove")
        self.select_edges_btn = QtWidgets.QPushButton("Select Edges")

        action_layout.addWidget(self.select_edges_btn, 0, 0, 1, 0)
        action_layout.addWidget(self.add_btn, 1, 0)
        action_layout.addWidget(self.remove_btn, 1, 1)

        content_layout.addLayout(action_layout)

        main_layout.addLayout(content_layout)
        parent.setLayout(main_layout)

    class ComboData():
        def __init__(self, node, bevel_node):
            self.node = node
            self.bevel_node = bevel_node


dock = dockwindow.DockWindowManager(BevelEditorWidget)
