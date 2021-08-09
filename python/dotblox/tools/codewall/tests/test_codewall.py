from dotblox.tools.codewall import CodeWallWidget
from dotblox.qt import standaloneqt


def main(app):
    win = CodeWallWidget()
    win.show()
    return win


if __name__ == '__main__':
    standaloneqt.run(main)