import os
from dotenv import load_dotenv

load_dotenv()

STAFF_SINK = "ephratawolde990@gmail.com"
STAFF_SINK_PHONE = "+251900000000"

def is_outbound_enabled() -> bool:
    """Check if real outbound is enabled. Default is False (sink mode)."""
    val = os.getenv("TENACIOUS_OUTBOUND_ENABLED", "").strip().lower()
    return val == "true"

def gate_email(to_email: str) -> str:
    """
    Gate function for email outbound.
    Returns real address if enabled, staff sink if not.
    """
    if is_outbound_enabled():
        return to_email
    print(f"  [KILL SWITCH] Outbound disabled — routing {to_email} to staff sink")
    return STAFF_SINK

def gate_sms(to_number: str) -> str:
    """
    Gate function for SMS outbound.
    Returns real number if enabled, staff sink if not.
    """
    if is_outbound_enabled():
        return to_number
    print(f"  [KILL SWITCH] Outbound disabled — routing {to_number} to staff sink")
    return STAFF_SINK_PHONE

def gate_booking(prospect_email: str) -> str:
    """
    Gate function for Cal.com bookings.
    Returns real email if enabled, staff sink if not.
    """
    if is_outbound_enabled():
        return prospect_email
    print(f"  [KILL SWITCH] Outbound disabled — booking routed to staff sink")
    return STAFF_SINK

if __name__ == "__main__":
    print(f"Outbound enabled: {is_outbound_enabled()}")
    print(f"Email gate test: {gate_email('cto@realcompany.com')}")
    print(f"SMS gate test: {gate_sms('+1234567890')}")
    print(f"Booking gate test: {gate_booking('cto@realcompany.com')}")