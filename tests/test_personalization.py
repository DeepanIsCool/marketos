"""
Unit tests — Personalization Agent
Tests: fast-path (thin profile), LLM path (rich profile), token injection,
       profile richness scoring, language detection, SLA enforcement.
"""

import pytest
import time

pytestmark = pytest.mark.unit

SAMPLE_VARIANT = {
    "variant_id":           "V-001",
    "subject_line":         "{{first_name}}, VoltX Sale — 48hrs only",
    "preview_text":         "Buy 2 Get 1 Free",
    "body_html":            "<html><body><p>Hello {{first_name}} from {{city}}</p></body></html>",
    "body_text":            "Hello {{first_name}} from {{city}}. Shop now.",
    "cta_text":             "Shop Now",
    "cta_url":              "https://voltx.in/bf",
    "readability_score":    82.0,
    "tone_alignment_score": 91.0,
    "spam_risk_score":      9.0,
    "estimated_open_rate":  31.5,
    "estimated_ctr":        4.2,
}

CAMPAIGN_PLAN = {
    "campaign_id": "TEST-0001", "campaign_name": "VoltX BF",
    "goal": "500 conversions", "tone": "bold",
    "target_audience": "Men 18-30 India", "channels": ["email"],
    "budget": 75000.0, "timeline": "3 days",
    "key_messages": ["Buy 2 Get 1 Free"], "tasks": [],
}


class TestTokenInjector:
    def test_injects_first_name(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        result = TokenInjectorSkill.inject("Hello {{first_name}}", {"first_name": "Rahul"})
        assert result == "Hello Rahul"

    def test_fallback_to_there(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        result = TokenInjectorSkill.inject("Hello {{first_name}}", {})
        assert result == "Hello there"

    def test_injects_city(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        result = TokenInjectorSkill.inject("{{city}} exclusive", {"city": "Mumbai"})
        assert result == "Mumbai exclusive"

    def test_resolve_strips_unknown_tokens(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        result = TokenInjectorSkill.resolve("Hi {{first_name}} {{favorite_product}}!", {"first_name": "Rahul"})
        assert result == "Hi Rahul!"

    def test_profile_richness_empty_is_zero(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        score = TokenInjectorSkill.profile_richness({})
        assert score == 0.0

    def test_profile_richness_full_is_one(self):
        from agents.personalization.personalization_agent import TokenInjectorSkill

        full = {
            "first_name": "Rahul", "city": "Bengaluru", "segment": "high_intent",
            "last_purchase_days_ago": 14, "total_orders": 5,
            "email_opens_30d": 8, "email_clicks_30d": 3, "preferred_time": "evening",
        }
        score = TokenInjectorSkill.profile_richness(full)
        assert score == 1.0


class TestLanguageDetect:
    def test_detects_from_contact_field(self):
        from agents.personalization.personalization_agent import LanguageDetectSkill

        lang = LanguageDetectSkill.resolve({"language": "hi"})
        assert lang == "hi"

    def test_infers_from_country(self):
        from agents.personalization.personalization_agent import LanguageDetectSkill

        lang = LanguageDetectSkill.resolve({"country": "DE"})
        assert lang == "de"

    def test_defaults_to_en(self):
        from agents.personalization.personalization_agent import LanguageDetectSkill

        lang = LanguageDetectSkill.resolve({})
        assert lang == "en"


class TestSegmentFallback:
    def test_known_segment_returns_context(self):
        from agents.personalization.personalization_agent import SegmentFallbackSkill

        ctx = SegmentFallbackSkill.get_context("lapsed")
        assert "tone_hint" in ctx
        assert len(ctx["tone_hint"]) > 0

    def test_unknown_segment_returns_default(self):
        from agents.personalization.personalization_agent import SegmentFallbackSkill

        ctx = SegmentFallbackSkill.get_context("totally_unknown")
        assert ctx["tone_hint"] == "friendly"


class TestPersonalizeForContact:
    def test_fast_path_with_thin_profile(self):
        from agents.personalization.personalization_agent import personalize_for_contact

        result = personalize_for_contact(
            contact_id="sim-001",
            variant=SAMPLE_VARIANT,
            campaign_plan=CAMPAIGN_PLAN,
            contact_data={"first_name": "Rahul", "city": "Bengaluru"},
        )
        assert "Rahul" in result["subject_line"], "First name must be injected"
        assert "fallback_used" in result

    def test_returns_all_required_keys(self):
        from agents.personalization.personalization_agent import personalize_for_contact

        result = personalize_for_contact(
            contact_id="sim-002",
            variant=SAMPLE_VARIANT,
            campaign_plan=CAMPAIGN_PLAN,
            contact_data=None,
        )
        for key in ["subject_line", "preview_text", "body_html", "body_text",
                    "cta_text", "personalization_signals", "fallback_used"]:
            assert key in result, f"Missing key: {key}"

    def test_sla_under_three_seconds(self):
        from agents.personalization.personalization_agent import personalize_for_contact

        start = time.time()
        personalize_for_contact(
            contact_id="sim-sla",
            variant=SAMPLE_VARIANT,
            campaign_plan=CAMPAIGN_PLAN,
            contact_data=None,   # thin profile → fast-path
        )
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Personalization SLA breach: {elapsed:.2f}s > 3s"

    def test_does_not_invent_data(self):
        from agents.personalization.personalization_agent import personalize_for_contact

        result = personalize_for_contact(
            contact_id="unknown-contact",
            variant=SAMPLE_VARIANT,
            campaign_plan=CAMPAIGN_PLAN,
            contact_data={},   # empty profile
        )
        # Should not contain unreplaced template tokens
        assert "{{" not in result["subject_line"], "Must not leave unreplaced tokens"
        assert "{{" not in result["body_html"],    "Must not leave unreplaced tokens in HTML"
