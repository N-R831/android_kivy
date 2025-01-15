from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
)
from kivymd.uix.pickers import MDDockedDatePicker
from kivymd.uix.boxlayout import MDBoxLayout

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.backgroundColor
    orientation: "vertical"
    MDNavigationLayout:

        MDScreenManager:
            id:MDScreenManager
            MDScreen:
                name:"kake_Entry_screen"

                MDLabel:
                    text: "MDLabel"
                    halign: "left"
                MDButton:
                    pos_hint: {"center_x": .5, "center_y": .5}
                    on_release: nav_drawer.set_state("toggle")
                    MDButtonText:
                        text: "AAA"
            MDScreen:
                name:"kake_Record_screen"
                MDLabel:
                    text: "Record"
                    pos_hint: {"center_x": .1, "center_y": .1}
                MDButton:
                    pos_hint: {"center_x": .5, "center_y": .5}
                    on_release: nav_drawer.set_state("toggle")

                    MDButtonText:
                        text: "BBB"

        MDNavigationDrawer:
            id: nav_drawer
            radius: 0, dp(16), dp(16), 0

            MDNavigationDrawerMenu:

                MDNavigationDrawerLabel:
                    text: "Kake"

                MDNavigationDrawerItem:
                    on_release:
                        root.current = "kake_Entry_screen"
                        nav_drawer.set_state("toggle")
                        print(root.current)
                    MDNavigationDrawerItemText:
                        text: "Entry"
                        
                MDNavigationDrawerItem:
                    on_release:
                        root.current = "kake_Record_screen"
                        nav_drawer.set_state("toggle")
                        print(root.current)
                    MDNavigationDrawerItemText:
                        text: "Record"
                        
                MDNavigationDrawerItem:
                    MDNavigationDrawerItemText:
                        text: "Setting"

                MDNavigationDrawerDivider:
                
                MDNavigationDrawerLabel:
                    text: "Master"

                MDNavigationDrawerItem:
                    MDNavigationDrawerItemText:
                        text: "Entry"
                        
                MDNavigationDrawerItem:
                    MDNavigationDrawerItemText:
                        text: "Record"

'''


class Main(MDApp):
    def build(self):
        return Builder.load_string(KV)
    
    def kake_entry_released(self):
        sm = MDScreenManager()
        sm.current = 'kake_Entry_screen'
    

Main().run()