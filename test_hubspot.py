from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
import os
from dotenv import load_dotenv

load_dotenv()

client = HubSpot(access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"))

# Create a test contact
contact = SimplePublicObjectInputForCreate(
    properties={
        "firstname": "Test",
        "lastname": "Prospect",
        "email": "test.prospect@example.com",
        "company": "Acme Corp",
        "jobtitle": "CTO"
    }
)

response = client.crm.contacts.basic_api.create(
    simple_public_object_input_for_create=contact
)

print(f"Contact created! ID: {response.id}")
print(f"Properties: {response.properties}")