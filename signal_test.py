from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def fetch_job_listing(company_url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(company_url)
        page.wait_for_timeout(2000)
        title = page.title()
        body_text = page.inner_text("body")[:500]
        browser.close()
        return {
            "url": company_url,
            "title": title,
            "snippet": body_text,
            "fetched_at": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    result = fetch_job_listing("https://www.builtinnyc.com/jobs")
    with open("test_job_listing.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Saved to test_job_listing.json")
    print(f"Title: {result['title']}")