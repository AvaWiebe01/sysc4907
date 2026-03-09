
from datetime import datetime
from kivy.app import App
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.screenmanager import Screen
from ui.interface_buttons import MenuButton, CustomPopup, NetworkPopup
import subprocess

class ConfigMenu(Screen):
    app = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()

    def start_network_gui(self):
        # Scan for available networks
        subprocess.run(["nmcli", "dev", "wifi", "rescan"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
            
        # Get list of available SSIDs
        output = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"],capture_output=True,text=True,timeout=10)
            
        networks = output.stdout.splitlines()
        
        # Create and show popup with network list
        NetworkPopup(networks=networks, on_connect_callback=self.on_network_connect).open()
    
    def on_network_connect(self, ssid, password):
        try:
            subprocess.Popen(["nmcli", "device", "wifi", "connect", ssid, "password", password],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True)
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