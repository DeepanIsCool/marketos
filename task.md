```
# MARKETOS AUTONOMOUS MARKETING PLATFORM — ENGINEERING FIX PROMPT

## CODEBASE CONTEXT
You are working on MarketOS, a 16-agent autonomous marketing operations platform built on:
- **LangGraph** (Python 3.12) for agent orchestration
- **Apache Kafka** (Redpanda local) for inter-agent messaging
- **PostgreSQL 16 + pgvector** for OLTP + vector memory
- **ClickHouse** for analytics OLAP
- **Redis 7** for working memory + distributed locks
- **FastAPI** API layer + background Worker
- **LLM**: Google Gemini 2.0 Flash (via LangChain)

The pipeline executes 16 specialized agents in sequence:
supervisor → competitor → copy → image → compliance → finance → email → sms → social → analytics → monitor → ab_test → lead_scoring → seo → reporting → END

All agents communicate via a typed LangGraph state dict. Agents are Python classes inheriting AgentBase or standalone node functions. The project root contains: agents/, graph/, schemas/, utils/, infra/, api.py, worker.py, demo_full_pipeline.py.

---

## YOUR ROLE
You are a FAANG-level senior engineer. You do not improvise. Before writing any code:
1. Fetch the official documentation for every library you touch
2. Read the existing file completely before editing it
3. Make surgical edits — do not rewrite files that don't need it
4. After each fix, verify the fix is consistent with all files that import the changed module

---

## DOCUMENTATION TO FETCH BEFORE STARTING

Fetch these URLs and read them before writing any code:

```

https://langchain-ai.github.io/langgraph/reference/graphs/
https://python.langchain.com/docs/concepts/structured_outputs/
https://docs.sendgrid.com/for-developers/sending-email/v3-mail-send-overview
https://clickhouse.com/docs/en/integrations/python
https://github.com/confluentinc/confluent-kafka-python/blob/master/README.md
https://pgvector.github.io/pgvector/
https://docs.pydantic.dev/latest/concepts/models/
https://docs.anthropic.com/en/docs/build-with-claude/tool-use

````

---

## FIXES — EXECUTE IN THIS EXACT ORDER

### FIX 1 — CRITICAL: reporting_agent.py (3 undefined variables crash)
**File:** `agents/reporting/reporting_agent.py`

**Problem:** Three `NameError` crashes at runtime:
- `recipient` is never defined in `execute()` scope
- `html` is never defined (PDF is generated as `pdf_path` but a separate HTML email body is referenced as `html` which doesn't exist)
- `report_path` is used in `kv()` but the variable is named `pdf_path`

**Fix:**
1. Add `recipient = state.get("recipient_email")` near the top of `execute()`, after plan extraction
2. Build a minimal HTML string for the email body from `insights` dict (subject + executive summary + grade + top insights as `<ul>` — no external template needed)
3. Replace `report_path` with `pdf_path` in the `kv()` call
4. Confirm `send_email()` is only called when `recipient` is not None

Do NOT change the PDF generation logic. Do NOT change the ReportLab code.

---

### FIX 2 — CRITICAL: Personalization Agent wire-up
**File:** `agents/email/email_agent.py`
**Reference file (do not edit):** `agents/personalization/personalization_agent.py`

**Problem:** `personalize_for_contact()` exists but is never called. Every email is sent with generic un-personalized copy, silently violating PRD §2.1 (SLA < 3s/contact, called synchronously pre-send).

**Fix:**
1. Import `personalize_for_contact` from `agents.personalization.personalization_agent`
2. After `selected` variant is resolved and before `send_email()` is called, call:
```python
personalized = personalize_for_contact(
    contact_id=recipient or "default",
    variant=selected.model_dump(),
    campaign_plan=plan_data,
    contact_data=None,  # will trigger fast-path for unknown contacts
)
````

3. Use `personalized["subject_line"]`, `personalized["body_html"]` for the actual send
4. Keep the original `selected` fields for logging/Kafka events (don't mutate the state copy_output)
5. Add a `kv("Personalization", ...)` log line showing which signals were used

---

### FIX 3 — CRITICAL: copy_variants DB INSERT missing

**File:** `agents/copy/copy_agent.py`

**Problem:** Generated variants are never written to the `copy_variants` PostgreSQL table. The A/B test agent queries this table and always gets empty results.

**Fix:**

1. Add `psycopg2` import with the same try/except guard pattern used in other agents
2. After `copy_output` is validated and `selected` is resolved, add a DB write function `_save_variants_to_db(campaign_id, variants)` that does a batch INSERT into `copy_variants` using `executemany` with `ON CONFLICT DO NOTHING`
3. Include all scored fields: `variant_id, subject_line, preview_text, body_html, body_text, cta_text, readability_score, tone_alignment_score, spam_risk_score, estimated_open_rate, estimated_ctr, is_winner`
4. Set `is_winner = TRUE` only for `selected_variant_id`
5. Wrap in try/except — DB failure must NOT block the pipeline

---

### FIX 4 — CRITICAL: monitor_agent.py bare psycopg2 import

**File:** `agents/monitor/monitor_agent.py`

**Problem:** `import psycopg2` and `import psycopg2.extras` are at module level with no guard. If psycopg2 is not installed, the entire graph import fails.

**Fix:**
Replace the top-level imports with the same guard pattern every other agent uses:

```python
try:
    import psycopg2
    import psycopg2.extras
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
```

Then wrap every `psycopg2.connect()` call with `if not PG_AVAILABLE: return` (same pattern as `ab_test_agent.py`).

---

### FIX 5 — HIGH: ClickHouse Kafka Sink Consumer (new file)

**New file:** `utils/clickhouse_sink.py`
**New file:** `infra/start_ch_sink.py`

**Problem:** Analytics agent queries ClickHouse for real metrics but zero agents write to it. Every analytics run uses simulated data.

**Fix:**
Create a standalone Kafka consumer that:

1. Subscribes to `contact.events` topic (where email_agent publishes send events)
2. For each message with `event_type` in `["email_sent", "email_open", "email_click", "bounce", "spam_complaint"]`, writes a row to `email_events_local` in ClickHouse
3. Uses `clickhouse_driver.Client` — fetch docs at https://clickhouse-driver.readthedocs.io/en/latest/
4. Batches inserts: accumulate 100 events OR 5 seconds, then flush — never insert row-by-row
5. Handles schema: `event_id (UUID), campaign_id, workspace_id, contact_id, event_type (Enum), provider, timestamp (DateTime64)`
6. Maps email_agent Kafka payload fields to ClickHouse columns explicitly — document the mapping in a comment
7. Gracefully handles ClickHouse unavailability (log + skip, don't crash)
8. `infra/start_ch_sink.py` is a simple `__main__` runner for this consumer

Also update `analytics_agent.py`: after the ClickHouse query, if the result returns all zeros AND we have `send_result` in state with a real `message_id`, log a warning: "ClickHouse sink may be lagging — metrics may be incomplete" instead of silently falling back to simulation.

---

### FIX 6 — HIGH: ab_variant_stats population

**File:** `agents/email/email_agent.py`

**Problem:** `ab_variant_stats` table is never populated so A/B test agent always uses simulated random data.

**Fix:**
After the send confirmation (after `send_email()` call), insert initial stats rows for each variant into `ab_variant_stats`:

```sql
INSERT INTO ab_variant_stats (campaign_id, workspace_id, variant_id, sends, opens, clicks, conversions)
VALUES (%s, %s, %s, %s, 0, 0, 0)
ON CONFLICT (campaign_id, variant_id) DO UPDATE SET sends = ab_variant_stats.sends + EXCLUDED.sends
```

Use `simulated_recipients` from the send strategy (default 25000 split equally across variants) as the initial `sends` count.
Wrap in try/except. Do NOT block send on DB failure.

---

### FIX 7 — HIGH: pgvector index — switch IVFFlat to HNSW

**File:** `infra/init_postgres.sql`

**Problem:** IVFFlat requires training data to build meaningful index. On fresh/small datasets it degrades to full scan. HNSW works correctly at any scale.

**Fix:**
Replace both index definitions:

```sql
-- REPLACE THIS:
CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- WITH THIS:
CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

Do this for BOTH `agent_episodic_memory` and `agent_semantic_memory` tables.
Also add a migration file `infra/migrate_hnsw.sql` that drops old indexes and creates new ones — for existing deployments:

```sql
DROP INDEX IF EXISTS idx_episodic_embedding;
DROP INDEX IF EXISTS idx_semantic_embedding;
CREATE INDEX idx_episodic_embedding ON agent_episodic_memory USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_semantic_embedding ON agent_semantic_memory USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

---

### FIX 8 — MEDIUM: finance_router key naming

**File:** `agents/finance/finance_agent.py`

**Problem:** `finance_router` returns `"personalization_agent"` but personalization is not a graph node — it's a sub-call inside email_agent. The routing key in `campaign_graph.py` maps `"personalization_agent"` → `"email_agent"` which works but is misleading and a maintenance trap.

**Fix:**
Change `finance_router` to return `"email_agent"` directly:

```python
def finance_router(state: dict) -> str:
    result = state.get("finance_result", {})
    if result.get("approved", True):
        return "email_agent"
    return "end"
```

Update `campaign_graph.py` conditional edges dict to match:

```python
g.add_conditional_edges("finance_agent", finance_router,
    {"email_agent": "email_agent", "end": END})
```

---

### FIX 9 — MEDIUM: Kafka topic pre-creation script

**New file:** `infra/create_topics.sh`

**Problem:** Redpanda auto-creates topics with defaults (1 partition, no retention config). PRD requires dead-letter queue and exactly-once semantics.

**Fix:**
Create a bash script that uses `rpk` to create all topics with proper config:

```bash
#!/bin/bash
# Run after: docker compose up -d redpanda
BROKER="localhost:9092"
TOPICS=(
  "agent.supervisor.tasks:3:1"
  "agent.supervisor.results:1:1"
  "campaign.events:3:1"
  "contact.events:6:1"
  "system.alerts:1:1"
  "system.metrics:3:1"
  "campaign.send.stats:3:1"
  "agent.dlq:1:1"
  # add all agent task/result topics
)
for ENTRY in "${TOPICS[@]}"; do
  IFS=':' read -r TOPIC PARTITIONS REPLICAS <<< "$ENTRY"
  rpk topic create "$TOPIC" \
    --brokers "$BROKER" \
    --partitions "$PARTITIONS" \
    --replicas "$REPLICAS" \
    --topic-config retention.ms=604800000 \
    --topic-config cleanup.policy=delete 2>/dev/null || echo "Topic $TOPIC already exists"
done
echo "All topics created."
```

Add DLQ-specific config: `--topic-config retention.ms=-1` (infinite retention for dead letters).

---

### FIX 10 — MEDIUM: entry_router no-op node removal

**File:** `graph/campaign_graph.py`

**Problem:** `entry_router` is a lambda that returns state unchanged — a superfluous node that adds a trace entry and latency.

**Fix:**
Remove the `entry_router` node. Use LangGraph's conditional start pattern:

```python
from langgraph.graph import START

g.add_conditional_edges(START, pipeline_router,
    {"supervisor": "supervisor", "onboarding_agent": "onboarding_agent"})
```

Remove `g.set_entry_point("entry_router")` and `g.add_node("entry_router", ...)`.
Verify `pipeline_router` function signature is compatible with LangGraph's conditional edge from START (it receives state dict — no change needed).

---

## SYSTEM DESIGN IMPROVEMENTS (implement after all fixes above)

### IMPROVEMENT A — Async Personalization for bulk sends

**File:** `agents/email/email_agent.py`

Currently personalization is synchronous per-contact (fine for single recipient demo). For bulk send, this will timeout. Add a `_personalize_batch()` helper that uses `asyncio.gather()` with a semaphore (max 10 concurrent) when `recipient_count > 1`. For the demo (single recipient), keep the synchronous path. Gate it with:

```python
if bulk_mode:  # len(contact_list) > 1
    personalized_variants = await _personalize_batch(contacts, selected, campaign_plan)
else:
    personalized = personalize_for_contact(...)
```

### IMPROVEMENT B — Dead Letter Queue handler

**New file:** `utils/dlq_handler.py`

Currently DLQ events are published but never consumed. Add a simple handler that:

1. Consumes from `agent.dlq`
2. Logs to PostgreSQL `monitor_incidents` with `status='dlq'`
3. Sends a Slack webhook notification (if `SLACK_WEBHOOK_URL` env var is set) — use `urllib.request` (no new deps)
4. Can be run standalone: `python -m utils.dlq_handler`

### IMPROVEMENT C — Supervisor should run SEO + Competitor as pre-pipeline, not post

**File:** `graph/campaign_graph.py`

**Current flow:** supervisor → competitor → copy → ... → seo → reporting
**Problem:** SEO and Competitor intel is available to Copy Agent (correct), but SEO runs AFTER analytics/monitor/ab_test — it's a weekly research tool being run in-line with every campaign, adding 10-15s of latency.

**Better architecture:**

- Keep competitor → copy (correct, copy uses intel)
- Move SEO to run in parallel with competitor at the start using LangGraph's parallel node pattern:

```python
# After supervisor, fan out:
g.add_edge("supervisor", "competitor_agent")
g.add_edge("supervisor", "seo_agent")  # parallel
# Both feed into copy_agent
g.add_edge("competitor_agent", "copy_agent")
g.add_edge("seo_agent", "copy_agent")
```

LangGraph handles fan-in automatically when both edges point to the same node. This saves sequential latency.

### IMPROVEMENT D — Health check endpoint should verify agent importability

**File:** `api.py`

Add a `/health/agents` endpoint that imports each agent module and reports any import errors. This catches the psycopg2 bare-import class of bugs before they hit the pipeline:

```python
@app.get("/health/agents")
async def agent_health():
    results = {}
    agent_modules = [
        "agents.supervisor.supervisor_agent",
        "agents.copy.copy_agent",
        # ... all 16
    ]
    for mod in agent_modules:
        try:
            importlib.import_module(mod)
            results[mod] = "ok"
        except Exception as e:
            results[mod] = str(e)
    return results
```

---

## VALIDATION CHECKLIST

After all fixes, run these in order and confirm each passes:

1. `python -c "from graph.campaign_graph import campaign_graph; print('Graph import OK')"` — must not raise
2. `python -c "from agents.reporting.reporting_agent import reporting_agent_node; print('Reporting import OK')"` — must not raise
3. `curl http://localhost:8000/health` — postgres, redis must show "connected"
4. `curl http://localhost:8000/health/agents` — all agents must show "ok"
5. `python main.py` with a short intent — full pipeline must complete without NameError
6. Check PostgreSQL: `SELECT COUNT(*) FROM copy_variants;` — must be > 0 after a run
7. Check PostgreSQL: `SELECT COUNT(*) FROM ab_variant_stats;` — must be > 0 after a run
8. Confirm email is received with personalized subject line (check `personalization_signals` in logs)

---

## CONSTRAINTS

- Do NOT upgrade any package versions
- Do NOT change the Pydantic schema field names in `schemas/campaign.py`
- Do NOT change the Kafka topic names in `utils/kafka_bus.py`
- Do NOT add new Python package dependencies except for fixes that explicitly require one (and only if that package is already in requirements.txt)
- Every DB write must be wrapped in try/except and must NOT block the pipeline on failure
- Every fix must be backward-compatible with the existing `demo_full_pipeline.py` run

```

```
