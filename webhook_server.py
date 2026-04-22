from fastapi import FastAPI, Request
import json
from datetime import datetime

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}

@app.post("/webhooks/email")
async def email_webhook(request: Request):
    data = await request.json()
    print(f"Email reply received: {json.dumps(data, indent=2)}")
    return {"status": "received"}

@app.post("/webhooks/sms")
async def sms_webhook(request: Request):
    data = await request.form()
    print(f"SMS received: {dict(data)}")
    return {"status": "received"}

@app.post("/webhooks/calendar")
async def calendar_webhook(request: Request):
    data = await request.json()
    print(f"Calendar event: {json.dumps(data, indent=2)}")
    return {"status": "received"}

@app.post("/webhooks/hubspot")
async def hubspot_webhook(request: Request):
    data = await request.json()
    print(f"HubSpot event: {json.dumps(data, indent=2)}")
    return {"status": "received"}