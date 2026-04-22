import json
import os
from datetime import datetime
from pathlib import Path

def load_tau2_results(results_path: str) -> dict:
    """Load tau2-bench results.json and extract key metrics."""
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    rewards = [t['reward'] for t in tasks if 'reward' in t and t.get('status') != 'infra_error']
    infra_errors = sum(1 for t in tasks if t.get('status') == 'infra_error')
    
    if not rewards:
        return None
    
    n = len(rewards)
    mean_reward = sum(rewards) / n
    
    # pass@1 — fraction of tasks with reward == 1.0
    pass_at_1 = sum(1 for r in rewards if r == 1.0) / n
    
    # 95% CI using normal approximation
    import math
    se = math.sqrt(pass_at_1 * (1 - pass_at_1) / n)
    ci_95 = 1.96 * se
    
    return {
        "n_evaluated": n,
        "n_infra_errors": infra_errors,
        "mean_reward": round(mean_reward, 4),
        "pass_at_1": round(pass_at_1, 4),
        "ci_95": round(ci_95, 4),
        "ci_lower": round(max(0, pass_at_1 - ci_95), 4),
        "ci_upper": round(min(1, pass_at_1 + ci_95), 4),
    }

def update_score_log(run_name: str, results_path: str, notes: str = ""):
    """Add a new entry to score_log.json."""
    score_log_path = Path("score_log.json")
    
    # Load existing log or start fresh
    if score_log_path.exists():
        with open(score_log_path, 'r') as f:
            log = json.load(f)
    else:
        log = {"runs": []}
    
    # Extract metrics
    metrics = load_tau2_results(results_path)
    if not metrics:
        print("No valid results found.")
        return
    
    # Add new entry
    entry = {
        "run_name": run_name,
        "timestamp": datetime.utcnow().isoformat(),
        "model": "openrouter/qwen/qwen3-235b-a22b",
        "domain": "retail",
        "notes": notes,
        **metrics
    }
    
    log["runs"].append(entry)
    
    with open(score_log_path, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"Added run '{run_name}' to score_log.json")
    print(f"  pass@1: {metrics['pass_at_1']} (95% CI: {metrics['ci_lower']} - {metrics['ci_upper']})")
    print(f"  mean reward: {metrics['mean_reward']}")
    print(f"  n evaluated: {metrics['n_evaluated']} (infra errors: {metrics['n_infra_errors']})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python score_logger.py <run_name> <results_path>")
        sys.exit(1)
    
    run_name = sys.argv[1]
    results_path = sys.argv[2]
    notes = sys.argv[3] if len(sys.argv) > 3 else ""
    
    update_score_log(run_name, results_path, notes)