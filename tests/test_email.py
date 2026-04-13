"""
Unit tests — Email Agent
Tests: send strategy generation, personalization wire-up,
       drip sequence, Kafka events, no-send when no recipient,
       ab_variant_stats seeding.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_email_produces_send_result(minimal_state):
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    sr = result.get("send_result")
    assert sr is not None
    assert sr.get("status") in ("SENT", "SCHEDULED", "QUEUED")
    assert sr.get("message_id", "").startswith("MSG-")


def test_email_no_real_send_without_recipient(minimal_state):
    from agents.email.email_agent import email_agent_node

    state = _copy.deepcopy(minimal_state)
    state["recipient_email"] = None
    result = email_agent_node(state)
    sr = result["send_result"]
    assert sr.get("real_email_sent") is False


def test_email_real_send_attempted_with_recipient(minimal_state):
    """If recipient is set, real_email_sent should be True or have a real error (not 'no recipient')."""
    from agents.email.email_agent import email_agent_node
    import os

    # Only test if credentials are present — skip otherwise
    if not os.getenv("SMTP_EMAIL") and not os.getenv("SENDGRID_API_KEY"):
        pytest.skip("No email credentials — skipping real send test")

    state = _copy.deepcopy(minimal_state)
    state["recipient_email"] = "test@example.com"
    result = email_agent_node(state)
    sr = result["send_result"]
    # Either sent or got a real provider error (not "no recipient configured")
    assert sr["real_email_status"] != "no recipient configured"


def test_email_includes_personalization_signals(minimal_state):
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    sr = result.get("send_result", {})
    # personalization_signals must be present (may be ["token_injection_only"] for unknown contact)
    assert "personalization_signals" in sr, "send_result must include personalization_signals"
    assert isinstance(sr["personalization_signals"], list)


def test_email_drip_sequence_has_three_items(minimal_state):
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    drip = result["send_result"].get("drip_sequence_preview", [])
    assert len(drip) >= 3, f"Must have 3+ drip emails, got {len(drip)}"


def test_email_optimal_send_time_is_string(minimal_state):
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    ost = result["send_result"].get("optimal_send_time", "")
    assert isinstance(ost, str) and len(ost) > 0


def test_email_publishes_contact_event(minimal_state):
    from agents.email.email_agent import email_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    email_agent_node(minimal_state)
    topics = [e["topic"] for e in get_event_log()]
    assert "contact.events" in topics, "Must publish email_sent to contact.events"


def test_email_seeds_ab_variant_stats_fields(minimal_state):
    """send_result must contain simulated_recipients > 0 for A/B seeding."""
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    sr = result["send_result"]
    assert sr.get("simulated_recipients", 0) > 0, \
        "simulated_recipients must be set for A/B stats seeding"


def test_email_appends_trace(minimal_state):
    from agents.email.email_agent import email_agent_node

    result = email_agent_node(minimal_state)
    assert any(t["agent"] == "email_agent" for t in result["trace"])
