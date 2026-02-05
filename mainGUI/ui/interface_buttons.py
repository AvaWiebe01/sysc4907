from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior

class MenuButton(ButtonBehavior, Image):
    target = StringProperty("")
    source_normal = StringProperty("")
    source_down = StringProperty("")

    def on_kv_post(self, base_widget):
        self.always_release = True
        if self.source_normal:
            self.source = self.source_normal

    def on_press(self):
        if self.source_down:
            self.source = self.source_down

    def on_release(self):
        self.source = self.source_normal


class CustomPopup(Popup):
    message = StringProperty("")