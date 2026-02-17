
from datetime import datetime
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import subprocess

class ConfigMenu(Screen):
    app = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()
        # Initialize hold-to-repeat state
        self._inc_hold_event = None
        self._inc_repeat_event = None
        self._dec_hold_event = None
        self._dec_repeat_event = None
        # Bind press/release handlers for year increment/decrement buttons
        try:
            self.ids.incrmnt_yr.bind(on_press=self._on_increment_press, on_release=self._on_increment_release)
            self.ids.dcrmnt_yr.bind(on_press=self._on_decrement_press, on_release=self._on_decrement_release)
        except Exception:
            pass

    def start_network_gui(self):
        possible_commands = [
            ["gnome-control-center", "network"],
            ["nm-connection-editor"],
            ["nm-applet"],
            ["kcmshell5", "kcm_networkmanagement"],
            ["systemsettings5", "network"]
        ]
        for command in possible_commands:
            try:
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
                return
            except Exception:
                pass

    def increment_year(self):
        current_year = datetime.now().year
        try:
            year = int(self.app.vehicle_year)
        except (TypeError, ValueError):
            year = current_year
        if year < current_year + 1:
            year += 1
        self.app.vehicle_year = str(year)
        self.app.save_config()

    def decrement_year(self):
        current_year = datetime.now().year
        try:
            year = int(self.app.vehicle_year)
        except (TypeError, ValueError):
            year = current_year
        if year > current_year - 45:
            year -= 1
        self.app.vehicle_year = str(year)
        self.app.save_config()

    def change_vehicle_type(self):
        if self.app.vehicle_type in self.app.valid_vehicle_types:
            i = self.app.valid_vehicle_types.index(self.app.vehicle_type)
            self.app.vehicle_type = self.app.valid_vehicle_types[(i + 1) % len(self.app.valid_vehicle_types)]
        else:
            self.app.vehicle_type = self.app.valid_vehicle_types[0]
        self.app.save_config()

    def change_vehicle_class(self):
        if self.app.vehicle_class in self.app.valid_vehicle_classes:
            i = self.app.valid_vehicle_classes.index(self.app.vehicle_class)
            self.app.vehicle_class = self.app.valid_vehicle_classes[(i + 1) % len(self.app.valid_vehicle_classes)]
        else:
            self.app.vehicle_class = self.app.valid_vehicle_classes[0]
        self.app.save_config()

    # --- Hold-to-repeat helpers for year increment/decrement ---
    def _on_increment_press(self, instance):
        # start a single-shot that will begin repeating after 1 second
        self._inc_hold_event = Clock.schedule_once(self._start_increment_repeat, 1.0)

    def _start_increment_repeat(self, dt):
        self._inc_hold_event = None
        # immediately perform one increment to avoid waiting for the first interval
        self.increment_year()
        self._inc_repeat_event = Clock.schedule_interval(lambda dt: self.increment_year(), 0.1)

    def _on_increment_release(self, instance):
        # cancel holding timer if release happened before 1s
        if self._inc_hold_event is not None:
            try:
                self._inc_hold_event.cancel()
            except Exception:
                pass
            self._inc_hold_event = None
        # cancel repeating timer if active
        if self._inc_repeat_event is not None:
            try:
                self._inc_repeat_event.cancel()
            except Exception:
                pass
            self._inc_repeat_event = None

    def increment_year_release(self):
        # called from KV on release; only perform a single increment if repeat wasn't active
        if self._inc_repeat_event is None:
            self.increment_year()

    def _on_decrement_press(self, instance):
        self._dec_hold_event = Clock.schedule_once(self._start_decrement_repeat, 1.0)

    def _start_decrement_repeat(self, dt):
        self._dec_hold_event = None
        self.decrement_year()
        self._dec_repeat_event = Clock.schedule_interval(lambda dt: self.decrement_year(), 0.15)

    def _on_decrement_release(self, instance):
        if self._dec_hold_event is not None:
            try:
                self._dec_hold_event.cancel()
            except Exception:
                pass
            self._dec_hold_event = None
        if self._dec_repeat_event is not None:
            try:
                self._dec_repeat_event.cancel()
            except Exception:
                pass
            self._dec_repeat_event = None

    def decrement_year_release(self):
        if self._dec_repeat_event is None:
            self.decrement_year()