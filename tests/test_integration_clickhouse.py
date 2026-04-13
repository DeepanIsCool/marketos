"""
Integration tests — ClickHouse sink + analytics
Requires: docker compose up -d clickhouse
Tests: table exists, event insert, analytics query, sink consumer logic.
"""

import pytest
import os
import uuid
from datetime import datetime, timezone

pytestmark = pytest.mark.integration


def _ch_available():
    try:
        from clickhouse_driver import Client
        c = Client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            database=os.getenv("CLICKHOUSE_DB", "marketos_analytics"),
            user=os.getenv("CLICKHOUSE_USER", "marketos"),
            password=os.getenv("CLICKHOUSE_PASSWORD", "marketos_dev"),
            connect_timeout=3,
        )
        c.execute("SELECT 1")
        return True
    except Exception:
        return False


skip_no_ch = pytest.mark.skipif(not _ch_available(), reason="ClickHouse not reachable")


@skip_no_ch
def test_email_events_local_table_exists():
    from clickhouse_driver import Client

    ch = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        database=os.getenv("CLICKHOUSE_DB", "marketos_analytics"),
        user=os.getenv("CLICKHOUSE_USER", "marketos"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "marketos_dev"),
    )
    result = ch.execute("SHOW TABLES LIKE 'email_events_local'")
    assert len(result) > 0, "email_events_local table must exist"


@skip_no_ch
def test_insert_and_query_email_event():
    """Insert a test event and verify it's queryable."""
    from clickhouse_driver import Client

    ch = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        database=os.getenv("CLICKHOUSE_DB", "marketos_analytics"),
        user=os.getenv("CLICKHOUSE_USER", "marketos"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "marketos_dev"),
    )
    test_campaign_id = f"CH-TEST-{str(uuid.uuid4())[:8].upper()}"
    ts = datetime.now(timezone.utc)

    ch.execute(
        """
        INSERT INTO email_events_local
            (event_id, campaign_id, workspace_id, contact_id, event_type, provider, timestamp)
        VALUES
        """,
        [(str(uuid.uuid4()), test_campaign_id, "test", "c-001", "send", "smtp", ts)],
    )

    rows = ch.execute(
        "SELECT count() FROM email_events_local WHERE campaign_id = %(cid)s",
        {"cid": test_campaign_id},
    )
    assert rows[0][0] == 1, "Inserted event must be queryable"


@skip_no_ch
def test_analytics_agent_uses_real_clickhouse_data(minimal_state):
    """Seed ClickHouse then run analytics — must use real data not simulation."""
    import copy as _copy
    from clickhouse_driver import Client
    from agents.analytics.analytics_agent import analytics_agent_node

    ch = Client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        database=os.getenv("CLICKHOUSE_DB", "marketos_analytics"),
        user=os.getenv("CLICKHOUSE_USER", "marketos"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "marketos_dev"),
    )

    state = _copy.deepcopy(minimal_state)
    campaign_id = state["campaign_plan"]["campaign_id"]
    ts = datetime.now(timezone.utc)

    # Insert 100 sends + 30 opens + 5 clicks
    rows = []
    for i in range(100):
        rows.append((str(uuid.uuid4()), campaign_id, "test", f"c-{i}", "send", "smtp", ts))
    for i in range(30):
        rows.append((str(uuid.uuid4()), campaign_id, "test", f"c-{i}", "open", "smtp", ts))
    for i in range(5):
        rows.append((str(uuid.uuid4()), campaign_id, "test", f"c-{i}", "click", "smtp", ts))

    ch.execute(
        "INSERT INTO email_events_local "
        "(event_id, campaign_id, workspace_id, contact_id, event_type, provider, timestamp) VALUES",
        rows,
    )

    result = analytics_agent_node(state)
    m = result["analytics_result"]["metrics"]

    # Must use real data (not default 25000 simulated)
    assert m["total_sent"] == 100, f"Expected 100 sends from CH, got {m['total_sent']}"
    assert m["opens"] == 30
    assert m["clicks"] == 5


def test_clickhouse_sink_parse_timestamp():
    """ClickHouse sink must parse ISO timestamps correctly."""
    from utils.clickhouse_sink import _parse_timestamp

    ts = _parse_timestamp("2025-01-01T10:00:00+00:00")
    assert ts.year == 2025
    assert ts.month == 1

    ts_z = _parse_timestamp("2025-06-15T12:30:00Z")
    assert ts_z.month == 6

    ts_none = _parse_timestamp(None)
    assert ts_none is not None  # fallback to now


def test_clickhouse_sink_event_type_mapping():
    """Sink must map Kafka event_type strings to ClickHouse Enum values."""
    from utils.clickhouse_sink import EVENT_TYPE_MAP

    assert EVENT_TYPE_MAP["email_sent"] == "send"
    assert EVENT_TYPE_MAP["email_open"] == "open"
    assert EVENT_TYPE_MAP["email_click"] == "click"
    assert EVENT_TYPE_MAP["spam_complaint"] == "spam_complaint"
    assert EVENT_TYPE_MAP.get("unknown_event") is None  # must not map unknown types
