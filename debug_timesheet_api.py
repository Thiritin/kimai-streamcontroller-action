#!/usr/bin/env python3
"""
Debug script to test timesheet API response format
"""

import requests
import json
from typing import Optional

def test_timesheet_api(kimai_url: str, api_token: str):
    """Test the timesheet API to see what format it returns"""
    
    try:
        url = f"{kimai_url.rstrip('/')}/api/timesheets"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Get active timesheets with full expansion (nested objects)
        params = {"size": 1, "orderBy": "begin", "order": "DESC", "full": "true"}
        
        print(f"Making request to: {url}")
        print(f"With params: {params}")
        print(f"Headers: {{'Authorization': 'Bearer [HIDDEN]', 'Content-Type': 'application/json'}}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            timesheets = response.json()
            print(f"Response type: {type(timesheets)}")
            print(f"Response length: {len(timesheets) if isinstance(timesheets, list) else 'N/A'}")
            print(f"Raw response: {json.dumps(timesheets, indent=2)}")
            
            if timesheets and len(timesheets) > 0:
                timesheet = timesheets[0]
                print(f"\nFirst timesheet type: {type(timesheet)}")
                print(f"First timesheet: {json.dumps(timesheet, indent=2)}")
                
                # Check if active
                end_time = timesheet.get('end') if isinstance(timesheet, dict) else None
                print(f"\nEnd time: {end_time}")
                print(f"Is active: {end_time is None}")
                
                if end_time is None:
                    # Extract key information
                    if isinstance(timesheet, dict):
                        project_info = timesheet.get('project', {})
                        activity_info = timesheet.get('activity', {})
                        
                        print(f"\nProject info: {json.dumps(project_info, indent=2)}")
                        print(f"Activity info: {json.dumps(activity_info, indent=2)}")
                        
                        if project_info:
                            customer_info = project_info.get('customer', {})
                            print(f"Customer info: {json.dumps(customer_info, indent=2)}")
                    else:
                        print(f"ERROR: Expected dict but got {type(timesheet)}")
            else:
                print("No timesheets found")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("Timesheet API Debug Script")
    print("=" * 40)
    print("This script helps debug the timesheet API response format.")
    print("Please provide your Kimai URL and API token:")
    print()
    
    kimai_url = input("Kimai URL: ").strip()
    api_token = input("API Token: ").strip()
    
    if kimai_url and api_token:
        print("\n" + "=" * 40)
        test_timesheet_api(kimai_url, api_token)
    else:
        print("Please provide both URL and token")
