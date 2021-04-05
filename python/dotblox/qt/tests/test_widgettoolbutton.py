from PySide2 import QtCore, QtWidgets
from dotblox.qt import framewidget, standaloneqt
from dotblox.qt.widgettoolbutton import WidgetToolButton


def test_action():
    print("Action works!!")


def test(app, win, layout):
    win.setWindowTitle("WidgetToolButton Test")
    win.resize(128, 64)
    layout.setContentsMargins(0, 0, 0, 0)

    sub_widget = QtWidgets.QWidget()
    sub_widget.setWindowTitle("WidgetToolPopup Test")
    sub_layout = QtWidgets.QVBoxLayout()
    sub_layout.setContentsMargins(0, 0, 0, 0)
    btn = QtWidgets.QPushButton("Test Button")
    btn.clicked.connect(test_action)
    sub_layout.addWidget(btn)
    sub_widget.setLayout(sub_layout)

    style = win.style()

    btn = WidgetToolButton(sub_widget, icon=style.standardIcon(style.SP_DirIcon))

    layout.addWidget(btn)


standaloneqt.run_as_window(test)
