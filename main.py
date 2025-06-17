# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import actions
from .actions.StartTracking.StartTracking import StartTracking
from .actions.StopTracking.StopTracking import StopTracking

# Import settings
from .settings import KimaiPluginSettings

class PluginTemplate(PluginBase):
    def _add_icons(self):
        """Add icons for the actions"""
        self.add_icon("start", self.get_asset_path("start.png"))
        self.add_icon("stop", self.get_asset_path("stop.png"))

    def _add_colors(self):
        """Add colors for visual feedback"""
        self.add_color("default", [0, 0, 0, 0])
        self.add_color("success", [0, 255, 0, 100])
        self.add_color("error", [255, 0, 0, 100])

    def _register_actions(self):
        """Register all plugin actions"""
        # Start Tracking Action
        self.start_tracking_holder = ActionHolder(
            plugin_base=self,
            action_base=StartTracking,
            action_id="com_thiritin_kimai_plugin::StartTracking",
            action_name="Start Time Tracking",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.start_tracking_holder)

        # Stop Tracking Action
        self.stop_tracking_holder = ActionHolder(
            plugin_base=self,
            action_base=StopTracking,
            action_id="com_thiritin_kimai_plugin::StopTracking",
            action_name="Stop Time Tracking",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.stop_tracking_holder)

    def __init__(self):
        super().__init__()

        # Enable plugin settings
        self.has_plugin_settings = True
        
        # Initialize settings manager
        self.settings_manager = KimaiPluginSettings(self)

        # Initialize components
        self._add_icons()
        self._add_colors()
        self._register_actions()

        # Register plugin
        self.register(
            plugin_name="Kimai Time Tracking",
            github_repo="https://github.com/Thiritin/kimai-streamcontroller-action",
            plugin_version="1.0.0",
            app_version="1.0.0",
        )
    
    def get_settings_area(self):
        """Return the settings area for the plugin"""
        return self.settings_manager.get_settings_area()