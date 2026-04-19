# MarketOS Agent API Tests

## Supervisor Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/supervisor/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"user_intent": "Launch a Black Friday sale for VoltX drink to India men 18-30."}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "copy_agent",
    "errors": [],
    "trace": [
      {
        "agent": "supervisor",
        "status": "completed",
        "campaign_id": "ED4F1AC8",
        "timestamp": "2026-04-18T22:05:26.588763+00:00"
      }
    ],
    "user_intent": "Launch a Black Friday sale for VoltX drink to India men 18-30.",
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
         
...
```

## Competitor Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/competitor/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "user_intent": "Launch a Black Friday sale for VoltX drink to India men 18-30."}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "reporting_agent",
    "errors": [],
    "trace": [
      {
        "agent": "competitor_agent",
        "status": "completed",
        "intel_id": "CI-42D73F24",
        "alert_level": "normal",
        "timestamp": "2026-04-18T22:05:43.328493+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_ag
...
```

## Seo Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/seo/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "user_intent": "Launch a Black Friday sale for VoltX drink to India men 18-30."}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "competitor_agent",
    "errors": [],
    "trace": [
      {
        "agent": "seo_agent",
        "status": "completed",
        "briefing_id": "SEO-D2F9B259",
        "timestamp": "2026-04-18T22:05:57.769374+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          ]
        },
       
...
```

## Copy Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/copy/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "competitor_intel": "dummy"}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "compliance_agent",
    "errors": [],
    "trace": [
      {
        "agent": "copy_agent",
        "status": "completed",
        "variants_generated": 2,
        "selected_variant": "V-001",
        "timestamp": "2026-04-18T22:06:12.270154+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent
...
```

## Image Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/image/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "compliance_agent",
    "errors": [],
    "trace": [
      {
        "agent": "image_agent",
        "status": "completed",
        "img_type": "CID",
        "timestamp": "2026-04-18T22:06:37.129488+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          ]
        },
        {
       
...
```

## Compliance Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/compliance/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "email_agent",
    "errors": [],
    "trace": [
      {
        "agent": "compliance_agent",
        "status": "approved",
        "compliance_score": 100.0,
        "checks_run": 10,
        "timestamp": "2026-04-18T22:06:46.009813+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
       
...
```

## Finance Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/finance/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "email_agent",
    "errors": [],
    "trace": [
      {
        "agent": "finance_agent",
        "status": "approved",
        "spend_pct": 0.0,
        "roas": 0.0,
        "timestamp": "2026-04-18T22:06:48.155481+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          ]
        },
 
...
```

## Email Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/email/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}, "compliance_result": {"approved": true, "compliance_score": 100.0, "checks": [{"rule_id": "CANSPAM_001", "rule_name": "Honest subject line", "category": "CAN_SPAM", "passed": true, "severity": "CRITICAL", "detail": "Subject line is accurate and not misleading.", "remediation": null}, {"rule_id": "CANSPAM_002", "rule_name": "Unsubscribe mechanism present in email body", "category": "CAN_SPAM", "passed": true, "severity": "CRITICAL", "detail": "Unsubscribe mechanism is present in the email content.", "remediation": null}, {"rule_id": "CANSPAM_003", "rule_name": "Physical mailing address present in footer", "category": "CAN_SPAM", "passed": true, "severity": "CRITICAL", "detail": "Physical mailing address is present in the email footer.", "remediation": null}, {"rule_id": "CANSPAM_004", "rule_name": "Clear identification as promotional/advertisement", "category": "CAN_SPAM", "passed": true, "severity": "CRITICAL", "detail": "The email is clearly identified as a promotional email from VoltX.", "remediation": null}, {"rule_id": "GDPR_001", "rule_name": "No explicit collection of personal data without consent stated", "category": "GDPR", "passed": true, "severity": "CRITICAL", "detail": "The email does not explicitly collect personal data without consent.", "remediation": null}, {"rule_id": "GDPR_002", "rule_name": "Data processing purpose is clear and proportionate", "category": "GDPR", "passed": true, "severity": "CRITICAL", "detail": "The data processing purpose (sending promotional emails) is clear and proportionate.", "remediation": null}, {"rule_id": "DELIVER_001", "rule_name": "No high-risk spam trigger words (FREE!!, GUARANTEED, $$, WINNER, URGENT!!!)", "category": "DELIVERABILITY", "passed": true, "severity": "WARNING", "detail": "The email contains the word \'FREE\', which is a mild spam trigger. Consider rephrasing.", "remediation": "Consider rephrasing \'30% OFF on ALL flavors\' to \'30% discount on all flavors\'."}, {"rule_id": "DELIVER_002", "rule_name": "Subject line length \u2264 50 characters (optimal deliverability)", "category": "DELIVERABILITY", "passed": true, "severity": "INFO", "detail": "Subject line length is 40 characters, which is within the optimal range.", "remediation": null}, {"rule_id": "BRAND_001", "rule_name": "No unverifiable absolute claims (\"the BEST\", \"100% guaranteed results\")", "category": "BRAND_SAFETY", "passed": true, "severity": "CRITICAL", "detail": "The email does not contain any unverifiable absolute claims.", "remediation": null}, {"rule_id": "BRAND_002", "rule_name": "Discount/offer claims are specific and not misleading", "category": "BRAND_SAFETY", "passed": true, "severity": "CRITICAL", "detail": "The discount offer of 30% off is specific and not misleading.", "remediation": null}], "reason_code": null, "blocked_reason": null, "suggestions": ["Consider A/B testing different subject lines to improve open rates.", "Ensure the unsubscribe link functions correctly and leads to a clear opt-out process."], "reviewed_at": "2026-04-18T22:06:44.969551+00:00"}, "recipient_email": "test@example.com"}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "email_agent",
        "status": "sent",
        "message_id": "MSG-0F85DA5C-BC6",
        "campaign_id": "ED4F1AC8",
        "real_email_sent": true,
        "real_email_to": "test@example.com",
        "timestamp": "2026-04-18T22:06:52.608482+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          
...
```

## Sms Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/sms/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}, "recipient_phone": "+919876543210"}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "voice_agent",
    "errors": [],
    "trace": [
      {
        "agent": "sms_agent",
        "status": "sent",
        "message_id": "SMS-34550010-D26",
        "provider": "none",
        "timestamp": "2026-04-18T22:06:57.113733+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
         
...
```

## Voice Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/voice/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "recipient_phone": "+1234567890"}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "social_media_agent",
    "errors": [],
    "trace": [
      {
        "agent": "voice_agent",
        "status": "skipped",
        "call_sid": "V-SKIP-B48568DD",
        "timestamp": "2026-04-18T22:07:00.389144+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          ]
        },
     
...
```

## Social_media Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/social_media/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}, "copy_output": {"variants": [{"variant_id": "V-001", "subject_line": "\u26a1\ufe0f VoltX Black Friday: 30% OFF - Ends Soon!", "preview_text": "Fuel your fitness this winter! 72-hour flash sale on all VoltX flavors.", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">Unleash Your Potential This Black Friday!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">India, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive <strong>30% OFF</strong> on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Level up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Shop Now & Save!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">Limited stock available! Grab your VoltX now before it\'s gone. This is a promotional email from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "Unleash Your Potential This Black Friday!\n\nIndia, are you ready? VoltX Black Friday Flash Sale is HERE! Get a massive 30% OFF on ALL flavors for the next 72 hours only. Fuel your fitness journey and smash your goals this winter with VoltX.\n\nLevel up your performance with Black Friday prices you won\'t believe. Don\'t miss out on this limited-time offer!\n\n[Shop Now & Save!](https://example.com/offer)\n\nLimited stock available! Grab your VoltX now before it\'s gone.\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is a promotional email from VoltX.", "cta_text": "Shop Now & Save!", "cta_url": "https://example.com/offer", "hero_image_query": "fitness supplements", "hero_image_prompt": "A dynamic shot of a muscular man lifting weights in a gym, with a VoltX supplement container subtly placed in the foreground. Focus on energy and strength. NO TEXT.", "readability_score": 80.0, "tone_alignment_score": 95.0, "spam_risk_score": 7.0, "estimated_open_rate": 32.5, "estimated_ctr": 4.8}, {"variant_id": "V-002", "subject_line": "\ud83d\udd25 VoltX: Black Friday Deal That Crushes the Competition", "preview_text": "Why settle for less? VoltX gives you 30% off all flavors. 72 hours only!", "body_html": "<table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\" style=\"max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; color: #333333;\">\n  <tr>\n    <td align=\"center\" style=\"padding: 20px;\">\n      <a href=\"https://example.com/offer\">\n        <img src=\"cid:hero_image\" alt=\"VoltX Black Friday\" style=\"display: block; width: 100%; max-width: 600px; border: 0;\"/>\n      </a>\n    </td>\n  </tr>\n  <tr>\n    <td style=\"padding: 20px;\">\n      <h1 style=\"font-size: 24px; font-weight: bold; margin-bottom: 15px; color: #000;\">VoltX: Black Friday Deal That Crushes the Competition!</h1>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Tired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get <strong>30% OFF</strong> all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.</p>\n      <p style=\"font-size: 16px; line-height: 1.6; margin-bottom: 20px;\">Don\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!</p>\n      <table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">\n        <tr>\n          <td align=\"center\" style=\"padding: 10px;\">\n            <a href=\"https://example.com/offer\" style=\"background-color: #e44d26; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;\">Get VoltX Now!</a>\n          </td>\n        </tr>\n      </table>\n      <p style=\"font-size: 14px; line-height: 1.4; margin-top: 20px;\">India, are you ready to experience the VoltX difference? This is an advertisement from VoltX.</p>\n    </td>\n  </tr>\n  <tr>\n    <td align=\"center\" style=\"padding: 20px; font-size: 12px; color: #777777;\">\n      <p>Copyright \u00a9 2024 VoltX. All rights reserved.</p>\n    </td>\n  </tr>\n</table>", "body_text": "VoltX: Black Friday Deal That Crushes the Competition!\n\nTired of weak formulas and empty promises? This Black Friday, VoltX is here to deliver REAL results. Get 30% OFF all flavors for 72 hours only \u2013 a deal that leaves the competition in the dust.\n\nDon\'t settle for less. VoltX is engineered for peak performance, giving you the edge you need to dominate your workouts and achieve your fitness goals. Limited stock \u2013 act fast!\n\n[Get VoltX Now!](https://example.com/offer)\n\nIndia, are you ready to experience the VoltX difference?\n\nCopyright \u00a9 2024 VoltX. All rights reserved.\nThis is an advertisement from VoltX.", "cta_text": "Get VoltX Now!", "cta_url": "https://example.com/offer", "hero_image_query": "gym supplements india", "hero_image_prompt": "A high-energy shot of a VoltX supplement container with dynamic lighting, placed on a gym bench next to a shaker bottle and headphones. No people. NO TEXT.", "readability_score": 78.0, "tone_alignment_score": 92.0, "spam_risk_score": 9.0, "estimated_open_rate": 30.0, "estimated_ctr": 5.1}], "selected_variant_id": "V-001", "selection_reasoning": "V-001 is selected because it directly highlights the benefits of the VoltX Black Friday sale, focusing on fueling fitness journeys and achieving goals. The subject line is also more direct and urgent, which aligns well with the campaign\'s goals and target audience.", "brand_voice_notes": "The tone is urgent and energetic, using strong verbs and emphasizing the limited-time nature of the offer. Vocabulary is geared towards fitness enthusiasts, focusing on performance and achieving goals. The style is direct and persuasive, aiming to drive immediate action.", "hero_image_url": null, "hero_image_base64": null, "hero_image_type": null}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "social_media_agent",
        "status": "published",
        "platforms": [
          "x",
          "tiktok"
        ],
        "timestamp": "2026-04-18T22:07:07.333629+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"

...
```

## Analytics Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/analytics/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "analytics_agent",
        "status": "completed",
        "snapshot_id": "SNAP-A0D0FCFC",
        "anomalies": 0,
        "timestamp": "2026-04-18T22:07:10.088786+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
       
...
```

## Monitor Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/monitor/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "monitor_agent",
        "status": "completed",
        "health": "green",
        "alerts_fired": 0,
        "remediations": 0,
        "timestamp": "2026-04-18T22:07:10.136132+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative
...
```

## Ab_test Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/ab_test/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "lead_scoring",
    "errors": [],
    "trace": [
      {
        "agent": "ab_test_agent",
        "status": "completed",
        "test_id": "ABT-FFF26F4F",
        "winner": null,
        "timestamp": "2026-04-18T22:07:12.124884+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          
...
```

## Lead_scoring Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/lead_scoring/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "lead_scoring_agent",
        "status": "completed",
        "contacts_scored": 0,
        "new_mqls": 0,
        "new_sqls": 0,
        "timestamp": "2026-04-18T22:07:14.212168+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative
...
```

## Reporting Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/reporting/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"campaign_plan": {"campaign_id": "ED4F1AC8", "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30", "goal": "Achieve 1,500 conversions in 3 days", "target_audience": "Men aged 18-30 in India, fitness enthusiasts", "channels": ["email", "instagram", "youtube"], "budget": 75000.0, "timeline": "3 days, ending 29 Nov 2024", "tone": "urgent", "key_messages": ["Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.", "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!", "Don\'t miss out! Stock up on VoltX and power through your workouts this winter.", "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.", "Level up your performance with VoltX. Black Friday prices you won\'t believe!", "Limited stock available! Grab your VoltX now before it\'s gone."], "tasks": [{"agent": "copy_agent", "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.", "priority": "HIGH", "depends_on": []}, {"agent": "compliance_agent", "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "creative_agent", "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.", "priority": "HIGH", "depends_on": ["copy_agent"]}, {"agent": "email_agent", "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.", "priority": "HIGH", "depends_on": ["compliance_agent"]}, {"agent": "social_media_agent", "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.", "priority": "HIGH", "depends_on": ["creative_agent"]}, {"agent": "analytics_agent", "task": "Track campaign performance across all channels (email, Instagram, YouTube). Monitor conversions, cost per acquisition, and return on ad spend. Provide daily performance reports.", "priority": "HIGH", "depends_on": ["email_agent", "social_media_agent"]}], "created_at": "2026-04-18T22:05:25.699152+00:00"}}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "reporting_agent",
        "status": "completed",
        "report_id": "RPT-9F5421BF",
        "grade": "F",
        "timestamp": "2026-04-18T22:07:18.748700+00:00"
      }
    ],
    "campaign_plan": {
      "campaign_id": "ED4F1AC8",
      "campaign_name": "VoltX Black Friday Flash Sale India Men 18-30",
      "goal": "Achieve 1,500 conversions in 3 days",
      "target_audience": "Men aged 18-30 in India, fitness enthusiasts",
      "channels": [
        "email",
        "instagram",
        "youtube"
      ],
      "budget": 75000.0,
      "timeline": "3 days, ending 29 Nov 2024",
      "tone": "urgent",
      "key_messages": [
        "Unleash your potential this Black Friday with VoltX! Fuel your fitness journey with our limited-time offer.",
        "VoltX Black Friday Flash Sale: Get 30% off all flavors for 72 hours only!",
        "Don't miss out! Stock up on VoltX and power through your workouts this winter.",
        "India, are you ready? VoltX Black Friday deals are here to help you smash your fitness goals.",
        "Level up your performance with VoltX. Black Friday prices you won't believe!",
        "Limited stock available! Grab your VoltX now before it's gone."
      ],
      "tasks": [
        {
          "agent": "copy_agent",
          "task": "Write 2 email copy variants and 3 social media ad copy variants for VoltX Black Friday Flash Sale. Goal: 1,500 conversions. Tone: urgent. Highlight: 30% off all flavors.",
          "priority": "HIGH",
          "depends_on": []
        },
        {
          "agent": "compliance_agent",
          "task": "Run full CAN-SPAM, GDPR, deliverability compliance check on approved email copy variants. Ensure ad copy complies with Indian advertising standards.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "creative_agent",
          "task": "Design Instagram and YouTube ad creatives showcasing VoltX and the Black Friday offer. Target audience: Men 18-30 in India, fitness enthusiasts. Ad formats: Instagram stories, YouTube bumper ads.",
          "priority": "HIGH",
          "depends_on": [
            "copy_agent"
          ]
        },
        {
          "agent": "email_agent",
          "task": "Execute email campaign send to India-based fitness enthusiast list. Segment by past purchase behavior if available. Track opens, clicks, conversions.",
          "priority": "HIGH",
          "depends_on": [
            "compliance_agent"
          ]
        },
        {
          "agent": "social_media_agent",
          "task": "Launch Instagram and YouTube ad campaigns targeting men 18-30 in India, fitness enthusiasts. Optimize for conversions. Monitor ad performance and adjust bids as needed.",
          "priority": "HIGH",
          "depends_on": [
            "creative_agent"
          ]

...
```

## Onboarding Agent

**Command:**
```bash
curl -X POST http://localhost:8000/v1/agents/onboarding/run \
  -H "Content-Type: application/json" \
  -d '{"state": {"user_intent": "onboard client xyz"}}'
```

**Success Output:**
```json
{
  "ok": true,
  "data": {
    "current_step": "complete",
    "errors": [],
    "trace": [
      {
        "agent": "onboarding_agent",
        "status": "completed",
        "onboarding_id": "OB-3F3CE042",
        "workspace_type": "general",
        "drip_steps": 4,
        "timestamp": "2026-04-18T22:07:24.275589+00:00"
      }
    ],
    "user_intent": "onboard client xyz",
    "_episodic_memories": [
      {
        "summary": "general workspace onboarded. 4 drip emails scheduled.",
        "event_type": "onboarding_created",
        "metadata": {
          "onboarding_id": "OB-2DBC43EA",
          "workspace_type": "general"
        },
        "created_at": "2026-04-18T22:04:36.840008+00:00",
        "similarity": 0.8571942271618769
      },
      {
        "summary": "saas workspace onboarded. 5 drip emails scheduled.",
        "event_type": "onboarding_created",
        "metadata": {
          "onboarding_id": "OB-B9067818",
          "workspace_type": "saas"
        },
        "created_at": "2026-04-16T04:07:30.501987+00:00",
        "similarity": 0.8293845119441038
      },
      {
        "summary": "ecommerce workspace onboarded. 5 drip emails scheduled.",
        "event_type": "onboarding_created",
        "metadata": {
          "onboarding_id": "OB-6045560A",
          "workspace_type": "ecommerce"
        },
        "created_at": "2026-04-18T16:02:18.149897+00:00",
        "similarity": 0.825209953160089
      }
    ],
    "_memory_context": "  - [onboarding_created] general workspace onboarded. 4 drip emails scheduled.\n  - [onboarding_created] saas workspace onboarded. 5 drip emails scheduled.\n  - [onboarding_created] ecommerce workspace onboarded. 5 drip emails scheduled.",
    "onboarding_result": {
      "onboarding_id": "OB-3F3CE042",
      "workspace_type": "general",
      "drip_sequence": [
        {
          "day": 1,
          "subject": "Welcome \u2014 your first campaign takes 60 seconds",
          "goal": "Send first campaign",
          "milestone": "first_campaign_sent",
          "send_at": "2026-04-18T22:07:23.648120+00:00",
          "status": "scheduled",
          "personalization": {
            "user_name": "there"
          }
        },
        {
          "day": 3,
          "subject": "Did you know? A/B testing increases conversions 23%",
          "goal": "Enable A/B testing",
          "milestone": "ab_test_created",
          "send_at": "2026-04-20T22:07:23.648813+00:00",
          "status": "scheduled",
          "personalization": {
            "user_name": "there"
          }
        },
        {
          "day": 5,
          "subject": "Your analytics are live \u2014 here's what to watch",
          "goal": "View analytics",
          "milestone": "analytics_viewed",
          "send_at": "2026-04-22T22:07:23.649052+00:00",
          "status": "scheduled",
          "personalization": {
            "user_name": "there"
          }
        },
        {
          "day": 7,
          "subject": "Y
...
```

