from PySide2 import QtCore, QtGui, QtWidgets

__author__ = "Ryan Robinson"


class FlatToolButton(QtWidgets.QToolButton):
    def __init__(self, icon=None, parent=None):
        """ToolButton to match mayas style

        Args:
            icon (str): path of icon to be set
        """
        QtWidgets.QToolButton.__init__(self, parent=parent)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setIcon(QtGui.QIcon(icon))
        # Need a better way than to modify the stylesheet
        self.resetStylesheet()

    def resetStylesheet(self):
        """Convenience to reset the stylesheet back to the defaults"""
        QtWidgets.QToolButton.setStyleSheet(self, """
        {cls}{{
            margin:0;
            border: none;
        }}

        {cls}:pressed {{
            margin:0;
            border: none;
        }}
        """.format(cls=self.__class__.__name__))
