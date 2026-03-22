
"""
Configuration Management Module
Provides a simple text-based configuration file manager for the Road Monitor application.
Handles loading and saving vehicle settings and data collection preferences.
Uses atomic file operations to prevent corruption during saves.
"""

import os, tempfile
from pathlib import Path
from datetime import datetime

# Status string constants for data collection state.
DATA_ON = "ON"
DATA_OFF = "OFF"

# Configuration file markers (prefixes) for parsing key-value pairs.
VEHICLE_TYPE_MARKER = "Vehicle Type: "
VEHICLE_YEAR_MARKER = "Vehicle Year: "
VEHICLE_CLASS_MARKER = "Vehicle Class: "
DATA_COLLECTION_MARKER = "Data Collection: "


class ConfigManager:
    """
    Simple configuration file manager for loading and saving application settings.
    Manages vehicle configuration (type, year, class) and data collection preferences.
    Uses a plain text file format with key-value pairs for easy editing and portability.

    The configuration file format:
    Vehicle Type: SEDAN
    Vehicle Year: 2024
    Vehicle Class: ECONOMY
    Data Collection: OFF

    Attributes:
        path: Path object pointing to the configuration file location.
    """

    # Default configuration values used when the config file doesn't exist or is incomplete.
    DEFAULTS = {
        "vehicle_type": "SEDAN",
        "vehicle_year": str(datetime.now().year),  # Current year as default
        "vehicle_class": "ECONOMY",
        "data_collection": DATA_OFF,
    }

    def __init__(self, path: Path):
        """
        Initialize the configuration manager with the config file path.

        Args:
            path: Path object or string path to the configuration file.
        """
        # Convert to Path object and ensure parent directory exists.
        self.path = Path(path)
        # Create the config directory if it doesn't exist.
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        """
        Load configuration data from the file.
        If the file doesn't exist, creates it with default values.
        Parses the text file line by line, extracting values based on marker prefixes.

        Returns:
            dict: Dictionary containing the loaded configuration values.
                  Falls back to defaults for any missing or invalid entries.
        """
        # Start with a copy of the default values.
        data = self.DEFAULTS.copy()
        # If config file doesn't exist, save defaults and return them.
        if not self.path.exists():
            self.save(data)
            return data
        # Read and parse the existing config file.
        with self.path.open("r") as fh:
            for line in fh:
                # Parse vehicle type setting.
                if line.startswith(VEHICLE_TYPE_MARKER):
                    data["vehicle_type"] = line.split(":", 1)[1].strip()
                # Parse vehicle year setting.
                elif line.startswith(VEHICLE_YEAR_MARKER):
                    data["vehicle_year"] = line.split(":", 1)[1].strip()
                # Parse vehicle class setting.
                elif line.startswith(VEHICLE_CLASS_MARKER):
                    data["vehicle_class"] = line.split(":", 1)[1].strip()
                # Parse data collection setting.
                elif line.startswith(DATA_COLLECTION_MARKER):
                    data["data_collection"] = line.split(":", 1)[1].strip()
        # Return the loaded (or default) configuration data.
        return data

    def save(self, data: dict):
        """
        Save configuration data to the file using atomic write operations.
        Writes to a temporary file first, then atomically replaces the original
        to prevent corruption if the process is interrupted during save.

        Args:
            data: Dictionary containing configuration values to save.
        """
        # Get the directory containing the config file.
        dir_name = str(self.path.parent)
        # Create a temporary file in the same directory for atomic write.
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False) as tmp:
            # Write each configuration setting with its marker prefix.
            tmp.write(VEHICLE_TYPE_MARKER + data.get("vehicle_type", "") + "\n")
            tmp.write(VEHICLE_YEAR_MARKER + data.get("vehicle_year", "") + "\n")
            tmp.write(VEHICLE_CLASS_MARKER + data.get("vehicle_class", "") + "\n")
            tmp.write(DATA_COLLECTION_MARKER + data.get("data_collection", DATA_OFF) + "\n")
            # Store the temporary file name for atomic replacement.
            temp_name = tmp.name
        # Atomically replace the original file with the temporary one.
        # This prevents partial writes if the process crashes during save.
        os.replace(temp_name, str(self.path))