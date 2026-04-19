import pytest

pytestmark = pytest.mark.unit


def test_voice_prefers_env_daemon_url(monkeypatch):
    monkeypatch.setenv("VOICE_DAEMON_WSS_URL", "wss://voice.example.com/twilio/media")

    from agents.voice.voice_agent import _get_tunnel_url

    assert _get_tunnel_url() == "wss://voice.example.com/twilio/media"
