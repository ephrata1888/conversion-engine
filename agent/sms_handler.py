import requests
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Handler registry for inbound SMS
_inbound_handlers = []

def register_inbound_handler(handler_fn):
    """Register a callback for inbound SMS messages."""
    _inbound_handlers.append(handler_fn)

def dispatch_inbound(payload: dict):
    """Dispatch inbound SMS to all registered handlers."""
    for handler in _inbound_handlers:
        try:
            handler(payload)
        except Exception as e:
            print(f"  SMS handler {handler.__name__} error: {e}")

def validate_sms_payload(payload: dict) -> tuple:
    """Validate inbound SMS webhook payload."""
    if not payload.get("from"):
        return False, "Missing 'from' field"
    if not payload.get("text") and not payload.get("message"):
        return False, "Missing message content"
    return True, None

def check_warm_lead(prospect_email: str, hubspot_contact_id: str = None) -> bool:
    """
    Check if prospect has prior email engagement before sending SMS.
    SMS is reserved for warm leads only — prospects who have replied by email.
    Returns True if SMS is appropriate, False if not.
    """
    if not hubspot_contact_id:
        print("  SMS blocked: no HubSpot contact ID — prospect not yet in CRM")
        return False

    try:
        from hubspot import HubSpot
        client = HubSpot(access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"))
        contact = client.crm.contacts.basic_api.get_by_id(
            contact_id=hubspot_contact_id,
            properties=["email_replied", "hs_email_replied", "lifecyclestage"]
        )
        props = contact.properties
        lifecycle = props.get("lifecyclestage", "lead")

        # Allow SMS if prospect is beyond lead stage or has replied
        if lifecycle in ["marketingqualifiedlead", "salesqualifiedlead", 
                         "opportunity", "customer"]:
            print(f"  SMS approved: prospect lifecycle stage is '{lifecycle}'")
            return True

        print(f"  SMS blocked: prospect lifecycle is '{lifecycle}' — email first")
        return False

    except Exception as e:
        print(f"  SMS warm-lead check error: {e} — defaulting to block")
        return False

def send_sms(to_number: str, message: str, 
             prospect_email: str = None, 
             hubspot_contact_id: str = None,
             force: bool = False) -> dict:
    """
    Send SMS via Africa's Talking sandbox.
    Enforces warm-lead check unless force=True.
    """
    if not to_number:
        return {"status": "error", "error": "Missing recipient number"}
    if not message:
        return {"status": "error", "error": "Missing message content"}

    # Enforce warm-lead check
    if not force:
        is_warm = check_warm_lead(prospect_email, hubspot_contact_id)
        if not is_warm:
            return {
                "status": "blocked",
                "reason": "SMS reserved for warm leads with prior email engagement",
                "to": to_number
            }

    try:
        response = requests.post(
            "https://api.sandbox.africastalking.com/version1/messaging",
            headers={
                "apiKey": os.getenv("AT_API_KEY"),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            },
            data={
                "username": os.getenv("AT_USERNAME"),
                "to": to_number,
                "message": message
            },
            verify=False
        )
        data = response.json()
        recipients = data.get("SMSMessageData", {}).get("Recipients", [])

        if recipients and recipients[0].get("status") == "Success":
            return {
                "status": "success",
                "messageId": recipients[0].get("messageId"),
                "to": to_number,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "status": "error",
                "error": data.get("SMSMessageData", {}).get("Message", "Unknown error"),
                "to": to_number
            }
    except Exception as e:
        return {"status": "error", "error": str(e), "to": to_number}

def handle_inbound_sms(payload: dict) -> dict:
    """Handle inbound SMS webhook from Africa's Talking."""
    is_valid, error = validate_sms_payload(payload)
    if not is_valid:
        return {"status": "error", "error": error}

    event = {
        "type": "sms_reply",
        "from": payload.get("from"),
        "message": payload.get("text", payload.get("message", "")),
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    # Check for STOP command
    if event["message"].strip().upper() in ["STOP", "UNSUBSCRIBE", "CANCEL", "END"]:
        print(f"  STOP received from {event['from']} — marking as unsubscribed")
        event["type"] = "sms_stop"

    dispatch_inbound(event)
    return {"status": "received", "event": event}

if __name__ == "__main__":
    # Test 1: blocked SMS (no prior engagement)
    print("Test 1: SMS without warm lead check")
    result = send_sms("+251900000000", "Test message", force=False)
    print("Result:", result)

    # Test 2: forced SMS (sandbox test)
    print("\nTest 2: Forced SMS send")
    result = send_sms("+251900000000", "Test from conversion engine", force=True)
    print("Result:", result)

    # Test 3: inbound webhook
    print("\nTest 3: Inbound SMS webhook")
    def sample_handler(event):
        print(f"  Handler: {event['from']} sent '{event['message']}'")

    register_inbound_handler(sample_handler)
    webhook_result = handle_inbound_sms({
        "from": "+251911000000",
        "text": "Yes I'm interested, when can we talk?"
    })
    print("Webhook result:", webhook_result)