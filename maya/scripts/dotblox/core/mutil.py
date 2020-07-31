import maya.cmds as cmds
import hashlib


class PreserveSelection(object):
    """
    Usage:

        with PreserveSelection():
            pass

        @PreserveSelection()
        def func():
            pass

    """
    def __enter__(self):
        self.selection = cmds.ls(selection=True, long=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        existing_ls = cmds.ls(self.selection, long=True)
        cmds.select(existing_ls, replace=True)

    def __call__(self, func):
        def wrap(*args, **kwargs):
            selection = cmds.ls(selection=True, long=True)
            result = self.func(*args, **kwargs)
            existing_ls = cmds.ls(selection, long=True)
            cmds.select(existing_ls, replace=True)
            return result
        return wrap


class Undoable(object):
    """
        Usage:

        with Undoable():
            pass

        @Undoable()
        def func():
            pass
    """

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)

    def __call__(self, func):
        def wrap(*args, **kwargs):
            cmds.undoInfo(openChunk=True)
            try:
                result = func(*args, **kwargs)
            finally:
                cmds.undoInfo(closeChunk=True)
            return result

        return wrap


class OptionVar(object):
    def __init__(self, prefix=None):
        """Convenience class to set/get optionVars from maya

        Args:
            prefix (str): use case for tools to store and option var
                            prefixed with the tool name

        Usage:
            option_vars = OptionVar()
            option_var.get("named")

        """

        if prefix is None:
            prefix = ""
        if len(prefix):
            prefix += "_"
        self.prefix = prefix

    def set(self, key, value):
        if isinstance(value, (str, unicode)):
            kwarg = "stringValue"
        elif isinstance(value, float):
            kwarg = "floatValue"
        elif isinstance(value, int):
            kwarg = "intValue"
        else:
            raise RuntimeError("Unsupported type: " + type(value))

        cmds.optionVar(**{kwarg: [self._format_key(key), value]})

    def get(self, key, default=None):
        option_key = self._format_key(key)
        if cmds.optionVar(exists=option_key):
            return cmds.optionVar(query=option_key)
        return default

    def _format_key(self, key):
        return "{prefix}{key}".format(prefix=self.prefix, key=key)


class Repeatable():
    """
    Usage:
        @Repeatable()
        def as_decorator():
            pass


        Repeatable.repeat(test_make)
    """
    history = {}

    def _clean_dotbox_repeatable_history():
        repeat_history = cmds.repeatLast(query=True, commandNameList=True)
        for command in Repeatable.history.values()[:]:
            if command.label not in repeat_history:
                del Repeatable.history[command.id_]
    # Maya may not be initialized if running from mayapy
    if "scriptJob" in dir(cmds):
        for job in cmds.scriptJob(listJobs=True):
            if _clean_dotbox_repeatable_history.__name__ in job:
                job_id = int(job.split(":")[0])
                cmds.scriptJob(kill=job_id)
                break
        SCRIPT_JOB = cmds.scriptJob(event=["RecentCommandChanged", _clean_dotbox_repeatable_history])

    class RepeatableCommand():
        def __init__(self, func, args=(), kwargs={}):

            self.id_ = hashlib.md5(__name__
                              + func.__name__
                              + str(args)
                              + str(kwargs)).hexdigest()
            self.cmd = lambda: func(*args, **kwargs)
            self.mel = ("python(\"import {name}; {name}.{cls}.history['{id_}'].cmd()\")").format(
                    name=__name__,
                    cls=Repeatable.__name__,
                    id_=self.id_)
            self.label = "{cls}('{id_}')".format(
                    cls=self.__class__.__name__,
                    id_=self.id_)

            Repeatable.history[self.id_] = self

        def __call__(self):
            cmds.repeatLast(addCommand=self.mel, addCommandLabel=self.label)
            self.cmd()

    @classmethod
    def make(cls, func, args=(), kwargs={}):
        return Repeatable.RepeatableCommand(func, args, kwargs)

    def __call__(self, func):
        def wrap(*args, **kwargs):
            return self.make(func, args, kwargs)()
        return wrap
