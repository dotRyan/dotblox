from PySide2 import QtCore, QtGui, QtWidgets

__author__ = "Ryan Robinson"

from dotblox.qt.flattoolbutton import FlatToolButton


class WidgetToolButton(FlatToolButton):
    """QToolButton overrides to place the given widget as the
    popup menu

    Notes:
        Do not alter the instance by means of the built-in
         QToolButton methods that handle the menu and button state

    Args:
        widget (QtWidgets.QWidget): widget to be used for the popup
        icon (str): path of icon to be set
    """

    def __init__(self, widget, icon=None):
        FlatToolButton.__init__(self, icon=icon, parent=None)

        self.tool_popup = _WidgetToolButtonPopup(widget, self)
        self.tool_popup.aboutToHide.connect(self._on_popup_state_change)
        self.tool_popup.aboutToTear.connect(self._on_popup_state_change)
        self.tool_popup.hide()

    def setWidget(self, widget=None):
        """Set the current widget of the popup"""
        self.tool_popup.setWidget(widget)

    def widget(self):
        """Get the current widget of the popup"""
        return self.tool_popup.widget()

    def mousePressEvent(self, event):
        """Override to show widget popup

        Args:
            event(QtGui.QMouseEvent):
        """
        if not self.isDown():
            self.tool_popup.show()
            self.tool_popup.move(self._get_menu_pos())

        FlatToolButton.mousePressEvent(self, event)

    def _on_popup_state_change(self):
        # For some reason self.underMouse() is returning false
        # Manually handle the state of the button
        # when torn off or hidden (auto hidden from popup)
        if not self.rect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
            self.setDown(False)

    def _get_menu_pos(self):
        """Refactored from QToolButton.cpp"""
        horizontal = True

        rect = self.rect()
        desktop = QtWidgets.QDesktopWidget()
        screen = desktop.availableGeometry(self.mapToGlobal(rect.center()))
        sh = self.tool_popup.sizeHint()
        if horizontal:
            if (self.isRightToLeft()):
                if (self.mapToGlobal(QtCore.QPoint(0, rect.bottom())).y() + sh.height() <= screen.bottom()):
                    p = self.mapToGlobal(rect.bottomRight())
                else:
                    p = self.mapToGlobal(rect.topRight() - QtCore.QPoint(0, sh.height()))
                p.setX(p.x() - sh.width())

            else:
                if (self.mapToGlobal(QtCore.QPoint(0, rect.bottom())).y() + sh.height() <= screen.bottom()):
                    p = self.mapToGlobal(rect.bottomLeft())
                else:
                    p = self.mapToGlobal(rect.topLeft() - QtCore.QPoint(0, sh.height()))
        else:
            if (self.isRightToLeft()):
                if (self.mapToGlobal(QtCore.QPoint(rect.left(), 0)).x() - sh.width() <= screen.x()):
                    p = self.mapToGlobal(rect.topRight())
                else:
                    p = self.mapToGlobal(rect.topLeft())
                    p.setX(p.x() - sh.width())

            else:
                if (self.mapToGlobal(QtCore.QPoint(rect.right(), 0)).x() + sh.width() <= screen.right()):
                    p = self.mapToGlobal(rect.topRight())
                else:
                    p = self.mapToGlobal(rect.topLeft() - QtCore.QPoint(sh.width(), 0))

        p.setX(max(screen.left(), min(p.x(), screen.right() - sh.width())))
        p.setY(p.y() + 1)

        return p


class _WidgetToolButtonPopup(QtWidgets.QWidget):
    """Widget that acts as the popup for `WidgetToolButton`

    Args:
        widget (QtWidgets.QWidget):
        parent (QtWidgets.QWidget):

    Signals:
        aboutToHide: if the window is about to hide
        aboutToTear: if the window will be torn from the popup
    """

    aboutToHide = QtCore.Signal()
    aboutToTear = QtCore.Signal()

    def __init__(self, widget=None, parent=None):

        QtWidgets.QWidget.__init__(self, parent=parent)
        self.is_floating = False
        self._widget = None

        self._init_ui()
        self.setWidget(widget)

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._tear_off_btn = _TearOffButton()
        self._tear_off_btn.clicked.connect(self._on_tear_off)
        layout.addWidget(self._tear_off_btn)
        self.setLayout(layout)

    def setWidget(self, widget=None):
        """Set the current widget"""
        if widget is not None:
            self.layout().addWidget(widget)
            self.setWindowTitle(widget.windowTitle())

        if self._widget:
            self.layout().remove(self._widget)
        self._widget = widget

    def widget(self):
        """Get the current widget
        Returns:
            QtWidgets.QWidget:
        """
        return self._widget

    def mouseReleaseEvent(self, event):
        """Override the mouse release event to emit the click event of
        the button under the mouse.

        This happens when a user clicks and drags from  the
        `WidgetToolButton` to this popup.
        """
        if not self.is_floating:
            child_at = self.childAt(event.pos())
            action = lambda: None
            accept = False

            if child_at:
                if hasattr(child_at, "clicked"):
                    action = child_at.clicked.emit
                    accept = True

            if accept:
                self.hide()
                action()
                return

        return QtWidgets.QWidget.mouseReleaseEvent(self, event)

    def _on_tear_off(self):
        """Slot "for tearing off" the menu"""
        self.aboutToTear.emit()
        self.show(floating=True)

    def hideEvent(self, event):
        """Override to tell the tool button when its about to hide"""
        self.aboutToHide.emit()
        QtWidgets.QWidget.hideEvent(self, event)

    def show(self, floating=False):
        """Override show to handle weather the window is a popup
        or floating

        Args:
            floating (bool): set whether the tool should show as a popup or window
        """
        self.hide()
        self.is_floating = floating
        flags = QtCore.Qt.Window | QtCore.Qt.Tool if floating else QtCore.Qt.Popup
        self._tear_off_btn.setVisible(not self.is_floating)
        self.setWindowFlags(flags)
        QtWidgets.QWidget.show(self)


class _TearOffButton(QtWidgets.QPushButton):
    """Reimplemented to draw a button as a menu tearoff
    Should eventually figure out how to do this through the popup window
    and draw as a rect

    This way seems to be better in that case because then theres no need
    to add the functionality to see if it was pressed
    """

    def paintEvent(self, event):
        """Drawing of the tear off taken from QMenu.cpp
        """
        painter = QtGui.QPainter(self)
        rect = event.rect()
        menuOpt = QtWidgets.QStyleOptionMenuItem()
        menuOpt.initFrom(self)
        menuOpt.state = QtWidgets.QStyle.State_None
        menuOpt.checkType = menuOpt.NotCheckable
        menuOpt.maxIconWidth = 0
        menuOpt.tabWidth = 0
        menuOpt.rect = rect
        menuOpt.menuItemType = menuOpt.TearOff
        if (self.underMouse()):
            menuOpt.state |= QtWidgets.QStyle.State_Selected
        painter.setClipRect(menuOpt.rect)
        self.style().drawControl(QtWidgets.QStyle.CE_MenuTearoff, menuOpt, painter, self)
