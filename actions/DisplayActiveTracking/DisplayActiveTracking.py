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

class DisplayActiveTracking(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # State management
        self.update_timer_id = None
        self.current_timesheet = None
        self.is_updating = False
        
    def on_ready(self) -> None:
        # Reset state variables to handle page caching
        # This ensures proper state when navigating back to cached pages  
        self.current_timesheet = None
        self.is_updating = False
        # Note: Don't reset update_timer_id as it's managed by timer lifecycle
        
        # Set the default icon for display tracking
        self.set_media(media_path=self.plugin_base.get_asset_path("info.png"), size=0.75)
        
        # Register this instance for notifications
        self.plugin_base.register_action_instance(self)
        
        # Start periodic updates
        self.start_periodic_updates()
        
        # Initial update
        self.update_display()
        
    def on_key_down(self) -> None:
        # Manually refresh the display when pressed
        try:
            log.info("DisplayActiveTracking button pressed - refreshing display")
            self.update_display()
        except Exception as e:
            log.error(f"Error in on_key_down: {e}")
    
    def on_key_up(self) -> None:
        pass
    
    def start_periodic_updates(self) -> None:
        """Start periodic updates every 30 seconds"""
        try:
            if self.update_timer_id is not None:
                from gi.repository import GLib
                GLib.source_remove(self.update_timer_id)
            
            # Update every 30 seconds
            from gi.repository import GLib
            self.update_timer_id = GLib.timeout_add_seconds(30, self._periodic_update)
            
        except Exception as e:
            log.error(f"Error starting periodic updates: {e}")
    
    def stop_periodic_updates(self) -> None:
        """Stop periodic updates"""
        try:
            if self.update_timer_id is not None:
                from gi.repository import GLib
                GLib.source_remove(self.update_timer_id)
                self.update_timer_id = None
                
        except Exception as e:
            log.error(f"Error stopping periodic updates: {e}")
    
    def _periodic_update(self) -> bool:
        """Periodic update callback - returns True to continue timer"""
        try:
            if not self.is_updating:
                self.update_display()
            return True  # Continue the timer
        except Exception as e:
            log.error(f"Error in periodic update: {e}")
            return True  # Continue despite error
    
    def update_display(self) -> None:
        """Update the display with current active tracking information"""
        try:
            if self.is_updating:
                return
                
            plugin_global_settings = self.plugin_base.get_settings()
            kimai_url = plugin_global_settings.get("global_kimai_url", "")
            api_token = plugin_global_settings.get("global_api_token", "")
            
            if not kimai_url or not api_token:
                self._show_no_config()
                return
                
            # Run in background thread to avoid blocking UI
            threading.Thread(target=self._fetch_active_timesheet, 
                            args=(kimai_url, api_token), daemon=True).start()
                            
        except Exception as e:
            log.error(f"Error updating display: {e}")
            self._show_error()
    
    def _fetch_active_timesheet(self, kimai_url: str, api_token: str) -> None:
        """Fetch active timesheet in background thread"""
        try:
            self.is_updating = True
            
            active_timesheet = self._get_active_timesheet(kimai_url, api_token)
            
            # Update UI in main thread using a wrapper function to ensure proper parameter passing
            from gi.repository import GLib
            GLib.idle_add(lambda: self._update_display_with_timesheet(active_timesheet))
            
        except Exception as e:
            log.error(f"Error fetching active timesheet: {e}")
            from gi.repository import GLib
            GLib.idle_add(self._show_error)
        finally:
            self.is_updating = False
    
    def _get_active_timesheet(self, kimai_url: str, api_token: str) -> Optional[dict]:
        """Get the currently active timesheet with full expansion (nested objects)"""
        try:
            url = f"{kimai_url.rstrip('/')}/api/timesheets"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Get active timesheets with full expansion (nested objects)
            params = {"size": 1, "orderBy": "begin", "order": "DESC", "full": "true"}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                timesheets = response.json()
                log.debug(f"API response: {timesheets}")
                
                if timesheets and len(timesheets) > 0:
                    # Check if the first timesheet is active (no end time)
                    timesheet = timesheets[0]
                    log.debug(f"First timesheet: {type(timesheet)} - {timesheet}")
                    
                    if timesheet.get('end') is None:
                        log.info(f"Found active timesheet: {timesheet.get('id')}")
                        log.debug(f"Returning timesheet: {type(timesheet)} - {timesheet}")
                        return timesheet
            
            log.info("No active timesheet found")
            return None
            
        except Exception as e:
            log.error(f"Error getting active timesheet: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _update_display_with_timesheet(self, timesheet: Optional[dict]) -> None:
        """Update the display with timesheet information"""
        try:
            # Debug logging to understand what we're receiving
            log.debug(f"_update_display_with_timesheet called with: {type(timesheet)} - {timesheet}")
            
            self.current_timesheet = timesheet
            
            if timesheet is None:
                self._show_no_active_tracking()
                return
            
            # Safety check: ensure timesheet is a dictionary
            if not isinstance(timesheet, dict):
                log.error(f"Expected dict but got {type(timesheet)}: {timesheet}")
                self._show_error()
                return
            
            # Extract information from timesheet (now with full expansion)
            project_info = timesheet.get('project', {})
            activity_info = timesheet.get('activity', {})
            customer_info = project_info.get('customer', {}) if project_info else {}
            
            customer_name = customer_info.get('name', 'Unknown Customer') if customer_info else 'No Customer'
            project_name = project_info.get('name', 'Unknown Project') if project_info else 'No Project'
            activity_name = activity_info.get('name', 'Unknown Activity') if activity_info else 'No Activity'
            
            # Calculate elapsed time
            elapsed_text = self._calculate_elapsed_time(timesheet.get('begin'))
            
            # Set labels using different positions
            # Top line: Customer & Project (truncated to fit)
            customer_short = customer_name[:8] if customer_name != 'No Customer' else ''
            project_short = project_name[:8] if project_name != 'No Project' else ''
            top_text = f"{customer_short} {project_short}".strip()
            if top_text:
                self.set_top_label(top_text, font_size=9)
            else:
                self.set_top_label("")
            
            # Middle line: Activity
            activity_short = activity_name[:12] if activity_name != 'No Activity' else ''
            self.set_center_label(activity_short, font_size=10)
            
            # Bottom line: Elapsed time
            self.set_bottom_label(elapsed_text, font_size=11)
            
            # Set background color to indicate active tracking
            self.set_background_color([0, 100, 0, 80])  # Subtle green background
            
            log.info(f"Updated display: {customer_name} / {project_name} / {activity_name} ({elapsed_text})")
            
        except Exception as e:
            log.error(f"Error updating display with timesheet: {e}")
            log.error(f"Timesheet type: {type(timesheet)}, value: {timesheet}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            self._show_error()
    
    def _calculate_elapsed_time(self, start_time: str) -> str:
        """Calculate elapsed time from start time"""
        try:
            if not start_time:
                return "??:??"
                
            from datetime import datetime
            
            # Handle timezone information in the datetime string
            # Format can be: 2025-06-18T07:02:46+0200, 2025-06-18T07:02:46-0500, 2025-06-18T07:02:46Z, or 2025-06-18T07:02:46
            if '+' in start_time:
                # Positive timezone offset
                start_time = start_time.split('+')[0]
            elif start_time.endswith('Z'):
                # UTC timezone indicator
                start_time = start_time[:-1]
            elif '-' in start_time and start_time.count('-') > 2:
                # Negative timezone offset (more than 2 dashes means timezone)
                start_time = start_time.rsplit('-', 1)[0]
            
            start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            now_dt = datetime.now()
            elapsed = now_dt - start_dt
            
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            return f"{hours:02d}:{minutes:02d}"
            
        except Exception as e:
            log.debug(f"Error calculating elapsed time: {e}")
            log.debug(f"Start time format: '{start_time}'")
            return "??:??"
    
    def _show_no_active_tracking(self) -> None:
        """Show display when no active tracking"""
        try:
            # Clear all labels when no tracking is active
            self.set_top_label("")
            self.set_center_label("")
            self.set_bottom_label("")
            self.set_background_color([0, 0, 0, 0])  # Transparent background
            log.info("Display updated: No active tracking")
        except Exception as e:
            log.error(f"Error showing no active tracking: {e}")
    
    def _show_no_config(self) -> None:
        """Show display when configuration is missing"""
        try:
            self.set_top_label("")
            self.set_center_label("Config", font_size=10)
            self.set_bottom_label("Missing", font_size=10)
            self.set_background_color([100, 100, 0, 80])  # Yellow background
            log.warning("Display updated: Configuration missing")
        except Exception as e:
            log.error(f"Error showing no config: {e}")
    
    def _show_error(self) -> None:
        """Show error indicator"""
        try:
            self.set_top_label("")
            self.set_center_label("Error", font_size=12)
            self.set_bottom_label("")
            self.set_background_color([100, 0, 0, 80])  # Red background
            log.error("Display updated: Error state")
        except Exception as e:
            log.error(f"Error showing error state: {e}")

    def on_timesheet_started_notification(self) -> None:
        """Handle notification that a timesheet has been started"""
        try:
            log.info("Received notification that a timesheet was started - updating display")
            # Immediately update display
            self.update_display()
        except Exception as e:
            log.error(f"Error handling timesheet started notification: {e}")

    def on_timesheet_stopped_notification(self) -> None:
        """Handle notification that a timesheet has been stopped"""
        try:
            log.info("Received notification that a timesheet was stopped - updating display")
            # Immediately update display
            self.update_display()
        except Exception as e:
            log.error(f"Error handling timesheet stopped notification: {e}")

    def __del__(self):
        """Cleanup when action is destroyed"""
        try:
            log.info("DisplayActiveTracking action being destroyed - performing cleanup")
            
            # Stop periodic updates
            self.stop_periodic_updates()
            
            # Unregister from notifications
            if hasattr(self, 'plugin_base') and self.plugin_base is not None:
                try:
                    self.plugin_base.unregister_action_instance(self)
                    log.info("Unregistered from plugin notifications")
                except Exception as e:
                    log.error(f"Error unregistering from notifications: {e}")
                    
        except Exception as e:
            log.error(f"Error during DisplayActiveTracking cleanup: {e}")

    def get_config_rows(self) -> list:
        """Return configuration UI rows"""
        try:
            super_rows = super().get_config_rows()
            
            # Info row
            info_row = Adw.ActionRow(title="Display Settings")
            info_row.set_subtitle("This button displays the currently active time tracking information.")
            
            # Update interval info
            interval_row = Adw.ActionRow(title="Auto-Update")
            interval_row.set_subtitle("Updates every 30 seconds automatically. Press the button to refresh manually.")
            
            # Global settings reminder
            global_row = Adw.ActionRow(title="Global Settings")
            global_row.set_subtitle("Configure Kimai URL and API Token in Plugin Settings")
            
            return super_rows + [
                info_row,
                interval_row,
                global_row
            ]
            
        except Exception as e:
            log.error(f"Error building configuration UI: {e}")
            return super().get_config_rows()
