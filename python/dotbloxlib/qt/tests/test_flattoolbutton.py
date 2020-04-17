from PySide2 import QtCore, QtWidgets
from dotbloxlib.qt import standaloneqt
from dotbloxlib.qt.flattoolbutton import FlatToolButton


def test_action():
    print("Action works!!")


def test(app, win, layout):
    win.setWindowTitle("WidgetToolButton Test")
    win.resize(128, 64)
    layout.setContentsMargins(0, 0, 0, 0)

    style = win.style()

    btn = FlatToolButton(icon=style.standardIcon(style.SP_DirIcon))
    btn.clicked.connect(test_action)

    layout.addWidget(btn)


standaloneqt.run_as_window(test)
