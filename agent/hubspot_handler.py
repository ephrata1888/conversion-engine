from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
import os
from dotenv import load_dotenv

load_dotenv()

client = HubSpot(access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"))

def create_or_update_contact(email: str, firstname: str, lastname: str,
                              company: str, jobtitle: str = "") -> dict:
    """Create or update a HubSpot contact."""
    try:
        contact = SimplePublicObjectInputForCreate(
            properties={
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "company": company,
                "jobtitle": jobtitle
            }
        )
        response = client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=contact
        )
        print(f"  HubSpot contact created: {response.id}")
        return {"id": response.id, "properties": response.properties}
    except Exception as e:
        error_str = str(e)
        if "409" in error_str or "CONFLICT" in error_str:
            # Contact exists - extract ID from error message
            import re
            match = re.search(r"Existing ID: (\d+)", error_str)
            existing_id = match.group(1) if match else "unknown"
            print(f"  HubSpot contact already exists: {existing_id}")
            return {"id": existing_id, "status": "existing"}
        print(f"  HubSpot error: {e}")
        return None

if __name__ == "__main__":
    result = create_or_update_contact(
        email="test2@example.com",
        firstname="Test",
        lastname="Contact",
        company="Test Corp",
        jobtitle="CTO"
    )
    print(result)