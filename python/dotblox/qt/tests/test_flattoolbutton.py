from PySide2 import QtCore, QtWidgets
from dotblox.qt import standaloneqt
from dotblox.qt.flattoolbutton import FlatToolButton


def test_action():
    print("Action works!!")


def test(app, win, layout):
    win.setWindowTitle("FlatToolButton Test")
    win.resize(128, 64)
    layout.setContentsMargins(0, 0, 0, 0)
    h_layout = QtWidgets.QHBoxLayout()

    style = win.style()

    btn = FlatToolButton(icon=style.standardIcon(style.SP_DirIcon))
    btn.clicked.connect(test_action)
    h_layout.addWidget(btn)

    btn = FlatToolButton(icon=style.standardIcon(style.SP_DirIcon))
    btn.setEnabled(False)
    btn.clicked.connect(test_action)
    h_layout.addWidget(btn)

    layout.addLayout(h_layout)


if __name__ == '__main__':
    standaloneqt.run_as_window(test)
