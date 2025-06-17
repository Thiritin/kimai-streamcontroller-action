# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

# Import python modules
import os
import requests
import threading
from typing import Dict, Any

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class StartTracking(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def on_ready(self) -> None:
        # Set the icon for start tracking
        self.set_media(media_path=self.plugin_base.get_asset_path("start.png"), size=0.75)
        
    def on_key_down(self) -> None:
        # Start time tracking when button is pressed
        self.start_time_tracking()
    
    def on_key_up(self) -> None:
        pass
    
    def start_time_tracking(self) -> None:
        """Start time tracking in Kimai"""
        settings = self.get_settings()
        plugin_global_settings = self.plugin_base.get_settings()
        
        # Get global configuration (Kimai URL and API token)
        kimai_url = plugin_global_settings.get("global_kimai_url", "")
        api_token = plugin_global_settings.get("global_api_token", "")
        
        # Get action-specific configuration
        project_id = settings.get("project_id", "")
        activity_id = settings.get("activity_id", "")
        
        if not all([kimai_url, api_token, project_id, activity_id]):
            self.show_error()
            return
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=self._start_tracking_request, 
                        args=(kimai_url, api_token, project_id, activity_id),
                        daemon=True).start()
    
    def _start_tracking_request(self, kimai_url: str, api_token: str, project_id: str, activity_id: str) -> None:
        """Make the API request to start tracking"""
        try:
            from datetime import datetime
            
            url = f"{kimai_url.rstrip('/')}/api/timesheets"
            headers = {
                "X-AUTH-TOKEN": api_token,
                "Content-Type": "application/json"
            }
            
            # Get description from settings
            settings = self.get_settings()
            description = settings.get("description", "")
            
            data = {
                "begin": datetime.utcnow().isoformat(),
                "end": None,
                "project": int(project_id),
                "activity": int(activity_id),
                "description": description
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                self.show_success()
            else:
                self.show_error()
                
        except Exception as e:
            print(f"Error starting time tracking: {e}")
            self.show_error()
    
    def show_success(self) -> None:
        """Show success indicator"""
        self.set_background_color([0, 255, 0, 100])  # Green background
        
    def show_error(self) -> None:
        """Show error indicator"""
        self.set_background_color([255, 0, 0, 100])  # Red background
        
    def get_config_rows(self) -> list:
        """Return configuration UI rows"""
        super_rows = super().get_config_rows()
        
        # Project ID
        self.project_id_row = Adw.EntryRow(title="Project ID")
        self.project_id_row.set_text(str(self.get_settings().get("project_id", "")))
        self.project_id_row.connect("notify::text", self.on_project_id_changed)
        
        # Activity ID
        self.activity_id_row = Adw.EntryRow(title="Activity ID")
        self.activity_id_row.set_text(str(self.get_settings().get("activity_id", "")))
        self.activity_id_row.connect("notify::text", self.on_activity_id_changed)
        
        # Description
        self.description_row = Adw.EntryRow(title="Description")
        self.description_row.set_text(str(self.get_settings().get("description", "")))
        self.description_row.connect("notify::text", self.on_description_changed)
        
        # Info row
        info_row = Adw.ActionRow(title="Global Settings")
        info_row.set_subtitle("Configure Kimai URL and API Token in Plugin Settings")
        
        return super_rows + [
            info_row,
            self.project_id_row,
            self.activity_id_row,
            self.description_row
        ]
    
    def on_project_id_changed(self, entry, *args):
        settings = self.get_settings()
        settings["project_id"] = entry.get_text()
        self.set_settings(settings)
    
    def on_activity_id_changed(self, entry, *args):
        settings = self.get_settings()
        settings["activity_id"] = entry.get_text()
        self.set_settings(settings)
    
    def on_description_changed(self, entry, *args):
        settings = self.get_settings()
        settings["description"] = entry.get_text()
        self.set_settings(settings)
