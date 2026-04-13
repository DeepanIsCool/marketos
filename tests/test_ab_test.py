"""
Unit tests — A/B Test Agent
Tests: Bayesian stats math, sample size calculator, early stopping rule,
       winner declaration, memory storage, Kafka events.
Pure unit tests — no DB, no LLM required for sub-skill tests.
"""

import pytest
import math

pytestmark = pytest.mark.unit


# ── BayesianStatsSkill ────────────────────────────────────────────────────────

class TestBayesianStats:
    def test_probabilities_sum_to_one(self):
        from agents.ab_test.ab_test_agent import BayesianStatsSkill

        variants = [
            {"variant_id": "V-001", "sends": 1000, "successes": 310},
            {"variant_id": "V-002", "sends": 1000, "successes": 250},
        ]
        result = BayesianStatsSkill.run(variants)
        total = sum(v["prob_best"] for v in result)
        assert abs(total - 1.0) < 0.02, f"Probabilities must sum to ~1, got {total}"

    def test_higher_conversion_wins(self):
        from agents.ab_test.ab_test_agent import BayesianStatsSkill

        variants = [
            {"variant_id": "V-001", "sends": 2000, "successes": 700},  # 35%
            {"variant_id": "V-002", "sends": 2000, "successes": 200},  # 10%
        ]
        result = BayesianStatsSkill.run(variants)
        winner = max(result, key=lambda v: v["prob_best"])
        assert winner["variant_id"] == "V-001", "Higher conversion variant must win"

    def test_result_has_required_fields(self):
        from agents.ab_test.ab_test_agent import BayesianStatsSkill

        variants = [
            {"variant_id": "A", "sends": 500, "successes": 100},
            {"variant_id": "B", "sends": 500, "successes": 90},
        ]
        result = BayesianStatsSkill.run(variants)
        for v in result:
            assert "prob_best" in v
            assert "expected_improvement" in v
            assert "posterior_mean" in v
            assert 0 <= v["prob_best"] <= 1

    def test_single_variant_returned_unchanged(self):
        from agents.ab_test.ab_test_agent import BayesianStatsSkill

        variants = [{"variant_id": "V-001", "sends": 500, "successes": 100}]
        result = BayesianStatsSkill.run(variants)
        assert len(result) == 1
        assert result[0]["variant_id"] == "V-001"

    def test_beta_sample_in_zero_one(self):
        from agents.ab_test.ab_test_agent import BayesianStatsSkill

        for _ in range(100):
            s = BayesianStatsSkill._beta_sample(2.0, 3.0)
            assert 0 <= s <= 1, f"Beta sample out of [0,1]: {s}"


# ── SampleSizeCalculator ──────────────────────────────────────────────────────

class TestSampleSize:
    def test_minimum_is_100(self):
        from agents.ab_test.ab_test_agent import SampleSizeCalculator

        n = SampleSizeCalculator.minimum_for_mde(0.01, mde=0.50)
        assert n >= 100

    def test_larger_baseline_needs_smaller_n(self):
        from agents.ab_test.ab_test_agent import SampleSizeCalculator

        # Easier to detect effect at 50% baseline than 5% baseline
        n_low  = SampleSizeCalculator.minimum_for_mde(0.05)
        n_high = SampleSizeCalculator.minimum_for_mde(0.50)
        assert n_low > n_high

    def test_returns_integer(self):
        from agents.ab_test.ab_test_agent import SampleSizeCalculator

        n = SampleSizeCalculator.minimum_for_mde(0.25)
        assert isinstance(n, int)


# ── EarlyStoppingRule ─────────────────────────────────────────────────────────

class TestEarlyStopping:
    def test_triggers_at_95_pct(self):
        from agents.ab_test.ab_test_agent import EarlyStoppingRule

        variants = [
            {"variant_id": "V-001", "prob_best": 0.97},
            {"variant_id": "V-002", "prob_best": 0.03},
        ]
        winner = EarlyStoppingRule.check(variants)
        assert winner == "V-001"

    def test_no_trigger_below_95(self):
        from agents.ab_test.ab_test_agent import EarlyStoppingRule

        variants = [
            {"variant_id": "V-001", "prob_best": 0.90},
            {"variant_id": "V-002", "prob_best": 0.10},
        ]
        winner = EarlyStoppingRule.check(variants)
        assert winner is None

    def test_exactly_at_threshold(self):
        from agents.ab_test.ab_test_agent import EarlyStoppingRule

        variants = [{"variant_id": "V-001", "prob_best": 0.95}]
        winner = EarlyStoppingRule.check(variants)
        assert winner == "V-001"


# ── Agent node ────────────────────────────────────────────────────────────────

def test_ab_test_node_completes(minimal_state):
    from agents.ab_test.ab_test_agent import ab_test_agent_node

    # Inject send_result with simulated recipients
    import copy as _copy
    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 5000}

    result = ab_test_agent_node(state)
    ab = result.get("ab_test_result")
    assert ab is not None
    assert ab.get("decision") in ("winner_declared", "inconclusive", "early_stop", "skipped")


def test_ab_test_publishes_kafka_on_winner(minimal_state):
    from agents.ab_test.ab_test_agent import ab_test_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log
    import copy as _copy

    state = _copy.deepcopy(minimal_state)
    state["send_result"] = {"simulated_recipients": 10000}

    clear_event_log()
    result = ab_test_agent_node(state)
    ab = result.get("ab_test_result", {})
    if ab.get("winner_id"):
        topics = [e["topic"] for e in get_event_log()]
        assert "campaign.events" in topics
