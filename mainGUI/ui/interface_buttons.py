from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

DEBOUNCE_TIME = 0.05

class DebouncedButton(Button):
    debounce_interval = DEBOUNCE_TIME
    __events__ = ('on_perform_action',)
    last_release_time = 0

    def on_release(self):
        current_time = Clock.get_boottime()
        if current_time - self.last_release_time > self.debounce_interval:
            self.last_release_time = current_time
            self.dispatch('on_perform_action')
    
    def on_perform_action(self, *args):
        pass

class MenuButton(ButtonBehavior, Image):
    target = StringProperty("")
    source_normal = StringProperty("")
    source_down = StringProperty("")
    __events__ = ('on_perform_action',)
    debounce_interval = DEBOUNCE_TIME
    last_release_time = 0

    def on_kv_post(self, base_widget):
        self.always_release = True
        if self.source_normal:
            self.source = self.source_normal

    def on_press(self):
        if self.source_down:
            self.source = self.source_down

    def on_release(self):
        current_time = Clock.get_boottime()
        if current_time - self.last_release_time > self.debounce_interval:
            self.last_release_time = current_time
            self.dispatch('on_perform_action')

    def on_perform_action(self, *args):
        self.source = self.source_normal

class CustomPopup(Popup):
    message = StringProperty("")

class NetworkPopup(Popup):
    networks = ListProperty([])
    
    def __init__(self, networks=None, on_connect_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.background = "assets/Popups/background.png"
        self.auto_dismiss=True
        self.title = ""
        self.size_hint = (0.6,0.55)
        self.separator_height = 0
        self.on_connect_callback = on_connect_callback
        if networks:
            self.networks = networks
        self.build_network_list()
    
    def build_network_list(self):
        """Build the network list UI"""
        # Create main layout
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=20)

        # Title
        title = Label(
            text='Select Network',
            font_name='Orbitron',
            pos_hint={'center_x': 0.5, 'center_y': 1},
            font_size='24sp',
            size_hint_y=0.05,
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title)
        
        # Scrollable network list
        scroll = ScrollView(size_hint=(1, 0.7))
        network_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )
        network_list.bind(minimum_height=network_list.setter('height'))
        
        # Add network buttons
        for network in self.networks:
            if network.strip():  # Filter out empty SSIDs
                btn = DebouncedButton(
                    text=network,
                    font_name='Orbitron',
                    font_size='16sp',
                    size_hint_y=None,
                    height=50,
                    background_color=(0.15, 0.15, 0.15, 0.75),
                    color=(0, 1, 0.48235, 1)
                )
                btn.bind(on_perform_action=lambda btn, ssid=network: self.on_network_selected(ssid))
                network_list.add_widget(btn)
        
        scroll.add_widget(network_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_network_selected(self, ssid):
        """Handle network selection - show password input"""
        self.dismiss()  # Close the network list popup
        
        # Show password input popup
        password_popup = PasswordInputPopup(
            ssid=ssid,
            on_connect_callback=self.on_connect_callback,
            auto_dismiss=False,
            size_hint = (0.6,0.3),
            separator_height = 0
        )
        password_popup.open()


class PasswordInputPopup(Popup):
    def __init__(self, ssid, on_connect_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.ssid = ssid
        self.title = ""
        self.background = "assets/Popups/background.png"
        self.on_connect_callback = on_connect_callback
        self.build_password_input()
    
    def build_password_input(self):
        """Build the password input UI"""
        # Create main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=20, size_hint=(1, 1))
        
        # Password input field
        self.password_input = TextInput(
            multiline=False,
            password=True,
            font_name='Orbitron',
            font_size='18sp',
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text='Enter network password'
        )
        main_layout.add_widget(self.password_input)
        
        # Buttons layout
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        # Connect button
        connect_btn = DebouncedButton(
            text='Connect',
            font_name='Orbitron',
            font_size='20sp',
            background_color=(0,0,0,0),
            color=(0, 1, 0.48235, 1)
        )
        connect_btn.bind(on_perform_action=self.on_connect)
        buttons_layout.add_widget(connect_btn)
        
        # Cancel button
        cancel_btn = DebouncedButton(
            text='Cancel',
            font_name='Orbitron',
            font_size='20sp',
            background_color=(0,0,0,0),
            color=(1, 0.5, 0.5, 1)
        )
        cancel_btn.bind(on_perform_action=self.dismiss)
        buttons_layout.add_widget(cancel_btn)
        
        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)
    
    def on_connect(self, instance):
        """Handle connect button press"""
        password = self.password_input.text
        if self.on_connect_callback and password:
            self.on_connect_callback(self.ssid, password)
        self.dismiss()
