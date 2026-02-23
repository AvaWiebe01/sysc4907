from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.button import Button

DEBOUNCE_TIME = 0.05

class DebouncedButton(Button):
    debounce_interval = DEBOUNCE_TIME
    __events__ = ('on_perform_action',)
    last_release_time = 0

    def on_release(self):
        current_time = Clock.get_boottime()
        if current_time - self.last_release_time > self.debounce_interval:
            self.last_release_time = current_time
            self.dispatch('on_perform_action')
    
    def on_perform_action(self, *args):
        pass

class MenuButton(ButtonBehavior, Image):
    target = StringProperty("")
    source_normal = StringProperty("")
    source_down = StringProperty("")
    __events__ = ('on_perform_action',)
    debounce_interval = DEBOUNCE_TIME
    last_release_time = 0

    def on_kv_post(self, base_widget):
        self.always_release = True
        if self.source_normal:
            self.source = self.source_normal

    def on_press(self):
        if self.source_down:
            self.source = self.source_down

    def on_release(self):
        current_time = Clock.get_boottime()
        if current_time - self.last_release_time > self.debounce_interval:
            self.last_release_time = current_time
            self.dispatch('on_perform_action')

    def on_perform_action(self, *args):
        self.source = self.source_normal

class CustomPopup(Popup):
    message = StringProperty("")

