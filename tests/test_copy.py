"""
Unit tests — Copy Agent
Tests: variant generation, schema validation, scoring fields,
       HTML structure, DB write attempt, Kafka events, selected variant logic.
"""

import pytest

pytestmark = pytest.mark.unit


def test_copy_generates_two_variants(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    state = {
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    }
    result = copy_agent_node(state)

    co = result.get("copy_output")
    assert co is not None, "copy_output must be in result"
    assert len(co.get("variants", [])) >= 2, "Must produce at least 2 variants"


def test_copy_variants_have_required_fields(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    result = copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    variants = result["copy_output"]["variants"]
    required = [
        "variant_id", "subject_line", "preview_text", "body_html",
        "body_text", "cta_text", "cta_url",
        "readability_score", "tone_alignment_score", "spam_risk_score",
        "estimated_open_rate", "estimated_ctr",
    ]
    for v in variants:
        for field in required:
            assert field in v, f"Variant missing field: {field}"


def test_copy_scores_are_numeric(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    result = copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    for v in result["copy_output"]["variants"]:
        assert isinstance(v["readability_score"], (int, float))
        assert isinstance(v["spam_risk_score"], (int, float))
        assert isinstance(v["estimated_open_rate"], (int, float))
        assert 0 < v["estimated_open_rate"] < 100, "Open rate should be a percentage"


def test_copy_selected_variant_exists(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    result = copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    co = result["copy_output"]
    sel_id = co.get("selected_variant_id")
    variant_ids = [v["variant_id"] for v in co["variants"]]
    assert sel_id in variant_ids, f"selected_variant_id '{sel_id}' not in variants {variant_ids}"


def test_copy_html_contains_cta(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    result = copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    co = result["copy_output"]
    sel_id = co["selected_variant_id"]
    winner = next(v for v in co["variants"] if v["variant_id"] == sel_id)
    assert "<a " in winner["body_html"] or "href" in winner["body_html"], \
        "HTML must contain a link/CTA"


def test_copy_publishes_kafka_event(minimal_state):
    from utils.kafka_bus import clear_event_log, get_event_log
    from agents.copy.copy_agent import copy_agent_node

    clear_event_log()
    copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    topics = [e["topic"] for e in get_event_log()]
    assert "agent.copy_agent.results" in topics


def test_copy_sets_correct_next_step(minimal_state):
    from agents.copy.copy_agent import copy_agent_node

    result = copy_agent_node({
        "campaign_plan": minimal_state["campaign_plan"],
        "errors": [], "trace": [],
    })
    assert result["current_step"] == "compliance_agent"
