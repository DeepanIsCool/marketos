"""
Unit tests — Social Media Agent
Tests: platform formatting, hashtag limits, content calendar scheduling,
       simulated publish IDs, Kafka event publication.
"""

import pytest
import copy as _copy

pytestmark = pytest.mark.unit


class TestPlatformFormatter:
    def test_x_truncates_at_280(self):
        from agents.social.social_media_agent import PlatformFormatterSkill

        long_text = "A" * 300
        result = PlatformFormatterSkill.format("x", long_text, [])
        assert result["char_count"] <= 280
        assert result["within_limit"] is True

    def test_instagram_respects_hashtag_cap(self):
        from agents.social.social_media_agent import PlatformFormatterSkill

        hashtags = [f"tag{i}" for i in range(50)]
        result = PlatformFormatterSkill.format("instagram", "Post text", hashtags)
        assert len(result["hashtags_used"]) <= 30

    def test_linkedin_respects_3_hashtag_limit(self):
        from agents.social.social_media_agent import PlatformFormatterSkill

        hashtags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
        result = PlatformFormatterSkill.format("linkedin", "Post", hashtags)
        assert len(result["hashtags_used"]) <= 3

    def test_format_returns_required_fields(self):
        from agents.social.social_media_agent import PlatformFormatterSkill

        result = PlatformFormatterSkill.format("facebook", "Hello", ["marketing"])
        for field in ["platform", "formatted_text", "char_count", "hashtags_used", "within_limit"]:
            assert field in result


class TestHashtagOptimizer:
    def test_returns_list(self):
        from agents.social.social_media_agent import HashtagOptimizerSkill

        tags = HashtagOptimizerSkill.generate("instagram", "VoltX energy drink")
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_no_duplicates(self):
        from agents.social.social_media_agent import HashtagOptimizerSkill

        tags = HashtagOptimizerSkill.generate("instagram", "VoltX energy drink fitness")
        assert len(tags) == len(set(tags)), "No duplicate hashtags"


def test_social_agent_produces_posts(minimal_state):
    from agents.social.social_media_agent import social_media_agent_node

    result = social_media_agent_node(minimal_state)
    sr = result.get("social_result")
    assert sr is not None
    assert "posts" in sr
    # Must have at least 1 platform's content
    assert len(sr["posts"]) >= 1


def test_social_agent_publishes_kafka_event(minimal_state):
    from agents.social.social_media_agent import social_media_agent_node
    from utils.kafka_bus import clear_event_log, get_event_log

    clear_event_log()
    social_media_agent_node(minimal_state)
    topics = [e["topic"] for e in get_event_log()]
    assert "campaign.events" in topics


def test_social_posts_respect_x_limit(minimal_state):
    from agents.social.social_media_agent import social_media_agent_node, PlatformFormatterSkill

    result = social_media_agent_node(minimal_state)
    posts = result["social_result"]["posts"]

    if "x" in posts:
        x_post = posts["x"]
        formatted = PlatformFormatterSkill.format("x", x_post.get("text", ""), [])
        assert formatted["char_count"] <= 280, "X post must be ≤ 280 chars"
