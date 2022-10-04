import os.path
import runpy
import tempfile

from dotblox.tools import codewall


class HoudiniHook(codewall.Hook):
    APP = "houdini"

    def __init__(self):
        self.PY_TEMP = None
        self.GLOBALS = {}

    def _make_temp_py(self):
        """Houdini's python environment has issue with running exec from
        within this execution.

        Given:

        import hou
        def func():
            print(hou)

        >> hou is undefined

        This is any global variable. runpy seems to get around this.
        """
        if not self.PY_TEMP or not os.path.exists(self.PY_TEMP):
            self.PY_TEMP = tempfile.mktemp(".py")

    def run_file(self, file_path):
        globals = runpy.run_path(file_path, self.GLOBALS)
        self.GLOBALS.update(globals)

    def execute_text(self, text, file_name):
        if file_name is None or file_name.endswith(".py"):
            self._make_temp_py()
            with open(self.PY_TEMP, "w") as f:
                f.write(text)
            globals_ = runpy.run_path(self.PY_TEMP, self.GLOBALS)
            self.GLOBALS.update(globals_)

    def __del__(self):
        """Cleanup the temp file"""
        if self.PY_TEMP and os.path.exists(self.PY_TEMP):
            os.remove(self.PY_TEMP)


class HoudiniCodeWallWidget(codewall.CodeWallWidget):
    def __init__(self, parent=None):
        codewall.CodeWallWidget.__init__(self, hook=HoudiniHook(), parent=parent)
