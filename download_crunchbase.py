import requests
import os

url = "https://raw.githubusercontent.com/luminati-io/Crunchbase-dataset-samples/main/crunchbase-companies-information.csv"

print("Downloading Crunchbase CSV...")
response = requests.get(url, timeout=120)

if response.status_code == 200:
    os.makedirs("data", exist_ok=True)
    with open("data/crunchbase_sample.csv", "wb") as f:
        f.write(response.content)
    print(f"Downloaded {len(response.content)} bytes")
    print("Saved to data/crunchbase_sample.csv")
else:
    print(f"Failed: {response.status_code}")