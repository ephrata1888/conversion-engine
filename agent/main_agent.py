import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import handlers
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler import send_outreach_email
from sms_handler import send_sms
from hubspot_handler import create_or_update_contact
from cal_handler import get_available_slots, book_discovery_call
from enrichment_pipeline import build_hiring_signal_brief
from competitor_gap_brief import build_competitor_gap_brief

def compose_outreach_email(brief: dict, competitor_brief: dict) -> dict:
    """Compose a signal-grounded outreach email based on the hiring signal brief."""
    company = brief.get("company", {})
    signals = brief.get("signals", {})
    segment = brief.get("icp_segment", {})
    
    name = company.get("name", "")
    funding = signals.get("funding", {})
    ai_maturity = signals.get("ai_maturity", {})
    leadership = signals.get("leadership_change", {})
    
    # Build grounded opening based on signals
    opening_lines = []
    
    if funding.get("has_recent_funding"):
        rounds = funding.get("recent_rounds", [])
        if rounds:
            amount = rounds[0].get("money_raised", {}).get("value", 0)
            amount_str = f"${amount/1000000:.0f}M" if amount > 0 else "recent"
            opening_lines.append(
                f"Congratulations on your {amount_str} raise — that's a signal your engineering roadmap is about to accelerate."
            )
    
    if leadership.get("has_leadership_change"):
        hires = leadership.get("recent_hires", [])
        if hires:
            title = hires[0].get("title", "engineering leadership")
            opening_lines.append(
                f"With a new {title} recently on board, this is often when teams reassess their engineering mix and vendor relationships."
            )
    
    if not opening_lines:
        opening_lines.append(
            f"I've been looking at {name}'s engineering growth and wanted to share a quick observation."
        )
    
    # Build pitch based on segment
    segment_num = segment.get("segment", 4)
    
    if segment_num == 1:
        pitch = "Teams at your stage typically find that in-house hiring can't keep pace with the roadmap — Tenacious provides dedicated engineering squads that are operational in 2 weeks, not 3 months."
    elif segment_num == 2:
        pitch = "Tenacious helps engineering teams maintain delivery capacity while restructuring cost — replacing higher-cost roles with dedicated offshore equivalents without cutting output."
    elif segment_num == 3:
        pitch = "New engineering leaders often reassess their offshore mix in the first 90 days. Tenacious can provide a benchmark of what top-quartile teams at your stage are doing."
    else:
        if ai_maturity.get("score", 0) >= 2:
            pitch = "Tenacious has ML engineers and data platform specialists available now — project-based engagements for specific capability gaps, no long-term commitment required."
        else:
            pitch = "Tenacious can help stand up your first dedicated engineering function with a squad that matches your stack."
    
    # Add competitor gap if meaningful
    gap_line = ""
    gaps = competitor_brief.get("specific_gaps", [])
    if gaps and competitor_brief.get("maturity_gap", 0) > 0:
        gap = gaps[0]
        gap_line = f"\n\nQuick observation from your sector: {gap.get('description', '')} {gap.get('business_impact', '')}"
    
    subject = f"Engineering capacity at {name} — quick observation"
    
    body = f"""Hi,

{opening_lines[0]}

{pitch}{gap_line}

Would a 20-minute call this week make sense? I can share what we're seeing from teams at your stage and whether there's a fit.

Best,
Tenacious Consulting and Outsourcing
"""
    
    return {
        "subject": subject,
        "body": body,
        "segment": segment_num,
        "ai_maturity_score": ai_maturity.get("score", 0),
        "signal_grounded": len(opening_lines) > 0 and "observation" not in opening_lines[0]
    }

def run_prospect_pipeline(
    company_name: str,
    prospect_email: str,
    prospect_name: str,
    synthetic_path: str = None
) -> dict:
    """Run the full prospect pipeline end-to-end."""
    
    start_time = time.time()
    results = {
        "company": company_name,
        "prospect": prospect_name,
        "email": prospect_email,
        "timestamp": datetime.utcnow().isoformat(),
        "steps": {}
    }
    
    print(f"\n{'='*50}")
    print(f"Running pipeline for: {company_name}")
    print(f"{'='*50}")
    
    # Step 1: Build hiring signal brief
    print("\n[1/5] Building hiring signal brief...")
    t0 = time.time()
    brief = build_hiring_signal_brief(company_name, synthetic_path)
    results["steps"]["enrichment"] = {
        "status": "success" if "error" not in brief else "error",
        "latency_ms": int((time.time() - t0) * 1000),
        "segment": brief.get("icp_segment", {}).get("segment"),
        "ai_maturity": brief.get("signals", {}).get("ai_maturity", {}).get("score")
    }
    print(f"  Segment: {brief.get('icp_segment', {}).get('name')}")
    print(f"  AI Maturity: {brief.get('signals', {}).get('ai_maturity', {}).get('score')}")
    
    # Step 2: Build competitor gap brief
    print("\n[2/5] Building competitor gap brief...")
    t0 = time.time()
    company_data = brief.get("company", {})
    comp_brief = build_competitor_gap_brief(
        {"name": company_name, "industries": company_data.get("industries", "[]")}
    )
    results["steps"]["competitor_gap"] = {
        "status": "success",
        "latency_ms": int((time.time() - t0) * 1000),
        "peers_analyzed": comp_brief.get("sector_peers_analyzed", 0),
        "gaps_found": len(comp_brief.get("specific_gaps", []))
    }
    
    # Step 3: Compose outreach email
    print("\n[3/5] Composing outreach email...")
    t0 = time.time()
    email_content = compose_outreach_email(brief, comp_brief)
    results["steps"]["email_composition"] = {
        "status": "success",
        "latency_ms": int((time.time() - t0) * 1000),
        "signal_grounded": email_content.get("signal_grounded"),
        "segment": email_content.get("segment")
    }
    print(f"  Subject: {email_content['subject']}")
    
    # Step 4: Create HubSpot contact
    print("\n[4/5] Creating HubSpot contact...")
    t0 = time.time()
    hubspot_result = create_or_update_contact(
        email=prospect_email,
        firstname=prospect_name.split()[0],
        lastname=prospect_name.split()[-1] if len(prospect_name.split()) > 1 else "",
        company=company_name,
        jobtitle=brief.get("icp_segment", {}).get("name", ""),
    )
    results["steps"]["hubspot"] = {
        "status": "success" if hubspot_result else "error",
        "latency_ms": int((time.time() - t0) * 1000),
        "contact_id": hubspot_result.get("id") if hubspot_result else None
    }
    
    # Step 5: Send outreach email
    print("\n[5/5] Sending outreach email...")
    t0 = time.time()
    email_result = send_outreach_email(
        to_email=prospect_email,
        subject=email_content["subject"],
        body=email_content["body"]
    )
    if email_result:
        print(f"  Email sent successfully: {email_result.get('id', 'unknown')}")
    else:
        print(f"  Email failed")
    results["steps"]["email_sent"] = {
        "status": "success" if email_result else "error",
        "latency_ms": int((time.time() - t0) * 1000)
    }
    
    # Total latency
    results["total_latency_ms"] = int((time.time() - start_time) * 1000)
    results["hiring_signal_brief"] = brief
    results["competitor_gap_brief"] = comp_brief
    results["email_content"] = email_content
    
    print(f"\n{'='*50}")
    print(f"Pipeline complete in {results['total_latency_ms']}ms")
    print(f"{'='*50}")
    
    return results

if __name__ == "__main__":
    result = run_prospect_pipeline(
        company_name="DataStack AI",
        prospect_email="ephratawolde990@gmail.com",
        prospect_name="Jordan Smith",
        synthetic_path="data/synthetic_prospect.json"
    )
    
    os.makedirs("data", exist_ok=True)
    with open("data/pipeline_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\nFull result saved to data/pipeline_result.json")