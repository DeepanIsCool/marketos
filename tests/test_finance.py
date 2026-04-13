"""
Unit tests — Finance Agent
Tests: budget gate logic, ROAS calculation, pacing math,
       router function, DB-independent fallback.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


def test_finance_approves_zero_spend(minimal_state):
    from agents.finance.finance_agent import finance_agent_node

    result = finance_agent_node(minimal_state)
    fr = result.get("finance_result")
    assert fr is not None
    assert fr["approved"] is True


def test_finance_result_has_required_fields(minimal_state):
    from agents.finance.finance_agent import finance_agent_node

    result = finance_agent_node(minimal_state)
    fr = result["finance_result"]
    for field in ["approved", "budget_total", "budget_spent", "spend_pct", "pacing", "roi"]:
        assert field in fr, f"finance_result missing: {field}"


def test_finance_spend_pct_is_zero_on_fresh_campaign(minimal_state):
    from agents.finance.finance_agent import finance_agent_node

    result = finance_agent_node(minimal_state)
    fr = result["finance_result"]
    # Fresh campaign has no spend in DB — should be 0
    assert fr["spend_pct"] == 0.0
    assert fr["budget_spent"] == 0.0


def test_finance_router_returns_email_agent(minimal_state):
    from agents.finance.finance_agent import finance_router

    state = _copy.deepcopy(minimal_state)
    state["finance_result"] = {"approved": True}
    assert finance_router(state) == "email_agent"


def test_finance_router_returns_end_on_blocked(minimal_state):
    from agents.finance.finance_agent import finance_router

    state = _copy.deepcopy(minimal_state)
    state["finance_result"] = {"approved": False}
    assert finance_router(state) == "end"


def test_finance_blocks_overspend(monkeypatch, minimal_state):
    """Patch DB to return overspent state — gate must block."""
    import agents.finance.finance_agent as fa

    original = fa._load_campaign_spend
    fa._load_campaign_spend = lambda cid: {"spent": 90000.0, "conversions": 0}

    try:
        result = fa.finance_agent_node(minimal_state)
        fr = result["finance_result"]
        assert fr["approved"] is False, "Must block when spend > 110% of budget"
        assert fr["spend_pct"] > 1.10
    finally:
        fa._load_campaign_spend = original


def test_budget_pacing_skill_projects_correctly():
    from agents.finance.finance_agent import BudgetPacingSkill

    # Spent ₹10k in 10 hours on ₹100k budget → projects ₹24k EOD (24%)
    result = BudgetPacingSkill.calculate(spent=10000, budget=100000, hour_of_day=10)
    assert result["pacing_ok"] is True
    assert result["projected_spend"] == pytest.approx(24000.0, rel=0.05)


def test_roas_calculator_correct():
    from agents.finance.finance_agent import ROASCalculatorSkill

    result = ROASCalculatorSkill.calculate(spend=10000, conversions=20, avg_order_value=999)
    assert result["attributed_revenue"] == pytest.approx(19980.0)
    assert result["roas"] == pytest.approx(1.998, rel=0.01)
    assert result["profitable"] is False  # < 2x threshold


def test_roas_zero_spend_returns_zeroes():
    from agents.finance.finance_agent import ROASCalculatorSkill

    result = ROASCalculatorSkill.calculate(spend=0, conversions=5)
    assert result["roas"] == 0.0
    assert result["cpa"] == 0.0


def test_currency_norm_usd_to_inr():
    from agents.finance.finance_agent import CurrencyNormSkill

    inr = CurrencyNormSkill.to_inr(100.0, "USD")
    assert inr == pytest.approx(8350.0, rel=0.01)


def test_finance_appends_trace(minimal_state):
    from agents.finance.finance_agent import finance_agent_node

    result = finance_agent_node(minimal_state)
    trace = result.get("trace", [])
    assert any(t["agent"] == "finance_agent" for t in trace)
