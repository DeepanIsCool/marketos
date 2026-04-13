"""
Unit tests — Lead Scoring Agent
Tests: scoring weights, decay math, stage transitions, CRM escalation logic.
"""

import pytest

pytestmark = pytest.mark.unit


class TestScoreDecay:
    def test_no_decay_at_zero_days(self):
        from agents.lead_scoring.lead_scoring_agent import ScoreDecaySkill

        result = ScoreDecaySkill.apply(score=100.0, last_activity_days_ago=0)
        assert result == 100.0

    def test_half_score_at_decay_period(self):
        from agents.lead_scoring.lead_scoring_agent import ScoreDecaySkill, SCORE_DECAY_DAYS

        result = ScoreDecaySkill.apply(100.0, last_activity_days_ago=SCORE_DECAY_DAYS)
        assert abs(result - 50.0) < 1.0

    def test_decay_is_monotonic(self):
        from agents.lead_scoring.lead_scoring_agent import ScoreDecaySkill

        scores = [ScoreDecaySkill.apply(100.0, d) for d in [0, 10, 20, 30, 60]]
        assert scores == sorted(scores, reverse=True), "Decay must be monotonically decreasing"


class TestStageMachine:
    def test_subscriber_below_mql(self):
        from agents.lead_scoring.lead_scoring_agent import StageMachineSkill

        assert StageMachineSkill.resolve_stage(30.0) == "subscriber"

    def test_mql_at_threshold(self):
        from agents.lead_scoring.lead_scoring_agent import StageMachineSkill, MQL_THRESHOLD

        assert StageMachineSkill.resolve_stage(MQL_THRESHOLD) == "mql"

    def test_sql_at_threshold(self):
        from agents.lead_scoring.lead_scoring_agent import StageMachineSkill, SQL_THRESHOLD

        assert StageMachineSkill.resolve_stage(SQL_THRESHOLD) == "sql"

    def test_customer_on_purchase(self):
        from agents.lead_scoring.lead_scoring_agent import StageMachineSkill

        assert StageMachineSkill.resolve_stage(0.0, has_purchase=True) == "customer"

    def test_stage_changed_detects_upgrade(self):
        from agents.lead_scoring.lead_scoring_agent import StageMachineSkill

        assert StageMachineSkill.stage_changed("subscriber", "mql") is True
        assert StageMachineSkill.stage_changed("mql", "mql") is False
        assert StageMachineSkill.stage_changed("sql", "mql") is False  # downgrade = False


class TestBehaviourPatterns:
    def test_detects_high_click_rate(self):
        from agents.lead_scoring.lead_scoring_agent import BehaviourPatternSkill
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        history = [
            {"event_type": "email_click", "timestamp": (now - timedelta(hours=1)).isoformat()}
            for _ in range(4)
        ]
        signals = BehaviourPatternSkill.detect(history)
        assert any("clicks" in s.lower() for s in signals), "Must detect high click rate"

    def test_detects_pricing_page(self):
        from agents.lead_scoring.lead_scoring_agent import BehaviourPatternSkill

        history = [{"event_type": "page_visit", "url": "https://voltx.in/pricing"}]
        signals = BehaviourPatternSkill.detect(history)
        assert any("pricing" in s.lower() for s in signals)


def test_score_engagement_event_email_open():
    from agents.lead_scoring.lead_scoring_agent import score_engagement_event

    result = score_engagement_event("test-contact-open", "email_open")
    assert result["score_delta"] == 5.0
    assert result["lifecycle_stage"] in ("subscriber", "mql", "sql", "opportunity", "customer")


def test_score_engagement_event_purchase():
    from agents.lead_scoring.lead_scoring_agent import score_engagement_event

    result = score_engagement_event("test-contact-purchase", "purchase")
    assert result["new_score"] >= 100.0
    assert result["lifecycle_stage"] in ("sql", "opportunity", "customer")


def test_unsubscribe_reduces_score():
    from agents.lead_scoring.lead_scoring_agent import score_engagement_event

    result = score_engagement_event("test-contact-unsub", "unsubscribe")
    assert result["score_delta"] == -50.0


def test_lead_scoring_agent_node_completes(minimal_state):
    import copy as _copy
    from agents.lead_scoring.lead_scoring_agent import lead_scoring_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {"opens": 100, "clicks": 20, "spam_complaints": 1}
    }
    result = lead_scoring_agent_node(state)
    lr = result.get("lead_scoring_result")
    assert lr is not None
    assert lr["contacts_scored"] > 0
    assert "stage_distribution" in lr
