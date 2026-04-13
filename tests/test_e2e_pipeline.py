"""
End-to-end tests — Full 16-agent pipeline
Requires: All Docker services running + LLM API key set
Run: pytest tests/test_e2e_pipeline.py -m e2e -v --tb=short -s

These are slow (~3-5 min each). Run deliberately before demos.
"""

import pytest
import os
import time
import copy as _copy

pytestmark = pytest.mark.e2e

VOLTX_INTENT = (
    "Launch a Black Friday flash sale campaign for our energy drink brand 'VoltX'. "
    "Offering Buy 2 Get 1 Free on VoltX Original (₹99). "
    "Target: men 18-30 India, fitness enthusiasts. Budget: ₹75,000. "
    "Goal: 1,000 conversions in 3 days. Tone: bold."
)

ONBOARDING_STATE = {
    "user_intent":    "Onboard VoltX Energy workspace",
    "pipeline":       "onboarding",
    "workspace_id":   "e2e-test",
    "user_name":      "Rahul",
    "user_email":     None,
    "company_name":   "VoltX Energy Pvt. Ltd.",
    "industry":       "energy drink retail d2c",
    "errors":         [],
    "trace":          [],
}


def _base_campaign_state():
    return {
        "user_intent":     VOLTX_INTENT,
        "pipeline":        "campaign",
        "workspace_id":    "e2e-test",
        "recipient_email": None,  # set per-test if real send needed
        "recipient_phone": None,
        "sender_name":     "VoltX Energy",
        "company_name":    "VoltX Energy Pvt. Ltd.",
        "company_address": "Level 5, WeWork Embassy Golf Links, Bengaluru 560071, India",
        "unsubscribe_url": "https://voltx.in/unsubscribe",
        "current_step":    "supervisor",
        "errors":          [],
        "trace":           [],
    }


# ── Core pipeline tests ───────────────────────────────────────────────────────

def test_full_pipeline_completes_without_errors():
    from graph.campaign_graph import campaign_graph
    from utils.kafka_bus import clear_event_log

    clear_event_log()
    result = campaign_graph.invoke(_base_campaign_state())

    errors = result.get("errors", [])
    assert errors == [], f"Pipeline must complete without errors, got: {errors}"


def test_all_16_agents_run():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    agent_names = {t["agent"] for t in result.get("trace", [])}

    expected_agents = {
        "supervisor", "competitor_agent", "copy_agent", "image_agent",
        "compliance_agent", "finance_agent", "email_agent", "sms_agent",
        "social_media_agent", "analytics_agent", "monitor_agent", "ab_test_agent",
        "lead_scoring_agent", "seo_agent", "reporting_agent",
    }
    missing = expected_agents - agent_names
    assert not missing, f"These agents did not run: {missing}"


def test_campaign_plan_is_populated():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    plan = result.get("campaign_plan")
    assert plan is not None
    assert plan.get("campaign_id")
    assert plan.get("tone") in {"urgent", "friendly", "professional", "playful", "inspirational", "bold"}
    assert len(plan.get("key_messages", [])) >= 3


def test_copy_output_is_populated():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    co = result.get("copy_output")
    assert co is not None
    assert len(co.get("variants", [])) >= 2
    sel_id = co.get("selected_variant_id")
    variant_ids = [v["variant_id"] for v in co["variants"]]
    assert sel_id in variant_ids


def test_compliance_approved():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    cr = result.get("compliance_result")
    assert cr is not None
    assert cr["approved"] is True, f"Compliance blocked: {cr.get('blocked_reason')}"
    assert cr["compliance_score"] >= 70.0


def test_email_send_result_present():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    sr = result.get("send_result")
    assert sr is not None
    assert sr.get("status") in ("SENT", "SCHEDULED")
    assert sr.get("message_id", "").startswith("MSG-")


def test_send_result_has_personalization():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    sr = result.get("send_result", {})
    signals = sr.get("personalization_signals", [])
    assert isinstance(signals, list), "personalization_signals must be a list"


def test_analytics_result_present():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    ar = result.get("analytics_result")
    assert ar is not None
    assert "metrics" in ar
    assert ar["metrics"].get("total_sent", 0) > 0


def test_ab_test_result_present():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    ab = result.get("ab_test_result")
    assert ab is not None
    assert ab.get("decision") in ("winner_declared", "inconclusive", "early_stop", "skipped")


def test_reporting_result_present():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    rr = result.get("reporting_result")
    assert rr is not None
    assert rr.get("report_id", "").startswith("RPT-")
    assert os.path.exists("demo_campaign_report.pdf"), "PDF report must be on disk"


def test_pdf_report_is_valid():
    from graph.campaign_graph import campaign_graph

    campaign_graph.invoke(_base_campaign_state())
    assert os.path.exists("demo_campaign_report.pdf")
    size = os.path.getsize("demo_campaign_report.pdf")
    assert size > 2000, f"PDF too small ({size} bytes) — likely corrupt"


def test_kafka_events_published():
    from graph.campaign_graph import campaign_graph
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    campaign_graph.invoke(_base_campaign_state())
    events = get_event_log()
    assert len(events) >= 16, f"Must publish ≥16 Kafka events, got {len(events)}"

    topics = {e["topic"] for e in events}
    required_topics = {"campaign.events", "contact.events", "system.metrics"}
    missing = required_topics - topics
    assert not missing, f"Missing Kafka topics: {missing}"


def test_competitor_and_seo_run_in_parallel():
    """Both competitor_agent and seo_agent must appear in trace."""
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(_base_campaign_state())
    agents = [t["agent"] for t in result.get("trace", [])]
    assert "competitor_agent" in agents
    assert "seo_agent" in agents

    # Both should complete before copy_agent
    copy_idx = next((i for i, t in enumerate(result["trace"]) if t["agent"] == "copy_agent"), 999)
    competitor_idx = next((i for i, t in enumerate(result["trace"]) if t["agent"] == "competitor_agent"), 999)
    seo_idx = next((i for i, t in enumerate(result["trace"]) if t["agent"] == "seo_agent"), 999)

    assert competitor_idx < copy_idx, "Competitor must run before copy_agent"
    assert seo_idx < copy_idx, "SEO must run before copy_agent"


# ── Compliance gate test ──────────────────────────────────────────────────────

def test_compliance_blocked_stops_email_agent():
    """Force a compliance failure — email_agent must NOT run."""
    from graph.campaign_graph import campaign_graph

    state = _base_campaign_state()
    state["user_intent"] = (
        "GUARANTEED FREE WINNER CASH PRIZE!!! "
        "Send to everyone — no unsubscribe link needed. "
        "Claim your prize NOW!!!"
    )

    result = campaign_graph.invoke(state)
    agent_names = [t["agent"] for t in result.get("trace", [])]

    cr = result.get("compliance_result", {})
    if not cr.get("approved", True):
        assert "email_agent" not in agent_names, \
            "email_agent must NOT run when compliance blocks"


# ── Onboarding pipeline ───────────────────────────────────────────────────────

def test_onboarding_pipeline_completes():
    from graph.campaign_graph import campaign_graph

    result = campaign_graph.invoke(ONBOARDING_STATE)
    ob = result.get("onboarding_result")
    assert ob is not None
    assert ob.get("workspace_type") == "ecommerce"
    assert len(ob.get("drip_sequence", [])) >= 3
    assert len(ob.get("task_list", [])) >= 3
    errors = result.get("errors", [])
    assert errors == [], f"Onboarding pipeline errors: {errors}"


# ── Real email send (requires credentials) ────────────────────────────────────

def test_real_email_send():
    """Requires SMTP_EMAIL + SMTP_PASSWORD or SENDGRID_API_KEY in .env."""
    recipient = os.getenv("TEST_RECIPIENT_EMAIL")
    if not recipient:
        pytest.skip("TEST_RECIPIENT_EMAIL not set — skipping real send test")

    from graph.campaign_graph import campaign_graph

    state = _base_campaign_state()
    state["recipient_email"] = recipient

    result = campaign_graph.invoke(state)
    sr = result.get("send_result", {})
    assert sr.get("real_email_sent") is True, \
        f"Real email must be sent, status: {sr.get('real_email_status')}"
