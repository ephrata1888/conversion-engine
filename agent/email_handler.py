import resend
import os
from dotenv import load_dotenv

load_dotenv()

def send_outreach_email(to_email: str, subject: str, body: str) -> dict:
    """Send outreach email via Resend."""
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": subject,
            "html": f"<pre>{body}</pre>"
        })
        return response
    except Exception as e:
        print(f"Email error: {e}")
        return None

if __name__ == "__main__":
    result = send_outreach_email(
        to_email="ephratawolde990@gmail.com",
        subject="Test outreach",
        body="This is a test email from the conversion engine."
    )
    print(result)