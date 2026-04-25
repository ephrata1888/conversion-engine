\# Act IV — Mechanism Design



\## Mechanism: Bench-Gated Commitment Policy



\### Problem Statement

The agent has no access to Tenacious bench summary before answering capacity 

questions. Trigger rate on bench over-commitment probes: 0.90-0.95. Every 

qualified prospect eventually asks about availability. Without a bench check, 

the agent either fabricates capacity or gives vague non-answers that lose deals.



\### Design



The mechanism is a hard constraint implemented in `agent/bench\_policy.py`:



1\. `load\_bench\_summary()` — loads bench\_summary.json at pipeline startup

2\. `check\_bench\_capacity(stack, count)` — returns available/unavailable/unknown

3\. `get\_safe\_capacity\_response(stack, count)` — generates grounded response

4\. Agent MUST call check\_bench before responding to any capacity question

5\. If bench unavailable: always route to human delivery lead



\### Three Ablation Variants



\*\*Variant A (implemented): Hard constraint\*\*

Agent cannot respond to capacity questions without bench check.

Result: pass rate 1.000, Delta A = 1.000, p = 0.000004



\*\*Variant B: Soft suggestion\*\*

Agent is prompted to check bench but not required to.

Expected result: pass rate \~0.60 — LLM sometimes ignores soft constraints



\*\*Variant C: No mechanism (baseline)\*\*

Agent answers capacity questions without bench check.

Result: pass rate 0.000 — all probes fail



\### Statistical Test

\- Z-score: 4.472

\- p-value: 0.000004

\- Delta A positive with p < 0.05: confirmed

\- 95% CI mechanism: \[1.000, 1.000]

\- 95% CI baseline: \[0.000, 0.000]



\### Hyperparameters

\- bench\_summary.json refresh: daily

\- Stack matching: substring match (case-insensitive)

\- Fallback on unknown stack: always route to human

\- Fallback on missing bench file: always route to human



\### Limitations

\- Bench summary is a placeholder (real data comes from seed repo)

\- Stack matching is naive substring — "python data engineer" matches both 

&#x20; "python" and "data" stacks — needs disambiguation

\- Does not handle partial availability (e.g. 2 of 4 requested engineers available)

\- Does not account for upcoming bench changes (engineers finishing engagements)

