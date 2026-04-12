"""
MarketOS — Final Campaign Graph (Phase 4 — Complete)
All 16 agents. Two independent pipelines.

PIPELINE A — Campaign Execution (triggered by campaign intent):
  supervisor → copy → image → compliance → finance → email → sms → social
                                                              ↓
                                                         analytics → monitor → ab_test
                                                              ↓
                                                         lead_scoring → competitor → seo
                                                              ↓
                                                         reporting → END

PIPELINE B — Onboarding (triggered by new workspace signup):
  onboarding_agent → END

Note: SEO and Competitor agents run weekly/daily in production daemons.
      In the pipeline they run post-campaign for immediate context.
      personalization_agent is called inside email/sms agents (sub-call).
"""

from __future__ import annotations
from typing import TypedDict, Annotated, List, Optional
import operator

from langgraph.graph import StateGraph, END

# ── Import all agent nodes ─────────────────────────────────────────────────────
from agents.supervisor.supervisor_agent             import supervisor_node
from agents.copy.copy_agent                         import copy_agent_node
from agents.creative.image_engine                   import image_agent_node
from agents.compliance.compliance_agent             import compliance_agent_node, compliance_router
from agents.finance.finance_agent                   import finance_agent_node, finance_router
from agents.email.email_agent                       import email_agent_node
from agents.sms.sms_agent                           import sms_agent_node
from agents.social.social_media_agent               import social_media_agent_node
from agents.analytics.analytics_agent               import analytics_agent_node
from agents.monitor.monitor_agent                   import monitor_agent_node
from agents.ab_test.ab_test_agent                   import ab_test_agent_node
from agents.lead_scoring.lead_scoring_agent         import lead_scoring_agent_node
from agents.competitor.competitor_agent             import competitor_agent_node
from agents.seo.seo_agent                           import seo_agent_node
from agents.reporting.reporting_agent               import reporting_agent_node
from agents.onboarding.onboarding_agent             import onboarding_agent_node


# ── Graph State ────────────────────────────────────────────────────────────────

class CampaignState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────────────
    user_intent:             str
    pipeline:                Optional[str]   # "campaign" | "onboarding"

    # ── Onboarding context ──────────────────────────────────────────────────────
    workspace_id:            Optional[str]
    workspace_type:          Optional[str]
    user_name:               Optional[str]
    user_email:              Optional[str]
    industry:                Optional[str]

    # ── Send context ────────────────────────────────────────────────────────────
    recipient_email:         Optional[str]
    recipient_phone:         Optional[str]
    sender_name:             Optional[str]
    company_name:            Optional[str]
    company_address:         Optional[str]
    unsubscribe_url:         Optional[str]

    # ── Agent outputs ────────────────────────────────────────────────────────────
    campaign_plan:           Optional[dict]
    copy_output:             Optional[dict]
    compliance_result:       Optional[dict]
    finance_result:          Optional[dict]
    send_result:             Optional[dict]
    sms_result:              Optional[dict]
    social_result:           Optional[dict]
    analytics_result:        Optional[dict]
    monitor_result:          Optional[dict]
    ab_test_result:          Optional[dict]
    lead_scoring_result:     Optional[dict]
    competitor_result:       Optional[dict]
    seo_result:              Optional[dict]
    reporting_result:        Optional[dict]
    onboarding_result:       Optional[dict]

    # ── Internal ────────────────────────────────────────────────────────────────
    _episodic_memories:      Optional[list]

    # ── Control ─────────────────────────────────────────────────────────────────
    current_step:            str
    errors:                  Annotated[List[str], operator.add]
    trace:                   Annotated[List[dict], operator.add]


# ── Pipeline Router ────────────────────────────────────────────────────────────

def pipeline_router(state: dict) -> str:
    """Determines which pipeline to execute based on state.pipeline."""
    pipeline = state.get("pipeline", "campaign")
    if pipeline == "onboarding":
        return "onboarding_agent"
    return "supervisor"


# ── Campaign Graph ─────────────────────────────────────────────────────────────

def build_campaign_graph() -> StateGraph:
    g = StateGraph(CampaignState)

    # Register all nodes
    g.add_node("supervisor",          supervisor_node)
    g.add_node("copy_agent",          copy_agent_node)
    g.add_node("image_agent",         image_agent_node)
    g.add_node("compliance_agent",    compliance_agent_node)
    g.add_node("finance_agent",       finance_agent_node)
    g.add_node("email_agent",         email_agent_node)
    g.add_node("sms_agent",           sms_agent_node)
    g.add_node("social_media_agent",  social_media_agent_node)
    g.add_node("analytics_agent",     analytics_agent_node)
    g.add_node("monitor_agent",       monitor_agent_node)
    g.add_node("ab_test_agent",       ab_test_agent_node)
    g.add_node("lead_scoring_agent",  lead_scoring_agent_node)
    g.add_node("competitor_agent",    competitor_agent_node)
    g.add_node("seo_agent",           seo_agent_node)
    g.add_node("reporting_agent",     reporting_agent_node)
    g.add_node("onboarding_agent",    onboarding_agent_node)

    # Entry: dual pipeline
    g.set_entry_point("entry_router")
    g.add_node("entry_router", lambda state: state)
    g.add_conditional_edges("entry_router", pipeline_router,
        {"supervisor": "supervisor", "onboarding_agent": "onboarding_agent"})

    # ── Pipeline A: Campaign Execution ────────────────────────────────────
    g.add_edge("supervisor",         "competitor_agent")
    g.add_edge("competitor_agent",   "copy_agent")
    g.add_edge("copy_agent",         "image_agent")
    g.add_edge("image_agent",        "compliance_agent")

    g.add_conditional_edges("compliance_agent", compliance_router,
        {"email_agent": "finance_agent", "end": END})

    g.add_conditional_edges("finance_agent", finance_router,
        {"personalization_agent": "email_agent", "end": END})

    g.add_edge("email_agent",        "sms_agent")
    g.add_edge("sms_agent",          "social_media_agent")
    g.add_edge("social_media_agent", "analytics_agent")
    g.add_edge("analytics_agent",    "monitor_agent")
    g.add_edge("monitor_agent",      "ab_test_agent")
    g.add_edge("ab_test_agent",      "lead_scoring_agent")
    g.add_edge("lead_scoring_agent", "seo_agent")
    g.add_edge("seo_agent",          "reporting_agent")
    g.add_edge("reporting_agent",    END)

    # ── Pipeline B: Onboarding ─────────────────────────────────────────────
    g.add_edge("onboarding_agent",   END)

    return g.compile()


campaign_graph = build_campaign_graph()


# ── Convenience: run onboarding pipeline ─────────────────────────────────────

def run_onboarding(
    user_name:    str,
    user_email:   str,
    company_name: str = "",
    industry:     str = "",
    workspace_id: str = "default",
) -> dict:
    return campaign_graph.invoke({
        "user_intent":    f"Onboard new workspace for {user_name}",
        "pipeline":       "onboarding",
        "workspace_id":   workspace_id,
        "user_name":      user_name,
        "user_email":     user_email,
        "company_name":   company_name,
        "industry":       industry,
        "current_step":   "onboarding_agent",
        "errors":         [],
        "trace":          [],
    })
