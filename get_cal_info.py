import requests

API_KEY = "cal_live_4479fbda50bfbfbb195205d1f0c99f4d"

response = requests.get(
    "https://api.cal.com/v2/event-types",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "cal-api-version": "2024-06-14"
    }
)

print(response.status_code)
import json
print(json.dumps(response.json(), indent=2))