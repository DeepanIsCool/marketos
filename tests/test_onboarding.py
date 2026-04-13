"""
Unit tests — Onboarding Agent
Tests: workspace classification, drip sequence structure,
       task list generation, Kafka drip trigger event.
"""

import pytest

pytestmark = pytest.mark.unit


class TestWorkspaceClassifier:
    def test_classifies_ecommerce(self):
        from agents.onboarding.onboarding_agent import WorkspaceClassifierSkill

        t = WorkspaceClassifierSkill.classify("ShopifyStore", "retail", "d2c products")
        assert t == "ecommerce"

    def test_classifies_saas(self):
        from agents.onboarding.onboarding_agent import WorkspaceClassifierSkill

        t = WorkspaceClassifierSkill.classify("SaaS App", "software", "subscription platform")
        assert t == "saas"

    def test_classifies_agency(self):
        from agents.onboarding.onboarding_agent import WorkspaceClassifierSkill

        t = WorkspaceClassifierSkill.classify("Creative Agency", "marketing agency", "clients")
        assert t == "agency"

    def test_defaults_to_general(self):
        from agents.onboarding.onboarding_agent import WorkspaceClassifierSkill

        t = WorkspaceClassifierSkill.classify("Unknown Corp", "", "")
        assert t == "general"


class TestDripSequenceBuilder:
    def test_ecommerce_drip_has_five_steps(self):
        from agents.onboarding.onboarding_agent import DripSequenceBuilderSkill

        drip = DripSequenceBuilderSkill.build("ecommerce", "Priya")
        assert len(drip) == 5

    def test_drip_steps_have_required_fields(self):
        from agents.onboarding.onboarding_agent import DripSequenceBuilderSkill

        drip = DripSequenceBuilderSkill.build("general", "Rahul")
        for step in drip:
            assert "day" in step
            assert "subject" in step
            assert "goal" in step
            assert "send_at" in step
            assert "status" in step

    def test_drip_days_are_ascending(self):
        from agents.onboarding.onboarding_agent import DripSequenceBuilderSkill

        drip = DripSequenceBuilderSkill.build("saas", "Arjun")
        days = [s["day"] for s in drip]
        assert days == sorted(days)


class TestTaskListGenerator:
    def test_ecommerce_has_high_priority_tasks(self):
        from agents.onboarding.onboarding_agent import TaskListGeneratorSkill

        tasks = TaskListGeneratorSkill.generate("ecommerce")
        high_priority = [t for t in tasks if t["priority"] == "HIGH"]
        assert len(high_priority) >= 2

    def test_all_tasks_have_docs_link(self):
        from agents.onboarding.onboarding_agent import TaskListGeneratorSkill

        for workspace_type in ["ecommerce", "saas", "general"]:
            for task in TaskListGeneratorSkill.generate(workspace_type):
                assert task.get("docs", "").startswith("/docs/"), \
                    f"Task must have /docs/ link: {task}"


def test_onboarding_agent_completes():
    from agents.onboarding.onboarding_agent import onboarding_agent_node

    state = {
        "user_intent":    "Onboard VoltX workspace",
        "pipeline":       "onboarding",
        "workspace_id":   "test-workspace",
        "user_name":      "Rahul",
        "user_email":     "rahul@voltx.in",
        "company_name":   "VoltX Energy Pvt. Ltd.",
        "industry":       "energy drink d2c retail",
        "errors":         [],
        "trace":          [],
    }
    result = onboarding_agent_node(state)
    ob = result.get("onboarding_result")
    assert ob is not None
    assert ob.get("workspace_type") == "ecommerce"
    assert len(ob.get("drip_sequence", [])) >= 3
    assert len(ob.get("task_list", [])) >= 3


def test_onboarding_publishes_drip_event():
    from agents.onboarding.onboarding_agent import onboarding_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    state = {
        "user_intent": "Onboard test",
        "pipeline": "onboarding",
        "workspace_id": "test",
        "user_name": "Test",
        "user_email": "test@test.com",
        "errors": [], "trace": [],
    }
    onboarding_agent_node(state)
    topics = [e["topic"] for e in get_event_log()]
    assert "agent.email_agent.tasks" in topics, "Day-1 drip must be published to Kafka"
