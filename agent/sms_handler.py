import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_sms(to_number: str, message: str) -> dict:
    """Send SMS via Africa's Talking sandbox."""
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
        return response.json()
    except Exception as e:
        print(f"SMS error: {e}")
        return None

if __name__ == "__main__":
    result = send_sms("+251900000000", "Test SMS from conversion engine")
    print(result)