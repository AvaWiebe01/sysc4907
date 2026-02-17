
import logging
from pathlib import Path
import subprocess

from kivy.app import App
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, DictProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition

from core.shared_mem import SharedDataArray
from core.sensor_service import SensorService
from core.config_management import ConfigManager
from ui.interface_buttons import MenuButton, CustomPopup
from ui.road_graph import CustomGraph
from screens.config_screen import ConfigMenu
from screens.main_screen import MainMenu

Config.set('kivy', 'exit_on_escape', '0')

# UI base size
BASE_WIDTH = 800
BASE_HEIGHT = 480

# Config constants
DATA_ON = "ON"
DATA_OFF = "OFF"

VEHICLE_TYPE_MARKER = "Vehicle Type: "
VEHICLE_YEAR_MARKER = "Vehicle Year: "
VEHICLE_CLASS_MARKER = "Vehicle Class: "
DATA_COLLECTION_MARKER = "Data Collection: "

# Paths
PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "assets" / "config.txt"

# Window setup
Window.size = (BASE_WIDTH, BASE_HEIGHT)
Window.borderless = True
Window.clearcolor = (0.1, 0.1, 0.1, 1)

# Register the app font for use in KV
LabelBase.register(name="Orbitron", fn_regular=str(PROJECT_ROOT / "assets" / "font" / "orbitron" / "orbitron.otf"))

logger = logging.getLogger(__name__)

SHM_NAME = "shared_sensor_readings"
SEM_NAME = "access_readings_sem"

class CustomLayout(FloatLayout):
    pass

class RoadMonitor(App):
    condition_scale = NumericProperty(1)
    condition_text = DictProperty({1: "Terrible", 2: "Bad", 3: "Fair", 4: "Good", 5: "Excellent"})

    data_collection_on = BooleanProperty(False)
    vehicle_type = StringProperty("")
    vehicle_year = StringProperty("")
    vehicle_class = StringProperty("")
    data_collection_status = StringProperty(DATA_OFF)

    valid_vehicle_types = ["SEDAN", "SUV", "TRUCK", "MINIVAN"]
    valid_vehicle_classes = ["ECONOMY", "MID-RANGE", "LUXURY"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sensor_data = SharedDataArray()
        self.config_manager = ConfigManager(CONFIG_PATH)

    def get_road_data(self):
        road_data = self.sensor_data.read()
        self.condition_scale = self.get_condition(road_data[2])
        return road_data
    
    def get_condition(self, raw):
        try:
            v = int(round(float(raw)))
            return max(1, min(5, v))
        except:
            return 3
        
    def exit_without_reboot(self, window, key, scancode, codepoint, modifier):
        #Exit without rebooting if escape key is pressed (for development purposes)
        if key == 27:
            self.stop()

    def launch_connection_setup(self):
        pass

    def reboot_system(self):
        self.stop()
        subprocess.run("/sbin/reboot", shell=True, executable="/bin/bash")

    def show_popup(self):
        CustomPopup(message="Are you sure you want\nto reboot the system?").open()

    def load_config(self):
        data = self.config_manager.load()
        self.vehicle_type = data.get("vehicle_type", "")
        self.vehicle_year = data.get("vehicle_year", "")
        self.vehicle_class = data.get("vehicle_class", "")
        self.data_collection_status = data.get("data_collection", DATA_OFF)
        self.data_collection_on = (self.data_collection_status == DATA_ON)

    def save_config(self):
        data = {
            "vehicle_type": self.vehicle_type,
            "vehicle_year": self.vehicle_year,
            "vehicle_class": self.vehicle_class,
            "data_collection": self.data_collection_status,
        }
        self.config_manager.save(data)

    def on_stop(self):
        try:
            self.sensor_data.close()
        except Exception:
            pass

    def build(self):
        sm = ScreenManager(transition=CardTransition(duration=0.25))
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ConfigMenu(name="config"))
        self.load_config()
        Window.bind(on_keyboard=self.exit_without_reboot)
        return sm

if __name__ == "__main__":
    RoadMonitor().run()


    

