"""
Unit tests — Reporting Agent
Tests: PDF generation, HTML email build, no NameError crashes,
       grade field present, PDF file created on disk.
"""

import pytest
import copy as _copy
import os

pytestmark = pytest.mark.unit


def test_reporting_agent_completes_without_crash(minimal_state):
    from agents.reporting.reporting_agent import reporting_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {
        "metrics": {
            "total_sent": 25000, "delivered": 24425, "opens": 7000,
            "clicks": 1050, "bounces_hard": 200, "unsubscribes": 50,
            "spam_complaints": 7, "open_rate": 0.286, "ctr": 0.043,
            "bounce_rate": 0.008, "spam_rate": 0.0003, "delivery_rate": 0.977,
        },
        "anomalies": [],
    }
    state["ab_test_result"] = {"winner_id": "V-001", "decision": "winner_declared"}
    state["lead_scoring_result"] = {
        "stage_distribution": {"subscriber": 6000, "mql": 800, "sql": 200}
    }
    state["competitor_result"] = {"intel": {"executive_summary": "Stable market."}}
    state["recipient_email"] = None  # no real email send

    # Must not raise
    result = reporting_agent_node(state)
    rr = result.get("reporting_result")
    assert rr is not None, "reporting_result must be in state"
    assert rr.get("report_id", "").startswith("RPT-")


def test_reporting_generates_pdf(minimal_state, tmp_path, monkeypatch):
    from agents.reporting.reporting_agent import reporting_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {"metrics": {}, "anomalies": []}
    state["ab_test_result"] = {}
    state["lead_scoring_result"] = {}
    state["competitor_result"] = {}
    state["recipient_email"] = None

    result = reporting_agent_node(state)
    pdf_path = result.get("reporting_result", {}).get("report_path")
    assert pdf_path is not None, "report_path must be set"
    assert os.path.exists(pdf_path), f"PDF file must exist at {pdf_path}"
    assert os.path.getsize(pdf_path) > 1000, "PDF must not be empty"


def test_reporting_grade_is_present(minimal_state):
    from agents.reporting.reporting_agent import reporting_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {"metrics": {
        "open_rate": 0.28, "ctr": 0.04, "delivery_rate": 0.97,
        "bounce_rate": 0.008, "spam_rate": 0.0003,
    }, "anomalies": []}
    state["ab_test_result"] = {}
    state["lead_scoring_result"] = {}
    state["competitor_result"] = {}
    state["recipient_email"] = None

    result = reporting_agent_node(state)
    grade = result["reporting_result"].get("grade")
    assert grade is not None, "Grade must be present in reporting_result"
    assert any(g in str(grade) for g in ["A", "B", "C", "D", "F"]), \
        f"Grade must be A-F, got: {grade}"


def test_reporting_does_not_email_without_recipient(minimal_state):
    from agents.reporting.reporting_agent import reporting_agent_node

    state = _copy.deepcopy(minimal_state)
    state["analytics_result"] = {"metrics": {}, "anomalies": []}
    state["ab_test_result"] = {}
    state["lead_scoring_result"] = {}
    state["competitor_result"] = {}
    state["recipient_email"] = None

    result = reporting_agent_node(state)
    rr = result["reporting_result"]
    assert rr["emailed"] is False, "Must not send email when no recipient set"


def test_reporting_appends_trace(minimal_state):
    from agents.reporting.reporting_agent import reporting_agent_node

    state = _copy.deepcopy(minimal_state)
    for key in ["analytics_result", "ab_test_result", "lead_scoring_result", "competitor_result"]:
        state[key] = {}
    state["recipient_email"] = None

    result = reporting_agent_node(state)
    assert any(t["agent"] == "reporting_agent" for t in result["trace"])
