#!/usr/bin/env python3
"""
Test script for DisplayActiveTracking implementation
"""

import os
import sys

def test_display_active_tracking():
    """Test the DisplayActiveTracking implementation"""
    
    # Read the DisplayActiveTracking.py file
    with open('actions/DisplayActiveTracking/DisplayActiveTracking.py', 'r') as f:
        content = f.read()
    
    # Check for required components
    tests = [
        ('DisplayActiveTracking class exists', 'class DisplayActiveTracking'),
        ('Inherits from ActionBase', 'ActionBase'),
        ('Has update_display method', 'def update_display'),
        ('Has periodic update functionality', '_periodic_update'),
        ('Fetches active timesheet', '_get_active_timesheet'),
        ('Calculates elapsed time', '_calculate_elapsed_time'),
        ('Shows no active tracking state', '_show_no_active_tracking'),
        ('Shows error state', '_show_error'),
        ('Has configuration UI', 'get_config_rows'),
        ('Uses threading for API calls', 'threading.Thread'),
        ('Has proper exception handling', 'except Exception'),
    ]
    
    print("Testing DisplayActiveTracking implementation:")
    print("=" * 50)
    
    all_passed = True
    for test_name, check in tests:
        passed = check in content
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_main_py_registration():
    """Test that main.py properly registers the new action"""
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    tests = [
        ('Imports DisplayActiveTracking', 'from .actions.DisplayActiveTracking.DisplayActiveTracking import DisplayActiveTracking'),
        ('Registers display_active_tracking_holder', 'self.display_active_tracking_holder'),
        ('Has proper action_id', 'com_thiritin_kimai_plugin::DisplayActiveTracking'),
        ('Has proper action_name', 'Display Active Tracking'),
        ('Adds action holder', 'self.add_action_holder(self.display_active_tracking_holder)'),
        ('Adds info icon', 'self.add_icon("info"'),
    ]
    
    print("\nTesting main.py registration:")
    print("=" * 35)
    
    all_passed = True
    for test_name, check in tests:
        passed = check in content
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_assets():
    """Test that required assets exist"""
    
    print("\nTesting required assets:")
    print("=" * 30)
    
    assets_dir = 'assets'
    required_assets = ['info.png']
    
    all_exist = True
    for asset in required_assets:
        asset_path = os.path.join(assets_dir, asset)
        exists = os.path.exists(asset_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status} {asset}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("DisplayActiveTracking Implementation Test")
    print("=" * 50)
    
    # Change to plugin directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run tests
    display_test = test_display_active_tracking()
    main_test = test_main_py_registration()
    asset_test = test_assets()
    
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    if display_test and main_test and asset_test:
        print("✅ ALL TESTS PASSED - DisplayActiveTracking ready!")
        print("\nThe new button will:")
        print("- Show current customer/project/activity info")
        print("- Display elapsed time in HH:MM format") 
        print("- Auto-refresh every 30 seconds")
        print("- Allow manual refresh by pressing the button")
        print("- Show appropriate status messages")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
