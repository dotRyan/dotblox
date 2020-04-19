import sys

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets, QtCore
from maya import cmds
import maya.OpenMayaUI as omui


class DockWindow(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """This class is not meant to be instanced outside of `DockWindowManager`

    This class takes the given widget_cls and creates a dockable window that
    works with mayas workspace.

    When the window is closed. The window is retained and able to be shown again
    This prevents the window from being rebuilt each time

    An attribute of `_dock_win` is added to the widget instance as a way of
    passing the window instance into the widget.

    Attributes:
         startup_state: Maya will have the workspace at startup. This is a way
                        to check if this is the first time opening the window.
                        Can be used to set a default placement.
    """

    def __init__(self, widget_cls, width_sizing="preferred", height_sizing=None, retain=False, parent=None):
        MayaQWidgetDockableMixin.__init__(self, parent=parent)
        self.width_sizing = width_sizing
        self.height_sizing = height_sizing
        self.retain = retain

        # Create a frame that other windows can dock into
        self.docking_frame = QtWidgets.QMainWindow(self)
        self.docking_frame.layout().setContentsMargins(0, 0, 0, 0)
        self.docking_frame.setWindowFlags(QtCore.Qt.Widget)
        self.docking_frame.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)

        self.widget = widget_cls()
        # Not the cleanest way but this gives the underlying widget access to
        # this dock window
        self.widget._dock_win = self
        self.setObjectName(self.widget.objectName() + "Window")
        self.setWindowTitle(self.widget.windowTitle())

        self.docking_frame.setCentralWidget(self.widget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.docking_frame, 0)
        self.setLayout(layout)

        self.preferred_size = QtCore.QSize(self.minimumSize().width(),
                                           self.minimumSize().height())

        # See if maya is already aware of this workspace
        self.startup_state = cmds.workspaceControlState(self.workspace_control_name, query=True, exists=True)

    # Unsure if all the size hint stuff is necessary but it enforces

    def setSizeHint(self, size):
        self.preferred_size = size

    def sizeHint(self):
        return self.preferred_size

    def minimumSizeHint(self):
        return self.widget.minimumSizeHint()

    def minimumSize(self):
        return self.widget.minimumSizeHint()

    def create_workspace_control(self, source_module, attr="dock"):
        """Creates the workspace control and its defaults"""

        ui_script = """
import {module}
import {source_module}
if hasattr({source_module}, "{attr}"):
    if isinstance({source_module}.{attr}, {module}.{orig_control}):
        {source_module}.{attr}.show(restore=True)
        """.format(widget_module=self.widget.__module__,
                   module=__name__,
                   attr=attr,
                   orig_control=DockWindowManager.__name__,
                   source_module=source_module)

        close_script = """
import {module}
import {source_module}
if hasattr({source_module}, "{attr}"):
    if isinstance({source_module}.{attr}, {module}.{orig_control}):
        {source_module}.{attr}.close()
        """.format(widget_module=self.widget.__module__,
                   module=__name__,
                   attr=attr,
                   orig_control=DockWindowManager.__name__,
                   source_module=source_module)

        self.setDockableParameters(
                dockable=True,
                # `retain=False` deletes the workspace once the
                # QWidget is closed. Meaning the widget will rebuild each time
                # its closed
                retain=self.retain,
                minWidth=self.preferred_size.width(),
                width=self.preferred_size.width(),
                height=self.preferred_size.height(),
                widthSizingProperty=self.width_sizing,
                # Seem like setting this breaks if its "fixed"
                heightSizingProperty=self.height_sizing,
                uiScript=ui_script,
                closeCallback="None" if self.retain else close_script
        )

    @property
    def workspace_control_name(self):
        return self.objectName() + "WorkspaceControl"

    def show(self, *args, **kwargs):
        super(DockWindow, self).show(*args, **kwargs)

    def resize_workspace(self, width, height):

        if not cmds.workspaceControl(self.workspace_control_name, query=True, exists=True):
            return
        try:
            cmds.workspaceControl(self.workspace_control_name, edit=True,
                                resizeWidth=width,
                                resizeHeight=height)
            self.preferred_size = QtCore.QSize(width, height)
        except:
            cmds.warning("Unable to resize workspace. This is only supported in 2018+")
        self.resize(width, height)

    def delete_workspace(self):
        """Delete the workspace of this window
        This is primarily used when creating your own window since we retain
        the workspace when the window closes.
        """
        if cmds.workspaceControl(self.workspace_control_name, q=True, exists=True):
            cmds.workspaceControl(self.workspace_control_name, edit=True, cl=True)
            cmds.deleteUI(self.workspace_control_name, control=True)

    @classmethod
    def create(cls, widget_cls, module_name, restore=False, window_options=None, attr="dock"):
        """Create and setup the window with the given options.

        Args:
            widget_cls (QtWidgets.QWidget): the widget class to use as the central widget
            module_name (str): the module from where the creation was initialized
            restore (bool): should only be used on startup from maya
            window_options (dict): a combined way of passing in options into the window
                            width_sizing: preferred, fixed, None
                            height_sizing: preferred, fixed, None
            attr (str): the attribute that is used to find the instance
                  of the DockWindowManager

        Returns:
            (DockWindow): the created window
        """
        window_options = {} if window_options is None else window_options
        win = DockWindow(widget_cls, **window_options)

        if restore:
            # The current parent is the workspace control created by maya
            parent = omui.MQtUtil.getCurrentParent()
            win_ptr = omui.MQtUtil.findControl(win.objectName())
            omui.MQtUtil.addWidgetToMayaLayout(long(win_ptr), long(parent))
        else:
            # get the state before the workspace control is created
            win.create_workspace_control(module_name, attr)

        return win


class DockWindowManager(object):
    """
    Creates a way of managing a DockWindow

    Because of mayas way of initializing a workspace this class provides a
    central location for calling and recalling the window.

    """

    def __init__(self, widget_cls, window_options=None, attr="dock", module=None):
        """

        Args:
            widget_cls: widget_cls to be used by `DockWindow`
            window_options (dict): a combined way of passing in options into the window
                            width_sizing: preferred, fixed, None
                            height_sizing: preferred, fixed, None
                            retain: choose whether to delete the widget
                                    and its workspace when closed or keep
                                    the instance alive
            attr (str): the attribute that is used to find the instance
                        of the DockWindowManager
        """
        self.win = None
        self._widget_cls = widget_cls

        # Current defaults
        self.window_options = {
            "width_sizing": "preferred",
            "height_sizing": None,
            "retain": False
        }
        if window_options is not None:
            self.window_options = window_options

        self.attr = attr

        self.module = module
        # Dynamically get the module this class was called in if none was given
        if module is None:
            f_globals = sys._getframe(1).f_globals
            self.module = f_globals.get("__name__")

    def on_create(self):
        """A way to inject code at first runtime and the workspace does not exist"""
        pass

    def show(self, restore=False):
        # If there is a window just show it
        if self.win:
            self.win.show()
            return

        self.win = DockWindow.create(
                self._widget_cls,
                restore=restore,
                window_options=self.window_options,
                attr=self.attr,
                module_name=self.module
        )
        # Maya handles the visibility at startup so only show if were not restoring
        if not restore:
            if not self.win.isVisible():
                self.win.show()

            self.on_create()

    def close(self):
        """Closes the window and deletes the workspace

        This is used when the window is closed and retain has been set to
        True.
        `callback` should only be set by the window

        This can also be used while debugging.
        """
        if not self.win:
            pm.displayWarning("Window instance has already been "
                       "deleted for %s" % self._widget_cls.__name__)

        # Workspace is already handled if its not retained
        if self.win.retain:
            self.win.delete_workspace()
        self.win.deleteLater()
        self.win = None
