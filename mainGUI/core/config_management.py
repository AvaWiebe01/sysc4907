
import os, tempfile
from pathlib import Path
from datetime import datetime

# Config constants
DATA_ON = "ON"
DATA_OFF = "OFF"

VEHICLE_TYPE_MARKER = "Vehicle Type: "
VEHICLE_YEAR_MARKER = "Vehicle Year: "
VEHICLE_CLASS_MARKER = "Vehicle Class: "
DATA_COLLECTION_MARKER = "Data Collection: "


class ConfigManager:
    """Simple config file loader/saver for the app."""

    DEFAULTS = {
        "vehicle_type": "SEDAN",
        "vehicle_year": str(datetime.now().year),
        "vehicle_class": "ECONOMY",
        "data_collection": DATA_OFF,
    }

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        data = self.DEFAULTS.copy()
        if not self.path.exists():
            self.save(data)
            return data
        with self.path.open("r") as fh:
            for line in fh:
                if line.startswith(VEHICLE_TYPE_MARKER):
                    data["vehicle_type"] = line.split(":", 1)[1].strip()
                elif line.startswith(VEHICLE_YEAR_MARKER):
                    data["vehicle_year"] = line.split(":", 1)[1].strip()
                elif line.startswith(VEHICLE_CLASS_MARKER):
                    data["vehicle_class"] = line.split(":", 1)[1].strip()
                elif line.startswith(DATA_COLLECTION_MARKER):
                    data["data_collection"] = line.split(":", 1)[1].strip()
        return data

    def save(self, data: dict):
        dir_name = str(self.path.parent)
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False) as tmp:
            tmp.write(VEHICLE_TYPE_MARKER + data.get("vehicle_type", "") + "\n")
            tmp.write(VEHICLE_YEAR_MARKER + data.get("vehicle_year", "") + "\n")
            tmp.write(VEHICLE_CLASS_MARKER + data.get("vehicle_class", "") + "\n")
            tmp.write(DATA_COLLECTION_MARKER + data.get("data_collection", DATA_OFF) + "\n")
            temp_name = tmp.name
        os.replace(temp_name, str(self.path))