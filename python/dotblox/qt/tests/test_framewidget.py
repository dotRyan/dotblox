from PySide2 import QtCore, QtWidgets
from dotblox.qt import framewidget, standaloneqt


def test(app, win, layout):
    win.setWindowTitle("FrameWidget Test")
    layout.setContentsMargins(0, 0, 0, 0)

    frame = framewidget.FrameWidget("frameWidget collapsable", collapsible=True)
    frame.addWidget(QtWidgets.QPushButton("AAAAAAA"))
    frame.addWidget(QtWidgets.QComboBox())
    layout.addWidget(frame)

    frame = framewidget.FrameWidget("frameWidget static", collapsible=True)
    frame.addWidget(QtWidgets.QPushButton("BBBBBBB"))
    frame.addWidget(QtWidgets.QComboBox())
    layout.addWidget(frame)

    frame = framewidget.FrameWidget("frameWidget setLayout", collapsible=True)
    new_layout = QtWidgets.QVBoxLayout()
    frame.addWidget(QtWidgets.QPushButton("CCCCCCC"))
    frame.addWidget(QtWidgets.QComboBox())
    frame.setLayout(new_layout)

    layout.addWidget(frame)

    item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    layout.addSpacerItem(item)


standaloneqt.run_as_window(test)
