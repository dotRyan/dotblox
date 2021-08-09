
from dotblox.qt.texteditorwidget import TextEditorWidget
from dotblox.qt import standaloneqt

def main(app):
    win = TextEditorWidget()
    win.show()
    return win


if __name__ == '__main__':
    standaloneqt.run(main)