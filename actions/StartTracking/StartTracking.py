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
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class StartTracking(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize mappings
        self.customers_map = {}
        self.projects_map = {}
        self.activities_map = {}
        
    def on_ready(self) -> None:
        # Set the icon for start tracking
        self.set_media(media_path=self.plugin_base.get_asset_path("start.png"), size=0.75)
        
    def on_key_down(self) -> None:
        # Start time tracking when button is pressed
        try:
            log.info("StartTracking button pressed (on_key_down)")
            self.start_time_tracking()
        except Exception as e:
            log.error(f"Error in on_key_down: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            self.show_error()
    
    def on_key_up(self) -> None:
        pass
    
    def start_time_tracking(self) -> None:
        """Start time tracking in Kimai"""
        try:
            log.info("Start time tracking button pressed")
            
            settings = self.get_settings()
            plugin_global_settings = self.plugin_base.get_settings()
            
            # Get global configuration (Kimai URL and API token)
            kimai_url = plugin_global_settings.get("global_kimai_url", "")
            api_token = plugin_global_settings.get("global_api_token", "")
            
            # Get action-specific configuration
            project_id = settings.get("project_id", "")
            activity_id = settings.get("activity_id", "")
            
            log.info(f"Configuration check - Kimai URL: {'SET' if kimai_url else 'MISSING'}, "
                    f"API Token: {'SET' if api_token else 'MISSING'}, "
                    f"Project ID: {project_id if project_id else 'MISSING'}, "
                    f"Activity ID: {activity_id if activity_id else 'MISSING'}")
            
            # Check for missing configuration with detailed error logging
            missing_configs = []
            if not kimai_url:
                missing_configs.append("Kimai URL")
            if not api_token:
                missing_configs.append("API Token")
            if not project_id:
                missing_configs.append("Project ID")
            if not activity_id:
                missing_configs.append("Activity ID")
            
            if missing_configs:
                log.error(f"Missing required configuration: {', '.join(missing_configs)}")
                log.error(f"Current settings: {settings}")
                log.error(f"Global settings keys: {list(plugin_global_settings.keys())}")
                self.show_error()
                return
            
            log.info(f"Starting time tracking for project {project_id}, activity {activity_id}")
            
            # Run in separate thread to avoid blocking UI
            threading.Thread(target=self._start_tracking_request, 
                            args=(kimai_url, api_token, project_id, activity_id),
                            daemon=True).start()
                            
        except Exception as e:
            log.error(f"Unexpected error in start_time_tracking: {e}")
            log.error(f"Exception type: {type(e)}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            self.show_error()
    
    def _start_tracking_request(self, kimai_url: str, api_token: str, project_id: str, activity_id: str) -> None:
        """Make the API request to start tracking"""
        try:
            log.info(f"Starting API request to create timesheet - Project: {project_id}, Activity: {activity_id}")
            
            from datetime import datetime
            
            url = f"{kimai_url.rstrip('/')}/api/timesheets"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Get description from settings
            settings = self.get_settings()
            description = settings.get("description", "")
            
            # Validate and convert IDs to integers
            try:
                project_id_int = int(project_id)
                activity_id_int = int(activity_id)
            except ValueError as e:
                log.error(f"Invalid ID format - Project ID: '{project_id}', Activity ID: '{activity_id}', Error: {e}")
                self.show_error()
                return
            
            # Format datetime for Kimai API (HTML5 local datetime format)
            # Kimai expects: YYYY-MM-DDTHH:mm:ss (without timezone)
            # NOT ISO 8601 with timezone information
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            log.info(f"Using HTML5 local datetime format: {current_time}")
            
            data = {
                "begin": current_time,
                "end": None,
                "project": project_id_int,
                "activity": activity_id_int,
                "description": description
            }
            
            log.info(f"Making POST request to {url}")
            log.info(f"Request headers: {dict(headers)}")  # Don't log the actual token
            log.info(f"Request data: {data}")
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            log.info(f"Response status code: {response.status_code}")
            log.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                log.info(f"Successfully started time tracking. Response: {response_data}")
                log.info(f"Timesheet ID: {response_data.get('id', 'Unknown')}")
                self.show_success()
            else:
                log.error(f"Failed to start time tracking. Status: {response.status_code}")
                log.error(f"Response body: {response.text}")
                log.error(f"Request URL: {url}")
                log.error(f"Request data: {data}")
                log.error(f"Request headers (without token): {{'Content-Type': headers.get('Content-Type'), 'Authorization': 'Bearer [REDACTED]'}}")
                
                # Try to parse error response
                try:
                    error_data = response.json()
                    log.error(f"Parsed error response: {error_data}")
                except:
                    log.error("Could not parse error response as JSON")
                
                self.show_error()
                
        except requests.exceptions.Timeout:
            log.error(f"Timeout while starting time tracking. URL: {url}")
            log.error(f"Timeout occurred after 10 seconds")
            self.show_error()
        except requests.exceptions.ConnectionError as e:
            log.error(f"Connection error while starting time tracking. URL: {url}")
            log.error(f"Connection error details: {e}")
            self.show_error()
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while starting time tracking: {e}")
            log.error(f"URL: {url}")
            log.error(f"Request exception type: {type(e)}")
            self.show_error()
        except ValueError as e:
            log.error(f"Invalid project_id or activity_id: {e}")
            log.error(f"project_id: '{project_id}' (type: {type(project_id)}), activity_id: '{activity_id}' (type: {type(activity_id)})")
            self.show_error()
        except Exception as e:
            log.error(f"Unexpected error starting time tracking: {e}")
            log.error(f"Exception type: {type(e)}")
            log.error(f"URL: {url}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            self.show_error()
    
    def show_success(self) -> None:
        """Show success indicator"""
        try:
            log.info("Showing success indicator (green background)")
            self.set_background_color([0, 255, 0, 100])  # Green background
        except Exception as e:
            log.error(f"Error setting success background: {e}")
        
    def show_error(self) -> None:
        """Show error indicator"""
        try:
            log.info("Showing error indicator (red background)")
            self.set_background_color([255, 0, 0, 100])  # Red background
        except Exception as e:
            log.error(f"Error setting error background: {e}")
        
    def get_config_rows(self) -> list:
        """Return configuration UI rows"""
        try:
            log.info("Building configuration UI for StartTracking action")
            
            super_rows = super().get_config_rows()
            
            # Customer dropdown (for filtering only)
            self.customer_dropdown = Adw.ComboRow(title="Customer (Filter)")
            self.customer_model = Gtk.StringList()
            self.customer_dropdown.set_model(self.customer_model)
            self.customer_dropdown.connect("notify::selected", self.on_customer_changed)
            
            # Project dropdown
            self.project_dropdown = Adw.ComboRow(title="Project")
            self.project_model = Gtk.StringList()
            self.project_dropdown.set_model(self.project_model)
            self.project_dropdown.connect("notify::selected", self.on_project_changed)
            
            # Activity dropdown
            self.activity_dropdown = Adw.ComboRow(title="Activity")
            self.activity_model = Gtk.StringList()
            self.activity_dropdown.set_model(self.activity_model)
            self.activity_dropdown.connect("notify::selected", self.on_activity_changed)
            
            # Description
            current_description = str(self.get_settings().get("description", ""))
            self.description_row = Adw.EntryRow(title="Description")
            self.description_row.set_text(current_description)
            self.description_row.connect("notify::text", self.on_description_changed)
            
            # Refresh button
            self.refresh_button = Gtk.Button(label="Refresh Data")
            self.refresh_button.connect("clicked", self.on_refresh_clicked)
            refresh_row = Adw.ActionRow(title="Data Management")
            refresh_row.add_suffix(self.refresh_button)
            
            # Info row
            info_row = Adw.ActionRow(title="Global Settings")
            info_row.set_subtitle("Configure Kimai URL and API Token in Plugin Settings")
            
            # Load data initially
            log.info("Starting initial data load for dropdowns")
            self.load_customers_and_global_activities()
            
            log.info("Configuration UI built successfully")
            return super_rows + [
                info_row,
                refresh_row,
                self.customer_dropdown,
                self.project_dropdown,
                self.activity_dropdown,
                self.description_row
            ]
            
        except Exception as e:
            log.error(f"Error building configuration UI: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
            return super().get_config_rows()
    
    def load_customers_and_global_activities(self) -> None:
        """Load customers and global activities from Kimai API"""
        threading.Thread(target=self._fetch_customers_and_global_activities, daemon=True).start()
    
    def _fetch_customers_and_global_activities(self) -> None:
        """Fetch customers and global activities in background thread"""
        try:
            plugin_global_settings = self.plugin_base.get_settings()
            kimai_url = plugin_global_settings.get("global_kimai_url", "")
            api_token = plugin_global_settings.get("global_api_token", "")
            
            if not kimai_url or not api_token:
                return
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Fetch customers
            customers_url = f"{kimai_url.rstrip('/')}/api/customers"
            customers_response = requests.get(customers_url, headers=headers, timeout=10)
            
            # Fetch global activities
            global_activities_url = f"{kimai_url.rstrip('/')}/api/activities?globals=true"
            global_activities_response = requests.get(global_activities_url, headers=headers, timeout=10)
            
            if customers_response.status_code == 200 and global_activities_response.status_code == 200:
                customers_data = customers_response.json()
                global_activities_data = global_activities_response.json()
                
                log.info(f"Successfully fetched {len(customers_data)} customers and {len(global_activities_data)} global activities")
                
                # Update UI in main thread
                from gi.repository import GLib
                GLib.idle_add(self._update_customers_and_global_activities, customers_data, global_activities_data)
            else:
                if customers_response.status_code != 200:
                    log.error(f"Failed to fetch customers. Status: {customers_response.status_code}")
                    log.error(f"Customers URL: {customers_url}")
                    log.error(f"Customers response: {customers_response.text}")
                
                if global_activities_response.status_code != 200:
                    log.error(f"Failed to fetch global activities. Status: {global_activities_response.status_code}")
                    log.error(f"Global activities URL: {global_activities_url}")
                    log.error(f"Global activities response: {global_activities_response.text}")
                
        except requests.exceptions.Timeout:
            log.error(f"Timeout while fetching customers/global activities from {kimai_url}")
        except requests.exceptions.ConnectionError:
            log.error(f"Connection error while fetching customers/global activities from {kimai_url}")
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while fetching customers/global activities: {e}")
            log.error(f"Kimai URL: {kimai_url}")
        except Exception as e:
            log.error(f"Unexpected error fetching customers/global activities: {e}")
            log.error(f"Kimai URL: {kimai_url}")
    
    def _update_customers_and_global_activities(self, customers_data: list, global_activities_data: list) -> None:
        """Update customer dropdown and global activities"""
        # Store customer mappings
        self.customers_map = {}
        
        # Clear existing customer model
        self.customer_model.splice(0, self.customer_model.get_n_items())
        
        # Add "All Customers" option
        self.customer_model.append("All Customers")
        self.customers_map["All Customers"] = None
        
        # Populate customers
        for customer in customers_data:
            if customer.get('visible', True):  # Only show visible customers
                customer_name = customer.get('name', f"Customer {customer.get('id')}")
                customer_id = customer.get('id')
                display_text = f"{customer_name} (ID: {customer_id})"
                
                self.customer_model.append(display_text)
                self.customers_map[display_text] = customer_id
        
        # Update global activities
        self._update_activities_dropdown(global_activities_data, is_global=True)
        
        # Restore current customer selection
        settings = self.get_settings()
        saved_customer_filter = settings.get("customer_filter", "")
        
        if saved_customer_filter:
            for i, (display_text, customer_id) in enumerate(self.customers_map.items()):
                if str(customer_id) == str(saved_customer_filter):
                    self.customer_dropdown.set_selected(i)
                    # Load projects for this customer
                    if customer_id:
                        self.load_projects_for_customer(customer_id)
                    break
        else:
            # If no customer filter saved, select "All Customers" and load all projects
            self.customer_dropdown.set_selected(0)
            self.load_projects_for_customer(None)
    
    def load_projects_for_customer(self, customer_id: int = None) -> None:
        """Load projects for selected customer"""
        threading.Thread(target=self._fetch_projects_for_customer, args=(customer_id,), daemon=True).start()
    
    def _fetch_projects_for_customer(self, customer_id: int = None) -> None:
        """Fetch projects for specific customer in background thread"""
        try:
            plugin_global_settings = self.plugin_base.get_settings()
            kimai_url = plugin_global_settings.get("global_kimai_url", "")
            api_token = plugin_global_settings.get("global_api_token", "")
            
            if not kimai_url or not api_token:
                return
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Fetch projects (filtered by customer if specified)
            if customer_id:
                projects_url = f"{kimai_url.rstrip('/')}/api/projects?customer={customer_id}"
            else:
                projects_url = f"{kimai_url.rstrip('/')}/api/projects"
            
            projects_response = requests.get(projects_url, headers=headers, timeout=10)
            
            if projects_response.status_code == 200:
                projects_data = projects_response.json()
                
                log.info(f"Successfully fetched {len(projects_data)} projects for customer {customer_id}")
                
                # Update UI in main thread
                from gi.repository import GLib
                GLib.idle_add(self._update_projects_dropdown, projects_data)
            else:
                log.error(f"Failed to fetch projects. Status: {projects_response.status_code}")
                log.error(f"Projects URL: {projects_url}")
                log.error(f"Projects response: {projects_response.text}")
                
        except requests.exceptions.Timeout:
            log.error(f"Timeout while fetching projects from {kimai_url}")
        except requests.exceptions.ConnectionError:
            log.error(f"Connection error while fetching projects from {kimai_url}")
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while fetching projects: {e}")
            log.error(f"Kimai URL: {kimai_url}")
        except Exception as e:
            log.error(f"Unexpected error fetching projects: {e}")
            log.error(f"Kimai URL: {kimai_url}")
    
    def load_activities_for_project(self, project_id: int = None) -> None:
        """Load activities for selected project (or global if no project)"""
        threading.Thread(target=self._fetch_activities_for_project, args=(project_id,), daemon=True).start()
    
    def _fetch_activities_for_project(self, project_id: int = None) -> None:
        """Fetch activities for specific project in background thread"""
        try:
            plugin_global_settings = self.plugin_base.get_settings()
            kimai_url = plugin_global_settings.get("global_kimai_url", "")
            api_token = plugin_global_settings.get("global_api_token", "")
            
            if not kimai_url or not api_token:
                return
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Fetch activities (project-specific or global)
            if project_id:
                activities_url = f"{kimai_url.rstrip('/')}/api/activities?project={project_id}"
            else:
                activities_url = f"{kimai_url.rstrip('/')}/api/activities?globals=true"
            
            activities_response = requests.get(activities_url, headers=headers, timeout=10)
            
            if activities_response.status_code == 200:
                activities_data = activities_response.json()
                
                log.info(f"Successfully fetched {len(activities_data)} activities for project {project_id}")
                
                # Update UI in main thread
                from gi.repository import GLib
                GLib.idle_add(self._update_activities_dropdown, activities_data, project_id is None)
            else:
                log.error(f"Failed to fetch activities. Status: {activities_response.status_code}")
                log.error(f"Activities URL: {activities_url}")
                log.error(f"Activities response: {activities_response.text}")
                
        except requests.exceptions.Timeout:
            log.error(f"Timeout while fetching activities from {kimai_url}")
        except requests.exceptions.ConnectionError:
            log.error(f"Connection error while fetching activities from {kimai_url}")
        except requests.exceptions.RequestException as e:
            log.error(f"HTTP request error while fetching activities: {e}")
            log.error(f"Kimai URL: {kimai_url}")
        except Exception as e:
            log.error(f"Unexpected error fetching activities: {e}")
            log.error(f"Kimai URL: {kimai_url}")
    

    
    def _update_projects_dropdown(self, projects_data: list) -> None:
        """Update projects dropdown with fetched data"""
        try:
            log.info(f"Updating projects dropdown with {len(projects_data)} projects")
            
            # Store project mappings
            self.projects_map = {}
            
            # Clear existing projects model
            self.project_model.splice(0, self.project_model.get_n_items())
            
            # Populate projects
            visible_projects = 0
            for project in projects_data:
                if project.get('visible', True):  # Only show visible projects
                    project_name = project.get('name', f"Project {project.get('id')}")
                    project_id = project.get('id')
                    display_text = f"{project_name} (ID: {project_id})"
                    
                    self.project_model.append(display_text)
                    self.projects_map[display_text] = project_id
                    visible_projects += 1
                    log.debug(f"Added project: {display_text}")
            
            log.info(f"Added {visible_projects} visible projects to dropdown")
            log.info(f"Projects map has {len(self.projects_map)} entries")
            
            # Restore current project selection
            settings = self.get_settings()
            saved_project_id = settings.get("project_id", "")
            log.info(f"Attempting to restore project selection: '{saved_project_id}'")
            
            if saved_project_id:
                restored = False
                for i, (display_text, project_id) in enumerate(self.projects_map.items()):
                    if str(project_id) == str(saved_project_id):
                        log.info(f"Restoring project selection: index {i}, '{display_text}'")
                        self.project_dropdown.set_selected(i)
                        restored = True
                        break
                
                if not restored:
                    log.warning(f"Could not restore project selection - project_id '{saved_project_id}' not found in current projects")
                    # Clear the invalid project_id from settings
                    settings = self.get_settings()
                    settings["project_id"] = ""
                    self.set_settings(settings)
                    log.info("Cleared invalid project_id from settings")
                    # Fall through to auto-selection logic below
                    saved_project_id = ""  # Clear it so auto-selection logic runs
            
            # Auto-select logic (runs if no saved project_id OR if restoration failed)
            if not saved_project_id:
                log.info("No valid saved project_id found, checking for auto-selection")
                
                # If there's only one project, auto-select it and save to settings
                if len(self.projects_map) == 1:
                    display_text, project_id = list(self.projects_map.items())[0]
                    log.info(f"Auto-selecting single project: '{display_text}' (ID: {project_id})")
                    self.project_dropdown.set_selected(0)
                    
                    # Manually save the project_id since the selection change might not trigger
                    settings = self.get_settings()
                    settings["project_id"] = str(project_id)
                    self.set_settings(settings)
                    log.info(f"Manually saved project_id to settings: {project_id}")
                    
                    # Also load activities for this project
                    log.info(f"Auto-loading activities for project {project_id}")
                    self.load_activities_for_project(project_id)
                    
                    # Manually trigger the project changed handler to ensure consistency
                    log.info("Manually triggering project change handler")
                    self.on_project_changed(self.project_dropdown)
                elif len(self.projects_map) > 1:
                    log.info(f"Multiple projects available ({len(self.projects_map)}), user must select manually")
                else:
                    log.info("No projects available for this customer")
                
        except Exception as e:
            log.error(f"Error updating projects dropdown: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
    
    def _update_activities_dropdown(self, activities_data: list, is_global: bool = False) -> None:
        """Update activities dropdown with fetched data"""
        try:
            log.info(f"Updating activities dropdown with {len(activities_data)} activities (global: {is_global})")
            
            # Store activity mappings
            self.activities_map = {}
            
            # Clear existing activities model
            self.activity_model.splice(0, self.activity_model.get_n_items())
            
            # Populate activities
            visible_activities = 0
            for activity in activities_data:
                if activity.get('visible', True):  # Only show visible activities
                    activity_name = activity.get('name', f"Activity {activity.get('id')}")
                    activity_id = activity.get('id')
                    
                    # Add indicator for global activities
                    if is_global:
                        display_text = f"{activity_name} (Global, ID: {activity_id})"
                    else:
                        display_text = f"{activity_name} (ID: {activity_id})"
                    
                    self.activity_model.append(display_text)
                    self.activities_map[display_text] = activity_id
                    visible_activities += 1
                    log.debug(f"Added activity: {display_text}")
            
            log.info(f"Added {visible_activities} visible activities to dropdown")
            log.info(f"Activities map has {len(self.activities_map)} entries")
            
            # Restore current activity selection
            settings = self.get_settings()
            saved_activity_id = settings.get("activity_id", "")
            log.info(f"Attempting to restore activity selection: '{saved_activity_id}'")
            
            if saved_activity_id:
                restored = False
                for i, (display_text, activity_id) in enumerate(self.activities_map.items()):
                    if str(activity_id) == str(saved_activity_id):
                        log.info(f"Restoring activity selection: index {i}, '{display_text}'")
                        self.activity_dropdown.set_selected(i)
                        restored = True
                        break
                
                if not restored:
                    log.warning(f"Could not restore activity selection - activity_id '{saved_activity_id}' not found in current activities")
                    # Fall through to auto-selection logic below
                    saved_activity_id = ""  # Clear it so auto-selection logic runs
            
            # Auto-select logic (runs if no saved activity_id OR if restoration failed)
            if not saved_activity_id:
                log.info("No valid saved activity_id found, checking for auto-selection")
                
                # If there are activities available, auto-select the first one
                if len(self.activities_map) >= 1:
                    display_text, activity_id = list(self.activities_map.items())[0]
                    log.info(f"Auto-selecting first activity: '{display_text}' (ID: {activity_id})")
                    self.activity_dropdown.set_selected(0)
                    
                    # Manually save the activity_id since the selection change might not trigger
                    settings = self.get_settings()
                    settings["activity_id"] = str(activity_id)
                    self.set_settings(settings)
                    log.info(f"Manually saved activity_id to settings: {activity_id}")
                    
                    # Verify the setting was saved
                    verification_settings = self.get_settings()
                    saved_activity_id_verify = verification_settings.get("activity_id", "")
                    if saved_activity_id_verify == str(activity_id):
                        log.info(f"✓ Activity ID successfully saved and verified: {saved_activity_id_verify}")
                    else:
                        log.error(f"✗ Activity ID save verification failed. Expected: {activity_id}, Got: {saved_activity_id_verify}")
                else:
                    log.info("No activities available for this project/global context")
                    
        except Exception as e:
            log.error(f"Error updating activities dropdown: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
    
    def on_customer_changed(self, dropdown, *args) -> None:
        """Handle customer selection change - reload projects based on selected customer"""
        try:
            log.info("Customer selection changed")
            selected_index = dropdown.get_selected()
            log.info(f"Selected index: {selected_index}")
            
            if selected_index != Gtk.INVALID_LIST_POSITION and hasattr(self, 'customers_map'):
                # Get the display text for the selected item
                display_texts = list(self.customers_map.keys())
                log.info(f"Available customers: {len(display_texts)}")
                
                if selected_index < len(display_texts):
                    selected_text = display_texts[selected_index]
                    customer_id = self.customers_map[selected_text]
                    
                    log.info(f"Selected customer: '{selected_text}' (ID: {customer_id})")
                    
                    # Save customer for filtering (not used in API)
                    settings = self.get_settings()
                    old_customer_filter = settings.get("customer_filter", "")
                    settings["customer_filter"] = str(customer_id) if customer_id else ""
                    
                    # Clear project_id and activity_id when customer changes
                    # This prevents trying to restore invalid project/activity combinations
                    if old_customer_filter != settings["customer_filter"]:
                        log.info(f"Customer changed from '{old_customer_filter}' to '{settings['customer_filter']}' - clearing project and activity selections")
                        settings["project_id"] = ""
                        settings["activity_id"] = ""
                        
                        # Also clear the activity dropdown since activities are project-dependent
                        if hasattr(self, 'activity_model'):
                            log.info("Clearing activity dropdown due to customer change")
                            self.activity_model.splice(0, self.activity_model.get_n_items())
                            self.activities_map = {}
                    
                    self.set_settings(settings)
                    log.info(f"Updated customer filter in settings: {settings.get('customer_filter')}")
                    
                    # Load projects for this customer
                    log.info(f"Loading projects for customer {customer_id}")
                    self.load_projects_for_customer(customer_id)
                else:
                    log.warning(f"Selected index {selected_index} out of range for {len(display_texts)} customers")
            else:
                log.warning(f"Invalid selection or customers_map not ready. Index: {selected_index}, has customers_map: {hasattr(self, 'customers_map')}")
                
        except Exception as e:
            log.error(f"Error in on_customer_changed: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
    
    def on_project_changed(self, dropdown, *args) -> None:
        """Handle project selection change - reload activities based on selected project"""
        try:
            log.info("Project selection changed")
            selected_index = dropdown.get_selected()
            log.info(f"Selected index: {selected_index}")
            
            if selected_index != Gtk.INVALID_LIST_POSITION and hasattr(self, 'projects_map'):
                # Get the display text for the selected item
                display_texts = list(self.projects_map.keys())
                log.info(f"Available projects: {len(display_texts)}")
                
                if selected_index < len(display_texts):
                    selected_text = display_texts[selected_index]
                    project_id = self.projects_map[selected_text]
                    
                    log.info(f"Selected project: '{selected_text}' (ID: {project_id})")
                    
                    # Save to settings
                    settings = self.get_settings()
                    old_project_id = settings.get("project_id", "")
                    settings["project_id"] = str(project_id)
                    
                    # Clear activity_id when project changes since activities are project-specific
                    if old_project_id != str(project_id):
                        log.info(f"Project changed from '{old_project_id}' to '{project_id}' - clearing activity selection")
                        settings["activity_id"] = ""
                    
                    self.set_settings(settings)
                    log.info(f"Updated project_id in settings: {old_project_id} -> {project_id}")
                    
                    # Verify the setting was saved
                    verification_settings = self.get_settings()
                    saved_project_id = verification_settings.get("project_id", "")
                    if saved_project_id == str(project_id):
                        log.info(f"✓ Project ID successfully saved and verified: {saved_project_id}")
                    else:
                        log.error(f"✗ Project ID save verification failed. Expected: {project_id}, Got: {saved_project_id}")
                        log.error(f"Full verification settings: {verification_settings}")
                    
                    # Load activities for this project
                    log.info(f"Loading activities for project {project_id}")
                    self.load_activities_for_project(project_id)
                else:
                    log.warning(f"Selected index {selected_index} out of range for {len(display_texts)} projects")
            else:
                log.warning(f"Invalid selection or projects_map not ready. Index: {selected_index}, has projects_map: {hasattr(self, 'projects_map')}")
                
        except Exception as e:
            log.error(f"Error in on_project_changed: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
    
    def on_activity_changed(self, dropdown, *args) -> None:
        """Handle activity selection change"""
        try:
            log.info("Activity selection changed")
            selected_index = dropdown.get_selected()
            log.info(f"Selected index: {selected_index}")
            
            if selected_index != Gtk.INVALID_LIST_POSITION and hasattr(self, 'activities_map'):
                # Get the display text for the selected item
                display_texts = list(self.activities_map.keys())
                log.info(f"Available activities: {len(display_texts)}")
                
                if selected_index < len(display_texts):
                    selected_text = display_texts[selected_index]
                    activity_id = self.activities_map[selected_text]
                    
                    log.info(f"Selected activity: '{selected_text}' (ID: {activity_id})")
                    
                    # Save to settings
                    settings = self.get_settings()
                    settings["activity_id"] = str(activity_id)
                    self.set_settings(settings)
                    log.info(f"Updated activity_id in settings: {settings.get('activity_id')}")
                else:
                    log.warning(f"Selected index {selected_index} out of range for {len(display_texts)} activities")
            else:
                log.warning(f"Invalid selection or activities_map not ready. Index: {selected_index}, has activities_map: {hasattr(self, 'activities_map')}")
                
        except Exception as e:
            log.error(f"Error in on_activity_changed: {e}")
            import traceback
            log.error(f"Traceback: {traceback.format_exc()}")
    
    def on_description_changed(self, entry, *args):
        settings = self.get_settings()
        settings["description"] = entry.get_text()
        self.set_settings(settings)
    
    def on_refresh_clicked(self, button) -> None:
        """Refresh customers, projects and activities when button is clicked"""
        button.set_sensitive(False)
        button.set_label("Refreshing...")
        
        def restore_button():
            button.set_sensitive(True)
            button.set_label("Refresh Data")
        
        # Restore button after 3 seconds
        from gi.repository import GLib
        GLib.timeout_add_seconds(3, restore_button)
        
        # Reload all data
        self.load_customers_and_global_activities()
