"""
Smoke tests — Graph + API imports
These must pass before running anything else.
They are fast (no LLM calls) and catch import errors.
"""

import pytest

pytestmark = pytest.mark.unit


def test_graph_imports_cleanly():
    """If this fails, there's a module-level crash (bare import, syntax error)."""
    from graph.campaign_graph import campaign_graph
    assert campaign_graph is not None


def test_all_agent_modules_importable():
    import importlib

    modules = [
        "agents.supervisor.supervisor_agent",
        "agents.competitor.competitor_agent",
        "agents.copy.copy_agent",
        "agents.creative.image_engine",
        "agents.compliance.compliance_agent",
        "agents.finance.finance_agent",
        "agents.email.email_agent",
        "agents.sms.sms_agent",
        "agents.social.social_media_agent",
        "agents.analytics.analytics_agent",
        "agents.monitor.monitor_agent",
        "agents.ab_test.ab_test_agent",
        "agents.lead_scoring.lead_scoring_agent",
        "agents.seo.seo_agent",
        "agents.reporting.reporting_agent",
        "agents.onboarding.onboarding_agent",
        "agents.personalization.personalization_agent",
    ]
    errors = {}
    for mod in modules:
        try:
            importlib.import_module(mod)
        except Exception as e:
            errors[mod] = str(e)

    assert not errors, f"Agent import failures:\n" + "\n".join(
        f"  {mod}: {err}" for mod, err in errors.items()
    )


def test_utils_importable():
    import importlib

    utils = [
        "utils.kafka_bus",
        "utils.memory",
        "utils.json_utils",
        "utils.logger",
        "utils.sendgrid_mailer",
        "utils.clickhouse_sink",
        "utils.dlq_handler",
        "utils.agent_base",
    ]
    for mod in utils:
        try:
            importlib.import_module(mod)
        except Exception as e:
            pytest.fail(f"utils import failed: {mod} → {e}")


def test_schemas_importable():
    from schemas.campaign import (
        CampaignPlan, CopyVariant, CopyOutput,
        ComplianceResult, SendResult, AgentTask,
    )
    assert CampaignPlan is not None


def test_campaign_state_typeddict_has_required_fields():
    from graph.campaign_graph import CampaignState
    import typing

    hints = typing.get_type_hints(CampaignState)
    required = [
        "user_intent", "campaign_plan", "copy_output", "compliance_result",
        "send_result", "analytics_result", "ab_test_result", "lead_scoring_result",
        "reporting_result", "errors", "trace",
    ]
    for field in required:
        assert field in hints, f"CampaignState missing field: {field}"


def test_pipeline_router_returns_correct_branch():
    from graph.campaign_graph import pipeline_router

    assert pipeline_router({"pipeline": "campaign"}) == "supervisor"
    assert pipeline_router({"pipeline": "onboarding"}) == "onboarding_agent"
    assert pipeline_router({}) == "supervisor"  # default


def test_finance_router_returns_email_agent():
    from agents.finance.finance_agent import finance_router

    assert finance_router({"finance_result": {"approved": True}}) == "email_agent"
    assert finance_router({"finance_result": {"approved": False}}) == "end"


def test_compliance_router_returns_correct_next():
    from agents.compliance.compliance_agent import compliance_router

    assert compliance_router({"compliance_result": {"approved": True}}) == "email_agent"
    assert compliance_router({"compliance_result": {"approved": False}}) == "end"
