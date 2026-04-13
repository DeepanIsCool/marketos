# MARKETOS TEST SUITE — AGENT EXECUTION PROMPT

## YOUR ROLE
You are a senior QA engineer. Your job is to:
1. Run the test suite in the correct order
2. Fix any failures you find
3. Report what is still simulated vs actually working

---

## SETUP — RUN ONCE BEFORE TESTS

```bash
# 1. Start all Docker services
docker compose up -d

# 2. Wait for services to be healthy
docker compose ps  # all must show "healthy"

# 3. Create Kafka topics with correct config
bash infra/create_topics.sh

# 4. Run schema migrations (HNSW indexes)
docker compose exec postgres psql -U marketos -d marketos -f /docker-entrypoint-initdb.d/01_init.sql

# 5. Run Phase 3+4 schema additions
docker compose exec postgres psql -U marketos -d marketos < infra/init_phase3.sql
docker compose exec postgres psql -U marketos -d marketos < infra/init_phase4.sql

# 6. Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio --break-system-packages
```

---

## RUN ORDER — ALWAYS IN THIS SEQUENCE

### STEP 1 — Smoke tests (no LLM, no Docker, instant)
```bash
pytest tests/test_graph_import.py -v
```
**If this fails:** Fix the import error before running anything else.
Common causes: bare `import psycopg2` without guard, syntax error, missing module.

### STEP 2 — Unit tests (LLM required, no Docker)
```bash
pytest tests/ -m unit -v --tb=short -x
```
**Flags:** `-x` stops on first failure. Remove it to see all failures at once.

### STEP 3 — Integration tests (Docker required)
```bash
pytest tests/test_integration_db.py tests/test_integration_memory.py \
       tests/test_integration_kafka.py tests/test_integration_clickhouse.py \
       -m integration -v --tb=short
```

### STEP 4 — E2E tests (everything required, slow ~5 min)
```bash
pytest tests/test_e2e_pipeline.py -m e2e -v --tb=short -s
```

### STEP 5 — Real email send test (set env var first)
```bash
TEST_RECIPIENT_EMAIL=your@email.com pytest tests/test_e2e_pipeline.py::test_real_email_send -v -s
```

---

## CODEBASE FIXES STILL NEEDED

Fix these before running tests. Each fix is small and isolated.

### FIX A — CampaignState TypedDict missing fields (graph/campaign_graph.py)
The email agent uses `state.get("contact_id")` and `state.get("contact_list")`
but these are not declared in CampaignState. Add them:

```python
# In class CampaignState(TypedDict), add:
contact_id:    Optional[str]
contact_list:  Optional[list]
```

### FIX B — Remove compliance force-pass hack (agents/compliance/compliance_agent.py)
This line bypasses compliance for any VoltX campaign — dangerous for production:
```python
# REMOVE THIS BLOCK entirely:
force_pass = "VoltX" in plan.campaign_name
if force_pass:
    agent_log("COMPLIANCE", "⚠  FORCING PASS for Boss Demo (VoltX campaign detected)")
    result.approved = True
```
The deterministic CAN-SPAM checks (footer injection) already ensure VoltX campaigns pass legitimately.

### FIX C — schemas/campaign.py has duplicate content
The file defines `BaseModel` and imports twice (Phase 1 at top, Phase 3 at bottom).
Fix: remove the duplicate `from pydantic import BaseModel, Field` and `from typing import ...`
block at line ~100. Keep only the Phase 3 model classes (BudgetCheck, ROIAttribution, etc.).

### FIX D — ClickHouse sink must run for real analytics
Analytics agent needs the sink running to get real data instead of simulation.
Start it in a separate terminal before running campaigns:
```bash
python infra/start_ch_sink.py
```
Or add it to docker-compose.yml as a Python service.

### FIX E — Finance agent never records spend
`campaign_spend` table stays at ₹0 forever. After email_agent sends, add:
```python
# In email_agent_node(), after send_email() succeeds:
_record_email_send_cost(plan.campaign_id, workspace_id, total_sends)
```
Add this helper to email_agent.py:
```python
def _record_email_send_cost(campaign_id: str, workspace_id: str, sends: int) -> None:
    if not PG_AVAILABLE:
        return
    # Assume ₹0.50 per email send (SendGrid pricing approx)
    cost = sends * 0.50
    try:
        conn = psycopg2.connect(PG_DSN)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO campaign_spend (campaign_id, workspace_id, channel, amount_inr, conversions)
                VALUES (%s, %s, 'email', %s, 0)
            """, (campaign_id, workspace_id, cost))
        conn.commit()
        conn.close()
    except Exception as e:
        agent_log("EMAIL", f"Spend record failed (non-fatal): {e}")
```

---

## WHAT IS ACTUALLY WORKING vs SIMULATED

### ✅ ACTUALLY WORKING (proven end-to-end)
- Email send via SMTP + SendGrid fallback
- SMS send via MSG91 → Twilio failover chain
- Personalization (fast-path token injection always; LLM path when contact profile is rich)
- Compliance footer injection (deterministic, LLM-independent)
- A/B Bayesian stats (pure Python, no scipy)
- Lead scoring with DB persistence
- Copy variant DB write (copy_variants table)
- A/B stats seeding (ab_variant_stats table)
- Kafka event bus (in-memory fallback when Redpanda is down)
- pgvector memory (episodic + semantic with HNSW index)
- PDF report generation (ReportLab)
- Competitor intel via Serper.dev (requires SERPER_API_KEY)
- SEO + Competitor running in parallel (LangGraph fan-out)
- Finance budget gate (blocks when spend > 110% of budget)
- Monitor auto-remediation playbooks (publishes to Kafka)
- Onboarding drip sequence + task list

### ⚠ SIMULATED / INCOMPLETE
| What | Why | How to fix |
|------|-----|-----------|
| ClickHouse analytics | Sink runs separately, not auto-started | Run `python infra/start_ch_sink.py` |
| Social media publishing | No META_PAGE_ACCESS_TOKEN, LINKEDIN_ACCESS_TOKEN etc. | Set env vars |
| GSC (SEO) data | No GOOGLE_OAUTH_TOKEN | Set env var or accept sim |
| Finance spend tracking | Never writes to campaign_spend | Fix E above |
| Unsplash images | Needs UNSPLASH_ACCESS_KEY | Set env var |
| Gemini Imagen | Needs GEMINI_API_KEY (different from text gen) | Same key works |
| CRM webhook (lead scoring) | Needs CRM_WEBHOOK_URL | Set env var for HubSpot/Pipedrive |
| PagerDuty alerts | Monitor agent publishes to Kafka but no real PD call | Wire urllib.request call |

---

## ENV VARS CHECKLIST
Confirm these are set in .env before running full pipeline:

```
# Required for LLM (at least one)
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...    # optional, if LLM_PROVIDER=anthropic

# Required for email send
SMTP_EMAIL=...           # or SENDGRID_API_KEY + SENDGRID_FROM_EMAIL
SMTP_PASSWORD=...

# Required for SMS (at least one)
MSG91_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...

# Optional but enables real functionality
SERPER_API_KEY=...       # competitor agent live search
UNSPLASH_ACCESS_KEY=...  # real images in emails
META_PAGE_ACCESS_TOKEN=... # Facebook/Instagram publishing
LINKEDIN_ACCESS_TOKEN=... # LinkedIn publishing
CRM_WEBHOOK_URL=...      # lead score pushes to HubSpot/Pipedrive
SLACK_WEBHOOK_URL=...    # DLQ handler notifications
GOOGLE_OAUTH_TOKEN=...   # GSC data for SEO agent

# Infrastructure (defaults work for docker-compose)
DATABASE_URL=postgresql://marketos:marketos_dev@localhost:5433/marketos
REDIS_URL=redis://localhost:6379/0
KAFKA_BROKERS=localhost:9092
CLICKHOUSE_HOST=localhost
```

---

## TEST FAILURE QUICK REFERENCE

| Error | File | Fix |
|-------|------|-----|
| `NameError: recipient` | reporting_agent.py | Already fixed — check line ~140 |
| `ModuleNotFoundError: psycopg2` | any agent | Already has try/except guard — check pip install |
| `KeyError: contact_list` | email_agent.py | Add to CampaignState TypedDict (Fix A) |
| `AssertionError: PDF too small` | test_reporting.py | ReportLab not installed: `pip install reportlab` |
| `AssertionError: Must publish ≥16 events` | test_e2e | Normal if pipeline errored earlier |
| `AssertionError: All 16 agents ran` | test_e2e | Check trace — which agent is missing from run |
| `HNSW index must exist` | test_integration_db.py | Run migrate_hnsw.sql migration |
| `Topic agent.dlq must exist` | test_integration_kafka.py | Run infra/create_topics.sh |
