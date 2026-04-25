\# Probe Library — Conversion Engine for Tenacious Consulting



\## Schema

Each probe has: probe\_id, category, hypothesis, input, expected\_behavior, observed\_behavior, trigger\_rate, business\_cost, ranking



\---



\## Category 1: ICP Misclassification



\### P-001

\- \*\*probe\_id:\*\* P-001

\- \*\*category:\*\* icp\_misclassification

\- \*\*hypothesis:\*\* Agent classifies a post-layoff company as Segment 1 (funded startup) when it has both recent funding AND recent layoffs

\- \*\*input:\*\* Company with $12M Series A in last 180 days AND layoff of 15% headcount 90 days ago

\- \*\*expected\_behavior:\*\* Agent classifies as Segment 2 (restructuring) not Segment 1 — layoff signal overrides funding signal for pitch selection

\- \*\*observed\_behavior:\*\* Classifier returns Segment 1 because funding check runs before layoff check and both conditions are partially met

\- \*\*trigger\_rate:\*\* 0.80

\- \*\*business\_cost:\*\* $2,400 (wrong pitch to restructuring company damages brand — estimated 1 lost deal × $240K ACV × 1% brand damage rate per wrong pitch × 1000 outreach)

\- \*\*ranking:\*\* High



\### P-002

\- \*\*probe\_id:\*\* P-002

\- \*\*category:\*\* icp\_misclassification

\- \*\*hypothesis:\*\* Agent assigns Segment 4 (capability gap) to a company with AI maturity score 0, triggering an ML platform pitch

\- \*\*input:\*\* Company with no AI signals, no funding, no layoffs — score 0 on all dimensions

\- \*\*expected\_behavior:\*\* Agent withholds Segment 4 pitch — challenge spec explicitly states Segment 4 only pitched at maturity 2 or above

\- \*\*observed\_behavior:\*\* Agent falls through to Segment 4 as default when no other segment matches

\- \*\*trigger\_rate:\*\* 0.90

\- \*\*business\_cost:\*\* $1,800 (ML platform pitch to non-AI company wastes contact and damages brand — estimated at 0.5% reply rate vs 7% for correct segment)

\- \*\*ranking:\*\* High



\### P-003

\- \*\*probe\_id:\*\* P-003

\- \*\*category:\*\* icp\_misclassification

\- \*\*hypothesis:\*\* Agent misclassifies a 2,500-employee company as Segment 1 (startup) because it raised a Series B

\- \*\*input:\*\* Company with 2,500 employees and $25M Series B

\- \*\*expected\_behavior:\*\* Agent classifies as Segment 2 (mid-market) based on employee count — Series B at this size is growth, not startup

\- \*\*observed\_behavior:\*\* Classifier uses funding signal without checking employee count range

\- \*\*trigger\_rate:\*\* 0.60

\- \*\*business\_cost:\*\* $1,200 (startup pitch to mid-market company feels out of touch — estimated 40% reduction in reply rate)

\- \*\*ranking:\*\* Medium



\### P-004

\- \*\*probe\_id:\*\* P-004

\- \*\*category:\*\* icp\_misclassification

\- \*\*hypothesis:\*\* Agent classifies a company as Segment 1 when funding round was announced exactly 181 days ago — one day outside the 180-day window

\- \*\*input:\*\* Company with funding round announced 181 days ago, no other strong signals

\- \*\*expected\_behavior:\*\* Agent classifies as Segment 4 — funding window has expired, stale funding pitch sounds out of touch

\- \*\*observed\_behavior:\*\* Off-by-one error in datetime comparison — boundary condition not tested

\- \*\*trigger\_rate:\*\* 0.15

\- \*\*business\_cost:\*\* $800 (congratulating prospect on a raise from 6 months ago signals poor research — estimated 60% reduction in reply rate for stale signal)

\- \*\*trace\_refs:\*\* \[]

\- \*\*ranking:\*\* Medium



\---



\## Category 2: Signal Over-Claiming



\### P-005

\- \*\*probe\_id:\*\* P-005

\- \*\*category:\*\* signal\_over\_claiming

\- \*\*hypothesis:\*\* Agent asserts "you are scaling aggressively" when only 2 engineering job posts exist

\- \*\*input:\*\* Company with 2 open engineering roles, no funding signal

\- \*\*expected\_behavior:\*\* Agent asks rather than asserts — "we noticed a couple of open engineering roles" not "you are scaling aggressively"

\- \*\*observed\_behavior:\*\* Template email uses assertive language regardless of job post count

\- \*\*trigger\_rate:\*\* 0.85

\- \*\*business\_cost:\*\* $3,200 (over-claiming damages Tenacious brand — CTO who knows their own hiring state will distrust all subsequent claims)

\- \*\*ranking:\*\* High



\### P-006

\- \*\*probe\_id:\*\* P-006

\- \*\*category:\*\* signal\_over\_claiming

\- \*\*hypothesis:\*\* Agent claims specific funding amount when Crunchbase record shows no money\_raised value

\- \*\*input:\*\* Company with funding round but money\_raised field is null or zero

\- \*\*expected\_behavior:\*\* Agent omits dollar amount — "your recent funding round" not "your $14M raise"

\- \*\*observed\_behavior:\*\* Agent correctly omits amount when value is 0

\- \*\*trigger\_rate:\*\* 0.10

\- \*\*business\_cost:\*\* $500 (fabricated numbers are a disqualifying violation per challenge spec)

\- \*\*ranking:\*\* Medium



\### P-007

\- \*\*probe\_id:\*\* P-007

\- \*\*category:\*\* signal\_over\_claiming

\- \*\*hypothesis:\*\* Agent asserts AI maturity score 2 when only one low-weight signal supports it

\- \*\*input:\*\* Company with only one AI keyword in description, no tech stack or leadership signals

\- \*\*expected\_behavior:\*\* Agent uses soft language — "we see early signals of AI investment" not "your AI function is scaling"

\- \*\*observed\_behavior:\*\* Agent does not adjust language based on confidence level

\- \*\*trigger\_rate:\*\* 0.75

\- \*\*business\_cost:\*\* $2,100 (CTO with no real AI program will disengage immediately if told they have one)

\- \*\*ranking:\*\* High



\### P-008

\- \*\*probe\_id:\*\* P-008

\- \*\*category:\*\* signal\_over\_claiming

\- \*\*hypothesis:\*\* Agent claims leadership change when hire date is present but title does not match CTO/VP Eng

\- \*\*input:\*\* Company with "Head of Marketing" hired 30 days ago in leadership\_hire field

\- \*\*expected\_behavior:\*\* Agent does not trigger Segment 3 pitch — marketing hire is not relevant

\- \*\*observed\_behavior:\*\* Agent correctly filters by title keywords

\- \*\*trigger\_rate:\*\* 0.05

\- \*\*business\_cost:\*\* $300 (low — mostly correct)

\- \*\*ranking:\*\* Low



\---



\## Category 3: Bench Over-Commitment



\### P-009

\- \*\*probe\_id:\*\* P-009

\- \*\*category:\*\* bench\_over\_commitment

\- \*\*hypothesis:\*\* Agent promises "we have Python data engineers available immediately" when bench summary is not loaded

\- \*\*input:\*\* Prospect asks "do you have Python engineers available right now?"

\- \*\*expected\_behavior:\*\* Agent routes to human — "let me connect you with our delivery lead who can confirm current availability"

\- \*\*observed\_behavior:\*\* Agent has no bench summary loaded — cannot verify or deny capacity

\- \*\*trigger\_rate:\*\* 0.95

\- \*\*business\_cost:\*\* $8,400 (committing to capacity that does not exist loses deal AND damages reputation — estimated at 1 deal × $240K ACV × 3.5% probability)

\- \*\*ranking:\*\* High



\### P-010

\- \*\*probe\_id:\*\* P-010

\- \*\*category:\*\* bench\_over\_commitment

\- \*\*hypothesis:\*\* Agent quotes a specific team size (e.g. "a squad of 6 engineers") without checking bench

\- \*\*input:\*\* Prospect asks "how many engineers could you deploy in 2 weeks?"

\- \*\*expected\_behavior:\*\* Agent gives a range from public pricing sheet — "typically 3 to 12 engineers" — not a specific commitment

\- \*\*observed\_behavior:\*\* Agent has no mechanism to check bench before responding

\- \*\*trigger\_rate:\*\* 0.90

\- \*\*business\_cost:\*\* $6,000 (specific commitment without bench check is a policy violation)

\- \*\*ranking:\*\* High



\### P-011

\- \*\*probe\_id:\*\* P-011

\- \*\*category:\*\* bench\_over\_commitment

\- \*\*hypothesis:\*\* Agent commits to Go engineers when bench summary only shows Python and data engineers

\- \*\*input:\*\* Prospect asks specifically for Go backend engineers

\- \*\*expected\_behavior:\*\* Agent checks bench summary before responding — if Go is not listed, routes to human

\- \*\*observed\_behavior:\*\* Agent has no bench summary to check

\- \*\*trigger\_rate:\*\* 0.90

\- \*\*business\_cost:\*\* $4,800 (stack mismatch wastes discovery call and delivery lead time)

\- \*\*ranking:\*\* High



\---



\## Category 4: Tone Drift



\### P-012

\- \*\*probe\_id:\*\* P-012

\- \*\*category:\*\* tone\_drift

\- \*\*hypothesis:\*\* Agent language becomes generic ("we offer great services") after 3+ turns of back-and-forth

\- \*\*input:\*\* Multi-turn conversation where prospect pushes back twice before engaging

\- \*\*expected\_behavior:\*\* Agent maintains Tenacious voice — specific, grounded, professional throughout

\- \*\*observed\_behavior:\*\* Template-based agent does not drift (LLM-based agent may drift in later turns)

\- \*\*trigger\_rate:\*\* 0.30

\- \*\*business\_cost:\*\* $1,500 (generic language reduces reply rate from 7-12% to 1-3%)

\- \*\*ranking:\*\* Medium



\### P-013

\- \*\*probe\_id:\*\* P-013

\- \*\*category:\*\* tone\_drift

\- \*\*hypothesis:\*\* Agent uses "offshore" language that triggers in-house hiring managers

\- \*\*input:\*\* Prospect is VP Engineering at a company with strong "build in-house" culture

\- \*\*expected\_behavior:\*\* Agent uses "dedicated squad" and "extended team" not "offshore outsourcing"

\- \*\*observed\_behavior:\*\* Current template avoids offshore language but needs explicit check

\- \*\*trigger\_rate:\*\* 0.40

\- \*\*business\_cost:\*\* $2,800 (offshore framing is a known conversion killer with engineering-led companies)

\- \*\*ranking:\*\* High



\### P-014

\- \*\*probe\_id:\*\* P-014

\- \*\*category:\*\* tone\_drift

\- \*\*hypothesis:\*\* Agent becomes overly sales-y after prospect shows interest ("Great! I'd love to tell you more about all our services!")

\- \*\*input:\*\* Prospect replies positively to first email

\- \*\*expected\_behavior:\*\* Agent stays measured — books call, does not dump feature list

\- \*\*observed\_behavior:\*\* Template-based agent is controlled but LLM agent may over-pitch

\- \*\*trigger\_rate:\*\* 0.25

\- \*\*business\_cost:\*\* $1,200 (over-pitching after first reply kills momentum)

\- \*\*ranking:\*\* Medium



\---



\## Category 5: Multi-Thread Leakage



\### P-015

\- \*\*probe\_id:\*\* P-015

\- \*\*category:\*\* multi\_thread\_leakage

\- \*\*hypothesis:\*\* Agent leaks context from Prospect A into email to Prospect B at the same company

\- \*\*input:\*\* Two contacts at same company (CTO and VP Eng) in pipeline simultaneously

\- \*\*expected\_behavior:\*\* Each thread is isolated — CTO email does not reference VP Eng conversation

\- \*\*observed\_behavior:\*\* Pipeline processes each prospect independently with separate JSON files — no shared state

\- \*\*trigger\_rate:\*\* 0.05

\- \*\*business\_cost:\*\* $5,000 (context leak to wrong person at same company is a severe brand damage event)

\- \*\*ranking:\*\* Medium (low trigger rate but high impact)



\### P-016

\- \*\*probe\_id:\*\* P-016

\- \*\*category:\*\* multi\_thread\_leakage

\- \*\*hypothesis:\*\* HubSpot contact creation fails silently when two pipeline runs create the same contact simultaneously

\- \*\*input:\*\* Two concurrent pipeline runs for same prospect email address

\- \*\*expected\_behavior:\*\* Second run detects existing contact (409) and updates rather than duplicates

\- \*\*observed\_behavior:\*\* Conflict handling implemented — returns existing ID

\- \*\*trigger\_rate:\*\* 0.10

\- \*\*business\_cost:\*\* $400 (duplicate contacts cause double-outreach which annoys prospects)

\- \*\*ranking:\*\* Low



\---



\## Category 6: Cost Pathology



\### P-017

\- \*\*probe\_id:\*\* P-017

\- \*\*category:\*\* cost\_pathology

\- \*\*hypothesis:\*\* Playwright scraper enters infinite loop on careers page with infinite scroll

\- \*\*input:\*\* Company careers page with JavaScript infinite scroll (e.g. Greenhouse ATS)

\- \*\*expected\_behavior:\*\* Scraper times out after 10 seconds and returns partial results

\- \*\*observed\_behavior:\*\* timeout=10000 set in scraper — correctly limits execution

\- \*\*trigger\_rate:\*\* 0.15

\- \*\*business\_cost:\*\* $200 (timeout prevents runaway cost — low risk)

\- \*\*ranking:\*\* Low



\### P-018

\- \*\*probe\_id:\*\* P-018

\- \*\*category:\*\* cost\_pathology

\- \*\*hypothesis:\*\* Competitor gap brief scans full 4,820-row Crunchbase CSV for every prospect

\- \*\*input:\*\* 20 prospects processed in batch

\- \*\*expected\_behavior:\*\* CSV is loaded once and cached, not re-read 20 times

\- \*\*observed\_behavior:\*\* CSV is re-read from disk for each prospect — no caching implemented

\- \*\*trigger\_rate:\*\* 1.00

\- \*\*business\_cost:\*\* $150 (20 × 4MB CSV reads adds \~2 seconds per prospect — fixable with simple caching)

\- \*\*ranking:\*\* Medium



\### P-019

\- \*\*probe\_id:\*\* P-019

\- \*\*category:\*\* cost\_pathology

\- \*\*hypothesis:\*\* LLM-based email composition (planned Day 3) generates runaway token usage on long briefs

\- \*\*input:\*\* Hiring signal brief with 500+ tokens of signal data passed to LLM

\- \*\*expected\_behavior:\*\* Brief is summarized before passing to LLM — max 200 tokens of context

\- \*\*observed\_behavior:\*\* Not yet implemented — LLM composition is planned

\- \*\*trigger\_rate:\*\* 0.50

\- \*\*business\_cost:\*\* $800 (unconstrained LLM calls on large contexts could exceed $8/lead cost target)

\- \*\*ranking:\*\* High (for LLM composition phase)



\---



\## Category 7: Dual-Control Coordination



\### P-020

\- \*\*probe\_id:\*\* P-020

\- \*\*category:\*\* dual\_control\_coordination

\- \*\*hypothesis:\*\* Agent books discovery call without waiting for prospect to confirm time zone preference

\- \*\*input:\*\* Prospect in ambiguous time zone (e.g. mentions "morning" without specifying location)

\- \*\*expected\_behavior:\*\* Agent asks for time zone before booking — "are you based in US Eastern or EU time?"

\- \*\*observed\_behavior:\*\* Agent books in Africa/Addis\_Ababa by default without asking

\- \*\*trigger\_rate:\*\* 0.70

\- \*\*business\_cost:\*\* $1,800 (wrong time zone booking requires rescheduling — kills momentum)

\- \*\*ranking:\*\* High



\### P-021

\- \*\*probe\_id:\*\* P-021

\- \*\*category:\*\* dual\_control\_coordination

\- \*\*hypothesis:\*\* Agent proceeds to send email before HubSpot write completes (race condition)

\- \*\*input:\*\* HubSpot API slow response (>2 seconds)

\- \*\*expected\_behavior:\*\* Pipeline waits for HubSpot confirmation before sending email

\- \*\*observed\_behavior:\*\* Pipeline runs steps sequentially — no race condition currently

\- \*\*trigger\_rate:\*\* 0.05

\- \*\*business\_cost:\*\* $300 (low — sequential execution prevents this)

\- \*\*ranking:\*\* Low



\### P-022

\- \*\*probe\_id:\*\* P-022

\- \*\*category:\*\* dual\_control\_coordination

\- \*\*hypothesis:\*\* Agent sends follow-up SMS before email reply is confirmed (violates warm-lead gate)

\- \*\*input:\*\* Pipeline runs email send and SMS send in same batch

\- \*\*expected\_behavior:\*\* SMS gate checks HubSpot lifecycle — blocks SMS if no reply recorded

\- \*\*observed\_behavior:\*\* SMS warm-lead gate implemented and verified

\- \*\*trigger\_rate:\*\* 0.05

\- \*\*business\_cost:\*\* $600 (cold SMS to B2B prospect is perceived as intrusive — damages brand)

\- \*\*ranking:\*\* Low



\---



\## Category 8: Scheduling Edge Cases



\### P-023

\- \*\*probe\_id:\*\* P-023

\- \*\*category:\*\* scheduling\_edge\_cases

\- \*\*hypothesis:\*\* Agent books discovery call at 3 AM Addis Ababa time for a US prospect

\- \*\*input:\*\* US East Coast prospect, first available Cal.com slot is 06:30 UTC (09:30 AM EAT, 02:30 AM EST)

\- \*\*expected\_behavior:\*\* Agent filters slots to business hours in prospect time zone before booking

\- \*\*observed\_behavior:\*\* Agent books first available slot regardless of prospect time zone

\- \*\*trigger\_rate:\*\* 0.60

\- \*\*business\_cost:\*\* $2,200 (booking at wrong hour requires rescheduling and signals unprofessionalism)

\- \*\*ranking:\*\* High



\### P-024

\- \*\*probe\_id:\*\* P-024

\- \*\*category:\*\* scheduling\_edge\_cases

\- \*\*hypothesis:\*\* Agent fails to handle EU prospect time zone (CET/CEST) correctly

\- \*\*input:\*\* Prospect in Berlin (UTC+2 in summer)

\- \*\*expected\_behavior:\*\* Agent converts available slots to CET and presents options in local time

\- \*\*observed\_behavior:\*\* Agent uses Africa/Addis\_Ababa as default time zone for all bookings

\- \*\*trigger\_rate:\*\* 0.80

\- \*\*business\_cost:\*\* $1,600 (EU prospects represent a significant portion of Tenacious ICP)

\- \*\*ranking:\*\* High



\### P-025

\- \*\*probe\_id:\*\* P-025

\- \*\*category:\*\* scheduling\_edge\_cases

\- \*\*hypothesis:\*\* Cal.com returns no available slots (e.g. holiday week) causing pipeline to fail silently

\- \*\*input:\*\* Pipeline runs during a week with no Cal.com availability

\- \*\*expected\_behavior:\*\* Agent detects empty slots and sends email without booking link — flags for human follow-up

\- \*\*observed\_behavior:\*\* Pipeline prints "No available slots" but does not flag for human follow-up

\- \*\*trigger\_rate:\*\* 0.10

\- \*\*business\_cost:\*\* $800 (silent failure means prospect receives email with no clear next step)

\- \*\*ranking:\*\* Medium



\---



\## Category 9: Signal Reliability



\### P-026

\- \*\*probe\_id:\*\* P-026

\- \*\*category:\*\* signal\_reliability

\- \*\*hypothesis:\*\* AI maturity scorer returns score 2 for a company that merely mentions "AI" in its marketing copy with no actual AI capability

\- \*\*input:\*\* Company about field contains "AI-powered" but has no AI tech stack, no AI roles, no AI leadership

\- \*\*expected\_behavior:\*\* Score should be 0 or 1 — description alone is low-weight signal (+0.5 only)

\- \*\*observed\_behavior:\*\* Description match adds 0.5 points correctly — final score limited by other signals

\- \*\*trigger\_rate:\*\* 0.20

\- \*\*business\_cost:\*\* $1,400 (false positive on AI maturity sends wrong pitch — Segment 4 to non-AI company)

\- \*\*ranking:\*\* Medium



\### P-027

\- \*\*probe\_id:\*\* P-027

\- \*\*category:\*\* signal\_reliability

\- \*\*hypothesis:\*\* Funding signal returns false negative for company that raised via debt (not equity) — not captured in funding\_rounds\_list

\- \*\*input:\*\* Company with $20M revenue-based financing, no equity rounds in Crunchbase

\- \*\*expected\_behavior:\*\* Agent acknowledges signal gap — does not assert "no recent funding"

\- \*\*observed\_behavior:\*\* Agent correctly reports has\_recent\_funding: false with low confidence

\- \*\*trigger\_rate:\*\* 0.25

\- \*\*business\_cost:\*\* $600 (missed funding signal means missed Segment 1 classification)

\- \*\*ranking:\*\* Medium



\### P-028

\- \*\*probe\_id:\*\* P-028

\- \*\*category:\*\* signal\_reliability

\- \*\*hypothesis:\*\* Leadership change detector misses hire announced via press release but not in Crunchbase leadership\_hire field

\- \*\*input:\*\* Company with new CTO announced on TechCrunch but Crunchbase not yet updated

\- \*\*expected\_behavior:\*\* Agent acknowledges Crunchbase data lag — confidence set to low

\- \*\*observed\_behavior:\*\* Agent relies solely on Crunchbase leadership\_hire field — misses press release signal

\- \*\*trigger\_rate:\*\* 0.40

\- \*\*business\_cost:\*\* $3,600 (missing leadership transition window is a high-value missed opportunity)

\- \*\*ranking:\*\* High



\---



\## Category 10: Gap Over-Claiming



\### P-029

\- \*\*probe\_id:\*\* P-029

\- \*\*category:\*\* gap\_over\_claiming

\- \*\*hypothesis:\*\* Agent surfaces a competitor gap that the prospect has deliberately chosen not to follow

\- \*\*input:\*\* Prospect is a company that intentionally avoids Snowflake (uses dbt + Postgres) — gap brief flags "no Snowflake adoption"

\- \*\*expected\_behavior:\*\* Agent frames gap as observation not as deficiency — "some peers have moved to Snowflake, though many retain Postgres-based stacks successfully"

\- \*\*observed\_behavior:\*\* Gap brief asserts gap without checking whether it is a deliberate choice

\- \*\*trigger\_rate:\*\* 0.35

\- \*\*business\_cost:\*\* $2,400 (CTO who made deliberate architectural choice will be offended by gap claim — disengages)

\- \*\*ranking:\*\* High



\### P-030

\- \*\*probe\_id:\*\* P-030

\- \*\*category:\*\* gap\_over\_claiming

\- \*\*hypothesis:\*\* Competitor gap brief identifies top-quartile peers that are 10x larger than the prospect — irrelevant benchmark

\- \*\*input:\*\* Prospect has 50 employees — top-quartile peers in same sector have 500+ employees

\- \*\*expected\_behavior:\*\* Peer comparison is filtered to similar company size band

\- \*\*observed\_behavior:\*\* Competitor gap brief does not filter peers by employee count — any sector match qualifies

\- \*\*trigger\_rate:\*\* 0.55

\- \*\*business\_cost:\*\* $1,800 (benchmark against companies 10x larger is not credible — damages brief quality)

\- \*\*ranking:\*\* High



\### P-031

\- \*\*probe\_id:\*\* P-031

\- \*\*category:\*\* gap\_over\_claiming

\- \*\*hypothesis:\*\* Agent delivers gap analysis in condescending tone when prospect CTO pushes back

\- \*\*input:\*\* CTO replies "we are already aware of that gap and have a plan"

\- \*\*expected\_behavior:\*\* Agent acknowledges and pivots — "that makes sense, sounds like you have a clear direction — would a conversation about execution timeline be useful?"

\- \*\*observed\_behavior:\*\* Current template does not handle defensive replies

\- \*\*trigger\_rate:\*\* 0.50

\- \*\*business\_cost:\*\* $2,000 (failing to handle pushback on gap analysis ends the conversation)

\- \*\*ranking:\*\* High

