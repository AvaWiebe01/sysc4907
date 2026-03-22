"""
Sensor Service Module
Provides a background service for continuously reading sensor data from shared memory.
Updates the Road Monitor application with real-time road condition data.
Runs in a separate thread to avoid blocking the GUI while collecting sensor readings.
"""

from threading import Thread
from kivy.clock import Clock
import time

class SensorService:
    """
    Background service for reading and processing sensor data from shared memory.
    Runs in a separate daemon thread to continuously collect road condition data
    and update the application state. Uses Kivy's Clock to safely update the GUI
    from the background thread.

    Attributes:
        shared_memory: Reference to the SharedDataArray for reading sensor data.
        app: Reference to the Road Monitor application instance for updating state.
        read_interval: Time in seconds between sensor readings (default 0.05s).
        running: Boolean flag indicating if the service is actively collecting data.
    """

    def __init__(self, shared_memory, app, read_interval=0.05):
        """
        Initialize the sensor service with required dependencies.

        Args:
            shared_memory: SharedDataArray instance for accessing sensor data.
            app: Road Monitor application instance to update with sensor readings.
            read_interval: Time interval between readings in seconds (default 0.05).
        """
        # Store reference to shared memory for reading sensor data.
        self.shared_memory = shared_memory
        # Store reference to the main application for updating condition data.
        self.app = app
        # Set the interval between sensor readings (controls sampling rate).
        self.read_interval = read_interval
        # Flag to track if the service is currently running.
        self.running = False

    def start(self):
        """
        Start the sensor data collection service.
        Launches a background daemon thread that continuously reads sensor data.
        If the service is already running, this method does nothing.
        """
        # Prevent starting multiple instances of the service.
        if self.running:
            return
        # Mark the service as running.
        self.running = True
        # Start a daemon thread to run the data collection loop.
        # Daemon threads automatically terminate when the main program exits.
        Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        """
        Main data collection loop running in the background thread.
        Continuously reads sensor data from shared memory and schedules GUI updates.
        Uses Clock.schedule_once to safely update the GUI from the background thread.
        """
        # Continue running while the service is marked as active.
        while self.running:
            # Read the latest sensor data from shared memory.
            data = self.shared_memory.read()
            # Schedule the data application on the main thread using Kivy's Clock.
            # This ensures thread-safe updates to the GUI and application state.
            Clock.schedule_once(lambda dt: self._apply(data))
            # Pause for the specified interval before the next reading.
            time.sleep(self.read_interval)

    def _stop(self):
        """
        Stop the sensor data collection service.
        Sets the running flag to False, which will cause the background loop to exit.
        """
        # Set the running flag to False to signal the loop to terminate.
        self.running = False

    def _apply(self, data):
        """
        Apply sensor data to the application state.
        Converts raw sensor readings to application-friendly values and updates the app.
        This method runs on the main thread (scheduled via Clock) for thread safety.

        Args:
            data: Raw sensor data array from shared memory.
        """
        # Convert the road condition value (data[2]) to an integer scale (1-5).
        # This is the single point where raw sensor data is converted to app format.
        self.app.condition_scale = int(round(data[2]))
        # Store the complete raw data sample for potential future use.
        self.app.latest_sample = data
