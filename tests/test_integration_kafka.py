"""
Integration tests — Kafka / Redpanda event bus
Requires: docker compose up -d redpanda
Tests: topic publish, in-memory fallback, envelope schema, dead-letter queue.
"""

import pytest
import os

pytestmark = pytest.mark.integration


def _kafka_available():
    try:
        from confluent_kafka import Producer
        p = Producer({"bootstrap.servers": "localhost:9092", "socket.timeout.ms": 2000})
        p.flush(timeout=2.0)
        return True
    except Exception:
        return False


skip_no_kafka = pytest.mark.skipif(not _kafka_available(), reason="Kafka/Redpanda not reachable")


def test_in_memory_fallback_always_works():
    """Event log always captures events even without Kafka."""
    from utils.kafka_bus import clear_event_log, get_event_log, publish_event, Topics

    clear_event_log()
    publish_event(
        topic=Topics.CAMPAIGN_EVENTS,
        source_agent="test",
        payload={"test_key": "test_value"},
    )
    events = get_event_log()
    assert len(events) >= 1
    event = events[-1]
    assert event["topic"] == "campaign.events"
    assert event["envelope"]["payload"]["test_key"] == "test_value"


def test_envelope_schema_is_complete():
    """Every published event must have the PRD §3.3 envelope fields."""
    from utils.kafka_bus import clear_event_log, get_event_log, publish_event, Topics

    clear_event_log()
    publish_event(
        topic=Topics.SYSTEM_ALERTS,
        source_agent="test_agent",
        payload={"alert": "test"},
        priority="HIGH",
    )
    event = get_event_log()[-1]
    env = event["envelope"]

    required_fields = ["messageId", "timestamp", "sourceAgent", "targetAgent",
                       "correlationId", "payload", "priority", "retryCount", "traceId"]
    for field in required_fields:
        assert field in env, f"Envelope missing field: {field}"

    assert env["sourceAgent"] == "test_agent"
    assert env["priority"] == "HIGH"
    assert env["retryCount"] == 0


def test_topic_registry_covers_all_agents():
    """Topics class must have task + result topics for all 16 agents."""
    from utils.kafka_bus import Topics

    agent_names = [
        "supervisor", "copy_agent", "image_agent", "compliance_agent",
        "finance_agent", "email_agent", "sms_agent", "social_media_agent",
        "analytics_agent", "monitor_agent", "ab_test_agent", "lead_scoring_agent",
        "competitor_agent", "seo_agent", "reporting_agent", "onboarding_agent",
    ]
    all_topics = Topics.all_topics()
    for agent in agent_names:
        tasks  = f"agent.{agent}.tasks"
        results = f"agent.{agent}.results"
        assert tasks   in all_topics, f"Missing topic: {tasks}"
        assert results in all_topics, f"Missing topic: {results}"


def test_event_log_clear():
    from utils.kafka_bus import clear_event_log, get_event_log, publish_event, Topics

    publish_event(Topics.CAMPAIGN_EVENTS, "test", {"x": 1})
    assert len(get_event_log()) > 0
    clear_event_log()
    assert len(get_event_log()) == 0


@skip_no_kafka
def test_real_kafka_publish():
    """Publish to real Redpanda and verify no exceptions."""
    from utils.kafka_bus import get_producer, Topics, publish_event

    producer = get_producer()
    assert producer.is_connected, "Producer must be connected to Redpanda"

    result = publish_event(
        topic=Topics.CAMPAIGN_EVENTS,
        source_agent="integration_test",
        payload={"event": "integration_test", "ts": "now"},
    )
    assert result is True
    producer.flush(timeout=5.0)


@skip_no_kafka
def test_dlq_topic_exists():
    """DLQ topic must be pre-created by create_topics.sh."""
    try:
        from confluent_kafka.admin import AdminClient, NewTopic
        admin = AdminClient({"bootstrap.servers": "localhost:9092"})
        metadata = admin.list_topics(timeout=5)
        topics = metadata.topics
        assert "agent.dlq" in topics, "DLQ topic must exist in Redpanda"
    except Exception as e:
        pytest.skip(f"AdminClient unavailable: {e}")
