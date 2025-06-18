#!/usr/bin/env python3
"""
Test script for pause icon implementation
"""

import os
import sys

def test_icon_references():
    """Test that the pause icon implementation references correct assets"""
    
    # Read the StartTracking.py file
    with open('actions/StartTracking/StartTracking.py', 'r') as f:
        content = f.read()
    
    # Check for correct icon references
    tests = [
        ('start.png reference in _set_stopped_state', 'start.png'),
        ('stop.png reference in _set_running_state', 'stop.png'),
        ('No clock emoji references', '🕐' not in content),
        ('No clock_states array', 'clock_states' not in content),
        ('Uses elapsed_timer_id', 'elapsed_timer_id'),
        ('Has _start_elapsed_time_display method', '_start_elapsed_time_display'),
        ('Has _stop_elapsed_time_display method', '_stop_elapsed_time_display'),
        ('Has _update_elapsed_time_display method', '_update_elapsed_time_display'),
    ]
    
    print("Testing pause icon implementation:")
    print("=" * 50)
    
    all_passed = True
    for test_name, check in tests:
        if isinstance(check, bool):
            passed = check
        else:
            passed = check in content
            
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Pause icon implementation looks good.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

def test_asset_files():
    """Test that required asset files exist"""
    print("\nTesting asset files:")
    print("=" * 30)
    
    assets_dir = 'assets'
    required_assets = ['start.png', 'stop.png']
    
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
    print("Pause Icon Implementation Test")
    print("=" * 50)
    
    # Change to plugin directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run tests
    code_test = test_icon_references()
    asset_test = test_asset_files()
    
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    if code_test and asset_test:
        print("✅ ALL TESTS PASSED - Implementation ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
