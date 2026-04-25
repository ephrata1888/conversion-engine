"""Run pipeline 20 times to measure p50/p95 latency."""
import sys
import os
import json
import time
import math
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent"))
from main_agent import run_prospect_pipeline

SYNTHETIC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "synthetic_prospect.json"
)

latencies = []
results = []

print("Running 20 pipeline iterations for latency measurement...")
print("(Kill switch active — all outbound routes to staff sink)")

for i in range(20):
    print(f"\nRun {i+1}/20...")
    t0 = time.time()
    result = run_prospect_pipeline(
        company_name="DataStack AI",
        prospect_email="ephratawolde990@gmail.com",
        prospect_name="Jordan Smith",
        synthetic_path=SYNTHETIC_PATH
    )
    latency = int((time.time() - t0) * 1000)
    latencies.append(latency)
    results.append({
        "run": i+1,
        "latency_ms": latency,
        "total_latency_ms": result.get("total_latency_ms") if result else latency
    })
    print(f"  Latency: {latency}ms")

# Compute statistics
latencies.sort()
n = len(latencies)
p50 = latencies[n // 2]
p95 = latencies[int(n * 0.95)]
mean = sum(latencies) / n

print(f"\n{'='*50}")
print(f"Latency Results (n={n})")
print(f"{'='*50}")
print(f"p50: {p50}ms ({p50/1000:.1f}s)")
print(f"p95: {p95}ms ({p95/1000:.1f}s)")
print(f"mean: {mean:.0f}ms ({mean/1000:.1f}s)")
print(f"min: {min(latencies)}ms")
print(f"max: {max(latencies)}ms")

# Save results
output = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "n_runs": n,
    "p50_ms": p50,
    "p95_ms": p95,
    "mean_ms": int(mean),
    "min_ms": min(latencies),
    "max_ms": max(latencies),
    "p50_seconds": round(p50/1000, 2),
    "p95_seconds": round(p95/1000, 2),
    "runs": results
}

out_path = os.path.join(os.path.dirname(__file__), "latency_results.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to eval/latency_results.json")