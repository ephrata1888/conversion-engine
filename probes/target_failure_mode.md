\# Target Failure Mode — Act IV



\## Selected Failure Mode: Bench Over-Commitment (Category 3)



\### Why This Is the Highest-ROI Failure



\*\*Trigger rate:\*\* 0.90-0.95 on capacity questions. Nearly every qualified prospect 

eventually asks about availability. This is not an edge case — it is the core 

qualification question.



\*\*Business cost derivation:\*\*



\- Average engagement ACV (talent outsourcing): $240,000-$720,000

\- Discovery-call-to-proposal conversion: 35-50%

\- A capacity commitment that cannot be honored kills the deal at proposal stage

\- Estimated deal loss probability per wrong commitment: 70%

\- Expected cost per occurrence: $240,000 × 0.40 (avg conversion) × 0.70 = $67,200

\- At 1% of outreach converting to capacity questions: 1,000 prospects × 0.01 × $67,200 = $672,000 annualized risk



\*\*Brand damage multiplier:\*\* A committed-then-retracted capacity promise is shared 

within networks. Estimated 2-3x multiplier on direct deal loss.



\*\*Why other categories rank lower:\*\*



\- Signal over-claiming: high frequency but lower per-occurrence cost ($2-3K vs $67K)

\- ICP misclassification: fixable with ordering logic, lower brand damage

\- Scheduling: annoying but recoverable — prospect reschedules rather than disengages

\- Gap over-claiming: high cost but lower trigger rate (35-55%)



\### The Fix (Act IV Mechanism)



Implement a \*\*bench-gated commitment policy\*\*:



1\. Load bench\_summary.json at pipeline startup

2\. Add a `check\_bench\_capacity(stack, count)` function that returns available/unavailable/unknown

3\. When prospect asks about capacity, agent MUST call check\_bench before responding

4\. If bench shows capacity: agent confirms with specific stack and range

5\. If bench shows no capacity: agent routes to human delivery lead

6\. If bench summary is not loaded: agent always routes to human



This is a hard constraint — not a soft preference. The agent cannot commit to 

capacity it cannot verify.



\### Measurable Success Criterion



Bench over-commitment probe trigger rate drops from 0.90 to below 0.10 on 

held-out slice after mechanism is implemented.



\### Business Impact of Fix



Eliminating bench over-commitment at 90% trigger rate on capacity questions 

reduces annualized deal loss risk from $672,000 to $67,200 — a $604,800 

expected value improvement at 1,000-prospect outreach scale.

