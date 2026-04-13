"""
Unit tests — Compliance Agent
Tests: approval flow, footer injection, blocking logic, score calculation,
       deterministic CAN-SPAM checks, Kafka event, audit trail.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_compliance_approves_valid_copy(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node

    result = compliance_agent_node(minimal_state)
    cr = result.get("compliance_result")
    assert cr is not None
    assert cr["approved"] is True
    assert cr["compliance_score"] >= 0


def test_compliance_runs_all_checks(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node

    result = compliance_agent_node(minimal_state)
    checks = result["compliance_result"]["checks"]
    # Should have at minimum the 2 deterministic CAN-SPAM checks
    rule_ids = [c["rule_id"] for c in checks]
    assert "CANSPAM_002" in rule_ids, "Must check unsubscribe presence"
    assert "CANSPAM_003" in rule_ids, "Must check physical address"


def test_compliance_injects_footer_when_missing(minimal_state):
    """Remove unsubscribe from HTML — compliance must inject it."""
    from agents.compliance.compliance_agent import compliance_agent_node

    state = _copy.deepcopy(minimal_state)
    # Strip footer from variant HTML
    for v in state["copy_output"]["variants"]:
        v["body_html"] = "<html><body><p>Hello there</p></body></html>"
        v["body_text"] = "Hello there."

    result = compliance_agent_node(state)
    # After compliance, the selected variant's HTML must contain unsubscribe
    co = result.get("copy_output", {})
    sel_id = co.get("selected_variant_id")
    winner = next((v for v in co.get("variants", []) if v["variant_id"] == sel_id), None)
    assert winner is not None
    assert "unsubscribe" in winner["body_html"].lower(), \
        "Compliance must inject unsubscribe link into HTML"
    assert "unsubscribe" in winner["body_text"].lower(), \
        "Compliance must inject unsubscribe into plain text"


def test_compliance_injects_address_when_missing(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node

    state = _copy.deepcopy(minimal_state)
    for v in state["copy_output"]["variants"]:
        v["body_html"] = "<html><body><p>Test</p><a href='x'>Unsubscribe</a></body></html>"
        v["body_text"] = "Test\nUnsubscribe: https://x.com"

    result = compliance_agent_node(state)
    co = result.get("copy_output", {})
    sel_id = co.get("selected_variant_id")
    winner = next((v for v in co.get("variants", []) if v["variant_id"] == sel_id), None)
    address = minimal_state["company_address"].lower()
    assert address in winner["body_html"].lower() or address in winner["body_text"].lower(), \
        "Compliance must inject physical address"


def test_compliance_score_is_numeric(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node

    result = compliance_agent_node(minimal_state)
    score = result["compliance_result"]["compliance_score"]
    assert isinstance(score, (int, float))
    assert 0 <= score <= 100


def test_compliance_approved_routes_to_finance(minimal_state):
    from agents.compliance.compliance_agent import compliance_router

    state = _copy.deepcopy(minimal_state)
    state["compliance_result"] = {"approved": True, "compliance_score": 94.0, "checks": []}
    assert compliance_router(state) == "email_agent"  # mapped to finance_agent in graph


def test_compliance_blocked_routes_to_end(minimal_state):
    from agents.compliance.compliance_agent import compliance_router

    state = _copy.deepcopy(minimal_state)
    state["compliance_result"] = {"approved": False, "compliance_score": 30.0, "checks": []}
    assert compliance_router(state) == "end"


def test_compliance_publishes_kafka_event(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    compliance_agent_node(minimal_state)
    topics = [e["topic"] for e in get_event_log()]
    assert "agent.compliance_agent.results" in topics


def test_compliance_check_severities_are_valid(minimal_state):
    from agents.compliance.compliance_agent import compliance_agent_node

    result = compliance_agent_node(minimal_state)
    valid_severities = {"INFO", "WARNING", "CRITICAL"}
    for check in result["compliance_result"]["checks"]:
        assert check["severity"] in valid_severities, \
            f"Invalid severity: {check['severity']}"
