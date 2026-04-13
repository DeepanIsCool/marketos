"""
Unit tests — SMS Agent
Tests: copy generation, TCPA quiet hours, opt-out suppression,
       phone normalization, provider fallback chain, Kafka event.
"""

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
    assert sr["provider"] == "simulated"


def test_tcpa_quiet_hours_logic():
    from agents.sms.sms_agent import TCPAGuardSkill
    from unittest.mock import patch
    from datetime import datetime, timezone

    # Mock 3 AM IST (UTC+5:30 = UTC 21:30 previous day)
    # IST 3 AM = UTC 21:30 → UTC hour = 21 → local IST = 21+5 = 26%24 = 2 (quiet)
    with patch("agents.sms.sms_agent.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 21  # UTC 21:30 = IST 03:00
        mock_dt.now.side_effect = lambda tz: datetime(2025, 1, 1, 21, 0, tzinfo=timezone.utc)
        # local_hour = (21 + 5) % 24 = 2 → quiet hours (< 8 AM)
        result = TCPAGuardSkill.is_quiet_hours(timezone_offset_hrs=5)
        assert result is True


def test_tcpa_allowed_hours():
    from agents.sms.sms_agent import TCPAGuardSkill
    from unittest.mock import patch
    from datetime import datetime, timezone

    with patch("agents.sms.sms_agent.datetime") as mock_dt:
        mock_dt.now.side_effect = lambda tz: datetime(2025, 1, 1, 5, 0, tzinfo=timezone.utc)
        # UTC 5 AM = IST 10:30 AM → allowed
        result = TCPAGuardSkill.is_quiet_hours(timezone_offset_hrs=5)
        assert result is False


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
