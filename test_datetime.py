#!/usr/bin/env python3
"""
Test script to demonstrate the datetime format difference for Kimai API
"""

from datetime import datetime

print("=== Datetime Format Comparison for Kimai API ===")

# Old format (ISO 8601 with timezone - INCORRECT for Kimai)
old_format = datetime.utcnow().isoformat()
print(f"❌ Old (ISO 8601 UTC):     {old_format}")

# New format (HTML5 local datetime - CORRECT for Kimai)
new_format = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
print(f"✅ New (HTML5 local):      {new_format}")

print("\nKey differences:")
print("- Old format includes 'Z' timezone indicator")
print("- New format uses local time without timezone")
print("- Kimai treats the datetime as local time and applies user's timezone")
print("\nThis should fix the timesheet creation issues!")
