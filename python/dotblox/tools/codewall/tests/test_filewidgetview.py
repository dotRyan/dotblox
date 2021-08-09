import os

from dotblox.tools.codewall.ui.fileviewwidget import FileViewWidget
from dotblox.qt import standaloneqt

def main(app):
    win = FileViewWidget(os.path.expanduser("~/Desktop"))
    win.show()
    return win


if __name__ == '__main__':
    standaloneqt.run(main)