from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
import os
import json
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

client = HubSpot(access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"))

def create_or_update_contact(email, firstname, lastname, company, jobtitle="", enrichment_data=None):
    """Create or update a HubSpot contact with enrichment fields."""
    properties = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "company": company,
        "jobtitle": jobtitle
    }

    if enrichment_data:
        icp = enrichment_data.get("icp_segment", {})
        signals = enrichment_data.get("signals", {})
        ai_maturity = signals.get("ai_maturity", {})

        properties["icp_segment"] = str(icp.get("segment", ""))
        properties["icp_segment_name"] = icp.get("name", "")
        properties["icp_confidence"] = str(icp.get("confidence", ""))
        properties["ai_maturity_score"] = str(ai_maturity.get("score", ""))
        properties["ai_maturity_confidence"] = ai_maturity.get("confidence", "")
        properties["enriched_at"] = enrichment_data.get(
            "enriched_at", datetime.now(timezone.utc).isoformat()
        )
        properties["enrichment_signals"] = json.dumps({
            "funding": signals.get("funding", {}).get("has_recent_funding", False),
            "layoffs": signals.get("layoffs", {}).get("has_recent_layoffs", False),
            "leadership_change": signals.get("leadership_change", {}).get("has_leadership_change", False),
            "ai_maturity": ai_maturity.get("score", 0)
        })

    try:
        contact = SimplePublicObjectInputForCreate(properties=properties)
        response = client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=contact
        )
        print(f"  HubSpot contact created: {response.id}")
        return {"id": response.id, "properties": response.properties, "status": "created"}

    except ApiException as e:
        error_body = json.loads(e.body) if e.body else {}
        if e.status == 409 or "CONFLICT" in str(error_body.get("category", "")):
            match = re.search(r"Existing ID: (\d+)", str(error_body.get("message", "")))
            existing_id = match.group(1) if match else "unknown"
            print(f"  HubSpot contact already exists: {existing_id}")
            return {"id": existing_id, "status": "existing"}
        print(f"  HubSpot error {e.status}: {error_body.get('message', str(e))}")
        return None
    except Exception as e:
        print(f"  HubSpot unexpected error: {e}")
        return None

def update_contact_booking(contact_id, booking_data):
    """Update a HubSpot contact after a Cal.com booking is confirmed."""
    try:
        properties = {
            "discovery_call_booked": "true",
            "discovery_call_id": str(booking_data.get("id", "")),
            "discovery_call_time": booking_data.get("startTime", ""),
            "discovery_call_url": booking_data.get("videoCallUrl", ""),
            "booking_status": booking_data.get("status", "")
        }
        update = SimplePublicObjectInput(properties=properties)
        response = client.crm.contacts.basic_api.update(
            contact_id=contact_id,
            simple_public_object_input=update
        )
        print(f"  HubSpot contact updated with booking: {contact_id}")
        return {"id": contact_id, "status": "updated"}
    except Exception as e:
        print(f"  HubSpot booking update error: {e}")
        return None

if __name__ == "__main__":
    result = create_or_update_contact(
        email="test4@example.com",
        firstname="Test",
        lastname="Four",
        company="Test Corp",
        jobtitle="CTO",
        enrichment_data={
            "icp_segment": {"segment": 1, "name": "Recently-funded startup", "confidence": 0.8},
            "signals": {
                "funding": {"has_recent_funding": True},
                "layoffs": {"has_recent_layoffs": False},
                "leadership_change": {"has_leadership_change": False},
                "ai_maturity": {"score": 2, "confidence": "high"}
            },
            "enriched_at": datetime.now(timezone.utc).isoformat()
        }
    )
    print(result)