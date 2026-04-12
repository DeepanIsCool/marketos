"""
MarketOS — Image Agent (Hybrid Visual Engine)
Pipeline:
  1. Unsplash photography search (fast, high quality, free tier)
  2. Gemini Vision relevance check on the photo (multimodal)
  3. Gemini Imagen 4 generation as fallback (AI-generated, no text)
  4. HTML injection of the winning image into the selected copy variant

Production extension:
- Cache verified images in S3 by query hash (avoid repeated API calls)
- Store base64 in campaign_assets table with CDN URL after upload
- Track usage for brand consistency across campaigns
"""

from __future__ import annotations
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage

from agents.llm.llm_provider import get_llm
from utils.logger import agent_log, step_banner, divider, kv, section
from utils.kafka_bus import publish_event, Topics


# ── Agent Node ───────────────────────────────────────────────────────────────

def image_agent_node(state: dict) -> dict:
    step_banner("IMAGE AGENT  ─  Hybrid AI Visual Engine")

    copy_data = state.get("copy_output")
    if not isinstance(copy_data, dict):
        err = "Image Agent skipped: missing or malformed copy_output"
        agent_log("IMAGE", f"ERROR — {err}")
        return {**state, "errors": state.get("errors", []) + [err], "current_step": "failed"}

    # ── Find winning variant ─────────────────────────────────────────────
    selected_id = copy_data.get("selected_variant_id")
    variants    = copy_data.get("variants") or []
    winner      = next(
        (v for v in variants if isinstance(v, dict) and v.get("variant_id") == selected_id),
        variants[0] if variants else None,
    )

    if not isinstance(winner, dict):
        err = f"Winning variant '{selected_id}' not found in copy_output"
        agent_log("IMAGE", f"ERROR — {err}")
        return {**state, "errors": state.get("errors", []) + [err], "current_step": "failed"}

    query  = winner.get("hero_image_query")
    prompt = winner.get("hero_image_prompt")

    img_url  = None
    img_b64  = None
    img_type = None

    # ── Phase 1: Unsplash ────────────────────────────────────────────────
    if query:
        agent_log("IMAGE", f"Phase 1 — Unsplash search: '{query}'")
        unsplash_url = _fetch_unsplash(query)

        if unsplash_url:
            agent_log("IMAGE", "Photo found. Phase 2 — Gemini Vision relevance check...")
            is_relevant = _verify_image_relevance(unsplash_url, query)
            if is_relevant:
                agent_log("IMAGE", "✅ Vision check passed — using Unsplash photo")
                img_url  = unsplash_url
                img_type = "URL"
            else:
                agent_log("IMAGE", "⚠ Vision check failed — photo not relevant, trying Imagen")
        else:
            agent_log("IMAGE", "⚠ Unsplash returned no result")
    else:
        agent_log("IMAGE", "No hero_image_query provided — skipping Unsplash")

    # ── Phase 3: Gemini Imagen fallback ─────────────────────────────────
    if not img_url:
        if prompt:
            agent_log("IMAGE", "Phase 3 — Gemini Imagen generation...")
            img_b64 = _generate_imagen(prompt)
            if img_b64:
                agent_log("IMAGE", "✅ Gemini Imagen generation successful")
                img_type = "CID"
            else:
                agent_log("IMAGE", "❌ Imagen generation failed — proceeding text-only")
        else:
            agent_log("IMAGE", "No hero_image_prompt found — skipping Imagen fallback")

    # ── Phase 4: Inject image into HTML ─────────────────────────────────
    if img_url:
        img_tag = (
            f'<img src="{img_url}" width="600" '
            f'style="display:block;width:100%;max-width:600px;height:auto;" '
            f'alt="Campaign Visual">'
        )
        winner = _inject_image(winner, img_tag, "<!-- HERO IMAGE -->")
        kv("Image Source", f"Unsplash URL: {img_url[:70]}...")

    elif img_b64:
        img_tag = (
            '<img src="cid:hero_image" width="600" '
            'style="display:block;width:100%;max-width:600px;height:auto;" '
            'alt="Campaign Visual">'
        )
        winner = _inject_image(winner, img_tag, "<!-- HERO IMAGE -->")
        kv("Image Source", "Gemini Imagen (inline CID attachment)")

    else:
        agent_log("IMAGE", "⚠ No image secured — sending text-only email")

    # ── Update copy_data with image metadata ─────────────────────────────
    # Patch the winner back into the variants list
    updated_variants = []
    for v in variants:
        if isinstance(v, dict) and v.get("variant_id") == winner.get("variant_id"):
            updated_variants.append(winner)
        else:
            updated_variants.append(v)

    copy_data["variants"]           = updated_variants
    copy_data["hero_image_url"]     = img_url
    copy_data["hero_image_base64"]  = img_b64
    copy_data["hero_image_type"]    = img_type

    divider()

    # ── Publish to Kafka ────────────────────────────────────────────────
    publish_event(
        topic=Topics.IMAGE_RESULTS,
        source_agent="image_agent",
        payload={
            "event":    "image_processed",
            "img_type": img_type or "none",
            "has_url":  img_url is not None,
            "has_b64":  img_b64 is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {
        **state,
        "copy_output":  copy_data,
        "current_step": "compliance_agent",
        "trace": state.get("trace", []) + [{
            "agent":     "image_agent",
            "status":    "completed",
            "img_type":  img_type or "none",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }


# ── Internal Helpers ─────────────────────────────────────────────────────────

def _inject_image(winner: dict, img_tag: str, placeholder: str) -> dict:
    """
    Inject the image tag into the HTML body.
    Replaces placeholder comment if present; otherwise inserts after <body>
    or the opening wrapper table.
    """
    html = winner.get("body_html", "")

    if placeholder in html:
        # Replace the placeholder comment row wrapper
        row_html = (
            f"<tr><td style='padding:0;font-family:Arial,sans-serif;'>"
            f"{img_tag}"
            f"</td></tr>"
        )
        html = html.replace(placeholder, row_html, 1)

    elif "<img src=\"cid:hero_image\"" in html:
        # Already has a CID placeholder — swap it
        import re
        html = re.sub(r'<img\s+src="cid:hero_image"[^>]*>', img_tag, html, count=1)

    else:
        # Best-effort: insert after first <td inside the main content area
        insert_after = "<td align=\"center\">"
        if insert_after in html:
            row_html = (
                f"<tr><td style='padding:0;font-family:Arial,sans-serif;'>"
                f"{img_tag}"
                f"</td></tr>"
            )
            idx = html.find(insert_after) + len(insert_after)
            html = html[:idx] + row_html + html[idx:]

    winner["body_html"] = html
    return winner


def _fetch_unsplash(query: str) -> str | None:
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        agent_log("IMAGE", "UNSPLASH_ACCESS_KEY not set in .env — skipping Unsplash")
        return None

    q   = urllib.parse.quote(query)
    url = f"https://api.unsplash.com/photos/random?query={q}&orientation=landscape"
    headers = {
        "Accept-Version": "v1",
        "Authorization":  f"Client-ID {api_key}",
        "User-Agent":     "MarketOS/1.0",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        urls = data.get("urls")
        return urls.get("regular") if isinstance(urls, dict) else None

    except urllib.error.HTTPError as e:
        codes = {401: "invalid API key", 403: "rate limit / forbidden", 404: "no photos found"}
        agent_log("IMAGE", f"Unsplash HTTP {e.code}: {codes.get(e.code, e.reason)}")
        return None
    except Exception as e:
        agent_log("IMAGE", f"Unsplash exception: {e}")
        return None


def _verify_image_relevance(image_url: str, query: str) -> bool:
    """
    Use Gemini's multimodal capability to verify the photo is on-brand.
    Falls back to True on any error so we don't lose a good photo due to
    a transient API issue.
    """
    try:
        llm = get_llm(temperature=0)
        prompt = (
            f"You are evaluating an image for a marketing email header. "
            f"The campaign subject is: '{query}'.\n"
            f"Look at the image. Does it visually represent this subject in a professional, "
            f"aesthetically pleasing way suitable for a marketing email?\n"
            f"Respond ONLY with YES or NO."
        )
        message = HumanMessage(content=[
            {"type": "text",      "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}},
        ])
        response = llm.invoke([message])
        content  = response.content

        # Normalise content (could be str or list of blocks)
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") if isinstance(c, dict) else str(c)
                for c in content
            )
        return "YES" in str(content).strip().upper()

    except Exception as e:
        agent_log("IMAGE", f"Vision check exception: {e} — assuming YES")
        return True   # Don't penalise a good photo on transient failure


def _generate_imagen(prompt: str) -> str | None:
    """
    Call Gemini Imagen 4 Fast via REST.
    Returns base64-encoded image bytes or None on failure.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        agent_log("IMAGE", "GEMINI_API_KEY not set — cannot run Imagen")
        return None

    # Force no text in the image
    full_prompt = (
        prompt.rstrip(".")
        + ". Absolutely NO text, typography, letters, words, or captions in the image."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/imagen-4.0-fast-generate-001:predict?key={api_key}"
    )
    payload = {
        "instances":  [{"prompt": full_prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "16:9"},
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())

        preds = data.get("predictions")
        if isinstance(preds, list) and preds:
            return preds[0].get("bytesBase64Encoded")
        return None

    except Exception as e:
        agent_log("IMAGE", f"Imagen API exception: {e}")
        return None
