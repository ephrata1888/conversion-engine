import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AT_API_KEY")
username = os.getenv("AT_USERNAME")

url = "https://api.sandbox.africastalking.com/version1/messaging"

headers = {
    "apiKey": api_key,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

data = {
    "username": username,
    "to": "+251900000000",
    "message": "Test from Conversion Engine agent"
}

response = requests.post(url, headers=headers, data=data, verify=False)
print(response.status_code)
print(response.json())