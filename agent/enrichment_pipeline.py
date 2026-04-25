import csv
import json
import re
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def load_crunchbase_company(company_name: str) -> dict:
    """Find a company in the Crunchbase CSV by name."""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "crunchbase_sample.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
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
def check_layoffs_fyi(company_name: str, days: int = 120) -> dict:
    """Check layoffs.fyi CSV for layoff events in last N days."""
    import csv as csv_module
    from datetime import timezone
    
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "layoffs_2026.csv"
    )
    
    if not os.path.exists(csv_path):
        return {"has_recent_layoffs": False, "recent_layoffs": [], 
                "source": "layoffs_fyi", "error": "CSV not found"}
    
    cutoff = datetime.now() - timedelta(days=days)
    recent_layoffs = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            if company_name.lower() in row.get("Company", "").lower():
                date_str = row.get("Date", "")
                if date_str:
                    try:
                        layoff_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                        if layoff_date > cutoff:
                            recent_layoffs.append({
                                "date": date_str,
                                "count": row.get("Laid_Off_Count", ""),
                                "percentage": row.get("Percentage", ""),
                                "source": row.get("Source", ""),
                                "stage": row.get("Stage", "")
                            })
                    except:
                        pass
    
    return {
        "has_recent_layoffs": len(recent_layoffs) > 0,
        "recent_layoffs": recent_layoffs,
        "source": "layoffs_fyi"
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

    tech = parse_json_field(company.get("builtwith_tech", "[]"))
    ai_tech_keywords = ["tensorflow", "pytorch", "databricks", "snowflake",
                        "dbt", "weights", "ray", "hugging", "openai"]
    tech_names = [t.get("name", "").lower() for t in tech]
    ai_tech_found = [t for t in tech_names if any(k in t for k in ai_tech_keywords)]

    if ai_tech_found:
        score += 1
        signals.append(f"AI/ML tech stack: {ai_tech_found}")

    employees = parse_json_field(company.get("current_employees", "[]"))
    ai_titles = ["ai", "ml", "machine learning", "data science",
                 "artificial intelligence", "chief scientist"]
    ai_leaders = [e for e in employees
                  if any(t in e.get("title", "").lower() for t in ai_titles)]

    if ai_leaders:
        score += 1
        signals.append(f"AI leadership: {[e.get('title') for e in ai_leaders]}")

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
                          layoffs: dict, leadership: dict,
                          ai_maturity: dict = None) -> dict:
    """Classify prospect into one of 4 ICP segments."""
    num_employees = company.get("num_employees", "")

    if funding["has_recent_funding"] and not layoffs["has_recent_layoffs"]:
        if num_employees in ["1-10", "11-50", "51-100", "101-250"]:
            return {
                "segment": 1,
                "name": "Recently-funded Series A/B startup",
                "confidence": 0.8,
                "reason": f"Recent funding + {num_employees} employees"
            }

    if leadership["has_leadership_change"]:
        return {
            "segment": 3,
            "name": "Engineering-leadership transition",
            "confidence": 0.85,
            "reason": f"New CTO/VP Eng: {leadership['recent_hires']}"
        }

    if layoffs["has_recent_layoffs"]:
        if num_employees in ["251-500", "501-1000", "1001-5000"]:
            return {
                "segment": 2,
                "name": "Mid-market platforms restructuring cost",
                "confidence": 0.75,
                "reason": f"Recent layoffs + {num_employees} employees"
            }

    # Segment 4 — only if AI maturity >= 2
    ai_score = ai_maturity.get("score", 0) if ai_maturity else 0
    if ai_score >= 2:
        return {
            "segment": 4,
            "name": "Specialized capability gaps",
            "confidence": 0.5,
            "reason": "No strong signal for segments 1-3, AI maturity >= 2"
        }
    
    # Abstain — no segment has sufficient confidence
    return {
        "segment": "abstain",
        "name": "No segment match",
        "confidence": 0.0,
        "reason": "No qualifying signal found for any segment. Generic exploratory email only."
    }

def check_robots_txt(domain: str, path: str = "/careers") -> bool:
    """Check if robots.txt allows scraping the given path."""
    try:
        import urllib.robotparser
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"https://{domain}/robots.txt")
        rp.read()
        return rp.can_fetch("TRP1-Week10-Research", f"https://{domain}{path}")
    except:
        return True  # If robots.txt unreachable, assume allowed

def scrape_job_posts(website: str) -> list:
    """Scrape job titles from company careers page."""
    if not website:
        return []

    # Extract domain for robots.txt check
    domain = website.replace("https://", "").replace("http://", "").split("/")[0]

    careers_urls = [
        website.rstrip("/") + "/careers",
        website.rstrip("/") + "/jobs",
        website.rstrip("/") + "/about/careers"
    ]

    job_titles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Set user agent per data handling policy Rule 4
        context = browser.new_context(
            user_agent="TRP1-Week10-Research (trainee@trp1.example)"
        )
        page = context.new_page()

        for url in careers_urls:
            try:
                # Check robots.txt before scraping
                path = "/" + "/".join(url.split("/")[3:])
                if not check_robots_txt(domain, path):
                    print(f"  robots.txt disallows scraping {url} — skipping")
                    continue

                page.goto(url, timeout=10000)
                page.wait_for_timeout(2000)  # Rate limit: 2s between requests

                # Check for captcha
                page_text = page.inner_text("body")[:3000]
                if any(w in page_text.lower() for w in ["captcha", "verify you are human", "i am not a robot"]):
                    print(f"  Captcha detected at {url} — logging as rate_limited")
                    break

                lines = page_text.split("\n")
                for line in lines:
                    line = line.strip()
                    if (10 < len(line) < 100 and
                        any(w in line.lower() for w in
                            ["engineer", "developer", "manager", "analyst",
                             "scientist", "architect", "lead", "director"])):
                        job_titles.append(line)

                if job_titles:
                    break

            except Exception as e:
                continue

        browser.close()

    return job_titles[:20]

def load_synthetic_or_crunchbase(company_name: str, synthetic_path: str = None) -> dict:
    """Load company from synthetic JSON or Crunchbase CSV."""
    if synthetic_path and os.path.exists(synthetic_path):
        with open(synthetic_path, "r") as f:
            return json.load(f)
    return load_crunchbase_company(company_name)

def load_job_posts_from_snapshot(company_id: str) -> tuple:
    """Load job posts from frozen April 2026 snapshot."""
    snapshot_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "job_posts_snapshot_2026_04_01.json"
    )
    if os.path.exists(snapshot_path):
        with open(snapshot_path, "r") as f:
            snapshot = json.load(f)
        company_data = snapshot.get("companies", {}).get(company_id, {})
        if company_data:
            return company_data.get("roles", []), company_data
    return [], {}

def build_hiring_signal_brief(company_name: str, synthetic_path: str = None) -> dict:
    """Build complete hiring signal brief for a prospect."""
    print(f"Building hiring signal brief for: {company_name}")

    company = load_synthetic_or_crunchbase(company_name, synthetic_path)
    if not company:
        return {"error": f"Company '{company_name}' not found"}

    print(f"  Found: {company.get('name', company_name)} ({company.get('country_code', 'unknown')})")

    funding = check_recent_funding(company)
    layoffs = check_layoffs(company)
    
    # Supplement with layoffs.fyi direct check
    layoffs_fyi = check_layoffs_fyi(company.get("name", company_name))
    if layoffs_fyi["has_recent_layoffs"] and not layoffs["has_recent_layoffs"]:
        layoffs = layoffs_fyi
        print(f"  Layoff signal from layoffs.fyi: {len(layoffs_fyi['recent_layoffs'])} event(s)")
    leadership = check_leadership_change(company)
    # Load job posts from frozen snapshot
    job_posts, job_post_data = load_job_posts_from_snapshot(
        company.get("id", company_name.lower().replace(" ", "-"))
    )
    ai_maturity = score_ai_maturity(company, job_posts)
    segment = classify_icp_segment(company, funding, layoffs, leadership, ai_maturity)

    brief = {
        "company": {
            "name": company.get("name", ""),
            "crunchbase_id": company.get("id", ""),
            "uuid": company.get("uuid", ""),
            "about": company.get("about", ""),
            "website": company.get("website", ""),
            "employees": company.get("num_employees", "unknown"),
            "country": company.get("country_code", "unknown"),
            "industries": company.get("industries", ""),
        },
        "signals": {
            "funding": {
                **funding,
                "confidence": "high" if funding["has_recent_funding"] and len(funding["recent_rounds"]) > 1 else "medium" if funding["has_recent_funding"] else "low",
                "confidence_reason": f"{len(funding['recent_rounds'])} round(s) found in last 180 days"
            },
            "layoffs": {
                **layoffs,
                "confidence": "high" if layoffs["has_recent_layoffs"] else "low",
                "confidence_reason": f"{len(layoffs['recent_layoffs'])} layoff event(s) found in last 120 days"
            },
            "leadership_change": {
                **leadership,
                "confidence": "high" if leadership["has_leadership_change"] else "low",
                "confidence_reason": f"{len(leadership['recent_hires'])} leadership hire(s) found in last 90 days"
            },
            "ai_maturity": ai_maturity,
            "job_posts": {
                "titles": job_posts,
                "count": len(job_posts),
                "open_roles_today": job_post_data.get("open_roles_today", len(job_posts)),
                "open_roles_60_days_ago": job_post_data.get("open_roles_60_days_ago", 0),
                "velocity_label": "doubled" if job_post_data.get("open_roles_today", 0) >= 2 * max(1, job_post_data.get("open_roles_60_days_ago", 1)) else "increased_modestly" if job_posts else "insufficient_signal",
                "confidence": "high" if len(job_posts) >= 5 else "medium" if len(job_posts) >= 2 else "low",
                "confidence_reason": f"{len(job_posts)} engineering job posts found"
            }
        },
        "icp_segment": segment,
        "enriched_at": datetime.now(timezone.utc).isoformat()
    }
    # Honesty flags
    honesty_flags = []
    if len(job_posts) < 5:
        honesty_flags.append("weak_hiring_velocity_signal")
    if ai_maturity["score"] >= 2 and ai_maturity["confidence"] == "low":
        honesty_flags.append("weak_ai_maturity_signal")
    if funding["has_recent_funding"] and layoffs["has_recent_layoffs"]:
        honesty_flags.append("conflicting_segment_signals")
        honesty_flags.append("layoff_overrides_funding")
    if not job_posts:
        honesty_flags.append("tech_stack_inferred_not_confirmed")
    brief["honesty_flags"] = honesty_flags

    # Data sources checked
    brief["data_sources_checked"] = [
        {"source": "crunchbase_odm", "status": "success",
         "note": "Static July 2024 snapshot", "fetched_at": company.get("timestamp", "2024-07-03")},
        {"source": "layoffs_fyi", "status": "success" if not layoffs.get("error") else "error",
         "fetched_at": datetime.now(timezone.utc).isoformat()},
        {"source": "job_posts_snapshot", "status": "success" if job_posts else "no_data",
         "note": "Frozen April 2026 snapshot", "fetched_at": "2026-04-01T00:00:00Z"}
    ]

    # Bench to brief match
    from bench_policy import check_bench_capacity, load_bench_summary
    bench = load_bench_summary()
    tech_raw = parse_json_field(company.get("builtwith_tech", "[]"))
    required_stacks = list(set([
        stack for t in tech_raw
        for stack in ["python", "go", "data", "ml", "infra"]
        if stack in t.get("name", "").lower()
    ]))
    bench_gaps = [s for s in required_stacks
                  if not check_bench_capacity(s, 1, bench)["can_commit"]]
    brief["bench_to_brief_match"] = {
        "required_stacks": required_stacks,
        "bench_available": len(bench_gaps) == 0,
        "gaps": bench_gaps
    }


    return brief

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_prospect.json")
    brief = build_hiring_signal_brief("DataStack AI", synthetic_path=data_path)

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "hiring_signal_brief.json")
    with open(output_path, "w") as f:
        json.dump(brief, f, indent=2)

    print("\nHiring Signal Brief:")
    print(json.dumps(brief, indent=2))
    print(f"\nSaved to {output_path}")