from threading import Thread
from kivy.clock import Clock
import time

class SensorService:
    def __init__(self, shared_memory , app, read_interval=0.05):
        self.shared_memory = shared_memory
        self.app = app
        self.read_interval = read_interval
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            data = self.shared_memory.read()
            Clock.schedule_once(lambda dt: self._apply(data))
            time.sleep(self.read_interval)

    def _stop(self):
        self.running = False

    def _apply(self, data):
        # single point where conversion happens
        self.app.condition_scale = int(round(data[2]))
        self.app.latest_sample = data
