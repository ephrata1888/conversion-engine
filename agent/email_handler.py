import resend
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Handler registry - downstream logic can register callbacks here
_reply_handlers = []

def register_reply_handler(handler_fn):
    """Register a callback for when an email reply is received."""
    _reply_handlers.append(handler_fn)
    print(f"  Registered reply handler: {handler_fn.__name__}")

def dispatch_reply(payload: dict):
    """Dispatch an inbound email reply to all registered handlers."""
    for handler in _reply_handlers:
        try:
            handler(payload)
        except Exception as e:
            print(f"  Handler {handler.__name__} error: {e}")

def validate_webhook_payload(payload: dict) -> tuple:
    """Validate inbound email webhook payload. Returns (is_valid, error_message)."""
    required_fields = ["from", "subject"]
    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}"
    if "@" not in payload.get("from", ""):
        return False, "Invalid email address in 'from' field"
    return True, None

def send_outreach_email(to_email: str, subject: str, body: str) -> dict:
    """Send outreach email via Resend with structured error handling."""
    if not to_email or "@" not in to_email:
        return {"status": "error", "error": f"Invalid email address: {to_email}"}
    if not subject or not body:
        return {"status": "error", "error": "Subject and body are required"}

    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": subject,
            "html": f"<pre style='font-family:sans-serif'>{body}</pre>"
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

def handle_inbound_webhook(payload: dict) -> dict:
    """Handle inbound email webhook from Resend."""
    is_valid, error = validate_webhook_payload(payload)
    if not is_valid:
        return {"status": "error", "error": error}

    event = {
        "type": "email_reply",
        "from": payload.get("from"),
        "subject": payload.get("subject"),
        "body": payload.get("text", payload.get("html", "")),
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    dispatch_reply(event)
    return {"status": "received", "event": event}

if __name__ == "__main__":
    # Test send
    result = send_outreach_email(
        to_email="ephratawolde990@gmail.com",
        subject="Test outreach with error handling",
        body="This is a test email from the conversion engine."
    )
    print("Send result:", result)

    # Test webhook handling
    def sample_handler(event):
        print(f"  Handler received: {event['from']} replied to '{event['subject']}'")

    register_reply_handler(sample_handler)

    test_payload = {
        "from": "prospect@example.com",
        "subject": "Re: Engineering capacity at DataStack AI",
        "text": "Thanks for reaching out, I'm interested."
    }
    webhook_result = handle_inbound_webhook(test_payload)
    print("Webhook result:", webhook_result)