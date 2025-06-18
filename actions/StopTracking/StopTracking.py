# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

# Import python modules
import os
import requests
import threading
from typing import Dict, Any, Optional
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class StopTracking(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def on_ready(self) -> None:
        # Set the icon for stop tracking
        self.set_media(media_path=self.plugin_base.get_asset_path("stop.png"), size=0.75)
        
    def on_key_down(self) -> None:
        # Stop time tracking when button is pressed
        self.stop_time_tracking()
    
    def on_key_up(self) -> None:
        pass
    
    def stop_time_tracking(self) -> None:
        """Stop time tracking in Kimai"""
        plugin_global_settings = self.plugin_base.get_settings()
        
        # Get global configuration
        kimai_url = plugin_global_settings.get("global_kimai_url", "")
        api_token = plugin_global_settings.get("global_api_token", "")
        
        if not all([kimai_url, api_token]):
            self.show_error()
            return
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=self._stop_tracking_request, 
                        args=(kimai_url, api_token),
                        daemon=True).start()
    
    def _stop_tracking_request(self, kimai_url: str, api_token: str) -> None:
        """Make the API request to stop tracking"""
        try:
            # First, get the active timesheet
            active_id = self._get_active_timesheet_id(kimai_url, api_token)
            
            if active_id is None:
                self.show_error()
                return
            
            # Stop the active timesheet
            url = f"{kimai_url.rstrip('/')}/api/timesheets/{active_id}/stop"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.patch(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                log.info(f"Successfully stopped time tracking for timesheet ID {active_id}")
                self.show_success()
            else:
                log.error(f"Failed to stop time tracking. Status: {response.status_code}")
                log.error(f"Response body: {response.text}")
                log.error(f"Request URL: {url}")
                log.error(f"Timesheet ID: {active_id}")
                self.show_error()
                
        except requests.exceptions.Timeout:
            log.error(f"Timeout while stopping time tracking. URL: {kimai_url}")
            self.show_error()
        except requests.exceptions.ConnectionError:
            log.error(f"Connection error while stopping time tracking. URL: {kimai_url}")
            self.show_error()
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while stopping time tracking: {e}")
            log.error(f"URL: {kimai_url}")
            self.show_error()
        except Exception as e:
            log.error(f"Unexpected error stopping time tracking: {e}")
            log.error(f"URL: {kimai_url}")
            self.show_error()
    
    def _get_active_timesheet_id(self, kimai_url: str, api_token: str) -> Optional[int]:
        """Get the ID of the currently active timesheet"""
        try:
            url = f"{kimai_url.rstrip('/')}/api/timesheets"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            params = {"active": "1"}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    active_id = data[0].get("id")
                    log.info(f"Found active timesheet with ID: {active_id}")
                    return active_id
                else:
                    log.warning("No active timesheet found")
                    return None
            else:
                log.error(f"Failed to get active timesheet. Status: {response.status_code}")
                log.error(f"Response body: {response.text}")
                log.error(f"Request URL: {url}")
                return None
            
        except requests.exceptions.Timeout:
            log.error(f"Timeout while getting active timesheet. URL: {kimai_url}")
            return None
        except requests.exceptions.ConnectionError:
            log.error(f"Connection error while getting active timesheet. URL: {kimai_url}")
            return None
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while getting active timesheet: {e}")
            log.error(f"URL: {kimai_url}")
            return None
        except Exception as e:
            log.error(f"Unexpected error getting active timesheet: {e}")
            log.error(f"URL: {kimai_url}")
            return None
    
    def show_success(self) -> None:
        """Show success indicator"""
        self.set_background_color([0, 255, 0, 100])  # Green background
        
    def show_error(self) -> None:
        """Show error indicator"""
        self.set_background_color([255, 0, 0, 100])  # Red background
        
    def get_config_rows(self) -> list:
        """Return configuration UI rows"""
        super_rows = super().get_config_rows()
        
        # Info row
        info_row = Adw.ActionRow(title="Global Settings")
        info_row.set_subtitle("Configure Kimai URL and API Token in Plugin Settings")
        
        return super_rows + [
            info_row
        ]

