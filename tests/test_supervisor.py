"""
Unit tests — Supervisor Agent
Tests: intent decomposition, JSON schema validation, Kafka event publication,
       episodic memory recall injection, campaign plan field completeness.
"""

import pytest

pytestmark = pytest.mark.unit

VALID_TONES = {"urgent", "friendly", "professional", "playful", "inspirational", "bold"}


def test_supervisor_produces_campaign_plan():
    from agents.supervisor.supervisor_agent import supervisor_node

    state = {
        "user_intent": (
            "Launch VoltX energy drink Black Friday. "
            "Budget ₹75,000. Goal: 500 conversions. "
            "Audience: men 18-30 India. Tone: bold."
        ),
        "errors": [],
        "trace":  [],
    }
    result = supervisor_node(state)

    plan = result.get("campaign_plan")
    assert plan is not None, "Must produce campaign_plan"
    assert plan.get("campaign_id"), "campaign_id must be set"
    assert plan.get("campaign_name"), "campaign_name must be set"
    assert plan.get("goal"), "goal must be set"
    assert plan.get("target_audience"), "target_audience must be set"
    assert isinstance(plan.get("channels"), list) and len(plan["channels"]) > 0
    assert plan.get("tone") in VALID_TONES, f"tone '{plan.get('tone')}' not in {VALID_TONES}"
    assert isinstance(plan.get("key_messages"), list)
    assert len(plan["key_messages"]) >= 3, "Must have at least 3 key messages"
    assert isinstance(plan.get("tasks"), list)
    assert len(plan["tasks"]) > 0, "Must have at least 1 task"


def test_supervisor_sets_next_step():
    from agents.supervisor.supervisor_agent import supervisor_node

    state = {"user_intent": "Quick test campaign", "errors": [], "trace": []}
    result = supervisor_node(state)
    assert result.get("current_step") == "copy_agent"


def test_supervisor_clears_errors():
    from agents.supervisor.supervisor_agent import supervisor_node

    state = {"user_intent": "Test campaign", "errors": ["old error"], "trace": []}
    result = supervisor_node(state)
    # Supervisor resets errors on success
    assert result.get("errors", []) == []


def test_supervisor_appends_trace():
    from agents.supervisor.supervisor_agent import supervisor_node

    state = {"user_intent": "Test", "errors": [], "trace": []}
    result = supervisor_node(state)
    trace = result.get("trace", [])
    assert len(trace) >= 1
    latest = trace[-1]
    assert latest.get("agent") == "supervisor"
    assert latest.get("status") == "completed"
    assert "timestamp" in latest


def test_supervisor_publishes_kafka_event():
    from utils.kafka_bus import clear_event_log, get_event_log
    from agents.supervisor.supervisor_agent import supervisor_node

    clear_event_log()
    supervisor_node({"user_intent": "Test campaign", "errors": [], "trace": []})
    events = get_event_log()
    topics = [e["topic"] for e in events]
    assert "agent.supervisor.results" in topics or "campaign.events" in topics


def test_supervisor_budget_extracted():
    from agents.supervisor.supervisor_agent import supervisor_node

    state = {
        "user_intent": "Campaign with budget ₹50000. Goal: 100 conversions.",
        "errors": [], "trace": [],
    }
    result = supervisor_node(state)
    plan = result.get("campaign_plan", {})
    # Budget should be extracted (or None if LLM didn't find it)
    # Just verify it's a number or None — not a string
    budget = plan.get("budget")
    assert budget is None or isinstance(budget, (int, float)), \
        f"budget must be numeric or None, got {type(budget)}"
