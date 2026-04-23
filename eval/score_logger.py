def load_tau2_results(results_path: str) -> dict:
    """Load tau2-bench results.json and extract key metrics."""
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    simulations = data.get('simulations', [])
    
    # Filter out infra errors - check info field for error key
    valid = []
    infra_errors = 0
    
    for s in simulations:
        info = s.get('info') or {}
        has_error = 'error' in info if isinstance(info, dict) else False
        reward_info = s.get('reward_info')
        
        if has_error or reward_info is None:
            infra_errors += 1
        else:
            valid.append(s)
    
    if not valid:
        return None
    
    rewards = [s['reward_info']['reward'] for s in valid]
    
    n = len(rewards)
    mean_reward = sum(rewards) / n
    pass_at_1 = sum(1 for r in rewards if r == 1.0) / n
    
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