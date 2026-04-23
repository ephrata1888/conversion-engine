import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HUBSPOT_ACCESS_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

properties = [
    {"name": "icp_segment", "label": "ICP Segment", "type": "string", "fieldType": "text"},
    {"name": "icp_segment_name", "label": "ICP Segment Name", "type": "string", "fieldType": "text"},
    {"name": "icp_confidence", "label": "ICP Confidence", "type": "string", "fieldType": "text"},
    {"name": "ai_maturity_score", "label": "AI Maturity Score", "type": "string", "fieldType": "text"},
    {"name": "ai_maturity_confidence", "label": "AI Maturity Confidence", "type": "string", "fieldType": "text"},
    {"name": "enriched_at", "label": "Enriched At", "type": "string", "fieldType": "text"},
    {"name": "enrichment_signals", "label": "Enrichment Signals", "type": "string", "fieldType": "text"},
    {"name": "discovery_call_booked", "label": "Discovery Call Booked", "type": "string", "fieldType": "text"},
    {"name": "discovery_call_id", "label": "Discovery Call ID", "type": "string", "fieldType": "text"},
    {"name": "discovery_call_time", "label": "Discovery Call Time", "type": "string", "fieldType": "text"},
    {"name": "discovery_call_url", "label": "Discovery Call URL", "type": "string", "fieldType": "text"},
    {"name": "booking_status", "label": "Booking Status", "type": "string", "fieldType": "text"},
]

for prop in properties:
    payload = {
        "name": prop["name"],
        "label": prop["label"],
        "type": prop["type"],
        "fieldType": prop["fieldType"],
        "groupName": "contactinformation"
    }
    
    response = requests.post(
        "https://api.hubapi.com/crm/v3/properties/contacts",
        headers=headers,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        print(f"  Created: {prop['name']}")
    elif response.status_code == 409:
        print(f"  Already exists: {prop['name']}")
    else:
        print(f"  Failed {prop['name']}: {response.status_code} {response.text[:100]}")

print("Done!")