import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Default bench summary - will be replaced by seed repo bench_summary.json
DEFAULT_BENCH = {
    "last_updated": "2026-04-23",
    "available_engineers": {
        "python": 4,
        "data": 3,
        "ml": 2,
        "go": 1,
        "infra": 2,
        "frontend": 1
    },
    "notes": "Placeholder bench summary - replace with real bench_summary.json from seed repo"
}

def load_bench_summary(path: str = None) -> dict:
    """Load bench summary from file or use default."""
    if path and os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    
    bench_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "bench_summary.json"
    )
    if os.path.exists(bench_path):
        with open(bench_path, "r") as f:
            return json.load(f)
    
    return DEFAULT_BENCH

def check_bench_capacity(stack: str, count: int = 1, bench: dict = None) -> dict:
    """
    Hard constraint: check bench before any capacity commitment.
    Returns available/unavailable/unknown with evidence.
    
    This is the core mechanism for bench-gated commitment policy.
    Agent MUST call this before responding to any capacity question.
    """
    if bench is None:
        bench = load_bench_summary()
    
    if not bench:
        return {
            "status": "unknown",
            "action": "route_to_human",
            "message": "Bench summary not loaded — routing to delivery lead for capacity confirmation",
            "can_commit": False
        }
    
    stack_lower = stack.lower().strip()
    available = bench.get("available_engineers", {})
    
    # Find matching stack
    matched_stack = None
    matched_count = 0
    for key, val in available.items():
        if key in stack_lower or stack_lower in key:
            matched_stack = key
            matched_count = val
            break
    
    if matched_stack is None:
        return {
            "status": "unknown",
            "action": "route_to_human",
            "message": f"Stack '{stack}' not found in bench summary — routing to delivery lead",
            "can_commit": False,
            "bench_updated": bench.get("last_updated", "unknown")
        }
    
    if matched_count >= count:
        return {
            "status": "available",
            "action": "can_confirm",
            "message": f"Bench shows {matched_count} {matched_stack} engineer(s) available as of {bench.get('last_updated', 'unknown')}",
            "can_commit": True,
            "available_count": matched_count,
            "requested_count": count,
            "bench_updated": bench.get("last_updated", "unknown")
        }
    else:
        return {
            "status": "unavailable",
            "action": "route_to_human",
            "message": f"Bench shows only {matched_count} {matched_stack} engineer(s) — requested {count} — routing to delivery lead",
            "can_commit": False,
            "available_count": matched_count,
            "requested_count": count,
            "bench_updated": bench.get("last_updated", "unknown")
        }

def get_safe_capacity_response(stack: str, count: int = 1, bench: dict = None) -> str:
    """
    Generate a safe capacity response based on bench check.
    Never commits to capacity the bench does not show.
    """
    result = check_bench_capacity(stack, count, bench)
    
    if result["can_commit"]:
        return (
            f"Based on our current bench, we have {result['available_count']} "
            f"{stack} engineers available. I'd recommend a quick call with our "
            f"delivery lead to confirm fit and timeline — would that work for you?"
        )
    else:
        return (
            f"Rather than give you a number I can't verify, let me connect you "
            f"directly with our delivery lead who can confirm current availability "
            f"for {stack} engineers. Can I book a 20-minute call this week?"
        )

def generate_bench_summary():
    """Generate a sample bench_summary.json for testing."""
    bench = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "available_engineers": {
            "python": 4,
            "data": 3,
            "ml": 2,
            "go": 1,
            "infra": 2,
            "frontend": 1,
            "java": 0,
            "rust": 0
        },
        "notes": "Sample bench summary for testing. Replace with real data from Tenacious."
    }
    
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "bench_summary.json"
    )
    with open(path, "w") as f:
        json.dump(bench, f, indent=2)
    print(f"Bench summary saved to {path}")
    return bench

if __name__ == "__main__":
    # Generate sample bench
    bench = generate_bench_summary()
    print("\nBench summary:", json.dumps(bench, indent=2))
    
    # Test cases
    print("\n--- Bench Policy Tests ---")
    
    tests = [
        ("python", 2),   # should be available
        ("python", 6),   # should be unavailable
        ("ml", 1),       # should be available
        ("java", 1),     # should be unavailable
        ("rust", 1),     # should be unavailable
        ("blockchain", 1) # should be unknown
    ]
    
    for stack, count in tests:
        result = check_bench_capacity(stack, count, bench)
        print(f"\n{stack} x{count}: {result['status'].upper()} — {result['message']}")
        print(f"  Safe response: {get_safe_capacity_response(stack, count, bench)[:100]}...")