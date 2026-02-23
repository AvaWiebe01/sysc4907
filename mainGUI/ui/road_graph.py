# ui/graph_widget.py
from kivy_garden.graph import Graph, LinePlot
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty

class CustomGraph(Graph):
    rt_plot = ObjectProperty(None)
    update_event = None
    update_time_interval = 0.02
    step_count = 1
    py = 0
    new_y = prev_y = 1
    new_x = 0

    def on_kv_post(self, base_widget):
        self.app = App.get_running_app()
        zero_plot = LinePlot(color=[1, 1, 1, 1], line_width=1.2)
        zero_plot.points = [(self.xmin, 0), (self.xmax, 0)]
        self.add_plot(zero_plot)
        self.rt_plot = LinePlot(color=[1,0,0.447,1], line_width=1.4)
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
        #sets the number of extra points to be drawn and the time interval to shift by
        divisor = 5
        interval = self.new_x

        #ignores updating the plot if the current reading is the same as the previous
        #this prevents duplicate points
        if self.new_y == self.prev_y:
            new_data = self.app.get_road_data()
            self.new_y = new_data[1]
            self.new_x = new_data[0]
            self.step_count = 1

        else:

            shifted = []

            #shift all readings along the x-axis by interval/divisor 
            #the main point of this is to make the graph "smoother" 
            #by drawing the line between points in segments rather than all at once
            #this is merely to increase refresh rate and has no affect on 
            #the accuracy of the displayed lineplot

            #shift all readings along the x-axis by interval/divisor 
            for x, y in self.rt_plot.points:
                if x + interval/divisor < self.xmax:
                    shifted.append((x + interval/divisor, y))

            #obtain previous y value from graph as reference when adding extra points
            if self.step_count == 1:
                if shifted:
                    self.py = shifted[-1][-1]

            #add extra points that are along the line between the previous and new y reading
            #this essentially causes the line to be drawn in segments rather than all at once
            #the end result of this is an increased refresh rate, and a smoother look
            if self.step_count < divisor:
                if shifted:
                    shifted.append((0, self.py + self.step_count*(self.new_y-self.py)/divisor))
                self.step_count += 1

            #adds the actual new y reading to the plot after all extra points are added
            else:
                self.prev_y = self.new_y
                shifted.append((0, self.new_y))

            #updates the line plot with new points
            self.rt_plot.points = shifted