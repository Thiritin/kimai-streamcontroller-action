# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import actions
from .actions.StartTracking.StartTracking import StartTracking
from .actions.StopTracking.StopTracking import StopTracking
from .actions.DisplayActiveTracking.DisplayActiveTracking import DisplayActiveTracking

# Import settings
from .settings import KimaiPluginSettings

class PluginTemplate(PluginBase):
    def _add_icons(self):
        """Add icons for the actions"""
        self.add_icon("start", self.get_asset_path("start.png"))
        self.add_icon("stop", self.get_asset_path("stop.png"))
        self.add_icon("info", self.get_asset_path("info.png"))

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

        # Display Active Tracking Action
        self.display_active_tracking_holder = ActionHolder(
            plugin_base=self,
            action_base=DisplayActiveTracking,
            action_id="com_thiritin_kimai_plugin::DisplayActiveTracking",
            action_name="Display Active Tracking",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            }
        )
        self.add_action_holder(self.display_active_tracking_holder)

    def __init__(self):
        super().__init__()

        # Enable plugin settings
        self.has_plugin_settings = True
        
        # Initialize settings manager
        self.settings_manager = KimaiPluginSettings(self)
        
        # Simple notification system for inter-action communication
        self.action_instances = []

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
    
    def register_action_instance(self, action_instance):
        """Register an action instance for notifications"""
        if action_instance not in self.action_instances:
            self.action_instances.append(action_instance)
    
    def unregister_action_instance(self, action_instance):
        """Unregister an action instance"""
        if action_instance in self.action_instances:
            self.action_instances.remove(action_instance)
    
    def notify_timesheet_stopped(self):
        """Notify all StartTracking instances that a timesheet has been stopped"""
        for instance in self.action_instances:
            if hasattr(instance, 'on_timesheet_stopped_notification'):
                try:
                    instance.on_timesheet_stopped_notification()
                except Exception as e:
                    from loguru import logger as log
                    log.error(f"Error notifying action instance: {e}")
    
    def notify_timesheet_started(self):
        """Notify all action instances that a timesheet has been started"""
        for instance in self.action_instances:
            if hasattr(instance, 'on_timesheet_started_notification'):
                try:
                    instance.on_timesheet_started_notification()
                except Exception as e:
                    from loguru import logger as log
                    log.error(f"Error notifying action instance: {e}")
    
    def get_settings_area(self):
        """Return the settings area for the plugin"""
        return self.settings_manager.get_settings_area()