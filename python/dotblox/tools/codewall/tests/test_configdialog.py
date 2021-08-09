
from dotblox.tools.codewall.ui.configdialog import ConfigDialog
from dotblox.qt import standaloneqt

def main(app):
    win = ConfigDialog("/path/to/config.dblx")
    if win.exec_():
        print win.result()
    return win


if __name__ == '__main__':
    standaloneqt.run(main)