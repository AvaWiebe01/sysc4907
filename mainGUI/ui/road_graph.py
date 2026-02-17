# ui/graph_widget.py
from kivy_garden.graph import Graph, LinePlot
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty

class CustomGraph(Graph):
    rt_plot = ObjectProperty(None)
    update_event = None
    update_time_interval = 0.05
    half_step = False
    new_y = 0
    new_x = 0
    prev_y = 1

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()
        zero_plot = LinePlot(color=[1, 1, 1, 1], line_width=1.2)
        zero_plot.points = [(self.xmin, 0), (self.xmax, 0)]
        self.add_plot(zero_plot)
        self.rt_plot = LinePlot(color=[1,0,0.447,1], line_width=1.2)
        self.rt_plot.points = [(0,0)]
        self.add_plot(self.rt_plot)

    def start_auto_update(self):
        if self.update_event: return
        else: 
            self.rt_plot.points = []
            self.update_event = Clock.schedule_interval(lambda dt: self.update(), self.update_time_interval)

    def stop_auto_update(self):
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def update(self):
        interval = self.new_x

        if self.new_y == self.prev_y:
            new_data = self.app.get_road_data()
            self.new_y = new_data[1]
            self.new_x = new_data[0]

        else:

            shifted = []

            # --- PHASE 1: just shift existing ---
            for x, y in self.rt_plot.points:
                if x + interval/2 < self.xmax:
                    shifted.append((x + interval/2, y))

            # --- PHASE 2: if this is second half, add new sample ---
            if self.half_step:
                self.prev_y = self.new_y

                if shifted:
                    px, py = shifted[-1]
                    shifted.append((px - interval/2, (py + self.new_y)/2))

                shifted.append((0, self.new_y))

            self.rt_plot.points = shifted

            # toggle phase for next call
            self.half_step = not self.half_step
