# Conversion Engine

**Automated Lead Generation and Qualification for Tenacious Consulting and Outsourcing**

> TRP1 Week 10 Challenge · Ephrata Wolde · April 2026

---

## ⚠️ Kill Switch — Read First

`TENACIOUS_OUTBOUND_ENABLED` **defaults to unset.**

When unset, **all outbound** (email, SMS, Cal.com bookings) routes to the staff sink. No real prospects are contacted during the challenge week.

```bash
# Verify kill switch is inactive (safe mode)
grep TENACIOUS_OUTBOUND_ENABLED .env
# Should return nothing or a commented-out line

# Run full pre-flight smoke test
bash infra/smoke_test.sh
# Expected: 5 green checks
```

See `infra/killswitch.md` for full documentation.

---

## Architecture

The system follows a **Researcher → Closer** pattern. The Researcher runs before any outreach and produces two verified JSON briefs. The Closer reads only those briefs — it cannot over-claim because it has no direct access to raw data.

```
┌─────────────────────────────────────────────────────────────┐
│                    PUBLIC DATA SOURCES                       │
│  Crunchbase ODM · layoffs.fyi · Job Posts Snapshot          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   RESEARCHER AGENT                           │
│  enrichment_pipeline.py → hiring_signal_brief.json          │
│  competitor_gap_brief.py → competitor_gap_brief.json        │
│                                                              │
│  Signals: funding · layoffs · leadership · AI maturity      │
│           job post velocity · competitor gap                 │
└──────────────────────┬──────────────────────────────────────┘
                       │  verified briefs only
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOSER AGENT                              │
│  compose_outreach_email() — signal-grounded, phrasing       │
│  shifts with confidence score                               │
└──────────────────────┬──────────────────────────────────────┘
                       │  gated by outbound_gate.py
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  OUTBOUND (KILL-SWITCH GATED)                │
│                                                              │
│  Resend ──────────── Email (primary channel)                 │
│  Africa's Talking ── SMS (warm leads only)                   │
│  HubSpot ─────────── CRM + 12 enrichment fields             │
│  Cal.com ─────────── Discovery call booking                  │
│  HubSpot ←────────── Booking confirmation update            │
│  Langfuse ────────── Per-trace observability                 │
└─────────────────────────────────────────────────────────────┘
```

**Channel hierarchy:** Email first → SMS only for warm leads who replied → Voice (discovery call booked by agent, delivered by human Tenacious delivery lead).

---

## Setup

### Requirements

- Python 3.10+
- Git

### Installation

```bash
git clone https://github.com/ephrata1888/conversion-engine.git
cd conversion-engine
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r agent/requirements.txt
```

### Environment Variables

Create `.env` in the root directory:

```bash
# Email
RESEND_API_KEY=re_xxxxxxxxxxxx

# SMS
AT_API_KEY=atsk_xxxxxxxxxxxx
AT_USERNAME=sandbox

# CRM
HUBSPOT_ACCESS_TOKEN=pat-eu1-xxxxxxxxxxxx

# Calendar
CAL_API_KEY=cal_live_xxxxxxxxxxxx
CAL_EVENT_TYPE_ID=5443589

# LLM
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Observability
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com

# Kill switch — LEAVE UNSET for safe mode (routes to staff sink)
# TENACIOUS_OUTBOUND_ENABLED=true
```

---

## Running the Pipeline

### Full pipeline for one synthetic prospect

```bash
python agent/main_agent.py
```

Expected output: 6 steps complete in ~6-7 seconds. Kill switch routes all outbound to staff sink.

### Webhook server with ngrok (for reply handling)

```bash
python start_webhook.py
# Outputs public URL — register in Resend, Africa's Talking, Cal.com
```

### tau2-Bench baseline

```bash
cd tau2-bench
tau2 run --domain retail --num-tasks 30 --num-trials 1 \
  --agent-llm openrouter/qwen/qwen3-235b-a22b \
  --user-llm openrouter/qwen/qwen3-235b-a22b \
  --save-to baseline_final --max-concurrency 1
```

### Ablation test (Act IV)

```bash
python eval/ablation_test.py
```

### Latency measurement (20 runs)

```bash
python eval/run_20_prospects.py
```

---

## Repository Structure

```
conversion-engine/
│
├── agent/                          # All agent source files
│   ├── main_agent.py               # 6-step pipeline orchestrator
│   ├── enrichment_pipeline.py      # Hiring signal brief with per-signal confidence
│   ├── competitor_gap_brief.py     # Top-quartile sector gap analysis
│   ├── email_handler.py            # Resend + bounce handling + callback registry
│   ├── sms_handler.py              # Africa's Talking + warm-lead gate
│   ├── hubspot_handler.py          # HubSpot contact + 12 enrichment fields
│   ├── cal_handler.py              # Cal.com API v2 slots and booking
│   ├── bench_policy.py             # Bench-gated commitment policy (Act IV)
│   ├── outbound_gate.py            # Kill switch gate for all outbound
│   └── requirements.txt
│
├── eval/                           # Evaluation and benchmark files
│   ├── score_log.json              # Instructor baseline + personal run with 95% CI
│   ├── trace_log.jsonl             # Full tau2-Bench trajectories (150 runs)
│   ├── baseline.md                 # Baseline methodology and findings
│   ├── ablation_results.json       # 3-condition ablation: baseline/auto-opt/mechanism
│   ├── held_out_traces.jsonl       # Raw traces from ablation conditions
│   ├── latency_results.json        # p50/p95 from 20 pipeline runs
│   ├── invoice_summary.json        # Cost per qualified lead derivation
│   ├── ablation_test.py            # Ablation harness
│   └── run_20_prospects.py         # Latency measurement script
│
├── probes/                         # Adversarial probe library (Act III)
│   ├── probe_library.md            # 31 probes across 10 failure categories
│   ├── failure_taxonomy.md         # Probes grouped by category and trigger rate
│   └── target_failure_mode.md      # Bench over-commitment — highest-ROI failure
│
├── data/                           # Data files
│   ├── crunchbase_sample.csv       # 1,001 Crunchbase records (Apache 2.0)
│   ├── layoffs_2026.csv            # layoffs.fyi dataset (CC-BY)
│   ├── job_posts_snapshot_2026_04_01.json   # Frozen April 2026 job posts
│   ├── bench_summary.json          # Tenacious delivery bench capacity
│   ├── hiring_signal_brief.json    # Sample output for DataStack AI
│   ├── competitor_gap_brief.json   # Sample output for DataStack AI
│   ├── synthetic_prospect.json     # Test prospect (not a real company)
│   └── pipeline_result.json        # Full pipeline output with latency
│
├── infra/
│   ├── killswitch.md               # Kill switch documentation
│   └── smoke_test.sh               # Pre-flight check (5 green checks)
│
├── policy/
│   └── acknowledgement_signed.txt  # Data handling policy acknowledgement
│
├── method.md                       # Act IV mechanism design and ablation
├── evidence_graph.json             # Every memo claim mapped to source trace
├── memo.pdf                        # 2-page decision memo (Act V)
├── webhook_server.py               # FastAPI webhook receiver
├── start_webhook.py                # ngrok + uvicorn launcher
└── README.md
```

---

## Production Stack Status

| Component | Tool | Status | Verification |
|-----------|------|--------|-------------|
| Email (primary) | Resend free tier | ✅ Verified | Draft headers applied, bounce handling |
| SMS (warm leads) | Africa's Talking sandbox | ✅ Verified | messageId ATXid_3ed474 confirmed |
| CRM | HubSpot Developer Sandbox | ✅ Verified | 12 custom enrichment fields |
| Calendar | Cal.com cloud (API v2) | ✅ Verified | Booking ID 18773861 confirmed |
| Observability | Langfuse cloud v4 | ✅ Verified | 20 Langfuse traces logged |
| Kill switch | outbound_gate.py | ✅ Active | All outbound routes to staff sink |

---

## Baseline Results

| Run | Model | pass@1 | 95% CI | Source |
|-----|-------|--------|--------|--------|
| Instructor shared baseline | Pinned dev-tier | **0.7267** | [0.6504, 0.7917] | `seed/score_log.json` |
| Personal reproduction (Qwen3) | openrouter/qwen/qwen3-235b-a22b | 0.371 | [0.279, 0.464] | `eval/score_log.json` |

**Pipeline latency (n=20):** p50 = 6.6s · p95 = 7.3s · Source: `eval/latency_results.json`

**Cost per qualified lead:** $1.63 (at 7% reply rate, 35% call conversion) · Target: <$5 · Source: `eval/invoice_summary.json`

---

## Act IV — Mechanism

**Target failure mode:** Bench over-commitment (trigger rate 0.90-0.95 on capacity questions)

**Mechanism:** Hard constraint in `agent/bench_policy.py`. Agent cannot respond to capacity questions without calling `check_bench_capacity(stack, count)` first. Routes to human delivery lead if bench is unavailable or unknown.

| Condition | pass@1 | 95% CI | Delta A | p-value |
|-----------|--------|--------|---------|---------|
| Baseline (no bench check) | 0.000 | [0.000, 0.000] | — | — |
| Auto-opt (prompt only) | 0.600 | [0.296, 0.904] | +0.600 | — |
| **Mechanism (hard constraint)** | **1.000** | [1.000, 1.000] | **+1.000** | **0.000004** |

---

## Data Sources

| Source | License | Use | Restriction |
|--------|---------|-----|-------------|
| Crunchbase ODM | Apache 2.0 (luminati-io) | Firmographics, funding, leadership, tech stack | Static July 2024 snapshot |
| layoffs.fyi | CC-BY | Layoff signal for Segment 2 classification | Weekly update available |
| Job posts (frozen) | Public | Engineering hiring velocity (60-day delta) | Frozen April 2026 snapshot |
| tau2-Bench | Apache 2.0 (Sierra Research) | Conversation benchmark | Retail domain dev slice |
| Tenacious seed materials | TRP1 limited license | ICP, style, bench, pricing | Challenge week only |

**Scraping policy (Rule 4):** All Playwright scraping uses user agent `TRP1-Week10-Research (trainee@trp1.example)`, checks robots.txt before scraping, enforces 2-second rate limit between requests, detects and stops on captcha, capped at 200 companies per week.

---

## Key Design Decisions

**1. Researcher-Closer separation:** The Closer cannot fabricate signals because it only sees the verified brief. This is a structural honesty constraint, not a prompt instruction.

**2. Per-signal confidence scores:** Every signal in the brief has its own `confidence` and `confidence_reason`. The email phrasing shifts automatically — low confidence forces "we noticed" language, high confidence allows "we can see" language.

**3. Hard bench constraint:** Bench over-commitment is the highest-ROI failure mode ($67K expected deal loss per occurrence). A hard Python constraint in `bench_policy.py` achieves 100% pass rate vs 60% for prompt optimization alone.

**4. Kill switch by default:** `TENACIOUS_OUTBOUND_ENABLED` is unset by default. Every outbound call passes through `gate_email()`, `gate_sms()`, or `gate_booking()`. Bypassing the gate in code is a policy violation.

**5. Draft metadata:** Every HubSpot record includes `tenacious_status=draft`. Every email includes `X-Tenacious-Status: draft` header. Per data handling policy Rule 6.

---

## Contact

Ephrata Wolde · TRP1 Cohort April 2026 · GitHub: [ephrata1888](https://github.com/ephrata1888)