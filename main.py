import os.path

from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder

from modules.inventors import Inventors
from modules.nations import Nations
from modules.inventions import Inventions

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase


class BMIScreen(Screen):
    pass


class InventorScreen(Screen):
    pass
    # def __init__(self, **kwargs):
    #     super(InventorScreen, self).__init__(**kwargs)
    #     self.inventors = Inventors()
    #     self.add_widget(self.inventors)


class NationScreen(Screen):
    pass
    # def __init__(self, **kwargs):
    #     super(NationScreen, self).__init__(**kwargs)
    #     self.nations = Nations()
    #     self.add_widget(self.nations)


class InventionScreen(Screen):
    pass


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class InventorsApp(MDApp):
    root_path = os.path.dirname(os.path.realpath(__file__))

    def build(self):
        self.title = "Why is Kivy so broken?"
        self.icon = 'img/icon256.png'
        self.theme_cls.primary_palette = "Gray"
        builder = Builder.load_file('main.kv')
        self.inventors = Inventors()
        self.nations = Nations()
        self.inventions = Inventions()
        # builder.ids.navigation.ids.tab_manager.screens[0].add_widget(self.inventors)
        builder.ids.tab_inventors.add_widget(self.inventors)
        builder.ids.tab_nations.add_widget(self.nations)
        builder.ids.tab_inventions.add_widget(self.inventions)
        return builder

    # def on_tab_switch(
    #         self, instance_tabs, instance_tab, instance_tab_label, tab_text
    # ):
    #     '''Called when switching tabs.
    #
    #     :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
    #     :param instance_tab: <__main__.Tab object>;
    #     :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
    #     :param tab_text: text or name icon of tab;
    #     '''
    #
    #     instance_tab.ids.label.text = tab_text


InventorsApp().run()
