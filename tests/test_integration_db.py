"""
Integration tests — Database (PostgreSQL + pgvector)
Requires: docker compose up -d postgres
Run: pytest tests/test_integration_db.py -m integration -v
"""

import pytest
import os

pytestmark = pytest.mark.integration

PG_DSN = os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos")


def _pg_available():
    try:
        import psycopg2
        conn = psycopg2.connect(PG_DSN)
        conn.close()
        return True
    except Exception:
        return False


skip_no_pg = pytest.mark.skipif(not _pg_available(), reason="PostgreSQL not reachable")


@skip_no_pg
def test_copy_variants_written_after_copy_agent(minimal_state):
    """After copy_agent runs, copy_variants table must have rows for this campaign."""
    import psycopg2
    from agents.copy.copy_agent import copy_agent_node

    state = {
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    }
    result = copy_agent_node(state)
    campaign_id = result["campaign_plan"]["campaign_id"]

    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM copy_variants WHERE campaign_id = %s", (campaign_id,))
    count = cur.fetchone()[0]
    conn.close()
    assert count >= 2, f"Expected ≥2 variants in DB for campaign {campaign_id}, got {count}"


@skip_no_pg
def test_ab_variant_stats_written_after_email_agent(minimal_state):
    """After email_agent runs, ab_variant_stats must have rows."""
    import psycopg2
    from agents.copy.copy_agent import copy_agent_node
    from agents.compliance.compliance_agent import compliance_agent_node
    from agents.finance.finance_agent import finance_agent_node
    from agents.email.email_agent import email_agent_node
    import copy as _copy

    state = {
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    }
    state = copy_agent_node(state)
    state = compliance_agent_node(state)
    state = finance_agent_node(state)
    state["recipient_email"] = None
    state = email_agent_node(state)

    campaign_id = state["campaign_plan"]["campaign_id"]
    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ab_variant_stats WHERE campaign_id = %s", (campaign_id,))
    count = cur.fetchone()[0]
    conn.close()
    assert count >= 2, f"Expected ≥2 ab_variant_stats rows, got {count}"


@skip_no_pg
def test_campaigns_table_has_running_status(minimal_state):
    """After copy_agent runs, campaigns table must have status=running."""
    import psycopg2
    from agents.copy.copy_agent import copy_agent_node

    state = {
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    }
    result = copy_agent_node(state)
    campaign_id = result["campaign_plan"]["campaign_id"]

    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute("SELECT status FROM campaigns WHERE campaign_id = %s", (campaign_id,))
    row = cur.fetchone()
    conn.close()
    assert row is not None, f"Campaign {campaign_id} not found in campaigns table"
    assert row[0] == "running"


@skip_no_pg
def test_hnsw_index_exists():
    """Verify HNSW index was created (not IVFFlat)."""
    import psycopg2

    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename IN ('agent_episodic_memory', 'agent_semantic_memory')
        AND indexname LIKE '%embedding%'
    """)
    rows = cur.fetchall()
    conn.close()

    assert len(rows) >= 2, "Must have embedding indexes on both memory tables"
    for name, defn in rows:
        assert "hnsw" in defn.lower(), \
            f"Index {name} must use HNSW, got: {defn}"


@skip_no_pg
def test_contact_scores_upsert():
    """Lead scoring DB write must be idempotent via ON CONFLICT."""
    from agents.lead_scoring.lead_scoring_agent import _save_contact_score, _load_contact_score

    cid = "integration-test-contact-upsert"
    _save_contact_score(cid, 50.0, "mql")
    result1 = _load_contact_score(cid)
    assert abs(result1["score"] - 50.0) < 1.0

    _save_contact_score(cid, 100.0, "sql")
    result2 = _load_contact_score(cid)
    assert abs(result2["score"] - 100.0) < 1.0
    assert result2["lifecycle_stage"] == "sql"
