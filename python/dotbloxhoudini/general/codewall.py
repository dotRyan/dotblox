from dotblox.tools import codewall

class HoudiniHook(codewall.Hook):
    APP = "houdini"
    pass

class HoudiniCodeWallWidget(codewall.CodeWallWidget):
    def __int__(self, parent):
        codewall.CodeWallWidget.__init__(self, hook=HoudiniHook(), parent=parent)
