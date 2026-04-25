"""
Start webhook server with ngrok tunnel.
Run this before starting the demo.
"""
import subprocess
import sys
import os

# Start ngrok tunnel
from pyngrok import ngrok, conf
conf.get_default().ngrok_path = r"C:\Users\Ephi\conversion-engine\ngrok.exe"
tunnel = ngrok.connect(8000)
public_url = tunnel.public_url
https_url = public_url.replace("http://", "https://")

print(f"\n{'='*50}")
print(f"Ngrok URL: {https_url}")
print(f"{'='*50}")
print(f"\nRegister this URL in Resend webhooks:")
print(f"  {https_url}/webhooks/email")
print(f"\nRegister this URL in Africa's Talking:")
print(f"  {https_url}/webhooks/sms")
print(f"\nRegister this URL in Cal.com:")
print(f"  {https_url}/webhooks/calendar")
print(f"\n{'='*50}")
print("Starting FastAPI server on port 8000...")
print("Press Ctrl+C to stop")
print(f"{'='*50}\n")

# Start uvicorn
os.system(f"{sys.executable} -m uvicorn webhook_server:app --host 0.0.0.0 --port 8000 --reload")