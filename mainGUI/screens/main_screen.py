"""
Main Screen Module
Provides the primary monitoring interface for the Road Monitor application.
Displays real-time road condition data as a line graph and allows users to
toggle sensor data collection on/off.
"""

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

# Status string constants for data collection state display.
DATA_ON = "ON"
DATA_OFF = "OFF"

class MainMenu(Screen):
    """
    Main monitoring screen for the Road Monitor application.
    Displays real-time road condition data visualization and sensor status.
    Allows users to start/stop data collection from vehicle sensors.
    
    Attributes:
        rt_graph: Reference to the real-time graph widget displaying road condition data.
    """
    # Reference to the real-time graph widget defined in the KV file.
    # Initialized in on_kv_post after the KV layout is fully parsed.
    rt_graph = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        """
        Initialization hook called after KV file parsing completes.
        Sets up references to the application instance and graph widget.
        If data collection is already enabled, starts the real-time graph updates.
        
        Args:
            base_widget: The base widget this screen is part of.
        """
        # Get reference to the main Road Monitor application instance.
        self.app = App.get_running_app()
        # Retrieve the real-time graph widget from the KV file by its ID.
        # Falls back to the default ObjectProperty if the ID lookup fails.
        self.rt_graph = self.ids.get('rt_graph') or self.rt_graph
        # If data collection is already enabled, immediately start updating the graph with sensor data.
        if self.app.data_collection_on: self.rt_graph.start_auto_update()

    def toggle_data_collection(self):
        """
        Toggle sensor data collection on/off and update the graph visualization.
        Switches the data collection state, updates the status display, and starts or stops
        the real-time graph updates accordingly. Persists the new state to the config file.
        """
        # Toggle the data collection boolean state (True <-> False).
        self.app.data_collection_on = not self.app.data_collection_on
        # Update the displayed status text to match the new state.
        # Shows "ON" when collecting, "OFF" when not collecting.
        self.app.data_collection_status = DATA_ON if self.app.data_collection_on else DATA_OFF
        # Start the real-time graph auto-updates if data collection is enabled,
        # otherwise stop the graph updates to conserve resources.
        self.rt_graph.start_auto_update() if self.app.data_collection_on else self.rt_graph.stop_auto_update()
        # Save the updated data collection preference to the application's config file.
        # Ensures the preference persists across application restarts.
        self.app.save_config()