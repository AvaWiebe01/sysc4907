from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

DATA_ON = "ON"
DATA_OFF = "OFF"

class MainMenu(Screen):
    # reference to the graph defined in KV (set in on_kv_post)
    rt_graph = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()
        self.rt_graph = self.ids.get('rt_graph') or self.rt_graph
        if self.app.data_collection_on: self.rt_graph.start_auto_update()

    def toggle_data_collection(self):
        # Toggle boolean and update status string
        self.app.data_collection_on = not self.app.data_collection_on
        self.app.data_collection_status = DATA_ON if self.app.data_collection_on else DATA_OFF
        self.rt_graph.start_auto_update() if self.app.data_collection_on else self.rt_graph.stop_auto_update()
        self.app.save_config()