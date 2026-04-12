"""
MarketOS — Copy Agent
Generates scored email copy variants based on the campaign plan.
Produces complete HTML email templates ready for sending.

Production responsibilities (full system):
- Reads brand voice DB from PostgreSQL workspace.brand_guidelines
- Stores variants in PostgreSQL copy_variants table
- Writes winner to agent.copy_agent.results Kafka topic
- Integrates with readability scoring microservice

Demo mode: in-memory generation with scoring via LLM.
"""

import json
import os
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage

from agents.llm.llm_provider import get_llm
from schemas.campaign import CampaignPlan, CopyVariant, CopyOutput
from utils.logger import agent_log, step_banner, kv, section, divider, check_line
from utils.kafka_bus import publish_event, Topics
from utils.memory import episodic_memory, semantic_memory

try:
    import redis as redis_lib
    _redis = redis_lib.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False
    _redis = None

WORKSPACE = os.getenv("WORKSPACE_ID", "default")

# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Copy Agent for MarketOS — an expert email copywriter trained on thousands of high-converting marketing campaigns.

EXPERTISE:
- Writing subject lines with 35%+ open rates
- Crafting persuasive email bodies with clear value propositions
- Designing CTAs that drive measurable conversions
- Adapting tone precisely to brand and audience
- Scoring copy against industry benchmarks

YOUR TASK:
Generate exactly 2 email copy variants based on the campaign plan provided.
Each variant must have a DIFFERENT angle/hook while targeting the same goal.

VARIANT ANGLES:
- Variant 1: Benefit-led (lead with what the customer GAINS)
- Variant 2: Competitive Edge (directly address or contrast against rival weaknesses found in research)

MARKET DIFFERENTIATION:
You will be provided with <market_intelligence>. Use this to:
- Contrast your offering against mentioned competitors.
- Use a tone that stands out from industry norms identified.
- Highlight features that rivals are lacking.

HTML EMAIL REQUIREMENTS:
- Use clean, responsive inline-CSS HTML (max-width: 600px) using table-based layouts.
- DYNAMIC DESIGN: You are generating bespoke templates. Adapt the color palette, typography, margins, and layout style to perfectly match the campaign's intent, brand identity, and audience (e.g., moody luxury, bright skincare, festive holiday).
- MUST include a strong hero image component: `<img src="cid:hero_image" ...>`
- One clear CTA button (styled inline, contrasting brand color)
- Footer MUST contain: "Unsubscribe" link, company address placeholder, privacy link.
- Never leave placeholder tokens in final HTML. Use realistic filler where needed.

SCORING CRITERIA (score 0–100):
- readability_score: Flesch-Kincaid grade level converted to 0-100 (higher = more readable for general audience)
- tone_alignment_score: How well the copy matches the requested tone (0-100)
- spam_risk_score: Lower is better. Check for spam trigger words, excessive caps, misleading subject
- estimated_open_rate: Industry benchmark adjusted for subject line quality (as percentage, e.g. 28.5)
- estimated_ctr: Estimated click-through rate (as percentage, e.g. 3.2)

OUTPUT RULES:
- Respond ONLY with valid JSON — no prose, no markdown code blocks
- HTML must be properly escaped inside the JSON string
- Unsplash Search Query: Provide a short 2-3 word `hero_image_query` for the Unsplash photo API (e.g. "autumn skincare" or "winter jacket").
- Gemini Imagen Prompt: Provide a highly descriptive `hero_image_prompt` (max 400 chars) as a fallback (e.g. "Minimalist 3D render of a Vitamin C bottle on bright orange pedestal..."). MUST specify NO TEXT, typography, or words.
- All scores must be numbers (not strings)

REQUIRED JSON SCHEMA:
{
  "variants": [
    {
      "variant_id": "V-001",
      "subject_line": "compelling subject line under 50 characters",
      "preview_text": "preview text under 90 characters (shown after subject in inbox)",
      "body_html": "<complete responsive HTML email here>",
      "body_text": "plain text version of the email body",
      "cta_text": "CTA button text",
      "cta_url": "https://example.com/offer",
      "hero_image_query": "autumn skincare",
      "hero_image_prompt": "A professional flat lay of organic skincare products with autumn leaves and golden lighting, high resolution, soft bokeh.",
      "readability_score": 82.0,
      "tone_alignment_score": 91.0,
      "spam_risk_score": 8.0,
      "estimated_open_rate": 31.5,
      "estimated_ctr": 4.2
    },
    { ... variant 2 ... }
  ],
  "selected_variant_id": "V-001",
  "selection_reasoning": "2–3 sentence explanation of why V-001 is selected over V-002",
  "brand_voice_notes": "notes on tone, vocabulary, and style choices made"
}"""

HTML_EMAIL_DESIGN_GUIDE = """
DESIGN INSTRUCTIONS:
Do not use a rigid generic template. Generate a tailored HTML design specific to the campaign intent, tone, and target audience.

Structure to include:
1. Preheader (subtle)
2. Header / Logo Area (styled to fit the brand's industry, e.g., playful for D2C, sleek for luxury)
3. Hero Image (`<img src="cid:hero_image" alt="Hero" width="600" style="display:block;width:100%;max-width:600px;height:auto;">`)
4. Main Content Area (Headline, Value Prop, Body, well-spaced)
5. Primary CTA (Button with inline styles, distinct brand color)
6. Footer (Company Name, Address, Unsubscribe, Social links)

Styling rules:
- Choose background colors, text colors, and font families intentionally based on the brand's tone (e.g., dark/gold for luxury, bright/warm for D2C skincare, festive for holidays).
- Use inline CSS ONLY.
- Ensure readability and mobile-responsiveness (max-width: 600px).
"""


# ── Agent Node ───────────────────────────────────────────────────────────────

def copy_agent_node(state: dict) -> dict:
    step_banner("COPY AGENT  ─  Email Copy Generation & Variant Scoring")

    plan_data = state.get("campaign_plan", {})
    plan = CampaignPlan(**plan_data)

    agent_log("COPY", f"Campaign: {plan.campaign_name}")
    agent_log("COPY", f"Tone requested: {plan.tone.upper()}")
    agent_log("COPY", f"Generating 2 copy variants (benefit-led + urgency-led)...")

    llm = get_llm(temperature=0.7)   # Slightly higher temp for creative copy

    # ── Fetch Market Intelligence ─────────────────────────────────────────
    intel = state.get("competitor_result", {}).get("intel", {})
    if not intel and REDIS_AVAILABLE and _redis:
        try:
            intel_key = f"market_intel:{WORKSPACE}:{plan.campaign_id}"
            raw = _redis.get(intel_key)
            if raw:
                intel = json.loads(raw)
                agent_log("COPY", "Fetched market intelligence from Redis pool")
        except Exception:
            pass

    intel_ctx = ""
    if intel:
        intel_ctx = f"""
MARKET INTELLIGENCE & COMPETITIVE LANDSCAPE:
Executive Summary: {intel.get('executive_summary', 'Neutral market state.')}
Key Competitors: {', '.join([c.get('name', 'Unknown') for c in intel.get('competitors', [])])}
Differentiation Strategy: Ensure the copy highlights why {plan.campaign_name} is superior to these specific rivals.
"""

    campaign_context = f"""
CAMPAIGN BRIEF:
- Name: {plan.campaign_name}
- Goal: {plan.goal}
- Target Audience: {plan.target_audience}
- Tone: {plan.tone}
{intel_ctx}

KEY MESSAGES TO INCORPORATE:
{chr(10).join(f'  {i+1}. {msg}' for i, msg in enumerate(plan.key_messages))}
"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=campaign_context),
    ]

    agent_log("COPY", "Calling LLM for copy generation...")
    # Enforce the Pydantic schema natively to ensure robust HTML escaping and valid structure
    structured_llm = llm.with_structured_output(CopyOutput)

    try:
        copy_output = structured_llm.invoke(messages)
        # LangChain returns the validated CopyOutput model directly
    except Exception as e:
        error_msg = f"Copy Agent generation failed: {e}"
        agent_log("COPY", f"ERROR — {error_msg}")
        return {**state, "errors": state.get("errors", []) + [error_msg], "current_step": "failed"}

    variants = copy_output.variants
    if not variants:
        error_msg = "Copy Agent produced zero variants"
        return {**state, "errors": state.get("errors", []) + [error_msg], "current_step": "failed"}

    # Determine the selected variant
    selected = next(
        (v for v in variants if v.variant_id == copy_output.selected_variant_id),
        variants[0]
    )

    # ── Terminal Output ──────────────────────────────────────────────────────
    agent_log("COPY", f"✓ Generated {len(variants)} variant(s)")
    divider()

    for v in variants:
        is_winner = v.variant_id == selected.variant_id
        marker = f" ◀ SELECTED" if is_winner else ""
        section(f"VARIANT {v.variant_id}{marker}")
        kv("Subject Line",        f'"{v.subject_line}"')
        kv("Preview Text",        f'"{v.preview_text}"')
        kv("Image Query",         f'"{v.hero_image_query}"', "CYAN")
        kv("CTA",                 f'[{v.cta_text}]  →  {v.cta_url}')
        kv("Readability Score",   f"{v.readability_score:.1f} / 100")
        kv("Tone Alignment",      f"{v.tone_alignment_score:.1f} / 100")
        kv("Spam Risk",           f"{v.spam_risk_score:.1f} / 100  (lower = safer)")
        kv("Est. Open Rate",      f"{v.estimated_open_rate:.1f}%")
        kv("Est. CTR",            f"{v.estimated_ctr:.1f}%")
        print()

    section("SELECTION DECISION")
    print(f"  Winner: {selected.variant_id}  |  {copy_output.selection_reasoning}")
    if copy_output.brand_voice_notes:
        print(f"\n  Voice notes: {copy_output.brand_voice_notes}")

    divider()

    # ── Publish copy results to Kafka ─────────────────────────────────────
    publish_event(
        topic=Topics.COPY_RESULTS,
        source_agent="copy_agent",
        payload={
            "event":           "copy_generated",
            "campaign_id":     plan.campaign_id,
            "variants_count":  len(variants),
            "selected":        selected.variant_id,
            "subject_line":    selected.subject_line,
            "timestamp":       datetime.now(timezone.utc).isoformat(),
        },
    )

    # ── Store to episodic memory ──────────────────────────────────────────
    episodic_memory.store(
        agent_name="copy_agent",
        event_type="copy_generated",
        summary=(
            f"Generated {len(variants)} copy variants for '{plan.campaign_name}'. "
            f"Winner: {selected.variant_id} with subject '{selected.subject_line}'. "
            f"Open rate est: {selected.estimated_open_rate}%."
        ),
        metadata={
            "campaign_id": plan.campaign_id,
            "selected_variant": selected.variant_id,
            "subject_line": selected.subject_line,
        },
    )

    return {
        **state,
        "copy_output":  copy_output.model_dump(),
        "current_step": "compliance_agent",
        "trace": state.get("trace", []) + [{
            "agent":              "copy_agent",
            "status":             "completed",
            "variants_generated": len(variants),
            "selected_variant":   selected.variant_id,
            "timestamp":          datetime.now(timezone.utc).isoformat(),
        }],
    }
