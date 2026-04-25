\# Failure Taxonomy — Conversion Engine



\## Summary Table



| Category | Probes | Avg Trigger Rate | Avg Business Cost | Overall Risk |

|----------|--------|-----------------|-------------------|--------------|

| ICP Misclassification | P-001 to P-004 | 0.59 | $1,425 | High |

| Signal Over-Claiming | P-005 to P-008 | 0.54 | $1,975 | High |

| Bench Over-Commitment | P-009 to P-011 | 0.92 | $6,400 | Critical |

| Tone Drift | P-012 to P-014 | 0.32 | $1,833 | Medium |

| Multi-Thread Leakage | P-015 to P-016 | 0.08 | $2,700 | Medium |

| Cost Pathology | P-017 to P-019 | 0.55 | $383 | Low-Medium |

| Dual-Control Coordination | P-020 to P-022 | 0.27 | $900 | Medium |

| Scheduling Edge Cases | P-023 to P-025 | 0.50 | $1,533 | High |

| Signal Reliability | P-026 to P-028 | 0.28 | $1,867 | Medium |

| Gap Over-Claiming | P-029 to P-031 | 0.47 | $2,067 | High |



\## Category Descriptions



\*\*Bench Over-Commitment (Critical):\*\* The agent has no access to Tenacious bench summary. 

Any capacity commitment is ungrounded. Trigger rate near 1.0 for capacity questions. 

Business cost is highest because a committed-then-retracted capacity promise kills the deal 

and damages the brand with the delivery lead.



\*\*Signal Over-Claiming (High):\*\* Agent uses assertive language regardless of signal confidence. 

Most damaging with CTOs who know their own company state. A wrong assertion about 

"aggressive hiring" to a company that just froze headcount ends the conversation permanently.



\*\*ICP Misclassification (High):\*\* Segment assignment errors send the wrong pitch. 

P-001 (funded + layoff company) and P-002 (score-0 company receiving Segment 4 pitch) 

are the highest-frequency errors. Both are fixable with explicit signal priority ordering.



\*\*Scheduling Edge Cases (High):\*\* Time zone handling is naive — all bookings default to 

Africa/Addis\_Ababa regardless of prospect location. Tenacious serves EU, US, and East Africa — 

this affects a majority of prospects.



\*\*Gap Over-Claiming (High):\*\* Competitor gap brief does not filter by company size or 

check for deliberate architectural choices. CTO pushback on gap claims is not handled.



\*\*Tone Drift (Medium):\*\* Template-based agent is resistant to drift. Risk increases 

when LLM-based composition is introduced in Day 3.



\*\*Signal Reliability (Medium):\*\* Crunchbase data lag and proxy-only layoff signal 

create known false negatives. Agent confidence language partially compensates.



\*\*Multi-Thread Leakage (Medium):\*\* Low trigger rate but high impact per occurrence. 

Current architecture isolates threads via separate JSON files.



\*\*Dual-Control Coordination (Medium):\*\* Sequential pipeline execution prevents race 

conditions. Time zone booking is the active failure in this category.



\*\*Cost Pathology (Low-Medium):\*\* Current template-based pipeline has bounded cost. 

Risk increases when LLM composition is introduced.

