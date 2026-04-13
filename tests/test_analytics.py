"""
Unit tests — Analytics Agent
Tests: simulation mode metrics, anomaly detection thresholds,
       insight generation, Kafka snapshot publication.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_analytics_produces_metrics(minimal_state):
    from agents.analytics.analytics_agent import analytics_agent_node

    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 25000, "message_id": "MSG-TEST-001"}
    result = analytics_agent_node(state)

    ar = result.get("analytics_result")
    assert ar is not None
    m = ar.get("metrics", {})
    assert m.get("total_sent", 0) > 0
    assert m.get("opens", 0) > 0


def test_analytics_metrics_are_realistic(minimal_state):
    from agents.analytics.analytics_agent import analytics_agent_node

    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 10000}
    result = analytics_agent_node(state)
    m = result["analytics_result"]["metrics"]

    assert 0 < m["open_rate"] < 1,    "open_rate must be 0-1 fraction"
    assert 0 < m["delivery_rate"] <= 1
    assert m["delivered"] <= m["total_sent"]
    assert m["opens"] <= m["delivered"]
    assert m["clicks"] <= m["opens"]


def test_anomaly_detection_spam_threshold():
    from agents.analytics.analytics_agent import _detect_anomalies

    metrics = {"spam_rate": 0.008}  # > 0.5% threshold
    anomalies = _detect_anomalies(metrics, "TEST-001")
    spam_anomaly = next((a for a in anomalies if a["metric"] == "spam_rate"), None)
    assert spam_anomaly is not None, "spam_rate > 0.5% must trigger anomaly"
    assert spam_anomaly["severity"] == "CRITICAL"


def test_anomaly_detection_no_false_positives():
    from agents.analytics.analytics_agent import _detect_anomalies

    metrics = {
        "spam_rate":     0.0001,  # safe
        "bounce_rate":   0.005,   # safe
        "open_rate":     0.28,    # good
        "delivery_rate": 0.98,    # good
    }
    anomalies = _detect_anomalies(metrics, "TEST-001")
    assert len(anomalies) == 0, f"No anomalies expected, got: {anomalies}"


def test_anomaly_detection_bounce_warning():
    from agents.analytics.analytics_agent import _detect_anomalies

    metrics = {"bounce_rate": 0.025}  # > 2% threshold
    anomalies = _detect_anomalies(metrics, "TEST-002")
    bounce = next((a for a in anomalies if a["metric"] == "bounce_rate"), None)
    assert bounce is not None
    assert bounce["severity"] == "WARNING"


def test_analytics_publishes_to_system_metrics(minimal_state):
    from agents.analytics.analytics_agent import analytics_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 5000}
    analytics_agent_node(state)
    topics = [e["topic"] for e in get_event_log()]
    assert "system.metrics" in topics


def test_analytics_insight_has_health_field(minimal_state):
    from agents.analytics.analytics_agent import analytics_agent_node

    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 5000}
    result = analytics_agent_node(state)
    insight = result["analytics_result"]["insight"]
    assert "overall_health" in insight
    assert insight["overall_health"] in ("excellent", "good", "warning", "critical")
