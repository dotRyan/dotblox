from PySide2 import QtCore, QtWidgets
import sys

__author__ = "Ryan Robinson"


def run(func):
    """
    Instantiates a QApplication


    app is passed into func

    func must return the window
    """
    try:
        if QtWidgets.QApplication.instance() is not None:
            raise RuntimeError("QApplication already instanced")

        app = QtWidgets.QApplication(sys.argv)

        # Keep an instance of the window
        win = func(app)

        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise


def run_as_window(func):
    """Instantiates a QWidget as a window

    app, win and layout are passed into func
    """

    def wrap(app):
        win = QtWidgets.QWidget()
        win.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        win.resize(640 / 2, 480 / 2)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        func(app, win, layout)

        win.setLayout(layout)
        win.show()
        return win

    run(wrap)
