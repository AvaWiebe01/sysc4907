"""
Interface Buttons Module
Provides custom button implementations and popup windows for the Road Monitor GUI.
Includes debounced buttons to prevent ghost inputs on touchscreen, network selection dialogs,
and password input popups for WiFi connectivity features.
"""

from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

# Debounce interval between touchscreen inputs (in seconds).
# Prevents duplicate registrations from accidental multiple taps.
DEBOUNCE_TIME = 0.05


# =======================
# TEXT-BASED BUTTONS
# =======================

class DebouncedButton(Button):
    """
    A text-based button with debouncing logic to prevent ghost inputs from touchscreen.
    Extends Kivy's Button class with a custom on_perform_action event that fires
    only if the time elapsed since the last release exceeds the debounce threshold.
    """

    # Debounce interval for this button instance (can be overridden per instance).
    debounce_interval = DEBOUNCE_TIME

    # Custom event that is dispatched after successful debouncing.
    # Event handlers can be registered in KV files with 'on_perform_action'.
    __events__ = ('on_perform_action',)

    # Timestamp of the last button release, used to calculate elapsed time for debouncing.
    last_release_time = 0

    def on_release(self):
        """
        Handles button release event with debouncing logic.
        Checks if enough time has passed since the last release to consider this
        a genuine user input (not a ghost/bouncing touch input).
        Dispatches the on_perform_action event only if debouncing passes.
        """
        # Retrieve current system uptime in seconds.
        current_time = Clock.get_boottime()

        # Calculate elapsed time since last release and compare against debounce threshold.
        # Only trigger the action if the elapsed time exceeds the debounce interval.
        if current_time - self.last_release_time > self.debounce_interval:
            # Update timestamp to mark this as the new "last release" time.
            self.last_release_time = current_time
            # Dispatch custom event for subclasses or KV files to handle.
            self.dispatch('on_perform_action')
    
    def on_perform_action(self, *args):
        """
        Placeholder for on_perform_action event.
        Actual behavior is typically defined in the KV file (roadmonitor.kv).
        Subclasses or KV bindings will override the behavior.
        """
        pass


# =======================
# IMAGE-BASED BUTTONS
# =======================

class MenuButton(ButtonBehavior, Image):
    """
    An image-based button that combines ButtonBehavior with an Image widget.
    Supports visual feedback (different images for pressed/unpressed states) and
    handles screen transitions. Includes debouncing for touchscreen reliability.
    
    Used throughout the GUI for icon buttons, particularly for navigating between
    the vehicle config menu and the main monitoring screen.
    """

    # Target screen name for navigation (e.g., 'config_menu', 'main_menu').
    # Used by the KV file or event handler to switch screens.
    # Some button instances may not use this property.
    target = StringProperty("")

    # Image file path for the unpressed (normal) button state.
    source_normal = StringProperty("")
    # Image file path for the pressed button state.
    source_down = StringProperty("")

    # Debounce interval for this button instance to prevent ghost inputs.
    debounce_interval = DEBOUNCE_TIME

    # Custom event dispatched after successful debouncing on button release.
    __events__ = ('on_perform_action',)
    # Timestamp of the last button release for debouncing calculations.
    last_release_time = 0

    def on_kv_post(self, base_widget):
        """
        Initialization hook called after KV file parsing completes.
        Sets up the button's initial behavior and appearance.
        
        Args:
            base_widget: The widget instance this behavior is attached to.
        """
        # Ensure button always releases (triggers on_release) even on drag operations.
        self.always_release = True
        # Set initial image to the "normal" (unpressed) state if one was specified.
        if self.source_normal:
            self.source = self.source_normal

    def on_press(self):
        """
        Handles visual feedback when button is pressed.
        Changes the displayed image to the "down" (pressed) state.
        """
        # Display the pressed-state image if one is defined.
        if self.source_down:
            self.source = self.source_down

    def on_release(self):
        """
        Handles button release with debouncing and visual feedback.
        Validates the input as genuine (not a ghost touch) before dispatching
        the on_perform_action event. Reverts image to normal state.
        """
        # Get current system uptime in seconds.
        current_time = Clock.get_boottime()

        # Apply debounce logic: only trigger action if enough time has passed.
        # This prevents multiple rapid triggers from a single touch.
        if current_time - self.last_release_time > self.debounce_interval:
            # Record this release time as the reference for next debounce check.
            self.last_release_time = current_time
            # Dispatch event to be handled by KV file or registered callbacks.
            self.dispatch('on_perform_action')

    def on_perform_action(self, *args):
        """
        Handles the debounced action event.
        Reverts the button image back to the normal (unpressed) state.
        Additional behavior can be defined in the KV file (roadmonitor.kv).
        """
        # Reset image to unpressed state.
        self.source = self.source_normal


# =======================
# POPUP WINDOWS
# =======================

class CustomPopup(Popup):
    """
    A base custom popup class with message support.
    Behavior and styling are defined in the KV file (roadmonitor.kv).
    
    Properties:
        message: String property that holds the text to display in the popup.
    """
    message = StringProperty("")

class NetworkPopup(Popup):
    """
    A popup dialog for selecting and connecting to available WiFi networks.
    Displays a scrollable list of detected network SSIDs and opens a password
    input dialog when a network is selected.
    
    Attributes:
        networks: List of available network SSIDs.
        on_connect_callback: Callback function to execute after successful password entry.
    """
    
    def __init__(self, networks=None, on_connect_callback=None, **kwargs):
        """
        Initialize the network selection popup.
        
        Args:
            networks: List of available WiFi network SSIDs.
            on_connect_callback: Function to call with (ssid, password) after user input.
            **kwargs: Additional arguments passed to parent Popup class.
        """
        super().__init__(**kwargs)

        # Set the popup's background image for visual consistency.
        self.background = "assets/Popups/background.png"
        self.networks = networks

        # Allow users to close popup by clicking outside of it.
        self.auto_dismiss = True

        # Configure popup styling to match other popups in the application.
        self.title = ""
        self.size_hint = (0.6, 0.55)
        self.separator_height = 0

        # Store the callback function to execute when connection is initiated.
        # This typically calls the "on_network_connect" function in config.py
        # to handle the final WiFi connection step.
        self.on_connect_callback = on_connect_callback
        if networks:
            self.networks = networks
        self.build_network_list()
    
    def build_network_list(self):
        """
        Construct the network selection UI with scrollable list of available networks.
        Displays either a list of SSIDs or an error message if no networks are found.
        """
        # Create the main vertical layout to hold title and network list.
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=20)

        # Add instruction text at the top of the popup.
        title = Label(
            text='Select Network',
            font_name='Orbitron',
            pos_hint={'center_x': 0.5, 'center_y': 1},
            font_size='24sp',
            size_hint_y=0.05,
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title)

        # Build network list only if at least one network is available.
        if len(self.networks) >= 1:

            # Create scrollable container for the network list.
            scroll = ScrollView(size_hint=(1, 0.7))
            # Layout to hold individual network button widgets.
            network_list = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=5
            )
            # Bind layout height to dynamically adjust container as items are added.
            network_list.bind(minimum_height=network_list.setter('height'))

            # Create a debounced button for each available network.
            for network in self.networks:
                # Skip empty network names.
                if network.strip():
                    # Create styled button with network SSID as label.
                    btn = DebouncedButton(
                        text=network,
                        font_name='Orbitron',
                        font_size='16sp',
                        size_hint_y=None,
                        height=50,
                        background_color=(0.15, 0.15, 0.15, 0.75),
                        color=(0, 1, 0.48235, 1)  # Green text color
                    )
                    # Bind button press to network selection handler.
                    btn.bind(on_perform_action=lambda btn, ssid=network: self.on_network_selected(ssid))
                    network_list.add_widget(btn)
        
            scroll.add_widget(network_list)
            main_layout.add_widget(scroll)

        # Display error message if no networks were detected.
        else:
            no_network_layout = FloatLayout()

            # Primary error message.
            no_network_label = Label(
                text='No Networks Were Found',
                font_name='Orbitron',
                pos_hint={'center_x': 0.5, 'center_y': 0.7},
                font_size='30sp',
                color=(1, 0.5, 0.5, 1)  # Red text color
            )

            # Helpful suggestion for resolving the issue.
            solution_label = Label(
                text='Ensure your smartphone\'s Hotspot\nfeature is turned on and active.',
                font_name='Orbitron',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                halign='center',
                font_size='16sp',
                color=(1, 0.5, 0.5, 1)  # Red text color
            )
            no_network_layout.add_widget(no_network_label)
            no_network_layout.add_widget(solution_label)
            main_layout.add_widget(no_network_layout)

        self.add_widget(main_layout)
    
    def on_network_selected(self, ssid):
        """
        Handle network selection and open password input dialog.
        Closes the current network list popup and opens the password input popup.
        
        Args:
            ssid: The selected network's SSID (network name).
        """
        # Close the network selection popup.
        self.dismiss()
        
        # Create and display password input popup for the selected network.
        password_popup = PasswordInputPopup(
            ssid=ssid,
            # Pass the callback function to the password popup for after connection.
            # This function (on_network_connect in config_screen.py) handles the final step
            # of connecting to the WiFi network with the provided credentials.
            on_connect_callback=self.on_connect_callback,
            auto_dismiss=False,
            size_hint=(0.6, 0.3),
            separator_height=0
        )
        password_popup.open()


class PasswordInputPopup(Popup):
    """
    A popup dialog for entering WiFi network password.
    Provides a text input field masked for security and Connect/Cancel buttons.
    
    Attributes:
        ssid: The network SSID that was selected.
        on_connect_callback: Callback function to execute when user clicks Connect.
    """

    def __init__(self, ssid, on_connect_callback=None, **kwargs):
        """
        Initialize the password input popup.
        
        Args:
            ssid: The WiFi network SSID to display and connect to.
            on_connect_callback: Function to call with (ssid, password) when user submits.
            **kwargs: Additional arguments passed to parent Popup class.
        """
        super().__init__(**kwargs)
        # Store the network SSID for later use in the callback.
        self.ssid = ssid
        # Configure popup styling for consistency.
        self.title = ""
        self.background = "assets/Popups/background.png"
        # Store the callback to execute when user connects with a password.
        self.on_connect_callback = on_connect_callback
        # Build the UI elements for password input.
        self.build_password_input()
    
    def build_password_input(self):
        """
        Construct the password input UI with text field and action buttons.
        Creates a visually styled interface for users to enter their network password securely.
        """
        # Create main layout to hold all UI elements.
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=20, size_hint=(1, 1))
        
        # Create password input field with masking for security.
        self.password_input = TextInput(
            multiline=False,  # Single line input only.
            password=True,    # Mask input with dots/asterisks.
            font_name='Orbitron',
            font_size='18sp',
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text='Enter network password'
        )
        main_layout.add_widget(self.password_input)
        self.password_input.focus = True
        
        # Create horizontal layout for Connect and Cancel buttons.
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        # Connect button: attempts to connect with provided password.
        connect_btn = DebouncedButton(
            text='Connect',
            font_name='Orbitron',
            font_size='20sp',
            background_color=(0, 0, 0, 0),
            color=(0, 1, 0.48235, 1)  # Green text color
        )
        # Bind button press to connection handler.
        connect_btn.bind(on_perform_action=self.on_connect)
        buttons_layout.add_widget(connect_btn)
        
        # Cancel button: closes the popup without connecting.
        cancel_btn = DebouncedButton(
            text='Cancel',
            font_name='Orbitron',
            font_size='20sp',
            background_color=(0, 0, 0, 0),
            color=(1, 0.5, 0.5, 1)  # Red text color
        )
        # Bind button press to popup dismiss method.
        cancel_btn.bind(on_perform_action=self.dismiss)
        buttons_layout.add_widget(cancel_btn)
        
        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)
    
    def on_connect(self, instance):
        """
        Handle the Connect button press event.
        Extracts the password from the input field and calls the callback
        if a password was entered. Then closes the popup.
        
        Args:
            instance: The button widget that triggered this event.
        """
        self.dismiss()
        # Get the password text from the input field.
        password = self.password_input.text
        # Only proceed if callback exists and password is not empty.
        if self.on_connect_callback and password:
            # Call the callback with the SSID and password for WiFi connection.
            # The callback (on_network_connect in config_screen.py) handles the actual connection.
            self.on_connect_callback(self.ssid, password)
            
        # Close this popup after attempting connection.
