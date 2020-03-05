"""
Each section is treated as its own object

Given the sections of

- main
- shapes
- history (inputs)
- outputs


What we want to paste:
- values
- current values
- connections

How:

- copy
- copy over [x] -> copy current selection and immediately paste over
* option box shift modifier should affect how far down the history a node type is found

- paste -> copy values to selected attributes
- paste over [x]-> copy  values to same attributes as in selection

- paste current -> copy current values to selected attributes
- paste current over [x]-> copy current values to same attributes as in selection

- connect -> connect copied attrs
- connect over [x] -> connect same attributes


TODO:
    - Tapping into "on show once" menu to disable menu items if the
        cannot be applied

    - Single error handling of missing nodes from within selection

    - copying across files is a necessary solution.
        this can be solved by serializing the selection
        however current implementation does not play nice with doing with.
        we would need to serialize the name, type, attr, and current value

        when pasting this needs to know if the node exists to be able to
        copy the current value

"""
import pymel.core as pm
from maya import cmds
from PySide2 import QtGui, QtWidgets, QtCore
#from itertools import cycle, islice


class SectionInfo():
    class SECTION():
        [
            MAIN,
            SHAPES,
            HISTORY,
            OUTPUTS
        ] = [i for i in range(4)]

    def __init__(self, section, nodes, attrs):
        self.nodes = pm.ls(nodes, long=True)
        self.attrs = []
        self.main_node = None
        if self.nodes:
            self.main_node = self.nodes[0]
            self.attrs = map(self.main_node.attr, attrs)
        self.section = section
        self.index = None

        self.initial_values = {attr.name(): attr.get() for attr in self.attrs}

class Selection():
    def __init__(self, main, shapes, history, outputs):
        self.main = main  # type: SectionInfo
        self.shapes = shapes  # type: SectionInfo
        self.history = history  # type: SectionInfo
        self.outputs = outputs  # type: SectionInfo

        main_node = self.main.main_node
        if self.history.nodes:
            self.history.index = get_index_in_historyof_type(self.history.main_node, main_node, future=False)

        if self.outputs.nodes:
            self.outputs.index = get_index_in_historyof_type(self.outputs.main_node, main_node, future=True)

        self._initial_values = {}
        for section in self:
            self._initial_values.update(section.initial_values)

    def __iter__(self):
        return iter([self.main,
                     self.shapes,
                     self.history,
                     self.outputs
                     ])

    def get_initial_value(self, attr):
        return self._initial_values[attr.name()]

class ChannelEditor():
    def __init__(self):
        self.channel_box = pm.ui.ChannelBox(
                pm.channelBox(pm.mel.globals["gChannelBoxName"],
                              query=True,
                              fullPathName=True))

    def install(self):
        self._ui_items = []
        menu_array = self.channel_box.getPopupMenuArray()
        # As of maya 2018 the first popup menu is the channels menu
        channels_menu = menu_array[0]
        # Doing this the pymel way throws errors since it can not
        # find the menu
        item_array = cmds.menu(channels_menu, query=True, itemArray=True)
        if not item_array:
            pm.mel.eval("generateChannelMenu %s|%s 1" % (self.channel_box.name(), channels_menu))
            item_array = cmds.menu(channels_menu, query=True, itemArray=True)

        insert_after_index = item_array.index("cutItem")
        insert_after_index -= 1

        self.copy_menu = pm.menuItem(
                label="Copy",
                parent=channels_menu,
                insertAfter=item_array[insert_after_index],
                command=lambda *x: self.copy())
        self.copy_menu_opt = pm.menuItem(
                parent=channels_menu,
                optionBox=True,
                insertAfter=self.copy_menu,
                command=lambda *x: self.copy(over=True))

        self.paste_menu = pm.menuItem(
                label="Paste", parent=channels_menu,
                insertAfter=self.copy_menu,
                command=lambda *x: self.paste())
        self.paste_menu_opt = pm.menuItem(
                label="Paste",
                parent=channels_menu,
                insertAfter=self.paste_menu,
                optionBox=True,
                command=lambda *x: self.paste(over=True))

        self.paste_cur_menu = pm.menuItem(
                label="Paste Current",
                parent=channels_menu,
                insertAfter=self.paste_menu,
                command=lambda *x: self.paste(current=True))
        self.paste_cur_menu_opt = pm.menuItem(
                label="Paste Current",
                parent=channels_menu,
                insertAfter=self.paste_cur_menu,
                optionBox=True,
                command=lambda *x: self.paste(current=True, over=True))

        self.connect_menu = pm.menuItem(
                label="Connect", parent=channels_menu,
                insertAfter=self.paste_cur_menu,
                command=lambda *x: self.connect())
        self.connect_menu_opt = pm.menuItem(
                label="Connect",
                parent=channels_menu,
                insertAfter=self.connect_menu,
                optionBox=True,
                command=lambda *x: self.connect(over=True))
        bottom_separator = pm.menuItem(
                divider=True,
                parent=channels_menu,
                insertAfter=self.connect_menu)



        self._ui_items.extend([
            self.copy_menu,
            self.paste_menu,
            self.paste_cur_menu,
            self.connect_menu,
            bottom_separator
        ])

    def uninstall(self):
        pm.deleteUI(self._ui_items)

    def get_selection(self):

        arg_values = [
            [SectionInfo.SECTION.MAIN,
             self.channel_box.getMainObjectList,
             self.channel_box.getSelectedMainAttributes],

            [SectionInfo.SECTION.SHAPES,
             self.channel_box.getShapeObjectList,
             self.channel_box.getSelectedShapeAttributes],

            [SectionInfo.SECTION.HISTORY,
             self.channel_box.getHistoryObjectList,
             self.channel_box.getSelectedHistoryAttributes],

            [SectionInfo.SECTION.OUTPUTS,
             self.channel_box.getOutputObjectList,
             self.channel_box.getSelectedOutputAttributes],

        ]

        def eval_selection(section, node_func, selected_func):
            attributes = selected_func() or []
            nodes = node_func() or []
            return SectionInfo(section, nodes, attributes)

        result = []
        for args in arg_values:
            result.append(eval_selection(*args))

        return Selection(*result)

    def set_clipboard(self, value):
        clipboard = QtGui.QClipboard()
        clipboard.setText(str(value))

    def copy(self, over=False):
        self.selection = self.get_selection()
        if over:
            self.paste(over=True)

    def paste(self, current=False, over=False):
        action = self._paste_current_action if current else self._paste_initial_action
        self._do_it(action, over=over)

    def connect(self, over=False):
        self._do_it(self._connect_action, over=over)

    def _paste_current_action(self, src_attr, dst_attr, _):
        print "current", src_attr, "->", dst_attr
        self._set_attr(dst_attr, src_attr.get())

    def _paste_initial_action(self, _, dst_attr, initial_value):
        print "initial", dst_attr, "->", initial_value
        self._set_attr(dst_attr, initial_value)

    def _set_attr(self, attr, value):
        try:
            attr.set(value)
        except Exception as e:
            pm.displayWarning(e.message)

    def _connect_action(self, src_attr, dst_attr, _):
        print("connect", src_attr, "->", dst_attr)
        if src_attr == dst_attr:
            return
        src_attr >> dst_attr

    def _do_it(self, action, over=False):
        if over:
            self._do_over(action)
        else:
            self._do_paste(action)

    def _do_over(self, action):
        """

        Args:
            action: function to run on the mapping of attributes `action(src_attr, dst_attr, initialValue)`
            over: copy to same attributes rather than the selected

        Returns:

        """
        is_shifted = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ShiftModifier)
        src_selection = self.selection
        dst_selection = self.get_selection()

        for src_section, dst_section in zip(src_selection, dst_selection):
            if not src_section.attrs:
                continue

            for src_attr in src_section.attrs:
                attr_name = src_attr.attrName(longName=True)
                dst_nodes = []  # TODO: remove this handle all cases!
                if dst_section.section == dst_section.SECTION.MAIN:
                    dst_nodes = dst_section.nodes[:]
                elif dst_section.section == dst_section.SECTION.SHAPES:
                    dst_nodes = dst_section.nodes[:]
                elif dst_section.section == dst_section.SECTION.HISTORY:
                    dst_nodes = self._history_search(
                            src_section.index,
                            src_section.main_node,
                            dst_selection.main.nodes[:],
                            future=False,
                            all=is_shifted)
                elif dst_section.section == dst_section.SECTION.OUTPUTS:
                    dst_nodes = self._history_search(
                            src_section.index,
                            src_section.main_node,
                            dst_selection.main.nodes[:],
                            future=True,
                            all=is_shifted)

                for node in dst_nodes:
                    if not node.hasAttr(attr_name):
                        continue
                    dst_attr = node.attr(attr_name)

                    action(src_attr, dst_attr, self.selection.get_initial_value(src_attr))

    def _do_paste(self, action):
        is_shifted = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ShiftModifier)
        src_selection = self.selection
        dst_selection = self.get_selection()

        src_attrs = []
        dst_attrs = []

        for src_section, dst_section in zip(src_selection, dst_selection):
            src_attrs.extend(src_section.attrs)

            _dst_attrs = []

            for attr in dst_section.attrs:
                attr_name = attr.attrName()
                if dst_section.section == dst_section.SECTION.MAIN:
                    nodes = [node.attr(attr_name) for node in dst_section.nodes if node.hasAttr(attr_name)]
                elif dst_section.section == dst_section.SECTION.SHAPES:
                    nodes = [node.attr(attr_name) for node in dst_section.nodes if node.hasAttr(attr_name)]
                elif dst_section.section == dst_section.SECTION.HISTORY:
                    nodes = self._history_search(
                            src_section.index,
                            src_section.main_node,
                            dst_selection.main.nodes,
                            future=False,
                            all=is_shifted)
                elif dst_section.section == dst_section.SECTION.OUTPUTS:
                    nodes = self._history_search(
                            src_section.index,
                            src_section.main_node,
                            dst_selection.main.nodes,
                            future=True,
                            all=is_shifted)

                dst_attrs.append(nodes)

        # Because I would rather have "shifted" traverse the history
        # than cycle.
        #
        # src_len = len(src_attrs)
        # dst_len = len(dst_attrs)

        # if src_len < dst_len and is_shifted:
        #     src_attrs = list(islice(cycle(src_attrs), dst_len))

        for src_attr, _dst_attrs in zip(src_attrs, dst_attrs):
            for dst_attr in _dst_attrs:
                action(src_attr, dst_attr, src_selection.get_initial_value(src_attr))


    def _history_search(self, index, search_node, other_nodes, all=False, future=False):
        res = []
        for other_node in other_nodes:
            history = get_history(other_node, future=future, type=search_node.type())
            if history is None:
                continue
            if all:
                res.extend(history)
                continue
            if index < len(history):
                res.append(history[index])

        return res


def get_history(node, future=False, type=None):
    """
   # print "inputs", node.listHistory(future=False, pdo=True, lf=True, interestLevel=2, groupLevels=False)
    # print "outputs", node.listHistory(future=True, pdo=True, lf=True, interestLevel=2, groupLevels=False)
    Args:
        node:
        future: False: inputs, True: outputs
        type:

    Returns:

    """
    history = node.listHistory(future=future, pdo=True, lf=True, interestLevel=2, groupLevels=False, type=type)
    # type: list[pm.PyNode]
    if node in history:
        history.remove(node)
    return history


def get_index_in_historyof_type(search_node, main_node, future=False):
    history = get_history(main_node, future=future, type=search_node.type())
    if search_node in history:
        return history.index(search_node)

channel_editor = ChannelEditor()