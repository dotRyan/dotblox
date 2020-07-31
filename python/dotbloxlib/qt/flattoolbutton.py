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
        if not isinstance(icon, QtGui.QIcon):
            icon = QtGui.QIcon(icon)
        self.setIcon(icon)

    def setIcon(self, icon):
        QtWidgets.QToolButton.setIcon(self, icon)
        self.__hover_icon = self._make_icon(.2)
        self.__disabled_icon = self._make_icon(-.2)

    def enterEvent(self, event):
        QtWidgets.QToolButton.enterEvent(self, event)
        # Maya does repaint for some reason
        self.repaint()

    def leaveEvent(self, event):
        QtWidgets.QToolButton.leaveEvent(self, event)
        # Maya does repaint for some reason
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        style = QtWidgets.QStyleOptionToolButton()
        style.initFrom(self)

        icon = self.icon()
        if style.state & QtWidgets.QStyle.State_MouseOver:
            icon = self.__hover_icon
        if not (style.state & QtWidgets.QStyle.State_Enabled):
            icon = self.__disabled_icon

        margin = round(event.rect().width() * 0.125)
        rect = event.rect().adjusted(margin, -margin, -margin, margin)
        icon.paint(painter, rect)
        painter.end()

    def _make_icon(self, factor=0):
        """Lightens or darkens an icon based on the factor

        Args:
            icon (QtQui.QIcon):
            factor (float): ideal range is (0-1 for lighter) (-1 - 0 for darker) and  but can be pushed further

        Returns:
            QtQui.QIcon: the adjusted icon

        """
        icon = self.icon()

        if factor == 0:
            return icon

        if icon.isNull():
            return

        px = icon.pixmap(icon.availableSizes()[-1])

        painter = QtGui.QPainter(px)
        if factor > 0:
            color = QtGui.QColor(255, 255, 255, 255 * factor)
        elif factor < 0:
            color = QtGui.QColor(0, 0, 0, 255 * abs(factor))

        painter.setCompositionMode(painter.CompositionMode_SourceAtop)
        painter.fillRect(px.rect(), color)
        painter.end()
        return QtGui.QIcon(px)
