"""
Configuration Screen Module
Provides the UI and logic for the vehicle configuration menu.
Handles WiFi network selection, vehicle year adjustments, and vehicle type/class settings.
"""

from datetime import datetime
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ui.interface_buttons import MenuButton, NetworkPopup
import subprocess

class ConfigMenu(Screen):
    """
    Configuration menu screen for vehicle and network settings.
    Allows users to configure WiFi connectivity, vehicle year, type, and class.
    
    Attributes:
        app: Reference to the running Road Monitor application instance.
    """
    # Reference to the main application instance (initialized in on_kv_post).
    app = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        """
        Initialization hook called after KV file parsing completes.
        Retrieves and stores a reference to the running Road Monitor application instance.
        This reference is essential for accessing and modifying vehicle configuration data.
        
        Args:
            base_widget: The base widget this screen is part of.
        """
        # Get the currently running Road Monitor app instance.
        # This app holds all relevant vehicle configuration information.
        self.app = App.get_running_app()

    def start_network_gui(self):
        """
        Initialize and display the WiFi network selection popup.
        Scans for available networks and presents them to the user in a scrollable list.
        """
        # Trigger a WiFi scan to detect all available networks in range.
        # Output is suppressed since we only need the side effect of the scan.
        subprocess.run(["nmcli", "dev", "wifi", "rescan"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            
        # Retrieve list of available WiFi SSIDs (network names) using nmcli.
        # Output is captured in tab-separated format (-t) with only SSID field (-f SSID).
        output = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True, timeout=10)
        
        # Convert output to a set of network SSIDs.
        # Using a set automatically removes duplicate network entries.
        networks = set(output.stdout.splitlines())
        
        # Create and display the network selection popup with the discovered networks.
        # Register on_network_connect as the callback to handle the user's WiFi connection attempt.
        NetworkPopup(networks=networks, on_connect_callback=self.on_network_connect).open()
    
    def on_network_connect(self, ssid, password):
        """
        Attempt to connect to the specified WiFi network.
        Called when user clicks Connect in the password input popup.
        Launches the connection as a background process without blocking the GUI.
        
        Note: Errors (e.g., wrong password, signal loss) are silently ignored.
        The user can retry by reopening the network selection menu.
        
        Args:
            ssid: The network name (SSID) to connect to.
            password: The network password provided by the user.
        """
        try:
            # Initiate WiFi connection using nmcli in a separate background process.
            # Popen allows the operation to run asynchronously without blocking the GUI.
            # Output is suppressed to avoid cluttering the console.
            # close_fds=True ensures file descriptors are not inherited by child process.
            subprocess.Popen(
                ["nmcli", "device", "wifi", "connect", ssid, "password", password],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True
            )
        except Exception:
            # Silently catch any exceptions (connection errors, signal loss, etc.).
            # User can attempt to reconnect by trying again from the network menu.
            pass

    def increment_year(self):
        """
        Increment the vehicle year by 1.
        Prevents setting the vehicle year to a future year.
        Updates the application configuration and persists to config file.
        """
        # Get the current year as the upper bound for validation.
        current_year = datetime.now().year

        # Retrieve the vehicle year stored in the app configuration.
        # If the stored value is invalid or missing, default to the current year.
        try:
            year = int(self.app.vehicle_year)
        except (TypeError, ValueError):
            year = current_year
        
        # Only increment if the resulting year would not exceed the current year.
        # This prevents users from setting vehicle years in the future.
        if year < current_year + 1:
            year += 1

        # Update the app's vehicle_year property with the new year (converted to string).
        self.app.vehicle_year = str(year)

        # Persist the updated vehicle year to the configuration file.
        self.app.save_config()

    def decrement_year(self):
        """
        Decrement the vehicle year by 1.
        Prevents setting the vehicle year to an age older than 45 years.
        Updates the application configuration and persists to config file.
        """
        # Get the current year as the reference point for age validation.
        current_year = datetime.now().year

        # Retrieve the vehicle year stored in the app configuration.
        # If the stored value is invalid or missing, default to the current year.
        try:
            year = int(self.app.vehicle_year)
        except (TypeError, ValueError):
            year = current_year

        # Only decrement if the resulting year would not be older than current_year - 45.
        # This enforces the application's constraint of a maximum 45-year-old vehicle.
        if year > current_year - 45:
            year -= 1

        # Update the app's vehicle_year property with the new year (converted to string).
        self.app.vehicle_year = str(year)

        # Persist the updated vehicle year to the configuration file.
        self.app.save_config()

    def change_vehicle_type(self):
        """
        Cycle to the next vehicle type in the list of valid types.
        Valid types include: SUV, Sedan, Truck, etc.
        Wraps around to the first type when the last type is reached.
        Updates the application configuration and persists to config file.
        """
        # Check if the current vehicle type is one of the predefined valid types.
        if self.app.vehicle_type in self.app.valid_vehicle_types:
            # Find the index of the current vehicle type.
            i = self.app.valid_vehicle_types.index(self.app.vehicle_type)
            # Set vehicle type to the next type in the list (wraps around using modulo).
            self.app.vehicle_type = self.app.valid_vehicle_types[(i + 1) % len(self.app.valid_vehicle_types)]

        # If the current vehicle type is invalid or unrecognized, reset to the first type.
        else:
            self.app.vehicle_type = self.app.valid_vehicle_types[0]

        # Persist the updated vehicle type to the configuration file.
        self.app.save_config()

    def change_vehicle_class(self):
        """
        Cycle to the next vehicle class in the list of valid classes.
        Valid classes include: Economy, Mid-Range, Luxury, etc.
        Wraps around to the first class when the last class is reached.
        Updates the application configuration and persists to config file.
        """
        # Check if the current vehicle class is one of the predefined valid classes.
        if self.app.vehicle_class in self.app.valid_vehicle_classes:
            # Find the index of the current vehicle class.
            i = self.app.valid_vehicle_classes.index(self.app.vehicle_class)
            # Set vehicle class to the next class in the list (wraps around using modulo).
            self.app.vehicle_class = self.app.valid_vehicle_classes[(i + 1) % len(self.app.valid_vehicle_classes)]

        # If the current vehicle class is invalid or unrecognized, reset to the first class.
        else:
            self.app.vehicle_class = self.app.valid_vehicle_classes[0]
        
        # Persist the updated vehicle class to the configuration file.
        self.app.save_config()