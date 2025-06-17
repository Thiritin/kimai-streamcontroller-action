# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class KimaiPluginSettings:
    def __init__(self, plugin_base):
        self.plugin_base = plugin_base
        
    def get_settings_area(self):
        """Create and return the global settings UI for the plugin"""
        group = Adw.PreferencesGroup()
        group.set_title("Global Kimai Settings")
        group.set_description("Configure your Kimai instance connection details. These settings will be used by all Kimai actions.")
        
        # Kimai URL setting
        self.kimai_url_row = Adw.EntryRow(title="Kimai URL")
        self.kimai_url_row.set_text(self.plugin_base.get_settings().get("global_kimai_url", ""))
        self.kimai_url_row.connect("notify::text", self.on_kimai_url_changed)
        group.add(self.kimai_url_row)
        
        # API Token setting
        self.api_token_row = Adw.PasswordEntryRow(title="API Token")
        self.api_token_row.set_text(self.plugin_base.get_settings().get("global_api_token", ""))
        self.api_token_row.connect("notify::text", self.on_api_token_changed)
        group.add(self.api_token_row)
        
        return group
    
    def on_kimai_url_changed(self, entry, *args):
        """Handle Kimai URL changes"""
        settings = self.plugin_base.get_settings()
        settings["global_kimai_url"] = entry.get_text()
        self.plugin_base.set_settings(settings)
    
    def on_api_token_changed(self, entry, *args):
        """Handle API token changes"""
        settings = self.plugin_base.get_settings()
        settings["global_api_token"] = entry.get_text()
        self.plugin_base.set_settings(settings)
