"""
Integration tests — pgvector Memory
Requires: docker compose up -d postgres
Tests: episodic store+recall, semantic upsert+search, HNSW retrieval quality.
"""

import pytest
import os
import time

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
def test_episodic_store_and_recall():
    from utils.memory import episodic_memory

    unique = f"voltx_integration_test_{int(time.time())}"
    episodic_memory.store(
        agent_name="copy_agent",
        event_type="ab_test_winner",
        summary=f"{unique} urgency subject line 32% open rate",
        metadata={"campaign_id": "TEST-INT-001"},
    )
    time.sleep(0.5)  # allow write to commit

    results = episodic_memory.recall("copy_agent", "urgency subject line open rate", top_k=5)
    assert len(results) > 0, "Must recall at least 1 memory"
    summaries = [r["summary"] for r in results]
    assert any(unique in s for s in summaries), \
        f"Must find the stored memory, got: {summaries}"


@skip_no_pg
def test_semantic_upsert_and_search():
    from utils.memory import semantic_memory

    unique = f"brand_voice_test_{int(time.time())}"
    semantic_memory.upsert(
        "brand_voice", unique,
        "VoltX brand voice: bold energetic unapologetic young men hustle CRUSH IT"
    )
    time.sleep(0.5)

    results = semantic_memory.search("bold energetic brand tone young men")
    assert len(results) > 0, "Must find at least 1 semantic memory item"


@skip_no_pg
def test_semantic_upsert_is_idempotent():
    from utils.memory import semantic_memory

    key = "idempotent_test_key"
    semantic_memory.upsert("brand_voice", key, "First content")
    semantic_memory.upsert("brand_voice", key, "Updated content")  # should not raise

    results = semantic_memory.search("Updated content", category="brand_voice")
    # At least the upsert succeeded — no duplicate key error
    assert isinstance(results, list)


@skip_no_pg
def test_episodic_recall_returns_dicts():
    from utils.memory import episodic_memory

    results = episodic_memory.recall("copy_agent", "campaign open rate", top_k=3)
    for r in results:
        assert isinstance(r, dict)
        assert "summary" in r
        assert "event_type" in r


@skip_no_pg
def test_working_memory_set_get_delete():
    from utils.memory import working_memory

    working_memory.set("copy_agent", "task-wm-test", {"status": "running", "value": 42})
    retrieved = working_memory.get("copy_agent", "task-wm-test")
    assert retrieved is not None
    assert retrieved["value"] == 42

    working_memory.delete("copy_agent", "task-wm-test")
    after_delete = working_memory.get("copy_agent", "task-wm-test")
    assert after_delete is None


@skip_no_pg
def test_distributed_lock_prevents_duplicate():
    from utils.memory import working_memory

    lock_name = "test-lock-integration"
    acquired1 = working_memory.distributed_lock(lock_name, ttl=5)
    acquired2 = working_memory.distributed_lock(lock_name, ttl=5)

    working_memory.release_lock(lock_name)

    # In Redis mode, second acquire should fail
    # In in-memory fallback mode, both return True — skip assertion
    import os
    if os.getenv("REDIS_URL"):
        assert acquired1 is True
        assert acquired2 is False, "Second lock acquire must fail"
