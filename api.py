"""
MarketOS — API Layer
FastAPI endpoints for campaign execution.

Architecture (PRD §3.3):
  POST /run-campaign       → Publishes to Kafka, returns 202 Accepted
  POST /run-campaign/sync  → Blocking execution (for local dev/demo)
  GET  /campaign/{id}/status → Poll campaign status from PostgreSQL
  GET  /health              → Infrastructure health check

Production: NestJS/GraphQL (PRD §3.1) — FastAPI is the Python prototype.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from utils.kafka_bus import publish_event, Topics, get_producer, get_event_log
from utils.logger import agent_log

# ── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="MarketOS API",
    version="2.0.0",
    description="Event-driven autonomous marketing platform API",
)


# ── Request / Response Models ────────────────────────────────────────────────

class CampaignRequest(BaseModel):
    user_intent:     str = Field(..., description="Natural language campaign intent")
    recipient_email: Optional[str] = Field(None, description="Email recipient for real send")
    recipient_phone: Optional[str] = Field(None, description="Phone number for SMS (with country code)")
    sender_name:     Optional[str] = Field("MarketOS", description="Sender display name")
    company_name:    Optional[str] = Field("MarketOS", description="Company name for compliance")
    company_address: Optional[str] = Field("Bengaluru, Karnataka, India", description="Physical address for CAN-SPAM")
    unsubscribe_url: Optional[str] = Field("https://example.com/unsubscribe", description="Unsubscribe URL")
    workspace_id:    Optional[str] = Field("default", description="Workspace ID for multi-tenancy")


class CampaignAcceptedResponse(BaseModel):
    campaign_id: str
    status:      str = "accepted"
    message:     str
    kafka_topic: str


class CampaignStatusResponse(BaseModel):
    campaign_id: str
    status:      str
    result_data: Optional[dict] = None
    created_at:  Optional[str] = None
    updated_at:  Optional[str] = None


class HealthResponse(BaseModel):
    status:    str
    kafka:     str
    postgres:  str
    redis:     str
    timestamp: str


# ── Async Campaign Endpoint (PRD-compliant) ──────────────────────────────────

@app.post("/run-campaign", response_model=CampaignAcceptedResponse, status_code=202)
async def run_campaign_async(request: CampaignRequest):
    """
    Accept a campaign intent and push to Kafka for async processing.
    Returns immediately with 202 Accepted.

    The background worker (worker.py) consumes from agent.supervisor.tasks
    and executes the full LangGraph pipeline.
    """
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
        "submitted_at":    datetime.now(timezone.utc).isoformat(),
    }

    # Publish to Kafka (or in-memory event log)
    published = publish_event(
        topic=Topics.SUPERVISOR_TASKS,
        source_agent="api",
        payload=payload,
        priority="HIGH",
    )

    # Store in PostgreSQL
    _create_campaign_record(campaign_id, request.workspace_id, request.user_intent)

    return CampaignAcceptedResponse(
        campaign_id=campaign_id,
        status="accepted",
        message=f"Campaign intent accepted. Poll GET /campaign/{campaign_id}/status for updates.",
        kafka_topic=Topics.SUPERVISOR_TASKS,
    )


# ── Sync Campaign Endpoint (for demo / local testing) ───────────────────────

@app.post("/run-campaign/sync")
async def run_campaign_sync(request: CampaignRequest, background_tasks: BackgroundTasks):
    """
    Blocking synchronous execution — runs the full pipeline in-process.
    Use for local dev/demo only. Production should use POST /run-campaign.
    """
    from graph.campaign_graph import campaign_graph

    campaign_id = f"CAMP-{int(time.time())}-{str(uuid.uuid4())[:4].upper()}"

    initial_state = {
        "user_intent":       request.user_intent,
        "pipeline":          "campaign",
        "workspace_id":      request.workspace_id,
        "recipient_email":   request.recipient_email,
        "recipient_phone":   request.recipient_phone,
        "sender_name":       request.sender_name or "MarketOS",
        "company_name":      request.company_name or "MarketOS",
        "company_address":   request.company_address or "Bengaluru, Karnataka, India",
        "unsubscribe_url":   request.unsubscribe_url or "https://example.com/unsubscribe",
        "current_step":      "supervisor",
        "errors":            [],
        "trace":             [],
    }

    try:
        result = campaign_graph.invoke(initial_state)
        return {
            "campaign_id":  campaign_id,
            "status":       "completed",
            "agents_run":   len(result.get("trace", [])),
            "errors":       result.get("errors", []),
            "trace":        result.get("trace", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Campaign Status Polling ──────────────────────────────────────────────────

@app.get("/campaign/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(campaign_id: str):
    """Poll the status of a submitted campaign."""
    try:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM campaigns WHERE campaign_id = %s", (campaign_id,))
            row = cur.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
        return CampaignStatusResponse(
            campaign_id=row["campaign_id"],
            status=row["status"],
            result_data=json.loads(row["result_data"]) if row.get("result_data") else None,
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
        )
    except HTTPException:
        raise
    except Exception as e:
        return CampaignStatusResponse(
            campaign_id=campaign_id,
            status="unknown",
            result_data={"error": str(e)},
        )


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health of all infrastructure services."""
    kafka_status = "disconnected"
    postgres_status = "disconnected"
    redis_status = "disconnected"

    # Kafka
    producer = get_producer()
    kafka_status = "connected" if producer.is_connected else "in-memory-mode"

    # PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        conn.cursor().execute("SELECT 1")
        conn.close()
        postgres_status = "connected"
    except Exception:
        postgres_status = "disconnected"

    # Redis
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    overall = "healthy" if all(s == "connected" for s in [postgres_status, redis_status]) else "degraded"

    return HealthResponse(
        status=overall,
        kafka=kafka_status,
        postgres=postgres_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ── Event Log (for demo verification) ───────────────────────────────────────

@app.get("/events")
async def get_events():
    """Return all Kafka events published since process start."""
    events = get_event_log()
    return {
        "total_events": len(events),
        "topics": list(set(e["topic"] for e in events)),
        "events": events[-50:],  # Last 50
    }


# ── DB Helper ────────────────────────────────────────────────────────────────

def _create_campaign_record(campaign_id: str, workspace_id: str, intent: str) -> None:
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO campaigns (campaign_id, workspace_id, campaign_name, status, created_at, updated_at)
                VALUES (%s, %s, %s, 'accepted', NOW(), NOW())
                ON CONFLICT (campaign_id) DO NOTHING
            """, (campaign_id, workspace_id or "default", intent[:200]))
        conn.commit()
        conn.close()
    except Exception as e:
        agent_log("API", f"Campaign record creation failed (non-fatal): {e}")


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
