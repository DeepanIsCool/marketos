# MarketOS — Autonomous AI Marketing Operations Platform

> **One click. Full campaign. 24/7 autonomous.**

MarketOS is an AI-native marketing platform built on a 17-agent LangGraph pipeline. A marketer defines a goal ("Drive 500 signups for our webinar"), and MarketOS decomposes, executes, monitors, optimizes, and reports — autonomously, around the clock.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [LLM Provider Configuration](#llm-provider-configuration)
- [Pipeline Flow](#pipeline-flow)
- [Agent Reference](#agent-reference)
  - [Supervisor Agent](#1-supervisor-agent)
  - [Competitor Agent](#2-competitor-agent)
  - [SEO Agent](#3-seo-agent)
  - [Copy Agent](#4-copy-agent)
  - [Image Agent (Creative)](#5-image-agent-creative)
  - [Compliance Agent](#6-compliance-agent)
  - [Finance Agent](#7-finance-agent)
  - [Email Agent](#8-email-agent)
  - [SMS Agent](#9-sms-agent)
  - [Voice Agent](#10-voice-agent)
  - [Social Media Agent](#11-social-media-agent)
  - [Analytics Agent](#12-analytics-agent)
  - [Monitor Agent](#13-monitor-agent)
  - [A/B Test Agent](#14-ab-test-agent)
  - [Lead Scoring Agent](#15-lead-scoring-agent)
  - [Reporting Agent](#16-reporting-agent)
  - [Onboarding Agent](#17-onboarding-agent)
  - [Personalization Agent](#sub-agent-personalization)
- [Infrastructure](#infrastructure)
- [Project Structure](#project-structure)

---

## Architecture Overview

```
                        ┌──────────────────┐
                        │   User Intent    │
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Supervisor     │  Decomposes intent → campaign plan
                        └───┬──────────┬───┘
                            │          │
                   ┌────────▼──┐  ┌────▼────────┐
                   │ Competitor│  │  SEO Agent  │  Intel gathering (parallel)
                   └────────┬──┘  └────┬────────┘
                            │          │
                        ┌───▼──────────▼───┐
                        │    Copy Agent    │  Email copy variants
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Image Agent    │  Unsplash + Gemini Imagen
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Compliance      │  CAN-SPAM / GDPR gate
                        └────────┬─────────┘
                                 │ (approved)
                        ┌────────▼─────────┐
                        │  Finance Agent   │  Budget pacing gate
                        └────────┬─────────┘
                                 │ (within budget)
            ┌────────────────────┼────────────────────┐
            │                    │                    │
   ┌────────▼───┐    ┌──────────▼──────┐    ┌────────▼─────────┐
   │   Email    │ →  │   SMS Agent     │ →  │   Voice Agent    │
   └────────────┘    └─────────────────┘    └────────┬─────────┘
                                                     │
                                            ┌────────▼─────────┐
                                            │  Social Media    │
                                            └────────┬─────────┘
                                                     │
         ┌───────────────────────────────────────────┐│
         │                                           ││
   ┌─────▼──────┐  ┌──────────┐  ┌──────────┐  ┌────▼▼────┐  ┌───────────┐
   │ Analytics  │→ │ Monitor  │→ │ A/B Test │→ │Lead Score│→ │ Reporting │→ END
   └────────────┘  └──────────┘  └──────────┘  └──────────┘  └───────────┘
```

**Separate Pipeline B**: `Onboarding Agent → END` (triggered by new workspace signup).

The **Personalization Agent** is a sub-call invoked synchronously by Email/SMS agents per contact (not a pipeline node).

---

## Quick Start

```bash
# 1. Clone and set up
git clone https://github.com/DeepanIsCool/marketos.git
cd marketos

# 2. Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env   # Edit with your API keys

# 5. Start infrastructure (optional — falls back gracefully)
docker-compose up -d   # PostgreSQL, ClickHouse, Kafka, Redis

# 6. Run the demo pipeline
python demo_full_pipeline.py
```

## LLM Provider Configuration

All agents route through a single factory function: `agents/llm/llm_provider.py → get_llm()`. 

No agent touches API keys directly.

```python
# .env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemma-4-31b-it:free   # Free tier default
```

| Provider | Model | Use Case |
|---|---|---|
| `gemini` | `gemini-2.0-flash` | Development (fast, free tier available) |
| `anthropic` | `claude-sonnet-4` | High-quality creative copy |
| `openrouter` | Configurable via `OPENROUTER_MODEL` | **Production** — route to any model |

To switch providers in production, change **one line** in `.env`. Zero code changes needed.

---

## Pipeline Flow

The campaign graph is defined in `graph/campaign_graph.py` and compiles into a LangGraph `StateGraph`.

### Execution Order (Pipeline A — Campaign)

| Step | Agent(s) | Gate? | Routes To |
|---|---|---|---|
| 1 | Supervisor | — | Competitor + SEO (parallel) |
| 2 | Competitor + SEO | — | Copy Agent |
| 3 | Copy Agent | — | Image Agent |
| 4 | Image Agent | — | Compliance Agent |
| 5 | Compliance Agent | ✅ `compliance_router` | Finance Agent or `END` |
| 6 | Finance Agent | ✅ `finance_router` | Email Agent or `END` |
| 7 | Email Agent | — | SMS Agent |
| 8 | SMS Agent | — | Voice Agent |
| 9 | Voice Agent | — | Social Media Agent |
| 10 | Social Media Agent | — | Analytics Agent |
| 11 | Analytics Agent | — | Monitor Agent |
| 12 | Monitor Agent | — | A/B Test Agent |
| 13 | A/B Test Agent | — | Lead Scoring Agent |
| 14 | Lead Scoring Agent | — | Reporting Agent |
| 15 | Reporting Agent | — | `END` |

### Gate Agents

- **Compliance Agent**: Returns `approved: true/false`. If rejected, the campaign halts (`→ END`) with a reason code.
- **Finance Agent**: Returns `budget_ok: true/false`. If over budget (`>110%` of daily), campaign halts.

---

## Agent Reference

Every agent follows the **Agent Base Pattern** defined in `utils/agent_base.py`:

1. **Memory Pre-fetch**: Recalls relevant episodic memories before executing.
2. **Semantic Memory Injection**: Loads brand knowledge from pgvector.
3. **Kafka Events**: Publishes `task_started` and `task_completed` to Kafka topics.
4. **OpenTelemetry Tracing**: All LLM calls are traced (if OTel is configured).
5. **Reflection Loop**: Optional self-critique pass (Reflexion pattern).
6. **Circuit Breaker**: Wraps external API calls with failure threshold.
7. **Retry with Backoff**: Exponential backoff with jitter for transient failures.

---

### 1. Supervisor Agent

> **File**: `agents/supervisor/supervisor_agent.py`
> **Node**: `supervisor_node`

**Role**: The orchestrator. Receives raw user intent and decomposes it into a structured `CampaignPlan` — the single source of truth for all downstream agents.

| | |
|---|---|
| **Skills** | `product-marketing-context`, `launch-strategy`, `marketing-ideas`, `marketing-psychology` |
| **Temperature** | `0.0` (deterministic) |
| **SLA** | < 500ms |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `user_intent` | `str` | Raw campaign description from user |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `campaign_plan` | `dict` | Structured plan with `campaign_id`, `campaign_name`, `goal`, `target_audience`, `channels`, `budget`, `timeline`, `tone`, `key_messages`, `tasks` |
| `current_step` | `str` | → `copy_agent` |

**Kafka Topics**: `agent.supervisor.tasks`, `agent.supervisor.results`, `campaign.events`

---

### 2. Competitor Agent

> **File**: `agents/competitor/competitor_agent.py`
> **Node**: `competitor_agent_node`

**Role**: Gathers competitive intelligence via web scraping (Playwright), search APIs, and the Meta Ad Library. Produces a structured intel feed for the Copy Agent and Supervisor.

| | |
|---|---|
| **Skills** | `competitor-alternatives`, `customer-research`, `pricing-strategy` |
| **Temperature** | `0.1` |
| **SLA** | Daily schedule + on-demand |
| **Base Class** | `utils.agent_base.AgentBase` (legacy, full-featured) |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `campaign_plan` | `dict` | From Supervisor — uses `target_audience`, `campaign_name`, `goal` |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `competitor_result` | `dict` | Contains `search_results`, `scraped_intel`, `llm_analysis` (positioning, threats, opportunities) |

---

### 3. SEO Agent

> **File**: `agents/seo/seo_agent.py`
> **Node**: `seo_agent_node`

**Role**: Runs SEO audits, keyword research, and content gap analysis. Feeds keyword intelligence to the Copy Agent so email copy and landing pages are search-optimized.

| | |
|---|---|
| **Skills** | `seo-audit`, `ai-seo`, `programmatic-seo`, `schema-markup`, `site-architecture` |
| **Temperature** | `0.0` |
| **SLA** | Weekly schedule + on-demand |
| **Base Class** | `utils.agent_base.AgentBase` (legacy) |

**Input State**: `campaign_plan`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `seo_result` | `dict` | Keywords, content gaps, technical issues, schema recommendations |

---

### 4. Copy Agent

> **File**: `agents/copy/copy_agent.py`
> **Node**: `copy_agent_node`

**Role**: Expert email copywriter. Generates 2+ scored copy variants (subject line, preheader, body HTML, CTA) based on the campaign plan, competitor intel, and SEO keywords. Selects a winner based on estimated performance metrics.

| | |
|---|---|
| **Skills** | `copywriting`, `copy-editing`, `email-sequence`, `cold-email`, `content-strategy`, `marketing-psychology` |
| **Temperature** | `0.7` (creative) |
| **SLA** | < 8s |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `campaign_plan` | `dict` | Full plan from Supervisor |
| `competitor_result` | `dict` | Intel from Competitor Agent |
| `seo_result` | `dict` | Keywords from SEO Agent |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `copy_output` | `dict` | Contains `variants` (list of `CopyVariant`), `selected_variant_id`, `rationale` |

Each `CopyVariant` includes: `variant_id`, `subject_line`, `preheader`, `body_html`, `body_text`, `cta_text`, `estimated_open_rate`, `estimated_ctr`, `persona_match_score`.

**Kafka Topics**: `agent.copy_agent.results`

---

### 5. Image Agent (Creative)

> **File**: `agents/creative/image_engine.py`
> **Node**: `image_agent_node`

**Role**: Hybrid visual engine. Searches Unsplash for relevant photography, validates relevance via Gemini Vision, and falls back to Gemini Imagen 4 for AI-generated images. Injects the final image into the winning HTML email variant.

| | |
|---|---|
| **Temperature** | N/A (vision + image generation) |
| **SLA** | < 30s |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `copy_output` | `dict` | Uses `variants` and `selected_variant_id` to find the winner |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `copy_output` | `dict` | **Mutated** — winner variant's `body_html` now contains the embedded image (`<img>` tag with base64 or Unsplash URL) |

**Pipeline**: `Unsplash search → Gemini Vision relevance check → Gemini Imagen 4 fallback → HTML injection`

---

### 6. Compliance Agent

> **File**: `agents/compliance/compliance_agent.py`
> **Node**: `compliance_agent_node`
> **Router**: `compliance_router`

**Role**: The legal firewall. Every campaign is gated through this agent. No email or SMS goes out without compliance approval. Checks CAN-SPAM, GDPR, DKIM/SPF/DMARC, suppression lists, and content guidelines.

| | |
|---|---|
| **Skills** | `copy-editing`, `product-marketing-context` |
| **Temperature** | `0.0` (deterministic legal checks) |
| **SLA** | < 500ms |
| **Gate** | ✅ Can halt pipeline |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `campaign_plan` | `dict` | Plan metadata |
| `copy_output` | `dict` | Copy to review for compliance |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `compliance_result` | `dict` | `approved: bool`, `score: float`, `checks: list[ComplianceCheck]`, `reason_code: str` |
| `copy_output` | `dict` | **Mutated** — CAN-SPAM footer injected if missing |

**Routing**: If `approved=false`, pipeline goes to `END`. Otherwise → `finance_agent`.

---

### 7. Finance Agent

> **File**: `agents/finance/finance_agent.py`
> **Node**: `finance_agent_node`
> **Router**: `finance_router`

**Role**: Two roles: (1) **Pre-send gate** — checks budget isn't exhausted/overpacing (blocks if spend > 110% of daily budget), and (2) **ROI attribution** — calculates ROAS, CPA, and channel-level breakdown.

| | |
|---|---|
| **Skills** | `pricing-strategy`, `revops`, `paid-ads` |
| **Temperature** | `0.0` |
| **SLA** | Hourly + overspend trigger |
| **Gate** | ✅ Can halt pipeline |

**Sub-skills**: `BudgetPacingSkill`, `ROASCalculatorSkill`, `CurrencyNormSkill`

**Input State**: `campaign_plan`, `analytics_result` (when available)

**Output State**:
| Key | Type | Description |
|---|---|---|
| `finance_result` | `dict` | `budget_ok: bool`, `daily_budget`, `spent_today`, `spend_pct`, `roas`, `cpa` |

**Routing**: If `budget_ok=false`, pipeline goes to `END`. Otherwise → `email_agent`.

---

### 8. Email Agent

> **File**: `agents/email/email_agent.py`
> **Node**: `email_agent_node`

**Role**: Executes the approved campaign. Sends real emails via SendGrid (or SMTP/Gmail fallback). Calls the Personalization Agent per-contact before each send. Stores delivery records in PostgreSQL.

| | |
|---|---|
| **Skills** | `email-sequence`, `copy-editing` |
| **Temperature** | `0.0` |
| **SLA** | Real-time |

**Input State**:
| Key | Type | Description |
|---|---|---|
| `campaign_plan` | `dict` | Plan with audience info |
| `copy_output` | `dict` | Compliance-approved copy with images |
| `recipient_email` | `str` | Target email address |
| `sender_name` | `str` | From name |
| `company_name` | `str` | For CAN-SPAM footer |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `send_result` | `dict` | `message_id`, `status`, `delivery_method`, `personalized` |

**Kafka Topics**: `contact.events` (delivery events)

---

### 9. SMS Agent

> **File**: `agents/sms/sms_agent.py`
> **Node**: `sms_agent_node`

**Role**: Generates SMS copy adapted from the email campaign, then sends via Twilio. Checks opt-out registry, manages character limits (160/GSM-7), and handles delivery receipts.

| | |
|---|---|
| **Skills** | `copywriting`, `marketing-psychology` |
| **Temperature** | `0.5` |
| **SLA** | Real-time |
| **Base Class** | `utils.agent_base.AgentBase` (legacy) |

**Input State**: `campaign_plan`, `copy_output`, `recipient_phone`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `sms_result` | `dict` | `message_sid`, `status`, `body_text`, `char_count`, `segments` |

---

### 10. Voice Agent

> **File**: `agents/voice/voice_agent.py` (orchestration) + `agents/voice/voice_daemon.py` (execution)
> **Node**: `voice_agent_node`

**Role**: Bidirectional voice AI. Generates a conversational persona and talking points, stores instructions in Redis, and dispatches an outbound Twilio call. The Voice Daemon bridges Twilio audio ↔ Gemini 2.5 Flash Native Audio in real-time via WebSockets.

| | |
|---|---|
| **Skills** | `voice-marketing`, `copywriting` |
| **Temperature** | `0.4` |
| **Voice Model** | `models/gemini-2.5-flash-native-audio-latest` |

**Architecture**:
1. LangGraph node generates persona + system instruction
2. Stored in Redis keyed by `campaign_id`
3. Twilio `calls.create()` with `<Connect><Stream>` TwiML pointing to daemon's ngrok tunnel
4. Daemon bridges Twilio µ-law 8kHz ↔ Gemini PCM 24kHz audio

**Input State**: `campaign_plan`, `copy_output`, `recipient_phone`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `voice_result` | `dict` | `call_sid`, `status`, `persona_name`, `daemon_url`, `model` |

**Daemon**: Run separately: `uvicorn agents.voice.voice_daemon:app --host 0.0.0.0 --port 8765`

---

### 11. Social Media Agent

> **File**: `agents/social/social_media_agent.py`
> **Node**: `social_media_agent_node`

**Role**: Generates platform-specific social posts (Instagram, LinkedIn, X/Twitter, Meta) derived from the winning email copy. Handles character limits, hashtag optimization, and aspect ratios per platform.

| | |
|---|---|
| **Skills** | `social-content`, `community-marketing`, `content-strategy`, `marketing-psychology` |
| **Temperature** | `0.6` |
| **SLA** | Scheduled |
| **Base Class** | `utils.agent_base.AgentBase` (legacy) |

**Input State**: `campaign_plan`, `copy_output`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `social_result` | `dict` | Per-platform posts with `caption`, `hashtags`, `media_url`, `optimal_post_time` |

---

### 12. Analytics Agent

> **File**: `agents/analytics/analytics_agent.py`
> **Node**: `analytics_agent_node`

**Role**: Polls ClickHouse for campaign performance metrics. Detects anomalies (open rate collapse, bounce spike, spam surge). Can run as a standalone daemon for 5-minute polling in production.

| | |
|---|---|
| **Skills** | `analytics-tracking`, `revops`, `ab-test-setup` |
| **Temperature** | `0.0` |
| **SLA** | 5 minutes (daemon) / immediate (pipeline) |

**Input State**: `campaign_plan`, `send_result`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `analytics_result` | `dict` | `metrics` (opens, clicks, bounces, spam), `anomalies`, `snapshot_id` |

**Kafka Topics**: `system.metrics`, `system.alerts`

---

### 13. Monitor Agent

> **File**: `agents/monitor/monitor_agent.py`
> **Node**: `monitor_agent_node`

**Role**: "The heartbeat of the 24/7 promise." Evaluates anomalies from Analytics and triggers escalations. Three tiers: INFO (Slack), WARNING (email + Slack), CRITICAL (auto-remediation + PagerDuty + Supervisor).

| | |
|---|---|
| **Skills** | `analytics-tracking`, `revops` |
| **Temperature** | `0.0` |
| **SLA** | < 30s (breach → action) |

**Auto-Remediation Playbooks**:
- `SPAM_RATE_HIGH` → Pause campaign domain, switch to backup
- `SMS_FAILURE` → Failover provider (Twilio → Vonage → SNS)
- `BUDGET_OVERPACE` → Cap spend via Ads API

**Input State**: `campaign_plan`, `analytics_result`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `monitor_result` | `dict` | `health_status`, `alerts` list, `auto_remediation_actions`, `escalation_tier` |

---

### 14. A/B Test Agent

> **File**: `agents/ab_test/ab_test_agent.py`
> **Node**: `ab_test_agent_node`

**Role**: Runs Bayesian A/B statistical tests (not naive open-rate comparison). Declares winners, suppresses losers mid-campaign, and writes learnings to episodic memory for the Copy Agent to learn from.

| | |
|---|---|
| **Skills** | `ab-test-setup`, `analytics-tracking`, `page-cro` |
| **Temperature** | `0.0` |
| **SLA** | Event-driven (100+ opens threshold) |

**Sub-skills**:
- `BayesianStatsSkill` — Beta-distribution Monte Carlo (10,000 draws, pure Python)
- `SampleSizeCalculator` — MDE-based minimum sample sizing
- `EarlyStoppingRule` — Declares winner early if P(best) ≥ 0.95

**Input State**: `campaign_plan`, `copy_output`, `analytics_result`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `ab_test_result` | `dict` | `test_id`, `winner_id`, `decision`, `confidence`, `key_learning`, `copy_insight` |

**Memory**: Stores winning patterns to `episodic_memory` under `copy_agent` so future campaigns incorporate learnings.

---

### 15. Lead Scoring Agent

> **File**: `agents/lead_scoring/lead_scoring_agent.py`
> **Node**: `lead_scoring_agent_node`

**Role**: Scores contacts based on engagement events (opens, clicks, page visits, purchases). Manages the subscriber → MQL → SQL → opportunity → customer lifecycle. Pushes score updates to CRM via webhook.

| | |
|---|---|
| **Skills** | `revops`, `sales-enablement`, `customer-research` |
| **Temperature** | `0.0` |
| **SLA** | < 2s/event |

**Sub-skills**:
- `ScoreDecaySkill` — Halves score every 30 days of inactivity
- `BehaviourPatternSkill` — Detects buying signals (3+ clicks in 24h, pricing page visits)
- `StageMachineSkill` — subscriber → MQL (50pts) → SQL (100pts) → opportunity → customer
- `CRMWebhookSkill` — HubSpot/Pipedrive/Salesforce webhook push

**Input State**: `campaign_plan`, `analytics_result`

**Output State**:
| Key | Type | Description |
|---|---|---|
| `lead_scoring_result` | `dict` | `contacts_scored`, `stage_distribution`, `new_mqls`, `new_sqls`, `summary` |

**Kafka Escalation**: Publishes to `agent.supervisor.tasks` when MQL/SQL threshold crossed.

---

### 16. Reporting Agent

> **File**: `agents/reporting/reporting_agent.py`
> **Node**: `reporting_agent_node`

**Role**: Aggregates all pipeline results into a comprehensive campaign performance report. Generates executive summaries, channel breakdowns, and LLM-powered recommendations.

| | |
|---|---|
| **Skills** | `analytics-tracking`, `revops`, `copy-editing` |
| **Temperature** | `0.3` |
| **SLA** | < 60s |
| **Reflection** | Enabled (verifies report before publishing) |
| **Base Class** | `utils.agent_base.AgentBase` (legacy) |

**Input State**: All prior agent results (`campaign_plan`, `analytics_result`, `ab_test_result`, `lead_scoring_result`, etc.)

**Output State**:
| Key | Type | Description |
|---|---|---|
| `reporting_result` | `dict` | `report_id`, `executive_summary`, `channel_performance`, `recommendations`, `next_campaign_suggestions` |

---

### 17. Onboarding Agent

> **File**: `agents/onboarding/onboarding_agent.py`
> **Node**: `onboarding_agent_node`

**Role**: Creates personalized onboarding plans for new workspaces. Classifies the workspace type (ecommerce/SaaS/agency/creator), builds a 7-day activation drip sequence, generates setup task lists, and predicts churn risks.

| | |
|---|---|
| **Skills** | `onboarding-cro`, `churn-prevention`, `lead-magnets`, `email-sequence` |
| **Temperature** | `0.5` |
| **SLA** | Event-driven (new signup) |
| **Pipeline** | **B** (separate from campaigns) |
| **Base Class** | `utils.agent_base.AgentBase` (legacy) |

**Sub-skills**:
- `WorkspaceClassifierSkill` — ecommerce / SaaS / agency / creator / general
- `DripSequenceBuilderSkill` — 7-day activation sequence with milestones
- `MilestoneTrackerSkill` — Tracks first_campaign_sent, analytics_connected, etc.
- `TaskListGeneratorSkill` — Setup checklist per workspace type

**Input State**:
| Key | Type | Description |
|---|---|---|
| `user_name` | `str` | New user's name |
| `user_email` | `str` | New user's email |
| `company_name` | `str` | Company name for classification |
| `industry` | `str` | Industry hint |

**Output State**:
| Key | Type | Description |
|---|---|---|
| `onboarding_result` | `dict` | `onboarding_id`, `workspace_type`, `drip_sequence`, `task_list`, `plan`, `milestones_done` |

---

### Sub-Agent: Personalization

> **File**: `agents/personalization/personalization_agent.py`
> **Function**: `personalize_for_contact()`

**Role**: Called synchronously by Email/SMS agents before every send. Uses a fast-path (token injection, no LLM) for contacts with thin profiles, and a full LLM rewrite for contacts with rich behavioral data. This keeps the < 3s SLA even at volume.

| | |
|---|---|
| **Skills** | `marketing-psychology`, `customer-research`, `copywriting` |
| **Temperature** | `0.3` |
| **SLA** | < 3s/contact |
| **Pipeline Node** | **No** — called as a sub-function |

**Sub-skills**: `ContactProfileSkill`, `LanguageDetectSkill`, `SegmentFallbackSkill`, `TokenInjectorSkill`

---

## Infrastructure

MarketOS uses a Docker Compose stack for local development:

| Service | Purpose | Port |
|---|---|---|
| **PostgreSQL + pgvector** | Campaigns, copy variants, audit logs, contact scores, episodic + semantic memory | 5433 |
| **ClickHouse** | Real-time analytics metrics, time-series campaign data | 9000 |
| **Apache Kafka (Redpanda)** | Inter-agent event bus, 11+ topics | 9092 |
| **Redis** | Working memory, task contexts, voice daemon tunnel URL | 6379 |

All services are **optional**. When unavailable, agents degrade gracefully:
- No PostgreSQL → In-memory dicts for memory
- No Kafka → Logging-based event simulation
- No Redis → Dict fallback for working memory
- No ClickHouse → Simulated campaign metrics

---

## Project Structure

```
marketos/
├── agents/
│   ├── llm/
│   │   └── llm_provider.py       # Central LLM factory (Gemini/Anthropic/OpenRouter)
│   ├── supervisor/
│   │   └── supervisor_agent.py
│   ├── copy/
│   │   └── copy_agent.py
│   ├── creative/
│   │   └── image_engine.py
│   ├── email/
│   │   └── email_agent.py
│   ├── sms/
│   │   └── sms_agent.py
│   ├── voice/
│   │   ├── voice_agent.py        # LangGraph node (orchestration)
│   │   └── voice_daemon.py       # FastAPI daemon (real-time audio bridge)
│   ├── social/
│   │   └── social_media_agent.py
│   ├── compliance/
│   │   └── compliance_agent.py
│   ├── finance/
│   │   └── finance_agent.py
│   ├── analytics/
│   │   └── analytics_agent.py
│   ├── monitor/
│   │   └── monitor_agent.py
│   ├── ab_test/
│   │   └── ab_test_agent.py
│   ├── lead_scoring/
│   │   └── lead_scoring_agent.py
│   ├── personalization/
│   │   └── personalization_agent.py
│   ├── reporting/
│   │   └── reporting_agent.py
│   ├── onboarding/
│   │   └── onboarding_agent.py
│   └── competitor/
│       └── competitor_agent.py
├── core/
│   ├── agent_base.py              # Lightweight skill-management base class
│   └── skill_loader.py            # Dynamic SKILL.md loader
├── graph/
│   └── campaign_graph.py          # LangGraph StateGraph definition
├── schemas/
│   └── campaign.py                # Pydantic models (CampaignPlan, CopyVariant, etc.)
├── utils/
│   ├── agent_base.py              # Production agent base (memory, Kafka, OTel, circuit breaker)
│   ├── kafka_bus.py               # Confluent Kafka publisher
│   ├── memory.py                  # pgvector episodic + semantic memory
│   ├── sendgrid_mailer.py         # Email delivery abstraction
│   ├── clickhouse_sink.py         # ClickHouse analytics writer
│   ├── json_utils.py              # Safe JSON extraction from LLM output
│   ├── logger.py                  # Structured terminal logging
│   └── dlq_handler.py             # Dead letter queue handler
├── infra/
│   ├── init_postgres.sql          # Schema: campaigns, contacts, audit_log, memory
│   ├── init_clickhouse.sql        # Schema: campaign_metrics time-series
│   ├── create_topics.sh           # Kafka topic provisioning script
│   └── ...
├── tests/                         # Unit + integration tests
├── api.py                         # FastAPI HTTP API layer
├── main.py                        # CLI entrypoint
├── worker.py                      # Kafka consumer worker
├── demo_full_pipeline.py          # End-to-end demo runner
├── docker-compose.yml             # Full infrastructure stack
└── requirements.txt               # Python dependencies
```

---

## License

Proprietary — DeepMarkAI © 2024-2026
