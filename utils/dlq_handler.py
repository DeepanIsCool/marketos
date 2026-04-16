"""
MarketOS — Dead Letter Queue Handler
Consumes agent.dlq, records incidents, and optionally notifies Slack.
"""

from __future__ import annotations

import json
import os
import urllib.request
import uuid
from datetime import datetime, timezone

from utils.logger import agent_log

try:
    from confluent_kafka import Consumer, KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

try:
    import psycopg2
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")
PG_DSN = os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def _write_incident(payload: dict) -> None:
    if not PG_AVAILABLE:
        return

    incident_id = f"DLQ-{str(uuid.uuid4())[:8].upper()}"
    try:
        conn = psycopg2.connect(PG_DSN)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitor_incidents
                    (incident_id, campaign_id, rule_id, severity, metric, observed_value, threshold, status, remediation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    incident_id,
                    payload.get("campaign_id"),
                    "DLQ_EVENT",
                    "CRITICAL",
                    "dlq",
                    1,
                    0,
                    "dlq",
                    payload.get("error") or payload.get("event") or json.dumps(payload),
                ),
            )
        conn.commit()
        conn.close()
    except Exception as exc:
        agent_log("DLQ", f"Incident write failed: {exc}")


def _send_slack(payload: dict) -> None:
    if not SLACK_WEBHOOK_URL:
        return

    body = {
        "text": (
            f"MarketOS DLQ event\n"
            f"campaign_id={payload.get('campaign_id', 'unknown')}\n"
            f"event={payload.get('event', payload.get('event_type', 'unknown'))}\n"
            f"error={payload.get('error', 'none')}"
        )
    }
    request = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5):
            pass
    except Exception as exc:
        agent_log("DLQ", f"Slack notification failed: {exc}")


def main() -> None:
    if not KAFKA_AVAILABLE:
        agent_log("DLQ", "Kafka consumer unavailable")
        return

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BROKERS,
            "group.id": "marketos-dlq-handler",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe(["agent.dlq"])
    agent_log("DLQ", "Listening on agent.dlq")

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() != KafkaError._PARTITION_EOF:
                    agent_log("DLQ", f"Kafka consumer error: {message.error()}")
                continue

            try:
                envelope = json.loads(message.value().decode("utf-8"))
                payload = envelope.get("payload", envelope)
            except Exception as exc:
                agent_log("DLQ", f"Malformed DLQ message: {exc}")
                consumer.commit(message=message)
                continue

            payload.setdefault("received_at", datetime.now(timezone.utc).isoformat())
            _write_incident(payload)
            _send_slack(payload)
            consumer.commit(message=message)
    except KeyboardInterrupt:
        agent_log("DLQ", "Shutdown requested")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
