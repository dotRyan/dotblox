from PySide2 import QtCore, QtGui, QtWidgets


class TextEditorWidget(QtWidgets.QPlainTextEdit):
    """Text Editor widget with line numbers"""
    def __init__(self, parent=None):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(lambda *x: self.update_line_number_area_width())
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.zoom_level = 1

        self._update_tab_stop()
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.update_line_number_area_width()


    def line_number_area_width(self):
        """Calculate the width of the bar"""
        digits = 1
        max_ = max(1, self.blockCount())
        while max_ >= 10:
            max_ /= 10
            digits += 1
        space = self.fontMetrics().width(" ")
        return (space * 4) + self.fontMetrics().width("9") * digits

    def _update_tab_stop(self):
        self.setTabStopWidth(self.fontMetrics().width(" ") *  8)

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if (rect.contains(self.viewport().rect())):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        QtWidgets.QPlainTextEdit.resizeEvent(self, event)

        content_rect = self.contentsRect()
        self.line_number_area.setGeometry(
                QtCore.QRect(content_rect.left(),
                             content_rect.top(),
                             self.line_number_area_width(),
                             content_rect.height()))

    def highlight_current_line(self):
        extra_selections = self.extraSelections()

        if not self.isReadOnly():

            palette = self.palette()

            base_color = palette.color(palette.All, palette.Base)
            lightness = base_color.lightnessF()

            if lightness > .5:
                line_color = base_color.darker(110)
            else:
                line_color = base_color.lighter(110)

            for extra_selection in extra_selections:
                extra_selection.format.clearBackground()

            selection = QtWidgets.QTextEdit.ExtraSelection()

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        palette = self.palette()
        text_color = palette.color(palette.All, palette.Text)

        base_color = palette.color(palette.All, palette.Base)
        lightness = base_color.lightnessF()

        if lightness > .5:
            bar_color = base_color.darker(150)
        else:
            bar_color = base_color.lighter(150)


        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), bar_color)

        painter.setPen(QtGui.QPen(text_color, 1))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())


        while block.isValid() and top <= event.rect().bottom():
            if (block.isVisible() and bottom >= event.rect().top()):
                painter.setPen(text_color)
                painter.drawText(0, top, self.line_number_area.width(), self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, str(block_number + 1) + " ")

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            level = 2
            if event.delta() > 0:
                self.zoomIn(level)
                self.zoom_level += level
            else:
                self.zoomOut(level)
                self.zoom_level -= level
            self._update_tab_stop()
            return

        QtWidgets.QPlainTextEdit.wheelEvent(self, event)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier \
                and event.key() == QtCore.Qt.Key_0:
            if self.zoom_level > 0:
                self.zoomOut(self.zoom_level)
            else:
                self.zoomIn(self.zoom_level)
            self.zoom_level = 0
            return
        QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        QtWidgets.QWidget.__init__(self, editor)
        self.code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

