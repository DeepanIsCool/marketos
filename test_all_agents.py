#!/usr/bin/env python3
"""
MarketOS — Agent API Test Harness
Tests each of the 17 agents via POST /v1/agents/{name}/run.
Produces a clean pass/fail report.

Usage:
  1. Start infra:   docker compose up -d
  2. Start API:     .venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
  3. Run tests:     .venv/bin/python test_all_agents.py
"""

import json, time, sys, requests

BASE = "http://127.0.0.1:8000"

# ── Shared fixtures that satisfy Pydantic schemas ────────────────────────────

CAMPAIGN_PLAN = {
    "campaign_id": "CAMP-TEST-001",
    "campaign_name": "Sports Car Basketball Promo",
    "goal": "Drive sports car purchases with free basketball tickets",
    "target_audience": "Sports car enthusiasts aged 25-45",
    "channels": ["email", "sms", "social"],
    "budget": 50000,
    "timeline": "2 weeks",
    "tone": "exciting",
    "key_messages": ["Free basketball match ticket", "Buy our new sports car"],
    "tasks": [
        {"agent": "email_agent", "task": "Send campaign email", "priority": "HIGH"},
    ],
}

COPY_VARIANT_FULL = {
    "variant_id": "V-001",
    "subject_line": "Free Basketball Tickets Inside!",
    "preview_text": "Buy our sports car, get courtside seats",
    "body_html": "<html><body><h1>Score Big!</h1><p>Buy our new sports car and get a FREE ticket to the championship basketball match!</p><a href='https://example.com'>Claim Your Ticket</a></body></html>",
    "body_text": "Buy our new sports car and get a FREE ticket to the championship basketball match!",
    "cta_text": "Claim Your Ticket",
    "cta_url": "https://example.com/offer",
    "readability_score": 85.0,
    "tone_alignment_score": 90.0,
    "spam_risk_score": 10.0,
    "estimated_open_rate": 32.0,
    "estimated_ctr": 4.5,
}

COPY_VARIANT_B = {
    "variant_id": "V-002",
    "subject_line": "Drive Off With Courtside Seats",
    "preview_text": "Limited offer on our new sports car",
    "body_html": "<html><body><h1>The Ultimate Combo</h1><p>New sports car + courtside basketball tickets. Limited time.</p><a href='https://example.com'>Get Yours</a></body></html>",
    "body_text": "New sports car + courtside basketball tickets. Limited time.",
    "cta_text": "Get Yours",
    "cta_url": "https://example.com/offer",
    "readability_score": 80.0,
    "tone_alignment_score": 85.0,
    "spam_risk_score": 12.0,
    "estimated_open_rate": 28.0,
    "estimated_ctr": 3.8,
}

COPY_OUTPUT = {
    "variants": [COPY_VARIANT_FULL, COPY_VARIANT_B],
    "selected_variant_id": "V-001",
    "selection_reasoning": "Higher estimated open rate and tone alignment",
    "brand_voice_notes": "Exciting, sports-themed",
}

SEND_RESULT = {
    "campaign_id": "CAMP-TEST-001",
    "message_id": "MSG-TEST-001",
    "status": "sent",
    "provider": "smtp",
    "real_email_sent": True,
    "real_email_status": "sent",
    "recipient_count": 1,
}

ANALYTICS_RESULT = {
    "metrics": {
        "total_sent": 1, "delivered": 1, "opens": 1, "clicks": 0,
        "bounces_soft": 0, "bounces_hard": 0, "unsubscribes": 0,
        "spam_complaints": 0, "open_rate": 100.0, "ctr": 0.0,
        "bounce_rate": 0.0, "spam_rate": 0.0, "delivery_rate": 100.0,
    },
    "anomalies": [],
    "snapshot_id": "SNAP-TEST",
}

COMPLIANCE_RESULT = {"approved": True, "score": 95.0, "reason_code": "approved"}

# ── Agent test definitions ───────────────────────────────────────────────────
# (agent_name, extra_state, timeout_seconds)

TESTS = [
    ("supervisor", {
        "user_intent": "Free basketball tickets with sports car purchase. Send email and SMS.",
    }, 30),

    ("competitor", {
        "campaign_plan": CAMPAIGN_PLAN,
    }, 90),

    ("seo", {
        "campaign_plan": CAMPAIGN_PLAN,
    }, 60),

    ("copy", {
        "campaign_plan": CAMPAIGN_PLAN,
        "competitor_result": {"analysis": "No direct competitors found"},
        "seo_result": {"keywords": ["sports car deal", "basketball tickets"]},
    }, 30),

    ("image", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
    }, 60),

    ("compliance", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
    }, 30),

    ("finance", {
        "campaign_plan": CAMPAIGN_PLAN,
        "compliance_result": COMPLIANCE_RESULT,
    }, 30),

    ("email", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
        "compliance_result": COMPLIANCE_RESULT,
        "recipient_email": "sadhukhandeepan@gmail.com",
        "sender_name": "MarketOS Test",
        "company_name": "MarketOS",
        "company_address": "Bengaluru, India",
        "unsubscribe_url": "https://example.com/unsubscribe",
    }, 90),

    ("sms", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
        "recipient_phone": "+917003574257",
    }, 30),

    ("voice", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
        "recipient_phone": "+917003574257",
    }, 30),

    ("social_media", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
    }, 90),

    ("analytics", {
        "campaign_plan": CAMPAIGN_PLAN,
        "send_result": SEND_RESULT,
    }, 30),

    ("monitor", {
        "campaign_plan": CAMPAIGN_PLAN,
        "analytics_result": ANALYTICS_RESULT,
    }, 30),

    ("ab_test", {
        "campaign_plan": CAMPAIGN_PLAN,
        "copy_output": COPY_OUTPUT,
        "analytics_result": ANALYTICS_RESULT,
    }, 30),

    ("lead_scoring", {
        "campaign_plan": CAMPAIGN_PLAN,
        "analytics_result": ANALYTICS_RESULT,
    }, 30),

    ("reporting", {
        "campaign_plan": CAMPAIGN_PLAN,
        "analytics_result": ANALYTICS_RESULT,
        "ab_test_result": {"decision": "no_winner", "reason": "insufficient data"},
        "lead_scoring_result": {"contacts_scored": 0, "new_mqls": 0, "new_sqls": 0},
        "send_result": SEND_RESULT,
        "sms_result": {"status": "skipped", "reason_code": "test"},
        "social_result": {"posts": []},
        "monitor_result": {"health_status": "stable"},
    }, 90),

    ("onboarding", {
        "user_name": "Test User",
        "user_email": "test@example.com",
        "company_name": "TestCo",
        "industry": "SaaS",
    }, 30),
]


def test_agent(name: str, extra_state: dict, timeout: int) -> dict:
    state = {"current_step": name, "errors": [], "trace": [], "workspace_id": "default"}
    state.update(extra_state)

    try:
        resp = requests.post(
            f"{BASE}/v1/agents/{name}/run",
            json={"state": state},
            timeout=timeout,
        )
        body = resp.json()

        if resp.status_code == 200 and body.get("ok"):
            return {
                "status": "PASS",
                "elapsed_ms": body["meta"]["elapsed_ms"],
                "error": None,
                "detail": None,
            }
        else:
            err_raw = body.get("error") or ""
            if not err_raw:
                detail = body.get("detail", {})
                err_raw = detail.get("error", str(detail)) if isinstance(detail, dict) else str(detail)
            err = err_raw[:300] if isinstance(err_raw, str) else str(err_raw)[:300]
            elapsed = 0
            try:
                elapsed = body.get("meta", {}).get("elapsed_ms", 0)
                if not elapsed:
                    elapsed = body.get("detail", {}).get("meta", {}).get("elapsed_ms", 0)
            except Exception:
                pass
            return {"status": "FAIL", "elapsed_ms": elapsed, "error": err, "detail": None}

    except requests.exceptions.Timeout:
        return {"status": "TIMEOUT", "elapsed_ms": timeout * 1000, "error": f"Request timed out after {timeout}s", "detail": None}
    except requests.exceptions.ConnectionError:
        return {"status": "CONN_ERR", "elapsed_ms": 0, "error": "Cannot connect to API server", "detail": None}
    except Exception as e:
        return {"status": "ERROR", "elapsed_ms": 0, "error": str(e)[:200], "detail": None}


def main():
    print(f"\n{'═'*70}")
    print(f"  MARKETOS AGENT API TEST SUITE")
    print(f"{'═'*70}")

    # 1. Health check
    try:
        h = requests.get(f"{BASE}/v1/health", timeout=5).json()
        d = h["data"]
        print(f"\n  INFRA: {d['status'].upper()}")
        print(f"    Kafka={d['kafka']}  PG={d['postgres']}  Redis={d['redis']}  CH={d['clickhouse']}")
    except Exception as e:
        print(f"\n  ⚠ API not reachable at {BASE}: {e}")
        print(f"  Start with: .venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # 2. Agent import health
    try:
        ah = requests.get(f"{BASE}/v1/health/agents", timeout=10).json()
        broken = [k for k, v in ah["data"].items() if v != "ok"]
        if broken:
            print(f"\n  ⚠ BROKEN IMPORTS: {', '.join(broken)}")
        else:
            print(f"  AGENTS: All 17 import OK")
    except Exception:
        pass

    print(f"\n{'─'*70}")
    print(f"  {'AGENT':<20} {'STATUS':<10} {'TIME':>8}  NOTES")
    print(f"{'─'*70}")

    results = {}
    for name, extra, timeout in TESTS:
        r = test_agent(name, extra, timeout)
        results[name] = r

        icon = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏱ ", "CONN_ERR": "🔌", "ERROR": "💥"}.get(r["status"], "?")
        time_str = f"{r['elapsed_ms']:.0f}ms" if r["elapsed_ms"] else "—"
        note = r["error"][:50] if r["error"] else ""
        print(f"  {name:<20} {icon} {r['status']:<7} {time_str:>8}  {note}")

    # 3. Summary
    passed = [k for k, v in results.items() if v["status"] == "PASS"]
    failed = {k: v for k, v in results.items() if v["status"] != "PASS"}

    print(f"\n{'═'*70}")
    print(f"  RESULTS: {len(passed)}/17 PASSED   {len(failed)}/17 FAILED")
    print(f"{'═'*70}")

    if failed:
        print(f"\n  FAILURE DETAILS:")
        print(f"  {'─'*66}")
        for name, r in failed.items():
            print(f"\n  ❌ {name}")
            print(f"     Status:  {r['status']}")
            print(f"     Error:   {r['error']}")
        print()

    # 4. Save JSON report
    report_path = "agent_test_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Full report saved to: {report_path}\n")


if __name__ == "__main__":
    main()
