
from datetime import datetime
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
import subprocess

class ConfigMenu(Screen):
    app = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()

    def start_network_gui(self):
        possible_commands = [
            ["gnome-control-center", "wi-fi"],
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