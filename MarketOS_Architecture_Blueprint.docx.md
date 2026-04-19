**MarketOS**

One-Click Marketing Intelligence Platform

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Full Architecture & Implementation Blueprint

# **1\. Executive Summary & Platform Vision**

MarketOS is a fully autonomous, AI-native marketing operations platform designed around a single principle: a marketer clicks once, and the platform executes, monitors, optimizes, and reports — indefinitely, around the clock. It is not a tool suite; it is a digital marketing team that never sleeps.

This document is the engineering team's comprehensive review and rewrite of the original plan. It includes additional agents identified as critical gaps, a revised data flow architecture, a hardened technology stack, detailed inter-agent communication protocols, a 24/7 monitoring and observability framework, and a phased implementation roadmap with concrete deliverables.

### **Core Design Principles**

- **Single-Intent Execution:** One-click campaign launch

- User defines goal (e.g., "Drive 500 signups for our webinar") and the Supervisor Agent decomposes it automatically

- **24/7 Autonomous Operation:** All agents run on schedule with no human prompting required

- Monitoring, optimization, and alerting run continuously via event-driven loops

- **Fault-Tolerant by Design:** No single point of failure. Each agent, service, and queue is redundant

- **Observability-First:** All AI decisions are logged, attributable, and explainable

- **Self-Improving:** Agents learn from campaign outcomes via structured feedback loops

# **2\. Complete Agent Roster (Revised & Expanded)**

The original plan identified 9 agents. After architecture review, we have identified 7 additional agents critical for a true one-click, 24/7 autonomous system. Total agent count: 16 specialized agents \+ 1 Supervisor.

| ARCH NOTE | All agents are stateful LangGraph nodes backed by Claude (claude-sonnet-4). Each agent has: (1) a system prompt defining expertise, (2) a tool registry of callable APIs, (3) a vector memory store in pgvector, and (4) a structured output schema for inter-agent messaging via Kafka. |
| :-------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

## **2.1 Agent Definitions Table**

| Agent                     | Tool Set                                              | Triggers / Schedule                                  | Output                                         | SLA              |
| :------------------------ | :---------------------------------------------------- | :--------------------------------------------------- | :--------------------------------------------- | ---------------- |
| **Supervisor**            | Kafka producer, task graph DB, all agent topic writes | User intent event OR scheduled campaign start        | Decomposed task graph to Kafka                 | **\<500ms**      |
| **Copy Agent**            | Claude API, brand voice DB, readability scorer        | Task event from Supervisor, SEO, or Email Agent      | Scored copy variants (JSON)                    | **\<8s**         |
| **Email Agent**           | SendGrid/SES API, contact DB, suppression list        | Campaign trigger, drip scheduler, bounce webhook     | Send confirmation, delivery metrics            | **Real-time**    |
| **SMS Agent**             | Twilio/Vonage API, opt-out registry, delivery hooks   | Campaign trigger, drip scheduler                     | Send status, delivery report                   | **Real-time**    |
| **Creative Agent**        | DALL-E, Unsplash, S3, render service, brand DB        | Creative task from Supervisor or A/B Agent           | Design JSON schema \+ rendered CDN URL         | **\<30s**        |
| **SEO Agent**             | GSC API, headless crawler, keyword rank API           | Weekly schedule \+ on-demand from Supervisor         | SEO briefing, content gap list                 | **Weekly**       |
| **Competitor Agent**      | Playwright, Meta Ad Library, pricing differ           | Daily schedule \+ alert from Monitor Agent           | Competitive intelligence feed (JSON)           | **Daily**        |
| **Analytics Agent**       | ClickHouse, GA4, ad platform APIs                     | Continuous 5-min polling \+ anomaly threshold breach | Metric summaries, anomaly alerts               | **5 min**        |
| **Finance Agent**         | Meta/Google/TikTok Ads API, Stripe, budget DB         | Hourly schedule \+ overspend trigger                 | Budget status, ROI attribution                 | **Hourly**       |
| **A/B Test Agent**        | Stats engine, variant store, campaign DB              | Post-send trigger (min 100 opens reached)            | Winner declaration, loser suppression          | **Event-driven** |
| **Lead Scoring Agent**    | CRM API, engagement event stream, ML scorer           | Contact engagement event from Kafka                  | Lead score update to CRM                       | **\<2s/event**   |
| **Social Media Agent**    | Meta/LinkedIn/X/TikTok APIs, scheduler DB             | Campaign trigger \+ daily content calendar           | Published post IDs, engagement metrics         | **Scheduled**    |
| **Personalization Agent** | Segment profiles, content DB, Claude API              | Pre-send event (called by Email/SMS Agent)           | Personalized message variant per contact       | **\<3s/contact** |
| **Monitor Agent**         | All metric streams, alert rule DB, PagerDuty          | Continuous stream consumer (Kafka)                   | Alerts, escalations, auto-remediation triggers | **\<30s**        |
| **Reporting Agent**       | ClickHouse, PDF renderer, email API                   | Scheduled (daily/weekly/monthly) \+ on-demand        | PDF/XLSX report email \+ stored URL            | **\<60s**        |
| **Onboarding Agent**      | CRM, product DB, drip engine, task tracker            | New user signup event                                | Onboarding drip sequence \+ task list          | **Event-driven** |
| **Compliance Agent**      | GDPR/CAN-SPAM rule DB, suppression list, audit log    | Pre-send gate (every campaign)                       | Approval or block with reason code             | **\<500ms**      |

## **2.2 New Agents — Architecture Rationale**

### **A/B Test Agent (Critical Gap in v1)**

The original plan mentioned A/B testing at the send level but had no agent to own it. Without an autonomous A/B Test Agent, someone must manually check results and pick a winner — breaking the one-click promise.

- Listens on Kafka topic campaign.send.stats for sample-size threshold breaches

- Runs Bayesian A/B statistical tests (not naive open-rate comparison) using a Python stats microservice

- Automatically promotes winner variant and suppresses loser mid-campaign

- Writes test result to the agent memory store so Copy Agent learns winning patterns

- Supports multivariate tests (subject line x CTA x send time) via factorial design

### **Lead Scoring Agent (Critical for Revenue Attribution)**

Without lead scoring, MarketOS fires campaigns into the void. This agent closes the loop from outbound marketing to inbound conversion, making ROI attribution accurate.

- Consumes engagement events (email open, link click, page visit, form fill) from Kafka in real-time

- Maintains a score model per workspace: configurable weights per action type

- Pushes score updates to CRM (HubSpot/Salesforce/Pipedrive) via webhook

- Triggers MQL/SQL threshold alerts to the Supervisor for nurture sequence escalation

### **Social Media Agent**

Email and SMS alone do not constitute a full marketing solution in 2024\. The Social Media Agent is required for omnichannel one-click campaigns.

- Publishes to Meta (Facebook \+ Instagram), LinkedIn, X (Twitter), TikTok via their official APIs

- Maintains a 30-day content calendar per workspace; auto-fills from Copy Agent output

- Monitors engagement (likes, comments, shares, reach) and feeds back to Analytics Agent

- Handles platform-specific formatting: image aspect ratios, character limits, hashtag optimization

### **Personalization Agent**

Generic blast campaigns have industry-average open rates of 21%. Personalized campaigns average 46%. This agent is the multiplier on all send-volume agents.

- Called synchronously by Email Agent and SMS Agent before every send (\< 3s SLA)

- Pulls contact profile from Segment (behavioral data) \+ CRM (demographic data)

- Rewrites subject line, body greeting, and CTA text using contact context via Claude API

- Falls back to segment-level personalization if individual profile is insufficient

### **Monitor Agent (24/7 System Health)**

This is the heartbeat of the 24/7 promise. Without a dedicated Monitor Agent, no other agent knows when something has gone wrong system-wide.

- Consumes ALL metric streams from Kafka as a universal subscriber

- Evaluates configured alert rules: threshold-based, anomaly-based, trend-based

- Escalation levels: (1) Slack/email notification, (2) PagerDuty page, (3) Auto-remediation trigger

- Auto-remediation examples: pause campaign on spam rate spike, switch SMS provider on delivery failure, cap ad spend on ROAS collapse

- Maintains a system health dashboard feed (all green/yellow/red per service)

### **Compliance Agent (Non-Negotiable for Legal Safety)**

Every campaign send must pass a compliance gate. A single CAN-SPAM, GDPR, or TCPA violation can result in fines exceeding $50,000. This agent is the legal firewall.

- Runs as a synchronous pre-send gate — no Email Agent or SMS Agent send proceeds without approval

- Checks: sender authentication (DKIM/SPF/DMARC), unsubscribe link presence, suppression list match, send-time compliance per jurisdiction

- GDPR checks: consent record exists for contact, data residency compliance, right-to-erasure flag

- TCPA checks for SMS: prior express written consent verified, quiet-hours enforcement per timezone

- All decisions logged to immutable audit trail in append-only PostgreSQL table

### **Onboarding Agent**

User activation is the most critical metric for SaaS survival. This agent ensures every new workspace gets value within 24 hours automatically.

- Triggered on new user signup event from auth service

- Creates a personalized onboarding plan based on workspace type (ecommerce, SaaS, agency)

- Launches a 7-day activation drip sequence via Email Agent

- Monitors activation milestones (first campaign sent, first design created, analytics connected) and adjusts drip accordingly

# **3\. System Architecture — Detailed Design**

## **3.1 High-Level Architecture Layers**

| Layer                   | Components & Responsibilities                                                                                                                                    |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Presentation**        | Next.js 14 (App Router) \+ TypeScript \+ Tailwind CSS. Real-time updates via WebSocket (Socket.io). Mobile app: React Native sharing component library.          |
| **API Gateway**         | NestJS REST \+ GraphQL (Apollo). Rate limiting (Redis). JWT auth (Auth0/Clerk). Request validation (Zod). OpenAPI spec auto-generated.                           |
| **Agent Orchestration** | LangGraph agent runner (Python). Supervisor coordinates task graph. Agents communicate via Kafka topics. Agent state in Redis (TTL: 24h).                        |
| **Event Bus**           | Apache Kafka (MSK on AWS). Topics per domain. Consumer groups per agent. Dead-letter queue for failed events. Exactly-once semantics via idempotency keys.       |
| **Core Services**       | NestJS microservices: Campaign Service, Contact Service, Creative Service, Finance Service, Auth Service. Each service owns its PostgreSQL schema.               |
| **AI Services**         | Claude API (primary LLM for all agents). DALL-E 3 / Stability AI (image gen). Google Cloud Vision (image analysis). Whisper (audio-to-text for any voice input). |
| **Data Layer**          | PostgreSQL 16 (primary OLTP). ClickHouse (analytics OLAP). Redis 7 (cache \+ pub/sub). pgvector (agent memory). S3 \+ CloudFront (creative assets).              |
| **Monitoring**          | Prometheus \+ Grafana (metrics). OpenTelemetry (tracing). Loki (logs). PagerDuty (alerting). Sentry (error tracking). Datadog APM (optional).                    |
| **Infrastructure**      | AWS EKS (Kubernetes). Terraform IaC. GitHub Actions CI/CD. ArgoCD (GitOps). Cloudflare (CDN \+ WAF \+ DDoS). AWS ACM (TLS).                                      |

## **3.2 One-Click Campaign Execution Flow**

This is the core user journey — from a single intent to a fully executed multi-channel campaign:

| STEP 1 | User types campaign intent: "Run a Black Friday sale campaign for our email list with a 30% discount. Budget: $5,000." Intent sent to API Gateway → Campaign Service → Supervisor Agent topic on Kafka. |
| :----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

| STEP 2 | Supervisor Agent receives intent. Calls Claude to decompose into a task graph: \[fetch audience segments\] → \[generate copy variants\] → \[generate creative assets\] → \[compliance check\] → \[schedule sends\] → \[set up A/B test\] → \[configure monitoring\]. |
| :----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| STEP 3 | Supervisor publishes parallel tasks to agent-specific Kafka topics. Copy Agent, Creative Agent, and Personalization Agent work simultaneously. Compliance Agent runs last before send. |
| :----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| STEP 4 | Email Agent \+ SMS Agent \+ Social Media Agent receive approved campaign payloads. Execute sends via provider APIs. Publish delivery status events back to Kafka. |
| :----: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| STEP 5 | Analytics Agent, A/B Test Agent, and Monitor Agent begin continuous monitoring. All metrics stream to ClickHouse. Finance Agent tracks spend in real-time. Reporting Agent queues scheduled report. |
| :----: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| RESULT | Campaign is live across all channels. Agents monitor, optimize, and report without any further human input. The user can check a unified dashboard or wait for the scheduled report. |
| :----: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

## **3.3 Inter-Agent Communication Protocol**

All inter-agent messaging uses a standardized envelope schema on Kafka to ensure type safety, traceability, and replay capability:

| MESSAGE SCHEMA | Every Kafka message: { messageId: UUID, timestamp: ISO8601, sourceAgent: string, targetAgent: string | "broadcast", correlationId: UUID (ties to user intent), payload: {}, priority: LOW | NORMAL | HIGH | CRITICAL, retryCount: number, traceId: string (OpenTelemetry) } |
| :------------: | :--------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------ | ---- | --------------------------------------------------------------- |

**Kafka Topic Naming Convention**

- agent.{agent-name}.tasks — inbound task queue per agent

- agent.{agent-name}.results — outbound results from agent

- campaign.events — campaign lifecycle events (created, started, paused, completed)

- contact.events — contact engagement events (open, click, bounce, unsubscribe)

- system.alerts — Monitor Agent publishes all alerts here

- system.metrics — aggregated metric snapshots for dashboard real-time updates

- agent.dlq — dead-letter queue: failed messages with error context for debugging

## **3.4 Agent Memory Architecture**

Agent memory is what separates a one-time AI task runner from a system that learns and improves. Each agent has three memory tiers:

| Memory Tier         | Storage                  | Contents & Usage                                                                                                       |
| :------------------ | :----------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Working Memory**  | Redis (TTL: 2 hours)     | Current task context, in-progress state, intermediate results. Cleared after task completion.                          |
| **Episodic Memory** | pgvector (permanent)     | Past campaign outcomes, A/B test results, audience engagement patterns. Retrieved via semantic search at task start.   |
| **Semantic Memory** | pgvector (per workspace) | Brand guidelines, product catalog, customer personas, approved messaging. The "brand brain" that all agents reference. |

# **4\. Data Architecture**

## **4.1 Database Responsibilities (Revised)**

Each database is purpose-selected. Mixing responsibilities is a primary cause of scaling failures in marketing platforms.

### **PostgreSQL 16 — Operational Data**

- Schemas: users, workspaces, contacts, campaigns, templates, schedules, budgets, audit_log

- Row-level security enforces workspace isolation (multi-tenancy at DB level)

- All writes go through the campaign/contact service — no direct DB access from agents

- Read replicas for reporting queries to avoid OLTP contention

- pgvector extension enabled for agent memory on the same cluster (separate schema)

### **ClickHouse — Analytics & Metrics**

- Receives all event data via Kafka consumer: sends, opens, clicks, bounces, conversions

- ReplicatedMergeTree tables for fault tolerance across 3 nodes

- Materialized views for pre-aggregated metrics (hourly/daily rollups) — dashboard queries \< 100ms

- Retention policy: raw events 90 days, aggregates permanent

- Analytics Agent and Reporting Agent query exclusively here — never PostgreSQL

### **Redis 7 — Cache & Real-Time**

- API response cache (TTL: 5 minutes for dashboard data)

- Agent working memory (TTL: 2 hours, auto-extend on active tasks)

- Rate limiting counters for API gateway

- WebSocket session store (Socket.io adapter)

- Distributed locks for campaign scheduler (prevent duplicate sends)

### **S3 \+ CloudFront — Creative Asset Pipeline**

- All rendered creatives stored in S3 with versioning enabled

- CloudFront CDN delivers assets globally with \< 50ms TTFB

- Lifecycle policy: move assets older than 1 year to S3 Glacier

- Pre-signed URLs for secure upload from browser (Creative Studio)

- Separate buckets per workspace for isolation and access policy simplicity

## **4.2 Multi-Tenancy Data Isolation Strategy**

MarketOS uses a hybrid isolation model: shared infrastructure with logical separation at the application layer, plus PostgreSQL row-level security as a second enforcement layer.

| ISOLATION MODEL | Every database row carries workspace_id. PostgreSQL RLS policies enforce: current_setting('app.workspace_id') \= workspace_id. The API gateway injects workspace_id into the request context from the JWT. No query can access cross-workspace data. |
| :-------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

- ClickHouse: workspace_id partition key — all queries automatically scoped

- S3: bucket-level prefix /workspace/{id}/ — IAM policies enforce path

- Redis: key prefix namespace:{workspace_id}:{key} — all cache keys scoped

- Kafka: topics are shared but messages carry workspace_id — agents filter at consumer level

- Enterprise tier: dedicated EKS namespaces and separate RDS instances for complete isolation

# **5\. 24/7 Monitoring & Observability Framework**

The Monitor Agent is the runtime layer. The observability stack is the infrastructure beneath it. Both must function independently — if the Monitor Agent fails, the infrastructure alerts must still fire.

## **5.1 Three-Tier Alert Architecture**

| Alert Tier   | Trigger Condition                        | Example                                        | Action                                           | Response SLA      |
| :----------- | :--------------------------------------- | :--------------------------------------------- | :----------------------------------------------- | ----------------- |
| **INFO**     | Metric outside normal range but trending | Open rate 5% below 30-day average              | Dashboard highlight \+ daily digest              | **Next report**   |
| **WARNING**  | Threshold breach that requires attention | Bounce rate \> 3% or spend 80% of budget       | Slack \+ email notification immediately          | **\< 5 minutes**  |
| **CRITICAL** | Auto-remediation required                | Spam rate \> 0.5% or service downtime detected | Auto-pause \+ PagerDuty \+ Supervisor escalation | **\< 30 seconds** |

## **5.2 Auto-Remediation Playbooks**

The Monitor Agent does not just alert — it acts. The following playbooks are pre-programmed and execute autonomously:

**Spam Rate Spike (\> 0.5%)**

1. Immediately pause all sends from the affected sending domain

2. Switch remaining sends to backup domain/IP pool

3. Notify Compliance Agent to audit recent send list for spam trap seeds

4. Page on-call engineer with full diagnostic payload

5. Generate incident report via Reporting Agent

**SMS Provider Failure (delivery rate \< 70%)**

6. Failover to secondary provider (Twilio \-\> Vonage \-\> AWS SNS) within 60 seconds

7. Re-queue undelivered messages on new provider

8. Finance Agent updates cost attribution to new provider rate card

9. Alert sent with failover confirmation and ETA for primary restoration

**Ad Spend Overpace (\> 110% of daily budget)**

10. Finance Agent fires budget cap signal to ad platform API (pause campaigns)

11. Supervisor Agent notified to hold any pending ad creative submissions

12. User notified with budget status and option to approve additional spend

13. Budget automatically reinstated at midnight with fresh daily allocation

# **6\. Creative Studio — Production Architecture**

The Creative Studio is a first-class engineering challenge. The v1 plan described the concept correctly. This section adds the production-grade implementation detail required for a scalable, AI-editable design system.

## **6.1 Design Rendering Pipeline**

- Step 1 — Schema Authoring: Human editor (Konva.js WYSIWYG) or Creative Agent writes JSON design schema

- Step 2 — Validation: Schema validated against Zod schema definitions (type, bounds, font availability, brand color compliance)

- Step 3 — Render Queue: Validated schema published to render.jobs Kafka topic

- Step 4 — Render Worker: Node.js worker pod consumes job. Launches Playwright (headless Chromium). Injects schema into React renderer. Screenshots at target resolution.

- Step 5 — Post-Processing: Sharp (Node.js) compresses output. Generates WebP \+ fallback PNG. Uploads to S3 with CDN invalidation.

- Step 6 — Schema Versioning: Every schema save creates a new version record in PostgreSQL. Diff stored for undo/redo.

## **6.2 AI Creative Agent Capabilities**

The Creative Agent is not a prompt-to-image system. It is a programmatic design system with natural language controls:

- Brand template selection: "Use our holiday template" retrieves template schema from workspace brand DB

- Element manipulation: "Make the headline 20% bigger and change to bold" modifies fontSize and fontWeight in JSON

- Color theming: "Apply our brand palette" replaces all color values with workspace brand colors

- Layout variants: "Create a 16:9 version for YouTube" recalculates all x/y/w/h coordinates for new canvas dimensions

- Copy injection: "Add the Black Friday headline from Copy Agent" injects approved copy into text element

- Image swap: "Replace hero image with a winter scene" calls Unsplash API, selects semantically matched image, updates src

- Human review gate: All AI-generated designs flagged for human approval before live use (configurable per workspace)

# **7\. Technology Stack — Revised & Hardened**

| Category               | Selected Technology                                      | Engineering Rationale                                                     |
| :--------------------- | :------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Frontend Framework** | Next.js 14 (App Router) \+ TypeScript 5                  | RSC for SEO, App Router for layouts, TypeScript for agent schema safety   |
| **UI Components**      | Tailwind CSS \+ shadcn/ui \+ Radix Primitives            | Accessible by default, headless, no vendor lock-in                        |
| **Creative Canvas**    | Konva.js (replaces Fabric.js)                            | Better React integration and performance for complex scenes               |
| **State Management**   | Zustand (UI state) \+ React Query v5 (server state)      | Separate concerns: local UI vs server data                                |
| **Real-time**          | Socket.io (WebSocket) \+ Server-Sent Events fallback     | SSE for dashboard metrics, WebSocket for collaborative editing            |
| **API Layer**          | NestJS \+ GraphQL (Apollo Server) \+ REST                | GraphQL for frontend flexibility, REST for webhook ingestion              |
| **Agent Framework**    | LangGraph (Python 3.12) \+ Claude claude-sonnet-4        | LangGraph for stateful graphs; Sonnet balances intelligence and cost      |
| **Event Bus**          | Apache Kafka (AWS MSK Serverless)                        | MSK removes ops burden; serverless scales to zero in dev                  |
| **Primary DB**         | PostgreSQL 16 (AWS RDS Multi-AZ)                         | Multi-AZ for automatic failover; PgBouncer for connection pooling         |
| **Analytics DB**       | ClickHouse Cloud                                         | Sub-second queries on billions of rows; managed service reduces ops       |
| **Cache / Pub-Sub**    | Redis 7 (AWS ElastiCache Cluster Mode)                   | Cluster mode for horizontal scaling; Redis Streams for lightweight queues |
| **Vector Store**       | pgvector (on PostgreSQL)                                 | Simpler ops than Pinecone; sufficient for \< 10M vectors per workspace    |
| **Object Storage**     | AWS S3 \+ CloudFront                                     | Industry standard; versioning \+ lifecycle policies built in              |
| **Image Generation**   | DALL-E 3 (primary) \+ Stability AI (fallback)            | Dual provider prevents single-point AI service dependency                 |
| **Email Provider**     | SendGrid (primary) \+ AWS SES (fallback)                 | Multi-provider with automatic failover on bounce spike                    |
| **SMS Provider**       | MSG91                                                    | Three-tier failover; SNS as cost-efficient bulk tier                      |
| **Auth**               | Clerk (Auth0 alternative)                                | Built-in MFA, organization support, and webhook support out of box        |
| **Infrastructure**     | AWS EKS \+ Terraform \+ ArgoCD                           | GitOps deployment; Terraform for reproducible infra                       |
| **Observability**      | OpenTelemetry \+ Grafana Stack (Prometheus, Loki, Tempo) | Vendor-neutral; Grafana Cloud for managed option                          |
| **CI/CD**              | GitHub Actions \+ ArgoCD                                 | GH Actions for build/test; ArgoCD for GitOps deploy                       |
| **CDN \+ Security**    | Cloudflare (CDN, WAF, DDoS, R2)                          | All-in-one; R2 as S3-compatible storage at lower egress cost              |

# **8\. Security Architecture**

Security was not addressed in the v1 plan. For a platform handling contact databases, financial data, and third-party API credentials, this is a critical omission. The following is non-negotiable for production.

## **8.1 Secrets Management**

- AWS Secrets Manager for all third-party API keys (Twilio, SendGrid, Meta, etc.)

- Keys never stored in environment variables or code — injected at runtime via Secrets Manager SDK

- Workspace API keys (user-provided) encrypted with AES-256-GCM before PostgreSQL storage

- Key rotation automated via Secrets Manager rotation Lambdas

## **8.2 API Security**

- All endpoints require JWT (RS256 algorithm). Public key from Clerk JWKS endpoint.

- Rate limiting: 1,000 req/min per workspace on API gateway (Redis token bucket)

- Webhook ingestion endpoints verified via HMAC signature (provider-specific)

- OWASP Top 10 mitigations: input validation (Zod), parameterized queries (Prisma ORM), CSRF tokens, security headers (helmet.js)

- Cloudflare WAF with custom rules for known marketing platform attack vectors

## **8.3 Data Privacy (GDPR/CCPA)**

- Contact PII stored with field-level encryption (name, email, phone)

- Right to erasure: automated contact deletion pipeline triggered by unsubscribe \+ erasure request

- Data residency: EU workspaces deployed in eu-west-1 (Ireland) RDS instance

- Consent tracking: every contact record carries consent_type, consent_date, consent_source fields

- Audit log: append-only table records all data access and modifications with timestamp \+ actor

_Engineering Team — Confidential Internal Document_
