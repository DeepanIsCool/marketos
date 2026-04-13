"""
Unit tests — Monitor Agent
Tests: alert rule evaluation, remediation playbook trigger,
       health status output, Kafka alert publication.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_monitor_green_when_no_anomalies(minimal_state):
    from agents.monitor.monitor_agent import monitor_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {
            "spam_rate": 0.0001, "bounce_rate": 0.005,
            "open_rate": 0.28,   "delivery_rate": 0.98,
        },
        "anomalies": [],
    }
    result = monitor_agent_node(state)
    mr = result.get("monitor_result")
    assert mr is not None
    assert mr["system_health"] == "green"
    assert len(mr["triggered"]) == 0


def test_monitor_red_on_spam_spike(minimal_state):
    from agents.monitor.monitor_agent import monitor_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {"spam_rate": 0.008},  # CRITICAL
        "anomalies": [],
    }
    result = monitor_agent_node(state)
    mr = result["monitor_result"]
    assert mr["system_health"] in ("yellow", "red")
    triggered_ids = [r["rule_id"] for r in mr["triggered"]]
    assert "SPAM_RATE_HIGH" in triggered_ids


def test_monitor_executes_remediation_on_critical(minimal_state):
    from agents.monitor.monitor_agent import monitor_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {"spam_rate": 0.01},
        "anomalies": [],
    }
    result = monitor_agent_node(state)
    mr = result["monitor_result"]
    # SPAM_RATE_HIGH is tier 3 → should trigger auto-remediation
    assert len(mr["remediations"]) > 0, "Tier-3 rule must trigger auto-remediation"


def test_evaluate_rules_logic():
    from agents.monitor.monitor_agent import _evaluate_rules

    rules = [
        {"rule_id": "SPAM", "metric": "spam_rate", "condition": "gt",
         "threshold": 0.005, "severity": "CRITICAL", "tier": 3},
        {"rule_id": "BOUNCE", "metric": "bounce_rate", "condition": "gt",
         "threshold": 0.020, "severity": "WARNING", "tier": 2},
    ]
    metrics = {"spam_rate": 0.008, "bounce_rate": 0.015}
    triggered = _evaluate_rules(metrics, rules)
    rule_ids = [r["rule_id"] for r in triggered]
    assert "SPAM" in rule_ids
    assert "BOUNCE" not in rule_ids  # 0.015 < 0.020 threshold


def test_monitor_publishes_remediation_event(minimal_state):
    from agents.monitor.monitor_agent import monitor_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {"spam_rate": 0.009},
        "anomalies": [],
    }
    clear_event_log()
    monitor_agent_node(state)
    topics = [e["topic"] for e in get_event_log()]
    assert "campaign.events" in topics or "system.alerts" in topics


def test_monitor_appends_trace(minimal_state):
    from agents.monitor.monitor_agent import monitor_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {"metrics": {}, "anomalies": []}
    result = monitor_agent_node(state)
    assert any(t["agent"] == "monitor_agent" for t in result["trace"])
