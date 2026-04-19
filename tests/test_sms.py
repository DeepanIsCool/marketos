"""
Unit tests — SMS Agent
Tests: copy generation, TCPA quiet hours, opt-out suppression,
       phone normalization, provider fallback chain, Kafka event.
"""

import json
import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_sms_generates_two_variants(minimal_state):
    from agents.sms.sms_agent import sms_agent_node

    result = sms_agent_node(minimal_state)
    sr = result.get("sms_result")
    assert sr is not None
    assert len(sr.get("variants", [])) >= 2


def test_sms_variants_have_char_count(minimal_state):
    from agents.sms.sms_agent import sms_agent_node

    result = sms_agent_node(minimal_state)
    for v in result["sms_result"]["variants"]:
        assert "char_count" in v
        assert isinstance(v["char_count"], int)
        assert v["char_count"] <= 480, "SMS must be ≤ 3 segments (480 chars)"


def test_sms_simulates_without_phone(minimal_state):
    from agents.sms.sms_agent import sms_agent_node

    state = _copy.deepcopy(minimal_state)
    state["recipient_phone"] = None
    result = sms_agent_node(state)
    sr = result["sms_result"]
    assert sr["provider"] == "none"
    assert sr["status"] == "skipped"
    assert sr["reason_code"] == "no_phone"


def test_sms_schedules_during_quiet_hours(minimal_state, monkeypatch):
    from agents.sms.sms_agent import sms_agent_node

    state = _copy.deepcopy(minimal_state)
    state["recipient_phone"] = "9876543210"
    monkeypatch.setattr("agents.sms.sms_agent.TCPAGuardSkill.is_quiet_hours", lambda timezone_name=None: True)
    monkeypatch.setattr(
        "agents.sms.sms_agent.TCPAGuardSkill.next_allowed_send_at",
        lambda timezone_name=None: __import__("datetime").datetime(2025, 1, 2, 8, 0),
    )

    result = sms_agent_node(state)
    sr = result["sms_result"]
    assert sr["provider"] == "none"
    assert sr["status"] == "scheduled"
    assert sr["reason_code"] == "quiet_hours"
    assert sr["scheduled_for"].startswith("2025-01-02T08:00:00")


def test_sms_can_override_quiet_hours(minimal_state, monkeypatch):
    from agents.sms.sms_agent import sms_agent_node

    state = _copy.deepcopy(minimal_state)
    state["recipient_phone"] = "9876543210"
    monkeypatch.setenv("SMS_ALLOW_QUIET_HOURS", "true")
    monkeypatch.setattr("agents.sms.sms_agent.TCPAGuardSkill.is_quiet_hours", lambda timezone_name=None: True)
    monkeypatch.setattr(
        "agents.sms.sms_agent.SMSProviderChain.send",
        lambda to, message: {"provider": "twilio", "status": "sent"},
    )

    result = sms_agent_node(state)
    sr = result["sms_result"]
    assert sr["status"] == "sent"
    assert sr["provider"] == "twilio"
    assert sr["reason_code"] is None


def test_tcpa_quiet_hours_logic():
    from agents.sms.sms_agent import TCPAGuardSkill
    from unittest.mock import patch
    from datetime import datetime

    with patch.object(TCPAGuardSkill, "local_now", return_value=datetime(2025, 1, 1, 3, 0)):
        assert TCPAGuardSkill.is_quiet_hours() is True


def test_tcpa_allowed_hours():
    from agents.sms.sms_agent import TCPAGuardSkill
    from unittest.mock import patch
    from datetime import datetime

    with patch.object(TCPAGuardSkill, "local_now", return_value=datetime(2025, 1, 1, 10, 30)):
        assert TCPAGuardSkill.is_quiet_hours() is False


def test_phone_normalization():
    from agents.sms.sms_agent import _normalize_phone

    assert _normalize_phone("9876543210") == "+919876543210"
    assert _normalize_phone("+917003574257") == "+917003574257"
    assert _normalize_phone("07003574257") == "+07003574257"


def test_sms_publishes_kafka_event(minimal_state):
    from agents.sms.sms_agent import sms_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    sms_agent_node(minimal_state)
    topics = [e["topic"] for e in get_event_log()]
    assert "contact.events" in topics


def test_sms_includes_stop_instruction(minimal_state):
    from agents.sms.sms_agent import sms_agent_node

    result = sms_agent_node(minimal_state)
    selected_id = result["sms_result"]["selected_id"]
    variants = result["sms_result"]["variants"]
    selected = next(v for v in variants if v["variant_id"] == selected_id)
    msg = selected.get("message", "").upper()
    # STOP instruction must be present (TRAI regulation)
    assert "STOP" in msg, f"SMS must include STOP instruction. Got: {msg}"


def test_sms_never_sends_unresolved_tokens(minimal_state, monkeypatch):
    from agents.sms.sms_agent import sms_agent_node

    state = _copy.deepcopy(minimal_state)
    state["recipient_phone"] = "9876543210"
    state["first_name"] = "Rahul"

    class StubLLM:
        def invoke(self, messages):
            return type("Resp", (), {
                "content": json.dumps({
                    "variants": [
                        {
                            "variant_id": "SMS-001",
                            "message": "Hi {{first_name}} {{favorite_product}}, use code NOW. STOP to 9999",
                            "char_count": 67,
                            "segments": 1,
                            "personalization_tokens": ["{{first_name}}", "{{favorite_product}}"],
                            "estimated_ctr": 3.2,
                            "angle": "urgency",
                        }
                    ],
                    "selected_variant_id": "SMS-001",
                    "optimal_send_time": "Now",
                    "drip_sequence": ["Reminder for {{first_name}} {{favorite_product}}. STOP to 9999"],
                    "selection_reasoning": "test",
                })
            })()

    sent = {}

    monkeypatch.setattr("agents.sms.sms_agent.sms_agent.get_llm", lambda temperature=0.5: StubLLM())
    monkeypatch.setattr("agents.sms.sms_agent.TCPAGuardSkill.is_quiet_hours", lambda timezone_name=None: False)
    monkeypatch.setattr(
        "agents.sms.sms_agent.SMSProviderChain.send",
        lambda to, message: sent.update({"to": to, "message": message}) or {"provider": "twilio", "status": "sent"},
    )

    result = sms_agent_node(state)
    selected = result["sms_result"]["variants"][0]

    assert "{{" not in sent["message"]
    assert "{{" not in selected["message"]
    assert "{{" not in result["sms_result"]["drip_sequence"][0]
    assert "Rahul" in sent["message"]
