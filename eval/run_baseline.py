"""
tau2-bench baseline runner for Conversion Engine - Act I
Usage: python eval/run_baseline.py
"""
import subprocess
import sys
import os

def run_baseline(
    num_tasks: int = 30,
    num_trials: int = 5,
    save_to: str = "baseline_final",
    model: str = "openrouter/qwen/qwen3-235b-a22b"
):
    """Run tau2-bench retail baseline."""
    
    tau2_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tau2-bench")
    
    cmd = [
        sys.executable, "-m", "tau2", "run",
        "--domain", "retail",
        "--num-tasks", str(num_tasks),
        "--num-trials", str(num_trials),
        "--agent-llm", model,
        "--user-llm", model,
        "--save-to", save_to,
        "--max-concurrency", "1",
        "--retry-delay", "3",
        "--max-retries", "1"
    ]
    
    print(f"Running tau2-bench baseline...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {tau2_dir}")
    
    result = subprocess.run(cmd, cwd=tau2_dir)
    return result.returncode

if __name__ == "__main__":
    returncode = run_baseline()
    
    if returncode == 0:
        print("\nBaseline complete. Now logging results...")
        import sys
        sys.path.append(os.path.dirname(__file__))
        from score_logger import update_score_log
        
        results_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "tau2-bench", "data", "simulations", "baseline_final", "results.json"
        )
        
        update_score_log(
            "baseline_final",
            results_path,
            "30-task 5-trial baseline, max-concurrency 1"
        )