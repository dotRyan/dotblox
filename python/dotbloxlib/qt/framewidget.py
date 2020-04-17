from PySide2 import QtWidgets, QtCore, QtGui

__author__ = "Ryan Robinson"


class FrameWidget(QtWidgets.QWidget):
    """A Widget that attempts to mimic mayas frameLayout

    Notes:
        This is a widget rather than a layout so it can be moved
        from place to place where as a layout cannot be moved in Qt.

        This background color will be set from the current themes
        button color.

    """

    def __init__(self, text="", collapsible=False, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._title_widget = _FrameTitle(text)
        layout.addWidget(self._title_widget)

        # The main frame that contains the items added to the widget
        self._content_widget = QtWidgets.QFrame()
        # The main layout items will be added to
        self._content_layout = QtWidgets.QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_widget.setLayout(self._content_layout)

        layout.addWidget(self._content_widget)
        QtWidgets.QWidget.setLayout(self, layout)

        self._title_widget.onCollapse.connect(self._on_title_pressed)
        self.setCollapsible(collapsible)

    def _on_title_pressed(self, collapse):
        self._content_widget.setVisible(not collapse)

    def setText(self, text):
        """Set the text diplayed in the title"""
        self._title_widget.setText(text)

    def text(self):
        """Get the current text displayed in the title """
        return self._title_widget.text()

    def setCollapsible(self, value):
        """Set whether the widget is collapsible"""
        self._title_widget.setCollapsible(value)

    def collapsible(self):
        """Get whether the widget is collapsible"""
        return self._title_widget.collapsible()

    def setCollapsed(self, value):
        """Set the collapsed state

        Args:
            value(bool): state of collapse
        """
        self._title_widget.setCollapsed(value)

    def collapsed(self):
        """Get the collapsed state

        Returns:
            bool:
        """
        return self._title_widget.collapsed()

    def addLayout(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.addLayout(*args, **kwargs)

    def addWidget(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.addWidget(*args, **kwargs)

    def removeWidget(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.removeWidget(*args, **kwargs)

    def removeItem(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.removeItem(*args, **kwargs)

    def addItem(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.addItem(*args, **kwargs)

    def addSpacerItem(self, *args, **kwargs):
        """Convenience method to add/remove items from the widget
        See Qt Docs for signatures
        """
        self._content_layout.addSpacerItem(*args, **kwargs)

    def layout(self):
        """Get the main layout items are added to"""
        return self._content_layout

    def setLayout(self, layout):
        """Set the main layout to the given"""
        self._content_layout = layout
        self._content_widget.setLayout(layout)

    def children(self):
        """Convenience method to get the children of the current layout
         """
        return self._content_layout.children()


class _FrameTitle(QtWidgets.QWidget):
    """The widget that handles the display of the title and the
    collapsed state of the :class:`FrameWidget`

    Args:
        text (str): text to set
    """

    onCollapse = QtCore.Signal(bool)

    def __init__(self, text):

        QtWidgets.QWidget.__init__(self)
        # The long edge of the arrow |>
        self._arrow_height = 11
        # The distance of the point from the long edge |-
        self._arrow_depth = 6
        # The base left margin used to offset the text and arrow
        self._base_margin = 10
        # Roundness of borders
        self.border_radius = 2
        self._text = ""

        self._collapsible = True
        self._collapsed = False

        self.setFixedHeight(22)
        self.setMinimumSize(QtCore.QSize(20, 22))
        self.setText(text)

    def setText(self, text):
        """Set the text of the frame"""
        self._text = text
        self.repaint()

    def text(self):
        """Get the current text of the frame"""
        return self._text

    def setCollapsible(self, value):
        """Set the widget as collapsible"""
        self._collapsible = value
        if not value:
            # Force show the contents if we are not collapsible
            self.setCollapsed(False)
        else:
            self.repaint()

    def collapsible(self):
        """Get whether the widget is collapsible or not"""
        return self._collapsible

    def setCollapsed(self, value):
        """Set the collapsed state"""
        self._collapsed = value
        self.repaint()
        self.onCollapse.emit(value)

    def collapsed(self):
        """Get the collapsed state"""
        return self._collapsed

    def mousePressEvent(self, event):
        """Override to handle the click functionality"""
        if self._collapsible:
            self.setCollapsed(not self._collapsed)
        QtWidgets.QWidget.mouseReleaseEvent(self, event)

    def paintEvent(self, event):
        """Override paint event to display custom options"""
        # Initialize everything we need
        rect = event.rect()  # type: QtCore.QRect
        painter = QtGui.QPainter(self)
        palette = self.palette()  # type: QtGui.QPalette

        transparent_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
        # Because the font is later set as bold. Store this to reset back
        orig_font = painter.font()  # type: QtGui.QFont

        # Handle drawing as a "flat" button
        btn_rect = rect.adjusted(0, 1, 0, -1)
        painter.setBrush(palette.button())
        painter.setPen(transparent_pen)
        painter.setBrush(palette.button())
        painter.drawRoundedRect(btn_rect, self.border_radius, self.border_radius, QtCore.Qt.AbsoluteSize)

        # Draw the text as bold with the with the windowText color
        text_margin = self._base_margin
        # If this is collapsible offset the text event more
        if self._collapsible:
            text_margin += 18
        text_rect = btn_rect.adjusted(text_margin, 1, 0, 0)
        painter.setPen(QtGui.QPen(palette.color(palette.WindowText)))
        font = painter.font()  # type: QtGui.QFont
        font.setBold(font.Bold)
        painter.setFont(font)
        painter.drawText(text_rect,
                         QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                         self._text)
        painter.setFont(orig_font)

        if not self._collapsible:
            return

        # Handle the collapsed indicator
        if self._collapsed:
            offset = (btn_rect.height() - self._arrow_height) / 2.0
            arrow = [
                QtCore.QPointF(self._base_margin, offset),
                QtCore.QPointF(self._base_margin + self._arrow_depth,
                               offset + (self._arrow_height / 2.0)),
                QtCore.QPointF(self._base_margin, offset + self._arrow_height),
            ]
        else:
            margin = self._base_margin - 3
            offset = (btn_rect.height() - self._arrow_depth) / 2.0
            arrow = [
                QtCore.QPointF(margin, offset),
                QtCore.QPointF(margin + (self._arrow_height / 2.0),
                               offset + self._arrow_depth),
                QtCore.QPointF(margin + self._arrow_height, offset),
            ]

        painter.setPen(transparent_pen)
        painter.setBrush(palette.buttonText())
        painter.drawPolygon(arrow)
