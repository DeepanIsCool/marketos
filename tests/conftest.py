"""
MarketOS — Shared pytest fixtures.
All fixtures return plain dicts that mirror real LangGraph state.
"""

import pytest


# ── Minimal valid campaign plan ────────────────────────────────────────────

@pytest.fixture
def plan():
    return {
        "campaign_id":     "TEST-0001",
        "campaign_name":   "VoltX BF Test",
        "goal":            "500 conversions in 3 days",
        "target_audience": "Men 18-30 India, fitness + gaming",
        "channels":        ["email"],
        "budget":          75000.0,
        "timeline":        "3 days",
        "tone":            "bold",
        "key_messages":    [
            "Buy 2 Get 1 Free on VoltX Original",
            "Sale ends Monday midnight",
            "₹99 per can — cheapest energy drink in India",
        ],
        "tasks":           [],
        "created_at":      "2025-01-01T00:00:00+00:00",
    }


# ── Minimal valid copy output (2 variants, both with footer) ───────────────

FOOTER_HTML = (
    "<tr><td>"
    "<p>VoltX Energy · Level 5, Bengaluru 560071</p>"
    "<a href='https://voltx.in/unsub'>Unsubscribe</a>"
    "</td></tr>"
)

BODY_HTML_BASE = (
    "<html><body><table><tr><td>"
    "<h1>VoltX Black Friday</h1><p>Buy 2 Get 1 Free</p>"
    "<a href='https://voltx.in/bf'>Shop Now</a>"
    "</td></tr>"
    + FOOTER_HTML
    + "</table></body></html>"
)

BODY_TEXT_BASE = (
    "VoltX Black Friday — Buy 2 Get 1 Free.\n"
    "Shop: https://voltx.in/bf\n\n"
    "VoltX Energy | Level 5, Bengaluru 560071\n"
    "Unsubscribe: https://voltx.in/unsub\n"
)


@pytest.fixture
def copy_output(plan):
    return {
        "variants": [
            {
                "variant_id":           "V-001",
                "subject_line":         "VoltX BF: Buy 2 Get 1 Free 🔥",
                "preview_text":         "48-hour flash sale — don't miss out",
                "body_html":            BODY_HTML_BASE,
                "body_text":            BODY_TEXT_BASE,
                "cta_text":             "Grab the Deal",
                "cta_url":              "https://voltx.in/bf",
                "hero_image_query":     "energy drink can neon",
                "hero_image_prompt":    "Neon green energy drink can on matte black surface",
                "readability_score":    82.0,
                "tone_alignment_score": 91.0,
                "spam_risk_score":      9.0,
                "estimated_open_rate":  31.5,
                "estimated_ctr":        4.2,
            },
            {
                "variant_id":           "V-002",
                "subject_line":         "Cheapest energy drink in India",
                "preview_text":         "More caffeine per rupee than Red Bull",
                "body_html":            BODY_HTML_BASE,
                "body_text":            BODY_TEXT_BASE,
                "cta_text":             "Shop Now",
                "cta_url":              "https://voltx.in/bf",
                "hero_image_query":     "energy drink gym",
                "hero_image_prompt":    "Gym athlete holding green energy drink can",
                "readability_score":    79.0,
                "tone_alignment_score": 88.0,
                "spam_risk_score":      11.0,
                "estimated_open_rate":  28.0,
                "estimated_ctr":        3.8,
            },
        ],
        "selected_variant_id": "V-001",
        "selection_reasoning": "V-001 has higher estimated open rate and stronger urgency framing.",
        "brand_voice_notes":   "Bold, punchy sentences. No passive voice.",
    }


# ── Compliance result ──────────────────────────────────────────────────────

@pytest.fixture
def compliance_result():
    return {
        "approved":          True,
        "compliance_score":  94.0,
        "checks":            [],
        "reason_code":       None,
        "blocked_reason":    None,
        "suggestions":       [],
        "reviewed_at":       "2025-01-01T00:00:00+00:00",
    }


# ── Full minimal pipeline state ────────────────────────────────────────────

@pytest.fixture
def minimal_state(plan, copy_output, compliance_result):
    return {
        "user_intent":       "Launch VoltX Black Friday campaign",
        "pipeline":          "campaign",
        "workspace_id":      "test",
        "campaign_plan":     plan,
        "copy_output":       copy_output,
        "compliance_result": compliance_result,
        "send_result":       None,
        "analytics_result":  None,
        "recipient_email":   None,
        "recipient_phone":   None,
        "sender_name":       "VoltX Energy",
        "company_name":      "VoltX Energy Pvt. Ltd.",
        "company_address":   "Level 5, WeWork Embassy Golf Links, Bengaluru 560071, India",
        "unsubscribe_url":   "https://voltx.in/unsubscribe",
        "errors":            [],
        "trace":             [],
        "current_step":      "supervisor",
    }
