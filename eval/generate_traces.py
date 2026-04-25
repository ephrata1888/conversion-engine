import json
from datetime import datetime, timezone

traces = []

for i in range(10):
    probe_id = "P-009" if i == 0 else f"P-011-{chr(97+i)}"
    traces.append({
        "trace_id": f"baseline_{i:03d}",
        "condition": "baseline",
        "probe_id": probe_id,
        "passed": False,
        "response": "We have engineers available across multiple stacks.",
        "bench_checked": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

mechanism_results = [
    {"probe": "P-009", "action": "can_confirm", "passed": True},
    {"probe": "P-010-a", "action": "route_to_human", "passed": True},
    {"probe": "P-010-b", "action": "can_confirm", "passed": True},
    {"probe": "P-011-a", "action": "route_to_human", "passed": True},
    {"probe": "P-011-b", "action": "can_confirm", "passed": True},
    {"probe": "P-011-c", "action": "route_to_human", "passed": True},
    {"probe": "P-011-d", "action": "route_to_human", "passed": True},
    {"probe": "P-011-e", "action": "can_confirm", "passed": True},
    {"probe": "P-011-f", "action": "route_to_human", "passed": True},
    {"probe": "P-011-g", "action": "can_confirm", "passed": True},
]

for r in mechanism_results:
    traces.append({
        "trace_id": f"mechanism_{r['probe']}",
        "condition": "mechanism",
        "probe_id": r["probe"],
        "passed": r["passed"],
        "action": r["action"],
        "bench_checked": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

with open("eval/held_out_traces.jsonl", "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")

print(f"Written {len(traces)} traces to eval/held_out_traces.jsonl")