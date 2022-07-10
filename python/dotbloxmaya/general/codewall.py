import os.path

from dotblox.tools import codewall
from dotbloxmaya.core.ui import dockwindow

from maya import cmds, mel

python_file_command = """
with open("{file_path}") as f:
    exec(compile(f.read(), "{file_path}", "exec"), globals(), locals())
"""

python_text_command = """
exec(compile(\"""{text}\""", "interactive", "exec"), globals(), locals())
"""


class MayaHook(codewall.Hook):

    def get_supported_extensions(self):
        extensions = codewall.Hook.get_supported_extensions(self)
        extensions.append(".mel")
        return extensions

    def run_file(self, file_path):
        if os.path.isfile(file_path):
            if file_path.endswith(".py"):
                cmds.evalDeferred(python_file_command.format(file_path=file_path))
            elif file_path.endswith(".mel"):
                mel.eval('source \"{file_path}\"'.format(file_path=file_path))

    def execute_text(self, text, file_name):
        print text
        if file_name.endswith(".py"):
            cmds.evalDeferred(python_text_command.format(text=text))
        elif file_name.endswith(".mel"):
            mel.eval(text)


class MayaCodeWallWidget(codewall.CodeWallWidget):
    def __init__(self, parent=None):
        codewall.CodeWallWidget.__init__(self, hook=MayaHook(), parent=parent)


dock = dockwindow.DockWindowManager(MayaCodeWallWidget)
