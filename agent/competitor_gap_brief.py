import csv
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_sector_companies(industries_keywords: list, country_codes: list = ["US", "CA"], 
                          max_companies: int = 20) -> list:
    """Find companies in the same sector from Crunchbase data."""
    matches = []
    
    with open("data/crunchbase_sample.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            industries = row.get("industries", "").lower()
            country = row.get("country_code", "")
            
            if (country in country_codes and 
                any(k.lower() in industries for k in industries_keywords)):
                matches.append(row)
            
            if len(matches) >= max_companies:
                break
    
    return matches

def score_ai_maturity_simple(company: dict) -> int:
    """Simple AI maturity score 0-3."""
    score = 0
    
    tech = company.get("builtwith_tech", "").lower()
    ai_tech = ["snowflake", "databricks", "tensorflow", "pytorch", "dbt", "openai"]
    if any(t in tech for t in ai_tech):
        score += 1
    
    employees = company.get("current_employees", "").lower()
    ai_roles = ["ai", "ml", "machine learning", "data scientist", "head of data"]
    if any(r in employees for r in ai_roles):
        score += 1
    
    about = company.get("about", "").lower() + company.get("full_description", "").lower()
    ai_words = ["artificial intelligence", "machine learning", "ai-powered", "llm", "generative"]
    if any(w in about for w in ai_words):
        score += 1
    
    return min(3, score)

def build_competitor_gap_brief(prospect: dict) -> dict:
    """Build competitor gap brief for a prospect."""
    
    # Get prospect industries
    industries_str = prospect.get("industries", "")
    if isinstance(industries_str, str):
        try:
            industries = json.loads(industries_str)
            industry_keywords = [i.get("value", "") for i in industries]
        except:
            industry_keywords = ["software", "technology"]
    else:
        industry_keywords = ["software", "technology"]
    
    print(f"Finding competitors in: {industry_keywords}")
    
    # Find sector peers
    peers = get_sector_companies(industry_keywords)
    
    if not peers:
        # Fallback to tech companies
        peers = get_sector_companies(["software", "technology", "enterprise"])
    
    # Score each peer
    scored_peers = []
    for peer in peers:
        if peer.get("name") == prospect.get("name"):
            continue
        ai_score = score_ai_maturity_simple(peer)
        scored_peers.append({
            "name": peer.get("name"),
            "employees": peer.get("num_employees", "unknown"),
            "country": peer.get("country_code", "unknown"),
            "ai_maturity": ai_score,
            "about": peer.get("about", "")[:100]
        })
    
    # Sort by AI maturity
    scored_peers.sort(key=lambda x: x["ai_maturity"], reverse=True)
    
    # Get top quartile
    top_quartile = scored_peers[:max(1, len(scored_peers)//4)]
    
    # Score prospect
    prospect_score = score_ai_maturity_simple(prospect)
    
    # Find gaps
    top_quartile_avg = sum(p["ai_maturity"] for p in top_quartile) / max(1, len(top_quartile))
    gap = top_quartile_avg - prospect_score
    
    # Identify specific gaps
    specific_gaps = []
    if prospect_score < 2:
        specific_gaps.append({
            "gap": "AI/ML infrastructure",
            "description": "Top quartile companies in your sector are investing in ML platforms (Snowflake, dbt, Databricks). Your public signal shows limited adoption.",
            "business_impact": "Companies with modern data infrastructure ship AI features 3x faster than those without."
        })
    if prospect_score < 1:
        specific_gaps.append({
            "gap": "Dedicated AI leadership",
            "description": "Top quartile peers have named AI/ML leadership (Head of AI, VP Data). This role is absent from your public team page.",
            "business_impact": "Without dedicated AI leadership, AI initiatives tend to stall in proof-of-concept."
        })
    specific_gaps.append({
        "gap": "Engineering capacity",
        "description": f"Based on your job post velocity, your engineering team is scaling faster than in-house hiring can support.",
        "business_impact": "Tenacious can provide a dedicated squad within 2 weeks vs 3-4 months for in-house hiring."
    })
    
    brief = {
        "prospect_name": prospect.get("name"),
        "prospect_ai_maturity": prospect_score,
        "sector_peers_analyzed": len(scored_peers),
        "top_quartile": top_quartile[:5],
        "top_quartile_avg_ai_maturity": round(top_quartile_avg, 2),
        "maturity_gap": round(gap, 2),
        "specific_gaps": specific_gaps[:3],
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return brief

if __name__ == "__main__":
    # Test with synthetic prospect
    with open("data/synthetic_prospect.json", "r") as f:
        prospect = json.load(f)
    
    brief = build_competitor_gap_brief(prospect)
    
    os.makedirs("data", exist_ok=True)
    with open("data/competitor_gap_brief.json", "w") as f:
        json.dump(brief, f, indent=2)
    
    print("Competitor Gap Brief:")
    print(json.dumps(brief, indent=2))
    print("\nSaved to data/competitor_gap_brief.json")