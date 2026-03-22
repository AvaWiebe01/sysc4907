"""
Road Graph Module
Provides a real-time line graph widget for visualizing road condition data.
Displays sensor readings as a smooth, continuously updating plot.
Used by MainMenu (main_screen.py) for the primary data monitoring interface.
Integrated into the GUI layout via roadmonitor.kv.
"""

from kivy_garden.graph import Graph, LinePlot
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty

class CustomGraph(Graph):
    """
    Custom real-time graph widget for displaying road condition data.
    Extends Kivy's Graph class to provide a scrolling line plot that updates
    with new sensor readings. Smooths the line visualization by interpolating
    points between data readings for a continuous, professional appearance.
    
    Attributes:
        rt_plot: The active LinePlot object displaying road condition data (displayed in pink/red).
        update_event: Reference to the scheduled Clock event for periodic graph updates.
        update_time_interval: Time in seconds between graph refresh cycles (lower = smoother updates).
        step_count: Current interpolation step in the segment-drawing process (1 to divisor).
        py: Y-value from the previous data point, used for interpolation calculations.
        new_y: The most recent road condition reading from the sensor data.
        prev_y: The previously rendered road condition value (used to detect duplicate readings).
        new_x: The x-axis (time) value for the most recent reading.
    """
    # The active line plot displaying road condition data. Initialized in on_kv_post.
    rt_plot = ObjectProperty(None)
    # Clock event handle for the periodic update scheduler. None when graph is not updating.
    update_event = None
    # Time interval (seconds) between graph update cycles. Affects smoothness and responsiveness.
    update_time_interval = 0.02
    # Current step in the interpolation process (ranges from 1 to divisor in update method).
    step_count = 1
    # Y-value of the previous data point, used as a reference for smooth interpolation.
    py = 0
    # Latest sensor reading Y-value and previous rendered Y-value (initialized to 1).
    new_y = prev_y = 1
    # X-axis position (timestamp) of the latest sensor reading.
    new_x = 0

    def on_kv_post(self, base_widget):
        """
        Initialization hook called after KV file parsing completes.
        Sets up the graph's visual elements including reference line and data line.
        Creates two LinePlots: a static zero reference line and a dynamic data line.
        
        Args:
            base_widget: The base widget this graph is part of.
        """
        # Retrieve the running Road Monitor application instance for accessing sensor data.
        self.app = App.get_running_app()
        # Create a white horizontal reference line at y=0 to show the baseline.
        # This helps users understand whether the road condition is above or below neutral.
        zero_plot = LinePlot(color=[1, 1, 1, 1], line_width=1.0)
        zero_plot.points = [(self.xmin, 0), (self.xmax, 0)]
        self.add_plot(zero_plot)
        # Create the main red/pink line plot for displaying real-time road condition data.
        # Color is [R=1, G=0, B=0.447, A=1] (red with slight pink hue).
        self.rt_plot = LinePlot(color=[1, 0, 0.447, 1], line_width=1.4)
        self.rt_plot.points = [(0, 0)]
        self.add_plot(self.rt_plot)
    
    def start_auto_update(self):
        """
        Start the real-time graph update cycle.
        Initializes the plot and schedules periodic updates via the Clock.
        Uses the update_time_interval property to control refresh frequency.
        Called by MainMenu when data collection is toggled on.
        """
        # If an update event is already scheduled, do nothing (prevent duplicate schedulers).
        if self.update_event:
            return
        else: 
            # Clear any existing points from the plot to start fresh.
            self.rt_plot.points = []
            # Schedule the update method to be called at regular intervals.
            # This creates a continuous stream of graph refreshes with smooth animations.
            self.update_event = Clock.schedule_interval(self.update, self.update_time_interval)

    def stop_auto_update(self):
        """
        Stop the real-time graph update cycle.
        Cancels the scheduled Clock event to halt graph refresh cycles.
        Called by MainMenu when data collection is toggled off.
        """
        # If an update event is currently scheduled, cancel it to conserve resources.
        if self.update_event:
            self.update_event.cancel()
            # Clear the reference to mark that no update is currently scheduled.
            self.update_event = None

    def update(self, dt):
        """
        Update the graph with new sensor data and handle smooth line interpolation.
        Called repeatedly by the Clock scheduler during active data collection.
        Implements a segment-drawing algorithm that interpolates between data points
        to create a smooth, continuous-looking line rather than discrete jumps.
        
        The animation works by dividing each line segment into multiple sub-segments,
        drawing them one at a time to create a fluid scrolling and drawing effect.
        
        Args:
            dt: Delta time since last call (provided by Clock.schedule_interval).
        """
        # Number of segments to divide each line segment into for smooth interpolation.
        # A divisor of 5 means we draw each transition in 5 steps for smooth animation.
        # Higher divisor = smoother animation but more computation and slower scrolling.
        divisor = 5
        # Time interval (x-axis distance) between the previous and new data points.
        interval = self.new_x

        # Skip updating if the latest sensor reading is the same as the previously rendered value.
        # This prevents adding duplicate points to the plot and reduces visual clutter.
        if self.new_y == self.prev_y:
            # Fetch the latest sensor reading from the Road Monitor app.
            # get_road_data() returns [timestamp, road_condition_value]
            new_data = self.app.get_road_data()
            # Update the new_y with the latest road condition reading (scale of 1-5).
            self.new_y = new_data[1]
            # Update the new_x with the timestamp of this reading.
            self.new_x = new_data[0]
            # Reset the interpolation step counter for the next segment to be drawn.
            self.step_count = 1

        # Process new data by animating the line between the previous and new data points.
        else:
            # List to accumulate the updated plot points (shifted and interpolated).
            shifted = []

            # Scroll all existing graph points to the right (shift x-axis position).
            # This creates the "scrolling" effect where old data moves off the left side.
            # Each point shifts by interval/divisor to animate the movement smoothly over multiple updates.
            # The animation quality depends on divisor: higher = smoother scrolling but slower.
            # This is purely visual and does not affect data accuracy - just the refresh rate appearance.
            for x, y in self.rt_plot.points:
                # Only keep points that remain within the graph's x-axis bounds after shifting.
                # Points that scroll beyond xmax (right edge) are discarded.
                if x + interval / divisor < self.xmax:
                    shifted.append((x + interval / divisor, y))

            # On the first interpolation step, capture the last plotted point's y-value.
            # This serves as the starting point for interpolating toward the new data point.
            if self.step_count == 1:
                # Retrieve the y-value of the rightmost existing point (most recent old data).
                if shifted:
                    self.py = shifted[-1][-1]

            # Add intermediate points along the line from previous to new data value.
            # These interpolated points are drawn at x=0 (right edge of graph).
            # Drawing the line in segments over multiple update cycles creates smooth animation.
            # Without this interpolation, the line would jump instantly from old to new value.
            if self.step_count < divisor:
                if shifted:
                    # Calculate interpolated y-value using linear interpolation formula.
                    # As step_count increments from 1 to divisor, the value smoothly transitions from py to new_y.
                    interpolated_y = self.py + self.step_count * (self.new_y - self.py) / divisor
                    # Add the intermediate point at the right edge of the visible graph.
                    shifted.append((0, interpolated_y))
                # Increment step counter for next interpolation segment in the next update cycle.
                self.step_count += 1

            # After all interpolation steps are complete, add the actual new data point.
            # This marks the completion of the animation between old and new readings.
            else:
                # Update the rendered y-value to match the new sensor reading for next cycle.
                self.prev_y = self.new_y
                # Add the final (actual) data point to the plot at the right edge.
                shifted.append((0, self.new_y))

            # Apply all the accumulated changes to the line plot.
            # This single assignment refreshes the entire visualization with shifted and interpolated data.
            self.rt_plot.points = shifted