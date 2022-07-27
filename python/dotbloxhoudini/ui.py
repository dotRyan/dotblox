import hou


class PANEL_DIRECTION():
    [LEFT,
     RIGHT,
     TOP,
     BOTTOM] = [i for i in range(4)]


def show_python_panel(panel_id, next_to=None, split=None, split_fraction=None):
    """Show the given panel

    Args:
        panel_id(str): ID of the panel as defined in the pypanel file
        next_to(hou.ui.paneTabType): the panel type to find to put given panel next to
        split(PANEL_DIRECTION): if the panel is to be split pass in the direciton
        split_fraction(float): split percentage 0-1


    """
    if not hou.isUIAvailable():
        return

    interface = hou.pypanel.interfaces().get(panel_id)
    if not interface:
        raise RuntimeError("Unable to find python panel with " + panel_id)

    pane_tabs = hou.ui.curDesktop().paneTabs()
    for pane_tab in pane_tabs:
        if not isinstance(pane_tab, hou.PythonPanel):
            continue
        if pane_tab.activeInterface().id() == interface.id():
            pane_tab.setIsCurrentTab()
            return

    python_panel = None
    if next_to:
        for pane_tab in pane_tabs:
            if pane_tab.type() != next_to:
                continue

            pane = pane_tab.pane()

            split_pane = pane
            extra_tab = None

            if split in [PANEL_DIRECTION.LEFT, PANEL_DIRECTION.RIGHT, PANEL_DIRECTION.TOP, PANEL_DIRECTION.BOTTOM]:
                if split == PANEL_DIRECTION.TOP:
                    split_pane = pane.splitVertically()
                elif split == PANEL_DIRECTION.LEFT:
                    split_pane = pane.splitHorizontally()

                if split in [PANEL_DIRECTION.TOP, PANEL_DIRECTION.LEFT]:
                    pane.splitSwap()

                if split_fraction is not None:
                    pane.setSplitFraction(split_fraction)

                extra_tab = split_pane.tabs()[0]
            elif split is not None:
                raise RuntimeError("split %s not supported" % split)

            python_panel = split_pane.createTab(hou.paneTabType.PythonPanel)
            if extra_tab:
                extra_tab.close()
            break

    if not python_panel:
        # No way to create a pane in a given direction in python so
        # hscript it is
        panel_id, _ = hou.hscript("pane -S -m pythonpanel -o")
        python_panel = hou.ui.curDesktop().findPaneTab(panel_id)

    python_panel.setActiveInterface(interface)
    python_panel.showToolbar(False)
