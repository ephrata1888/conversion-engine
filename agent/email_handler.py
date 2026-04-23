import resend
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Handler registry
_reply_handlers = []
_bounce_handlers = []
_delivery_handlers = []

def register_reply_handler(handler_fn):
    """Register a callback for email replies."""
    _reply_handlers.append(handler_fn)
    print(f"  Registered reply handler: {handler_fn.__name__}")

def register_bounce_handler(handler_fn):
    """Register a callback for email bounces."""
    _bounce_handlers.append(handler_fn)
    print(f"  Registered bounce handler: {handler_fn.__name__}")

def register_delivery_handler(handler_fn):
    """Register a callback for successful deliveries."""
    _delivery_handlers.append(handler_fn)
    print(f"  Registered delivery handler: {handler_fn.__name__}")

def dispatch_event(event_type: str, payload: dict):
    """Dispatch event to appropriate handlers."""
    handlers = {
        "email_reply": _reply_handlers,
        "email_bounce": _bounce_handlers,
        "email_delivered": _delivery_handlers
    }
    for handler in handlers.get(event_type, []):
        try:
            handler(payload)
        except Exception as e:
            print(f"  Handler {handler.__name__} error: {e}")

def validate_webhook_payload(payload) -> tuple:
    """
    Validate inbound email webhook payload.
    Returns (is_valid, error_message, cleaned_payload).
    """
    # Type check
    if not isinstance(payload, dict):
        return False, f"Payload must be a dict, got {type(payload).__name__}", None

    # Required fields
    required = ["type"]
    for field in required:
        if field not in payload:
            return False, f"Missing required field: '{field}'", None

    # Type validation
    valid_types = ["email.delivered", "email.bounced", "email.complained",
                   "email.opened", "email.clicked", "inbound"]
    event_type = payload.get("type", "")
    if not isinstance(event_type, str):
        return False, f"Field 'type' must be a string, got {type(event_type).__name__}", None

    # Extract and validate email data
    data = payload.get("data", {})
    if not isinstance(data, dict):
        # Try treating payload itself as data for inbound webhooks
        data = payload

    from_email = data.get("from", data.get("email_id", ""))
    if from_email and not isinstance(from_email, str):
        return False, f"Field 'from' must be a string", None
    if from_email and "@" not in from_email:
        return False, f"Field 'from' is not a valid email: {from_email}", None

    # Clean and return
    cleaned = {
        "type": event_type,
        "from": from_email,
        "subject": str(data.get("subject", "")),
        "body": str(data.get("text", data.get("html", data.get("body", "")))),
        "email_id": str(data.get("email_id", data.get("id", ""))),
        "bounce_type": data.get("bounce_type", ""),
        "raw": payload
    }
    return True, None, cleaned

def handle_bounce(event: dict):
    """Handle a bounced email — log and dispatch to bounce handlers."""
    bounce_type = event.get("bounce_type", "unknown")
    email_id = event.get("email_id", "unknown")
    from_email = event.get("from", "unknown")

    print(f"  BOUNCE [{bounce_type}] email_id={email_id} to={from_email}")

    # Permanent bounces (hard bounce) — mark contact as invalid
    if bounce_type in ["permanent", "hard"]:
        print(f"  Hard bounce detected — prospect email invalid: {from_email}")
        event["action_required"] = "mark_email_invalid"
    else:
        print(f"  Soft bounce detected — will retry: {from_email}")
        event["action_required"] = "retry_later"

    dispatch_event("email_bounce", event)

def handle_inbound_webhook(payload) -> dict:
    """
    Handle inbound email webhook from Resend.
    Supports reply, bounce, delivery, and complaint events.
    """
    is_valid, error, cleaned = validate_webhook_payload(payload)
    if not is_valid:
        print(f"  Webhook validation failed: {error}")
        return {"status": "error", "error": error}

    event_type = cleaned["type"]
    cleaned["received_at"] = datetime.now(timezone.utc).isoformat()

    # Route by event type
    if event_type == "email.bounced":
        cleaned["type"] = "email_bounce"
        handle_bounce(cleaned)
        return {"status": "received", "event_type": "bounce", "action": cleaned.get("action_required")}

    elif event_type == "email.delivered":
        cleaned["type"] = "email_delivered"
        print(f"  Delivery confirmed: email_id={cleaned['email_id']}")
        dispatch_event("email_delivered", cleaned)
        return {"status": "received", "event_type": "delivered"}

    elif event_type == "email.complained":
        print(f"  SPAM complaint from {cleaned['from']} — suppressing future sends")
        cleaned["type"] = "email_bounce"
        cleaned["action_required"] = "suppress_contact"
        dispatch_event("email_bounce", cleaned)
        return {"status": "received", "event_type": "complaint", "action": "suppress_contact"}

    elif event_type == "inbound":
        cleaned["type"] = "email_reply"
        dispatch_event("email_reply", cleaned)
        return {"status": "received", "event_type": "reply"}

    else:
        print(f"  Unhandled event type: {event_type}")
        return {"status": "ignored", "event_type": event_type}

def send_outreach_email(to_email: str, subject: str, body: str) -> dict:
    """Send outreach email via Resend with structured error handling."""
    if not isinstance(to_email, str) or "@" not in to_email:
        return {"status": "error", "error": f"Invalid email address: {to_email}"}
    if not isinstance(subject, str) or not subject.strip():
        return {"status": "error", "error": "Subject must be a non-empty string"}
    if not isinstance(body, str) or not body.strip():
        return {"status": "error", "error": "Body must be a non-empty string"}

    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        if not resend.api_key:
            return {"status": "error", "error": "RESEND_API_KEY not set in environment"}

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": subject,
            "html": f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{body}</pre>"
        })
        return {
            "status": "success",
            "id": response.get("id"),
            "to": to_email,
            "subject": subject,
            "sent_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        error_msg = str(e)
        print(f"  Email send error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "to": to_email,
            "subject": subject
        }

if __name__ == "__main__":
    # Test 1: Valid send
    print("Test 1: Valid email send")
    result = send_outreach_email(
        to_email="ephratawolde990@gmail.com",
        subject="Test with full error handling",
        body="This is a test email."
    )
    print("Result:", result)

    # Test 2: Invalid email
    print("\nTest 2: Invalid email")
    result = send_outreach_email("notanemail", "Test", "Body")
    print("Result:", result)

    # Test 3: Bounce event
    print("\nTest 3: Bounce webhook")
    def bounce_handler(event):
        print(f"  Bounce handler: action={event.get('action_required')}")
    register_bounce_handler(bounce_handler)

    result = handle_inbound_webhook({
        "type": "email.bounced",
        "data": {
            "email_id": "test-123",
            "from": "prospect@example.com",
            "bounce_type": "permanent"
        }
    })
    print("Result:", result)

    # Test 4: Malformed payload
    print("\nTest 4: Malformed payload")
    result = handle_inbound_webhook("not a dict")
    print("Result:", result)

    # Test 5: Missing required field
    print("\nTest 5: Missing type field")
    result = handle_inbound_webhook({"from": "someone@example.com"})
    print("Result:", result)

    # Test 6: Reply event
    print("\nTest 6: Reply webhook")
    def reply_handler(event):
        print(f"  Reply from {event['from']}: {event['body'][:50]}")
    register_reply_handler(reply_handler)

    result = handle_inbound_webhook({
        "type": "inbound",
        "data": {
            "from": "prospect@example.com",
            "subject": "Re: Engineering capacity",
            "text": "Interested, let's talk."
        }
    })
    print("Result:", result)