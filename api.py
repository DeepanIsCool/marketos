"""
MarketOS — API Layer (v1)
Versioned REST API with individual agent access, consistent response envelope,
and full pipeline execution.

Endpoints:
  GET  /v1/health                     → Infrastructure health
  GET  /v1/agents                     → List all agents with metadata
  POST /v1/agents/{name}/run          → Run a single agent
  POST /v1/pipeline/campaign          → Full pipeline (sync)
  POST /v1/pipeline/campaign/async    → Kafka-backed async (202)
  GET  /v1/pipeline/{id}/status       → Poll campaign status
"""

from __future__ import annotations

import importlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from utils.kafka_bus import publish_event, Topics, get_producer
from utils.logger import agent_log


# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="MarketOS API", version="1.0.0")


# ── Agent Registry ──────────────────────────────────────────────────────────

AGENT_REGISTRY: dict[str, dict] = {
    "supervisor":       {"module": "agents.supervisor.supervisor_agent",       "func": "supervisor_node",          "skills": ["product-marketing-context","launch-strategy","marketing-ideas","marketing-psychology"], "temperature": 0.0, "sla": "<500ms"},
    "competitor":       {"module": "agents.competitor.competitor_agent",       "func": "competitor_agent_node",    "skills": ["competitor-alternatives","customer-research","pricing-strategy"],                      "temperature": 0.1, "sla": "daily"},
    "seo":              {"module": "agents.seo.seo_agent",                    "func": "seo_agent_node",           "skills": ["seo-audit","ai-seo","programmatic-seo","schema-markup","site-architecture"],              "temperature": 0.0, "sla": "weekly"},
    "copy":             {"module": "agents.copy.copy_agent",                  "func": "copy_agent_node",          "skills": ["copywriting","copy-editing","email-sequence","cold-email","content-strategy","marketing-psychology"], "temperature": 0.7, "sla": "<8s"},
    "image":            {"module": "agents.creative.image_engine",            "func": "image_agent_node",         "skills": [],                                                                                         "temperature": None, "sla": "<30s"},
    "compliance":       {"module": "agents.compliance.compliance_agent",      "func": "compliance_agent_node",    "skills": ["copy-editing","product-marketing-context"],                                               "temperature": 0.0, "sla": "<500ms"},
    "finance":          {"module": "agents.finance.finance_agent",            "func": "finance_agent_node",       "skills": ["pricing-strategy","revops","paid-ads"],                                                   "temperature": 0.0, "sla": "hourly"},
    "email":            {"module": "agents.email.email_agent",                "func": "email_agent_node",         "skills": ["email-sequence","copy-editing"],                                                          "temperature": 0.0, "sla": "real-time"},
    "sms":              {"module": "agents.sms.sms_agent",                    "func": "sms_agent_node",           "skills": ["copywriting","marketing-psychology"],                                                     "temperature": 0.5, "sla": "real-time"},
    "voice":            {"module": "agents.voice.voice_agent",                "func": "voice_agent_node",         "skills": ["voice-marketing","copywriting"],                                                          "temperature": 0.4, "sla": "real-time"},
    "social_media":     {"module": "agents.social.social_media_agent",        "func": "social_media_agent_node",  "skills": ["social-content","community-marketing","content-strategy","marketing-psychology"],          "temperature": 0.6, "sla": "scheduled"},
    "analytics":        {"module": "agents.analytics.analytics_agent",        "func": "analytics_agent_node",     "skills": ["analytics-tracking","revops","ab-test-setup"],                                            "temperature": 0.0, "sla": "5min"},
    "monitor":          {"module": "agents.monitor.monitor_agent",            "func": "monitor_agent_node",       "skills": ["analytics-tracking","revops"],                                                            "temperature": 0.0, "sla": "<30s"},
    "ab_test":          {"module": "agents.ab_test.ab_test_agent",            "func": "ab_test_agent_node",       "skills": ["ab-test-setup","analytics-tracking","page-cro"],                                          "temperature": 0.0, "sla": "event-driven"},
    "lead_scoring":     {"module": "agents.lead_scoring.lead_scoring_agent",  "func": "lead_scoring_agent_node",  "skills": ["revops","sales-enablement","customer-research"],                                          "temperature": 0.0, "sla": "<2s"},
    "reporting":        {"module": "agents.reporting.reporting_agent",        "func": "reporting_agent_node",     "skills": ["analytics-tracking","revops","copy-editing"],                                             "temperature": 0.3, "sla": "<60s"},
    "onboarding":       {"module": "agents.onboarding.onboarding_agent",     "func": "onboarding_agent_node",    "skills": ["onboarding-cro","churn-prevention","lead-magnets","email-sequence"],                      "temperature": 0.5, "sla": "event-driven"},
}


def _load_agent_func(name: str):
    """Dynamically import and return an agent's node function."""
    entry = AGENT_REGISTRY.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    mod = importlib.import_module(entry["module"])
    return getattr(mod, entry["func"])


# ── Response Envelope ────────────────────────────────────────────────────────

def _envelope(data: dict, agent: str, elapsed_ms: float, trace_id: str, ok: bool = True, error: str | None = None):
    return {
        "ok": ok,
        "data": data,
        "error": error,
        "meta": {
            "agent": agent,
            "elapsed_ms": round(elapsed_ms, 1),
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


# ── Request Models ───────────────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    state: dict = Field(..., description="LangGraph state dict to pass to the agent")

class CampaignRequest(BaseModel):
    user_intent:     str = Field(..., description="Natural language campaign intent")
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    sender_name:     str = "MarketOS"
    company_name:    str = "MarketOS"
    company_address: str = "Bengaluru, Karnataka, India"
    unsubscribe_url: str = "https://example.com/unsubscribe"
    workspace_id:    str = "default"


# ── GET /v1/agents — List all agents ─────────────────────────────────────────

@app.get("/v1/agents")
async def list_agents():
    """Return metadata for all registered agents."""
    agents = []
    for name, meta in AGENT_REGISTRY.items():
        agents.append({
            "name": name,
            "module": meta["module"],
            "skills": meta["skills"],
            "temperature": meta["temperature"],
            "sla": meta["sla"],
        })
    return {"ok": True, "data": {"agents": agents, "total": len(agents)}}


# ── POST /v1/agents/{name}/run — Run single agent ───────────────────────────

@app.post("/v1/agents/{agent_name}/run")
async def run_agent(agent_name: str, request: AgentRunRequest):
    """Run a single agent with the provided state and return its output."""
    fn = _load_agent_func(agent_name)
    trace_id = str(uuid.uuid4())[:8]

    # Ensure required state keys exist
    state = {
        "current_step": agent_name,
        "errors": [],
        "trace": [],
        **request.state,
    }

    start = time.monotonic()
    try:
        result = fn(state)
        elapsed = (time.monotonic() - start) * 1000
        return _envelope(result, agent_name, elapsed, trace_id)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        raise HTTPException(
            status_code=500,
            detail=_envelope({}, agent_name, elapsed, trace_id, ok=False, error=str(e)),
        )


# ── POST /v1/pipeline/campaign — Full sync pipeline ─────────────────────────

@app.post("/v1/pipeline/campaign")
async def run_pipeline_sync(request: CampaignRequest):
    """Run the full campaign pipeline synchronously. Returns complete result."""
    from graph.campaign_graph import campaign_graph

    campaign_id = f"CAMP-{int(time.time())}-{str(uuid.uuid4())[:4].upper()}"
    trace_id = str(uuid.uuid4())[:8]

    state = {
        "user_intent":     request.user_intent,
        "pipeline":        "campaign",
        "workspace_id":    request.workspace_id,
        "recipient_email": request.recipient_email,
        "recipient_phone": request.recipient_phone,
        "sender_name":     request.sender_name,
        "company_name":    request.company_name,
        "company_address": request.company_address,
        "unsubscribe_url": request.unsubscribe_url,
        "current_step":    "supervisor",
        "errors":          [],
        "trace":           [],
    }

    start = time.monotonic()
    try:
        result = campaign_graph.invoke(state)
        elapsed = (time.monotonic() - start) * 1000
        return _envelope(
            {"campaign_id": campaign_id, "agents_run": len(result.get("trace", [])), "result": result},
            "pipeline",
            elapsed,
            trace_id,
        )
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        raise HTTPException(
            status_code=500,
            detail=_envelope({}, "pipeline", elapsed, trace_id, ok=False, error=str(e)),
        )


# ── POST /v1/pipeline/campaign/async — Kafka-backed ─────────────────────────

@app.post("/v1/pipeline/campaign/async", status_code=202)
async def run_pipeline_async(request: CampaignRequest):
    """Accept campaign intent, publish to Kafka, return 202."""
    campaign_id = f"CAMP-{int(time.time())}-{str(uuid.uuid4())[:4].upper()}"

    payload = {
        "campaign_id":     campaign_id,
        "user_intent":     request.user_intent,
        "recipient_email": request.recipient_email,
        "recipient_phone": request.recipient_phone,
        "sender_name":     request.sender_name,
        "company_name":    request.company_name,
        "company_address": request.company_address,
        "unsubscribe_url": request.unsubscribe_url,
        "workspace_id":    request.workspace_id,
    }

    publish_event(topic=Topics.SUPERVISOR_TASKS, source_agent="api", payload=payload, priority="HIGH")
    _store_campaign(campaign_id, request.workspace_id, request.user_intent)

    return {
        "ok": True,
        "data": {"campaign_id": campaign_id, "status": "accepted"},
        "meta": {"poll_url": f"/v1/pipeline/{campaign_id}/status"},
    }


# ── GET /v1/pipeline/{id}/status ─────────────────────────────────────────────

@app.get("/v1/pipeline/{campaign_id}/status")
async def get_pipeline_status(campaign_id: str):
    """Poll campaign status from PostgreSQL."""
    try:
        import psycopg2, psycopg2.extras
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM campaigns WHERE campaign_id = %s", (campaign_id,))
            row = cur.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
        return {
            "ok": True,
            "data": {
                "campaign_id": row["campaign_id"],
                "status": row["status"],
                "result_data": json.loads(row["result_data"]) if row.get("result_data") else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"ok": False, "data": None, "error": f"DB unavailable: {e}"}


# ── GET /v1/health ───────────────────────────────────────────────────────────

@app.get("/v1/health")
async def health_check():
    """Check infrastructure health."""
    checks = {"kafka": "disconnected", "postgres": "disconnected", "redis": "disconnected", "clickhouse": "disconnected"}

    checks["kafka"] = "connected" if get_producer().is_connected else "in-memory"

    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        conn.cursor().execute("SELECT 1")
        conn.close()
        checks["postgres"] = "connected"
    except Exception:
        pass

    try:
        import redis
        redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0")).ping()
        checks["redis"] = "connected"
    except Exception:
        pass

    try:
        from clickhouse_driver import Client
        Client(host=os.getenv("CLICKHOUSE_HOST", "localhost"), port=int(os.getenv("CLICKHOUSE_PORT", "9000"))).execute("SELECT 1")
        checks["clickhouse"] = "connected"
    except Exception:
        pass

    is_healthy = all(v == "connected" for v in checks.values())
    return {
        "ok": True,
        "data": {"status": "healthy" if is_healthy else "degraded", **checks},
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
    }


# ── GET /v1/health/agents ───────────────────────────────────────────────────

@app.get("/v1/health/agents")
async def agent_health():
    """Import-test every agent module."""
    results = {}
    for name, meta in AGENT_REGISTRY.items():
        try:
            importlib.import_module(meta["module"])
            results[name] = "ok"
        except Exception as e:
            results[name] = str(e)
    is_healthy = all(v == "ok" for v in results.values())
    return {"ok": is_healthy, "data": results}


# ── DB Helper ────────────────────────────────────────────────────────────────

def _store_campaign(campaign_id: str, workspace_id: str, intent: str):
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO campaigns (campaign_id, workspace_id, campaign_name, status) VALUES (%s,%s,%s,'accepted') ON CONFLICT (campaign_id) DO NOTHING",
                (campaign_id, workspace_id or "default", intent[:200]),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        agent_log("API", f"Campaign store failed: {e}")


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
