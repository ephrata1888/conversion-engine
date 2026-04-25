import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from outbound_gate import gate_booking

load_dotenv()

CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_EVENT_TYPE_ID = os.getenv("CAL_EVENT_TYPE_ID")
CAL_BASE_URL = "https://api.cal.com/v2"
HEADERS = {
    "Authorization": f"Bearer {CAL_API_KEY}",
    "cal-api-version": "2024-06-14"
}

def get_available_slots(days_ahead: int = 7) -> dict:
    """Get available booking slots for the next N days."""
    start = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    end = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    response = requests.get(
        f"{CAL_BASE_URL}/slots/available",
        headers=HEADERS,
        params={
            "eventTypeId": CAL_EVENT_TYPE_ID,
            "startTime": start,
            "endTime": end,
            "timeZone": "Africa/Addis_Ababa"
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting slots: {response.status_code} {response.text[:300]}")
        return {}

def book_discovery_call(
    prospect_name: str,
    prospect_email: str,
    slot_time: str,
    notes: str = ""
) -> dict:
    prospect_email = gate_booking(prospect_email)
    """Book a discovery call for a prospect."""
    payload = {
        "eventTypeId": int(CAL_EVENT_TYPE_ID),
        "start": slot_time,
        "timeZone": "Africa/Addis_Ababa",
        "language": "en",
        "responses": {
            "name": prospect_name,
            "email": prospect_email,
            "location": {
                "value": "integrations:cal-video",
                "optionValue": ""
            }
        },
        "metadata": {
            "source": "conversion-engine",
            "notes": notes
        }
    }
    
    response = requests.post(
        f"{CAL_BASE_URL}/bookings",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error booking: {response.status_code} {response.text[:500]}")
        return {"error": response.text}

if __name__ == "__main__":
    # Test 1: Get available slots
    print("Getting available slots...")
    slots = get_available_slots(days_ahead=3)
    print(json.dumps(slots, indent=2)[:500])
    
    # Test 2: Book a test slot
    print("\nBooking test slot...")
    result = book_discovery_call(
        prospect_name="Test Prospect",
        prospect_email="ephratawolde990@gmail.com",
        slot_time="2026-04-24T10:00:00Z",
        notes="Test booking from conversion engine"
    )
    print(json.dumps(result, indent=2))