# τ²-Bench Retail Baseline — Act I

## Instructor-Provided Shared Baseline (Reference for Memo)

| Metric | Value |
|--------|-------|
| Model | Pinned dev-tier model |
| Domain | retail |
| Tasks | 30 (dev slice) |
| Trials | 5 per task (150 total) |
| Valid runs | 150 (0 infra errors) |
| pass@1 | **0.7267** |
| 95% CI | [0.6504, 0.7917] |
| Avg cost/run | $0.0199 |
| p50 latency | 105.95s |
| p95 latency | 551.65s |
| Git commit | d11a97072c49d093f7b5a3e4fe9da95b490d43ba |

Source: `seed/score_log.json` — provided by program staff April 22, 2026.
All memo claims reference this baseline.

---

## Personal Reproduction Check (OpenRouter/Qwen3-235b-a22b)

| Metric | Value |
|--------|-------|
| Model | openrouter/qwen/qwen3-235b-a22b |
| Domain | retail |
| Tasks | 30 (dev slice) |
| Trials | 5 per task (150 attempted) |
| Valid runs | 105 (45 infra errors) |
| pass@1 | 0.371 |
| 95% CI | [0.279, 0.464] |
| Avg cost/run | ~$0.02-0.03 (not mapped in LiteLLM) |
| p50 latency | ~67s |
| p95 latency | ~161s |

## Unexpected Behavior

1. **Rate limiting:** OpenRouter weekly key limit was hit mid-run (45/150 infra errors). Instructor increased limit. Rerun with `--max-concurrency 1` and `--retry-delay 3`.
2. **Model not priced:** LiteLLM does not have pricing for `qwen3-235b-a22b-04-28`. All costs show $0.00. Estimated actual cost ~$3-4 for 150 runs.
3. **Default model:** Without explicit `--agent-llm` flag, tau2-bench defaults to GPT-4.1 which has no OpenAI quota. Must always pass `--agent-llm openrouter/qwen/qwen3-235b-a22b`.

## Gap to Reference

Personal run (0.371) is 35 points below instructor baseline (0.727). Gap is explained by:
- Model quality: Qwen3-235b vs pinned reference model
- Infra errors reducing valid sample: 105 vs 150
- Rate limiting introducing delays between turns
