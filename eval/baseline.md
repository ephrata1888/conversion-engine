\# τ²-Bench Retail Baseline — Act I



\## What Was Reproduced



Ran the τ²-Bench retail domain using `openrouter/qwen/qwen3-235b-a22b` as both 

agent and user simulator. 30 dev-slice tasks, 5 trials each (150 total runs), 

max-concurrency 1, retry-delay 3s, max-retries 1.



\## Results



| Metric | Value |

|--------|-------|

| Model | openrouter/qwen/qwen3-235b-a22b |

| Tasks | 30 (dev slice) |

| Trials | 5 per task |

| Total runs | 150 |

| Valid runs | 105 |

| Infra errors | 45 (rate limiting) |

| pass@1 | 0.371 |

| 95% CI | \[0.279, 0.464] |

| Mean reward | 0.371 |

| Avg cost/run | $0.00 (model not priced in LiteLLM) |



\## Published Reference



Published τ²-Bench retail SOTA is \~42% pass@1 (GPT-4.1 class). Our baseline of 

37.1% with Qwen3-235b is within expected range for a non-frontier model, 

approximately 5 percentage points below the published reference.



\## Confidence Interval



95% CI: \[0.279, 0.464] computed via normal approximation on n=105 valid runs.

The wide CI reflects the 45 infra errors (30%) which were excluded. A cleaner 

run with zero infra errors would tighten this interval.



\## Unexpected Behavior



1\. High infra error rate (45/150 = 30%) due to OpenRouter weekly rate limit 

&#x20;  being hit mid-run. Resolved by instructor increasing the limit.

2\. LiteLLM does not have pricing data for qwen3-235b-a22b-04-28 — all costs 

&#x20;  show as $0.00. Actual cost estimated at \~$2-3 based on token counts.

3\. Model defaulted to GPT-4.1 when no model was specified — required explicit 

&#x20;  --agent-llm and --user-llm flags.



\## Cost Per Run



Estimated $0.02-0.03 per task based on conversation length (\~10-15 turns).

Total baseline cost: approximately $3-4 for 150 runs.

