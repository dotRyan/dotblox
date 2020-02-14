import pymel.core as pm
from maya import cmds

node_instances = (cmds.listRelatives(

                shapes[0], allParents=True, fullPath=True) or [])

class Clipboard():
    def __init__(self, attrs):
        self.attrs = attrs
        self.values = [attr.get() for attr in attrs]

class ChannelEditor():
    def __init__(self):
        self.clipboard = Clipboard([])
        self.channel_box = pm.ui.ChannelBox(
                pm.channelBox(pm.mel.globals["gChannelBoxName"],
                              query=True,
                              fullPathName=True))

    def install(self):
        menu_array = self.channel_box.getPopupMenuArray()
        channels_menu = None
        for menu in menu_array:
            # Doing this the pymel way throws errors since it can not find the menu
            item_array = cmds.menu(menu, queery=True, itemArray=True)
            if not item_array:
                continue

            if cmds.menuItem(item_array[0]) == "Channels":
                channels_menu = menu
                break

        if channels_menu is None:
            raise RuntimeError("Unable to install because the channel menu "
                               "could not be found")


    def get_selection(self):

        def eval_selection(node_func, selected_func):
            attributes = selected_func()
            if not attributes:
                return []

            # Since we only care about if attributes are selected we know that
            # there is only one node that will ever be in this list and that
            # the result will be a list
            node = node_func()[0]
            node = pm.PyNode(node)
            return map(node.attr, attributes)

        arg_values = [
            [self.channel_box.getMainObjectList,
             self.channel_box.getSelectedMainAttributes],

            [self.channel_box.getShapeObjectList,
             self.channel_box.getSelectedShapeAttributes],

            [self.channel_box.getHistoryObjectList,
             self.channel_box.getSelectedHistoryAttributes],

            [self.channel_box.getOutputObjectList,
             self.channel_box.getSelectedOutputAttributes],

        ]

        result = []
        for args in arg_values:
            result.extend(eval_selection(*args))

        return result


channel_editor = ChannelEditor()