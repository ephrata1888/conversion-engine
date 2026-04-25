from fastapi import FastAPI, Request
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "agent"))

from email_handler import handle_inbound_webhook, register_reply_handler
from hubspot_handler import create_or_update_contact

app = FastAPI()

# Register reply handler — qualifies prospect and books call
def on_reply_received(event):
    from_email = event.get("from", "")
    body = event.get("body", "").lower()
    print(f"\n  [REPLY] From: {from_email}")
    print(f"  [REPLY] Body preview: {body[:100]}")

    positive_signals = [
        "interested", "yes", "tell me more", "sounds good",
        "let's talk", "lets talk", "when can we", "happy to",
        "sure", "absolutely", "great", "would love"
    ]

    if any(signal in body for signal in positive_signals):
        print(f"  [REPLY] Positive signal detected — booking discovery call")
        try:
            from cal_handler import get_available_slots, book_discovery_call
            slots = get_available_slots(days_ahead=5)
            slot_dates = slots.get("data", {}).get("slots", {})
            first_slot = None
            for date, times in slot_dates.items():
                if times:
                    first_slot = times[0].get("time")
                    break

            if first_slot:
                booking = book_discovery_call(
                    prospect_name=from_email.split("@")[0],
                    prospect_email=from_email,
                    slot_time=first_slot,
                    notes="Auto-booked after positive reply"
                )
                booking_id = booking.get("data", {}).get("id")
                print(f"  [REPLY] Discovery call booked: ID {booking_id}")
            else:
                print(f"  [REPLY] No available slots found")
        except Exception as e:
            print(f"  [REPLY] Booking error: {e}")
    else:
        print(f"  [REPLY] Neutral/negative reply — logging only")

register_reply_handler(on_reply_received)

@app.get("/")
def health_check():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}

@app.post("/webhooks/email")
async def email_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {}
    result = handle_inbound_webhook(data)
    return result

@app.post("/webhooks/sms")
async def sms_webhook(request: Request):
    data = await request.form()
    payload = dict(data)
    print(f"SMS received: {payload}")
    return {"status": "received"}

@app.post("/webhooks/calendar")
async def calendar_webhook(request: Request):
    data = await request.json()
    print(f"Calendar event: {json.dumps(data, indent=2)[:200]}")
    return {"status": "received"}

@app.post("/webhooks/hubspot")
async def hubspot_webhook(request: Request):
    data = await request.json()
    print(f"HubSpot event: {json.dumps(data, indent=2)[:200]}")
    return {"status": "received"}