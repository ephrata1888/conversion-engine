import csv
import json
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def load_crunchbase_company(company_name: str) -> dict:
    """Find a company in the Crunchbase CSV by name."""
    with open("data/crunchbase_sample.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if company_name.lower() in row["name"].lower():
                return row
    return None

def parse_json_field(field_str: str) -> list:
    """Safely parse a JSON field from CSV."""
    if not field_str or field_str == "null":
        return []
    try:
        return json.loads(field_str)
    except:
        return []

def check_recent_funding(company: dict, days: int = 180) -> dict:
    """Check if company has funding in last N days."""
    funding_rounds = parse_json_field(company.get("funding_rounds_list", "[]"))
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_rounds = []
    for round in funding_rounds:
        announced = round.get("announced_on", "")
        if announced:
            try:
                round_date = datetime.strptime(announced[:10], "%Y-%m-%d")
                if round_date > cutoff:
                    recent_rounds.append(round)
            except:
                pass
    
    return {
        "has_recent_funding": len(recent_rounds) > 0,
        "recent_rounds": recent_rounds,
        "total_rounds": len(funding_rounds)
    }

def check_layoffs(company: dict, days: int = 120) -> dict:
    """Check if company had layoffs in last N days."""
    layoffs = parse_json_field(company.get("layoff", "[]"))
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_layoffs = []
    for layoff in layoffs:
        date_str = layoff.get("date", "")
        if date_str:
            try:
                layoff_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if layoff_date > cutoff:
                    recent_layoffs.append(layoff)
            except:
                pass
    
    return {
        "has_recent_layoffs": len(recent_layoffs) > 0,
        "recent_layoffs": recent_layoffs
    }

def check_leadership_change(company: dict, days: int = 90) -> dict:
    """Check for new CTO/VP Engineering in last N days."""
    leadership_hires = parse_json_field(company.get("leadership_hire", "[]"))
    cutoff = datetime.now() - timedelta(days=days)
    
    relevant_titles = ["cto", "vp engineering", "vp of engineering", 
                       "chief technology", "head of engineering"]
    
    recent_leadership = []
    for hire in leadership_hires:
        title = hire.get("title", "").lower()
        date_str = hire.get("date", "")
        if any(t in title for t in relevant_titles) and date_str:
            try:
                hire_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if hire_date > cutoff:
                    recent_leadership.append(hire)
            except:
                pass
    
    return {
        "has_leadership_change": len(recent_leadership) > 0,
        "recent_hires": recent_leadership
    }

def score_ai_maturity(company: dict, job_posts: list = []) -> dict:
    """Score AI maturity 0-3 from public signals."""
    score = 0
    signals = []
    
    # Check tech stack for AI/ML tools
    tech = parse_json_field(company.get("builtwith_tech", "[]"))
    ai_tech_keywords = ["tensorflow", "pytorch", "databricks", "snowflake", 
                        "dbt", "weights", "ray", "hugging", "openai"]
    tech_names = [t.get("name", "").lower() for t in tech]
    ai_tech_found = [t for t in tech_names if any(k in t for k in ai_tech_keywords)]
    
    if ai_tech_found:
        score += 1
        signals.append(f"AI/ML tech stack: {ai_tech_found}")
    
    # Check current employees for AI leadership
    employees = parse_json_field(company.get("current_employees", "[]"))
    ai_titles = ["ai", "ml", "machine learning", "data science", 
                 "artificial intelligence", "chief scientist"]
    ai_leaders = [e for e in employees 
                  if any(t in e.get("title", "").lower() for t in ai_titles)]
    
    if ai_leaders:
        score += 1
        signals.append(f"AI leadership: {[e.get('title') for e in ai_leaders]}")
    
    # Check job posts for AI roles
    ai_job_keywords = ["ml engineer", "machine learning", "ai engineer", 
                       "llm", "applied scientist", "data platform"]
    ai_jobs = [j for j in job_posts 
               if any(k in j.lower() for k in ai_job_keywords)]
    
    if len(ai_jobs) >= 2:
        score += 1
        signals.append(f"AI job posts: {len(ai_jobs)} open roles")
    elif len(ai_jobs) == 1:
        score += 0.5
        signals.append(f"AI job posts: 1 open role")
    
    # Check about/description for AI mentions
    about = company.get("about", "").lower() + company.get("full_description", "").lower()
    ai_keywords = ["artificial intelligence", "machine learning", "ai-powered", 
                   "deep learning", "neural network", "llm", "generative ai"]
    ai_mentions = [k for k in ai_keywords if k in about]
    
    if ai_mentions:
        score += 0.5
        signals.append(f"AI in description: {ai_mentions}")
    
    final_score = min(3, int(score))
    confidence = "high" if len(signals) >= 3 else "medium" if len(signals) >= 2 else "low"
    
    return {
        "score": final_score,
        "confidence": confidence,
        "signals": signals
    }

def classify_icp_segment(company: dict, funding: dict, 
                          layoffs: dict, leadership: dict) -> dict:
    """Classify prospect into one of 4 ICP segments."""
    num_employees = company.get("num_employees", "")
    
    # Segment 1: Recently funded Series A/B startup
    if funding["has_recent_funding"] and not layoffs["has_recent_layoffs"]:
        if num_employees in ["1-10", "11-50", "51-100", "101-250"]:
            return {
                "segment": 1,
                "name": "Recently-funded Series A/B startup",
                "confidence": 0.8,
                "reason": f"Recent funding + {num_employees} employees"
            }
    
    # Segment 3: Leadership transition (check first - narrow window)
    if leadership["has_leadership_change"]:
        return {
            "segment": 3,
            "name": "Engineering-leadership transition",
            "confidence": 0.85,
            "reason": f"New CTO/VP Eng: {leadership['recent_hires']}"
        }
    
    # Segment 2: Mid-market restructuring
    if layoffs["has_recent_layoffs"]:
        if num_employees in ["251-500", "501-1000", "1001-5000"]:
            return {
                "segment": 2,
                "name": "Mid-market platforms restructuring cost",
                "confidence": 0.75,
                "reason": f"Recent layoffs + {num_employees} employees"
            }
    
    # Segment 4: Capability gap (needs AI maturity >= 2)
    return {
        "segment": 4,
        "name": "Specialized capability gaps",
        "confidence": 0.5,
        "reason": "No strong signal for segments 1-3"
    }

def build_hiring_signal_brief(company_name: str, synthetic_path: str = None) -> dict:
    """Build complete hiring signal brief for a prospect."""
    print(f"Building hiring signal brief for: {company_name}")
    
    # Step 1: Get Crunchbase data
    if synthetic_path and os.path.exists(synthetic_path):
        with open(synthetic_path, "r") as f:
            company = json.load(f)
    else:
        company = load_crunchbase_company(company_name)
    if not company:
        return {"error": f"Company '{company_name}' not found in Crunchbase data"}
    
    print(f"  Found: {company['name']} ({company.get('country_code', 'unknown')})")
    
    # Step 2: Check signals
    funding = check_recent_funding(company)
    layoffs = check_layoffs(company)
    leadership = check_leadership_change(company)
    ai_maturity = score_ai_maturity(company)
    
    # Step 3: Classify ICP segment
    segment = classify_icp_segment(company, funding, layoffs, leadership)
    
    # Step 4: Build brief
    brief = {
        "company": {
            "name": company["name"],
            "crunchbase_id": company["id"],
            "uuid": company["uuid"],
            "about": company.get("about", ""),
            "website": company.get("website", ""),
            "employees": company.get("num_employees", "unknown"),
            "country": company.get("country_code", "unknown"),
            "industries": company.get("industries", ""),
        },
        "signals": {
            "funding": funding,
            "layoffs": layoffs,
            "leadership_change": leadership,
            "ai_maturity": ai_maturity
        },
        "icp_segment": segment,
        "enriched_at": datetime.utcnow().isoformat()
    }
    
    return brief

if __name__ == "__main__":
    # Test with a company from the dataset
    brief = build_hiring_signal_brief("Winder Research")
    
    os.makedirs("data", exist_ok=True)
    with open("data/hiring_signal_brief.json", "w") as f:
        json.dump(brief, f, indent=2)
    
    print("\nHiring Signal Brief:")
    print(json.dumps(brief, indent=2))
    print("\nSaved to data/hiring_signal_brief.json")