# -*- coding: utf-8 -*-
from .panel import ABTab, ActivitiesTab, CharacterizationFactorsTab
from ..web.graphnav import GraphNavigatorWidget
# from ..web.graphnav import SankeyNavigatorWidget
from ...signals import signals
from .. import activity_cache
from ..tabs import (
    LCASetupTab,
    LCAResultsTab,
    ActivityTab,
)


class RightPanel(ABTab):
    side = "right"

    def __init__(self, *args):
        super(RightPanel, self).__init__(*args)

        self.tabs = {
            "Characterization Factors": CharacterizationFactorsTab(self),
            "Activities": ActivitiesTab(self),
            "LCA Setup": LCASetupTab(self),
            "Graph Explorer": GraphNavigatorWidget(),
            "LCA results": LCAResultsTab(self),
        }

        for tab_name, tab in self.tabs.items():
            self.addTab(tab, tab_name)

        # tabs hidden at start
        for tab_name in ["Activities", "Characterization Factors", "Graph Explorer", "LCA results"]:
            self.hide_tab(tab_name)

    #     # instantiate tabs
    #     self.CF_tab = CharacterizationFactorsTab(self)
    #     self.act_panel = ActivitiesTab(self)
    #     self.LCA_setup_tab = LCASetupTab(self)
    #     self.graph_navigator_tab = GraphNavigatorWidget()
    #     self.graph_navigator_tab.setVisible(False)
    #     self.lca_results_tab = LCAResultsTab(self)
    #
    #     # add tabs to Panel
    #     self.addTab(self.LCA_setup_tab, 'LCA Setup')
    #     self.addTab(self.graph_navigator_tab, 'Graph-Navigator')
    #
    #     # Signals
        self.connect_signals()
    #
    def connect_signals(self):
        signals.activity_tabs_changed.connect(self.update_activity_panel)
        signals.method_tabs_changed.connect(self.update_method_panel)
        # signals.lca_calculation.connect(self.add_Sankey_Widget)
        # self.currentChanged.connect(self.calculate_first_sankey)

    # def add_Sankey_Widget(self, cs_name):
    #     print("Adding Sankey Tab")
    #     # if not hasattr(self, "sankey_navigator_tab"):
    #     self.sankey_navigator_tab = SankeyNavigatorWidget(cs_name)
    #     self.addTab(self.sankey_navigator_tab, 'LCA Sankey')

    # def calculate_first_sankey(self):
    #     if hasattr(self, "sankey_navigator_tab"):
    #         if self.currentIndex() == self.indexOf(self.sankey_navigator_tab):
    #             print("Changed to Sankey Tab")
    #             if not self.sankey_navigator_tab.graph.json_data:
    #                 print("Calculated first Sankey")
    #                 self.sankey_navigator_tab.new_sankey()

    def update_method_panel(self):
        """Show or hide Characterization Factors."""
        if "Characterization Factors" in self.tabs:
            tab = self.tabs["Characterization Factors"]
            if tab.tab_dict:
                self.show_tab("Characterization Factors")
            else:
                self.hide_tab("Characterization Factors")

    def update_activity_panel(self):
        """Show or hide Characterization Factors."""
        if activity_cache != None:
        # if "Activities" in self.tabs:
        #     tab = self.tabs["Activities"]
        #     if tab.tab_dict:
            self.show_tab("Activities")
        else:
            self.hide_tab("Activities")
    #     if len(activity_cache):
    #         self.addTab(self.act_panel, 'Activities')
    #         # self.select_tab(self.act_panel)
    #     else:
    #         self.removeTab(self.indexOf(self.act_panel))
    #         self.setCurrentIndex(0)
    #
    #
    # def close_tab(self, index):
    #     if index >= 3:
    #         # TODO: Should look up by tab class, not index, as tabs are movable
    #         widget = self.widget(index)
    #         if isinstance(widget, ActivityTab):
    #             assert widget.activity in activity_cache
    #             del activity_cache[widget.activity]
    #         widget.deleteLater()
    #         self.removeTab(index)
    #
    #     self.setCurrentIndex(0)
