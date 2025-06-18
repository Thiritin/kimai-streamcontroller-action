#!/usr/bin/env python3
"""
Debug script to test Kimai plugin configuration and API access
"""

import sys
import os
import json

# Add the plugin directory to the path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

def test_settings():
    """Test if we can read the settings files"""
    print("=== Testing Settings Files ===")
    
    # Check global settings
    global_settings_path = "/home/martin/projects/kimai-streamcontroller-action/settings/settings.json"
    if os.path.exists(global_settings_path):
        try:
            with open(global_settings_path, 'r') as f:
                global_settings = json.load(f)
            print(f"✓ Global settings loaded: {len(global_settings)} entries")
            
            # Check for Kimai settings
            if 'global_kimai_url' in global_settings:
                print(f"✓ Kimai URL configured: {global_settings['global_kimai_url'][:20]}...")
            else:
                print("✗ Kimai URL not configured")
                
            if 'global_api_token' in global_settings:
                print(f"✓ API Token configured: {global_settings['global_api_token'][:10]}...")
            else:
                print("✗ API Token not configured")
                
        except Exception as e:
            print(f"✗ Error reading global settings: {e}")
    else:
        print(f"✗ Global settings file not found: {global_settings_path}")
    
    # Check page settings
    page_settings_path = "/home/martin/projects/kimai-streamcontroller-action/pages/Start.json"
    if os.path.exists(page_settings_path):
        try:
            with open(page_settings_path, 'r') as f:
                page_settings = json.load(f)
            print(f"✓ Page settings loaded")
            
            # Look for action settings
            action_settings_found = False
            if 'keys' in page_settings:
                for key_id, key_data in page_settings['keys'].items():
                    if 'states' in key_data:
                        for state_id, state_data in key_data['states'].items():
                            if 'actions' in state_data:
                                for action in state_data['actions']:
                                    if action.get('id') == 'com_thiritin_kimai_plugin::StartTracking':
                                        print(f"✓ Found StartTracking action on key {key_id}, state {state_id}")
                                        settings = action.get('settings', {})
                                        print(f"  - All settings: {settings}")
                                        print(f"  - Project ID: {settings.get('project_id', 'Not set')}")
                                        print(f"  - Activity ID: {settings.get('activity_id', 'Not set')}")
                                        print(f"  - Customer Filter: {settings.get('customer_filter', 'Not set')}")
                                        print(f"  - Description: {settings.get('description', 'Not set')}")
                                        action_settings_found = True
                                        
                                        # Check if this looks like a configuration issue
                                        has_customer = bool(settings.get('customer_filter'))
                                        has_project = bool(settings.get('project_id'))
                                        has_activity = bool(settings.get('activity_id'))
                                        
                                        if has_customer and not has_project:
                                            print(f"  ⚠️  Customer is set but project is missing - this suggests project selection didn't save properly")
                                        if has_project and not has_activity:
                                            print(f"  ⚠️  Project is set but activity is missing - this suggests activity selection didn't save properly")
                                        if has_customer and has_project and has_activity:
                                            print(f"  ✓ All required settings appear to be configured")
                        
            if not action_settings_found:
                print("✗ No StartTracking action configuration found")
                print("  This means you need to add a StartTracking action to your StreamController page first")
                
        except Exception as e:
            print(f"✗ Error reading page settings: {e}")
    else:
        print(f"✗ Page settings file not found: {page_settings_path}")

def test_api_connection():
    """Test basic API connection"""
    print("\n=== Testing API Connection ===")
    
    try:
        import requests
        
        # Try to read settings
        global_settings_path = "/home/martin/projects/kimai-streamcontroller-action/settings/settings.json"
        if not os.path.exists(global_settings_path):
            print("✗ Cannot test API - global settings not found")
            return
            
        with open(global_settings_path, 'r') as f:
            global_settings = json.load(f)
            
        kimai_url = global_settings.get('global_kimai_url', '')
        api_token = global_settings.get('global_api_token', '')
        
        if not kimai_url or not api_token:
            print("✗ Cannot test API - URL or token not configured")
            return
            
        # Test customers endpoint
        customers_url = f"{kimai_url.rstrip('/')}/api/customers"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Testing: {customers_url}")
        response = requests.get(customers_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            customers = response.json()
            print(f"✓ API connection successful - {len(customers)} customers found")
        else:
            print(f"✗ API error - Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except ImportError:
        print("✗ requests library not available")
    except Exception as e:
        print(f"✗ API test failed: {e}")

if __name__ == "__main__":
    test_settings()
    test_api_connection()
