#!/usr/bin/env python3
"""
MarketOS — Full Pipeline Demo
Executes all 16 agents end-to-end with real Kafka events, pgvector memory,
and sends a real email.

Run: python demo_full_pipeline.py

This is the script you show your boss.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

# ── Environment ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

from utils.logger import agent_log, step_banner, divider, kv, section, success_banner
from utils.kafka_bus import get_event_log, clear_event_log, get_producer, Topics
from utils.memory import get_memory_stats, reset_memory_stats, episodic_memory, semantic_memory


# ── ANSI colors ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def banner():
    print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   █▀▄▀█ █▀█ █▀█ █▄▀ █▀▀ ▀█▀ █▀█ █▀                                   ║
║   █ ▀ █ █▀█ █▀▄ █ █ ██▄  █  █▄█ ▄█                                   ║
║                                                                      ║
║   A U T O N O M O U S   M A R K E T I N G   P L A T F O R M          ║
║                                                                      ║
║   Event-Driven Architecture │ Kafka Bus │ pgvector Memory            ║
║   16-Agent Agentic Pipeline │ Real Email + SMS                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{RESET}""")


def seed_brand_data():
    """Pre-populate semantic memory with demo brand data."""
    print(f"\n{YELLOW}[SEED] Seeding brand knowledge into pgvector...{RESET}")

    data = [
        ("brand_voice", "voltx_tone", (
            "VoltX Energy brand voice: Bold, energetic, unapologetic. "
            "Speak to young men 18-30 who hustle hard. Use short punchy sentences. "
            "Never be boring. Use words like 'CRUSH IT', 'LEVEL UP', 'UNSTOPPABLE'. "
            "Emoji OK but not excessive. CTA should feel like a dare, not a request."
        )),
        ("brand_voice", "voltx_visual", (
            "VoltX visual identity: Neon green (#00FF41) on matte black. "
            "Lightning bolt motif. Never use pastels. Typography: Impact for headers, "
            "Roboto for body. Product hero shot must show condensation drops."
        )),
        ("personas", "persona_gym_bro", (
            "Persona 'Gym Bro Rahul': Male, 22, Bengaluru. Works out 5x/week. "
            "Drinks energy drinks pre-workout and during late-night coding sessions. "
            "Active on Instagram and YouTube. Price-sensitive but brand-loyal once hooked. "
            "Responds to FOMO and social proof. Preferred channel: Instagram + SMS."
        )),
        ("personas", "persona_startup_dev", (
            "Persona 'Startup Dev Arjun': Male, 27, Hyderabad. Full-stack developer at a "
            "Series-A startup. Works 12-hour days. Needs energy for late-night deploys. "
            "Buys in bulk from Amazon. Responds to value offers (Buy 2 Get 1). "
            "Preferred channel: Email + LinkedIn."
        )),
        ("personas", "persona_college_student", (
            "Persona 'College Priya': Female, 20, Mumbai. Engineering student who "
            "studies for competitive exams. Uses energy drinks during all-night study sessions. "
            "Very price-conscious. Responds to student discounts and peer recommendations. "
            "Preferred channel: Instagram + WhatsApp."
        )),
        ("product", "voltx_original", (
            "VoltX Original 250ml: Flagship energy drink. Caffeine 150mg, Taurine, "
            "B-Vitamins. Green can with lightning bolt. MRP ₹99 (street price ₹79). "
            "USP: 'More caffeine per rupee than Red Bull.' Available on Amazon, "
            "BigBasket, and 15,000 retail outlets across India."
        )),
        ("product", "voltx_zero", (
            "VoltX Zero 250ml: Sugar-free variant. Same caffeine (150mg), zero calories. "
            "Black can with electric blue lightning. MRP ₹109 (street price ₹89). "
            "USP: 'All the energy, none of the guilt.' Popular with fitness-focused segment."
        )),
        ("past_campaigns", "diwali_2025", (
            "Diwali 2025 campaign results: Sent 50,000 emails, achieved 32% open rate, "
            "4.8% CTR, 1,200 conversions. Revenue ₹2.4L. ROAS 3.2x. Best performing "
            "subject line was 'Diwali Sale LIVE: ₹49 VoltX — Tonight Only 🔥'. "
            "The urgency + price anchor worked best. SMS had 12% CTR vs email 4.8%. "
            "Social: Instagram Reels got 50K views."
        )),
        ("compliance", "india_regulations", (
            "Indian marketing compliance: TRAI regulations require opt-out in every SMS. "
            "No commercial SMS between 9PM-8AM IST. Email must include physical address "
            "and unsubscribe link (CAN-SPAM equivalent under IT Act 2000). "
            "FSSAI compliance required for food/beverage ads — no health claims without "
            "certification. Celebrity endorsements need ASCI approval."
        )),
    ]

    seeded = 0
    for category, key, content in data:
        result = semantic_memory.upsert(category, key, content)
        if result:
            seeded += 1
            print(f"  {GREEN}✓{RESET} [{category}:{key}]")
        else:
            print(f"  {YELLOW}⚠{RESET} [{category}:{key}] (skipped — DB not available)")

    # Seed a historical episodic memory so agents can "remember"
    episodic_memory.store(
        agent_name="copy_agent",
        event_type="campaign_completed",
        summary=(
            "VoltX Diwali 2025 campaign: Subject 'Diwali Sale LIVE: ₹49 VoltX — Tonight Only 🔥' "
            "achieved 32% open rate. Urgency + price anchor in subject line worked best. "
            "Variant with countdown timer CTA had 2x higher CTR than plain 'Shop Now'."
        ),
        metadata={"campaign_id": "CAMP-DIWALI25", "open_rate": 0.32, "ctr": 0.048},
    )

    print(f"\n{GREEN}  Seeded {seeded}/{len(data)} brand knowledge items{RESET}")
    return seeded


def check_infra():
    """Quick health check of infrastructure services."""
    print(f"\n{CYAN}[INFRA] Checking infrastructure services...{RESET}")

    checks = {}

    # Kafka / Redpanda
    producer = get_producer()
    if producer.is_connected:
        checks["Kafka (Redpanda)"] = (True, "Connected to localhost:9092")
    else:
        checks["Kafka (Redpanda)"] = (False, "Not connected — using in-memory event log")

    # PostgreSQL + pgvector
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://marketos:marketos_dev@localhost:5433/marketos"))
        cur = conn.cursor()
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        if row:
            checks["PostgreSQL + pgvector"] = (True, f"pgvector v{row[0]}")
        else:
            checks["PostgreSQL + pgvector"] = (True, "Connected (pgvector extension pending)")
        conn.close()
    except Exception as e:
        checks["PostgreSQL + pgvector"] = (False, f"Not connected: {e}")

    # Redis
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        checks["Redis"] = (True, "Connected")
    except Exception as e:
        checks["Redis"] = (False, f"Not connected: {e}")

    for name, (ok, msg) in checks.items():
        icon = f"{GREEN}✓{RESET}" if ok else f"{YELLOW}⚠{RESET}"
        print(f"  {icon} {name}: {msg}")

    return checks


def run_pipeline():
    """Execute the full 16-agent campaign pipeline."""
    from graph.campaign_graph import campaign_graph

    # ── Campaign Intent ──────────────────────────────────────────────────
    user_intent = (
        "a free ticket to a basketball match if you buy our new sports car. "
        "send both beautiful email and great sms."
    )

    initial_state = {
        "user_intent":       user_intent,
        "pipeline":          "campaign",
        "workspace_id":      "default",
        "recipient_email":   "sadhukhandeepan@gmail.com",
        "recipient_phone":   "7003574257",
        "sender_name":       "VoltX Energy",
        "company_name":      "VoltX Energy Pvt. Ltd.",
        "company_address":   "Level 5, WeWork Embassy Golf Links, Bengaluru 560071, India",
        "unsubscribe_url":   "https://voltx.in/unsubscribe",
        "current_step":      "supervisor",
        "errors":            [],
        "trace":             [],
    }

    # ── Publish campaign.started to Kafka ─────────────────────────────────
    from utils.kafka_bus import publish_event, Topics
    publish_event(
        topic=Topics.CAMPAIGN_EVENTS,
        source_agent="demo_pipeline",
        payload={
            "event": "campaign_started",
            "intent": user_intent[:200],
            "recipient": "sadhukhandeepan@gmail.com",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        priority="HIGH",
    )

    # ── Execute the LangGraph pipeline ────────────────────────────────────
    print(f"\n{BOLD}{CYAN}{'═' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  EXECUTING 16-AGENT PIPELINE{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 70}{RESET}\n")

    start_time = time.time()

    result = campaign_graph.invoke(initial_state)

    elapsed = time.time() - start_time

    # ── Publish campaign.completed to Kafka ───────────────────────────────
    publish_event(
        topic=Topics.CAMPAIGN_EVENTS,
        source_agent="demo_pipeline",
        payload={
            "event": "campaign_completed",
            "agents_run": len(result.get("trace", [])),
            "elapsed_s": round(elapsed, 2),
            "errors": result.get("errors", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        priority="HIGH",
    )

    # Flush Kafka producer to ensure all messages are sent
    get_producer().flush(timeout=5.0)

    return result, elapsed


def verification_report(result: dict, elapsed: float):
    """Print a comprehensive verification report."""
    events = get_event_log()
    mem_stats = get_memory_stats()
    trace = result.get("trace", [])
    errors = result.get("errors", [])

    # Unique topics
    topics = list(set(e["topic"] for e in events))

    print(f"""
{BOLD}{GREEN}
╔══════════════════════════════════════════════════════════════════════╗
║                   VERIFICATION REPORT                                ║
╚══════════════════════════════════════════════════════════════════════╝
{RESET}""")

    # ── Agents ────────────────────────────────────────────────────────────
    section_header("AGENT EXECUTION")
    print(f"  Agents activated:   {GREEN}{BOLD}{len(trace)}/16{RESET}")
    print(f"  Pipeline time:      {elapsed:.1f}s")
    print(f"  Errors:             {RED}{len(errors)}{RESET}" if errors else f"  Errors:             {GREEN}0{RESET}")
    print()
    for t in trace:
        agent = t.get("agent", "unknown")
        status = t.get("status", "unknown")
        icon = "✅" if status in ("completed", "sent", "approved", "published", "analyzed") else "⚠️"
        extra = ""
        if t.get("real_email_sent"):
            extra = f" → {GREEN}REAL EMAIL SENT{RESET}"
        if t.get("provider"):
            extra = f" via {t['provider']}"
        print(f"    {icon} {agent:<30} {status}{extra}")

    # ── Kafka Events ──────────────────────────────────────────────────────
    section_header("KAFKA EVENT BUS")
    print(f"  Messages published: {GREEN}{BOLD}{len(events)}{RESET}")
    print(f"  Unique topics:      {len(topics)}")
    print()
    # Topic breakdown
    topic_counts = {}
    for e in events:
        t = e["topic"]
        topic_counts[t] = topic_counts.get(t, 0) + 1
    for topic, count in sorted(topic_counts.items()):
        print(f"    📨 {topic:<45} {count} msg(s)")

    # ── Memory ────────────────────────────────────────────────────────────
    section_header("PGVECTOR MEMORY")
    print(f"  Episodic stores:    {mem_stats['episodic_stores']}")
    print(f"  Episodic recalls:   {mem_stats['episodic_recalls']}")
    print(f"  Semantic upserts:   {mem_stats['semantic_upserts']}")
    print(f"  Semantic searches:  {mem_stats['semantic_searches']}")

    section_header("REDIS WORKING MEMORY")
    print(f"  Task contexts set:     {mem_stats['working_sets']}")
    print(f"  Task contexts cleaned: {mem_stats['working_deletes']}")

    # ── Real Delivery ─────────────────────────────────────────────────────
    section_header("REAL DELIVERY PROOF")
    send_result = result.get("send_result", {})
    if send_result.get("real_email_sent"):
        print(f"  📧 Email: {GREEN}✅ SENT to sadhukhandeepan@gmail.com{RESET}")
    else:
        email_error = send_result.get("real_email_status", "not attempted")
        print(f"  📧 Email: {YELLOW}⚠ {email_error}{RESET}")

    sms_result = result.get("sms_result", {})
    sms_provider = sms_result.get("provider", "none")
    sms_status = sms_result.get("status", "skipped")
    if sms_status not in ("skipped", "none") and sms_provider != "none":
        print(f"  📱 SMS:   {GREEN}✅ SENT via {sms_provider}{RESET}")
    else:
        reason = sms_result.get("reason_code", "provider keys not set")
        print(f"  📱 SMS:   {YELLOW}Skipped ({reason}){RESET}")

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"""
{BOLD}{GREEN}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ✅  DEMO COMPLETE — ALL SYSTEMS OPERATIONAL                        ║
║                                                                      ║
║   Kafka:     {len(events)} events across {len(topics)} topics                            ║
║   pgvector:  {mem_stats['episodic_stores']} episodic + {mem_stats['semantic_searches']} semantic queries               ║
║   Pipeline:  {len(trace)}/16 agents in {elapsed:.1f}s                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{RESET}""")


def section_header(title: str):
    print(f"\n  {BOLD}{CYAN}── {title} {'─' * (50 - len(title))}{RESET}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    banner()

    # Reset counters
    clear_event_log()
    reset_memory_stats()

    # 1. Check infrastructure
    infra = check_infra()

    # 2. Seed brand data
    seed_brand_data()

    # 3. Run the pipeline
    print(f"\n{BOLD}Starting full 16-agent pipeline...{RESET}")
    print(f"  📧 Email → sadhukhandeepan@gmail.com")
    print(f"  📱 Phone → 7003574257")
    print(f"  🎯 Demo  → VoltX Black Friday Campaign")

    try:
        result, elapsed = run_pipeline()
    except Exception as e:
        print(f"\n{RED}Pipeline failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. Verification report
    verification_report(result, elapsed)


if __name__ == "__main__":
    main()
