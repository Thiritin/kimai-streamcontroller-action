#!/usr/bin/env python3
"""
Test script for timezone-aware datetime parsing
"""

from datetime import datetime

def test_datetime_parsing():
    """Test the datetime parsing with timezone information"""
    
    test_cases = [
        "2025-06-18T07:02:46+0200",
        "2025-06-18T07:02:46Z",
        "2025-06-18T07:02:46",
        "2025-06-18T07:02:46-0500",
    ]
    
    print("Testing datetime parsing with timezone handling:")
    print("=" * 50)
    
    for test_time in test_cases:
        try:
            print(f"\nTesting: '{test_time}'")
            
            # Apply the same logic as in our fixed code
            start_time_clean = test_time
            if '+' in start_time_clean:
                # Positive timezone offset
                start_time_clean = start_time_clean.split('+')[0]
            elif start_time_clean.endswith('Z'):
                # UTC timezone indicator
                start_time_clean = start_time_clean[:-1]
            elif '-' in start_time_clean and start_time_clean.count('-') > 2:
                # Negative timezone offset (more than 2 dashes means timezone)
                start_time_clean = start_time_clean.rsplit('-', 1)[0]
            
            print(f"Cleaned: '{start_time_clean}'")
            
            start_dt = datetime.strptime(start_time_clean, '%Y-%m-%dT%H:%M:%S')
            now_dt = datetime.now()
            elapsed = now_dt - start_dt
            
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            elapsed_text = f"{hours:02d}:{minutes:02d}"
            
            print(f"✅ SUCCESS: Parsed successfully")
            print(f"   Start time: {start_dt}")
            print(f"   Elapsed: {elapsed_text}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_datetime_parsing()
