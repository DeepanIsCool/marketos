-- MarketOS — PostgreSQL 16 + pgvector Schema
-- Runs automatically on first `docker compose up`

-- ── Extensions ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Campaigns ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaigns (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     VARCHAR(16) UNIQUE NOT NULL,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    campaign_name   TEXT NOT NULL,
    goal            TEXT,
    target_audience TEXT,
    channels        TEXT[],
    budget          NUMERIC(12,2),
    timeline        TEXT,
    tone            VARCHAR(32),
    key_messages    TEXT[],
    status          VARCHAR(32) DEFAULT 'created',  -- created|running|paused|completed|blocked
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

-- ── Copy Variants ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS copy_variants (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id           VARCHAR(16) REFERENCES campaigns(campaign_id),
    variant_id            VARCHAR(16) NOT NULL,
    subject_line          TEXT,
    preview_text          TEXT,
    body_html             TEXT,
    body_text             TEXT,
    cta_text              TEXT,
    readability_score     NUMERIC(5,2),
    tone_alignment_score  NUMERIC(5,2),
    spam_risk_score       NUMERIC(5,2),
    estimated_open_rate   NUMERIC(5,2),
    estimated_ctr         NUMERIC(5,2),
    is_winner             BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

-- ── Compliance Audit Log (append-only) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS compliance_audit (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id      VARCHAR(16),
    variant_id       VARCHAR(16),
    approved         BOOLEAN NOT NULL,
    compliance_score NUMERIC(5,2),
    checks_json      JSONB,
    reason_code      VARCHAR(64),
    blocked_reason   TEXT,
    reviewed_at      TIMESTAMPTZ DEFAULT NOW()
);
-- Append-only: no UPDATE/DELETE allowed (enforced at app layer, not DB)

-- ── Send Results ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS send_results (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id         VARCHAR(16) REFERENCES campaigns(campaign_id),
    message_id          VARCHAR(64),
    status              VARCHAR(32),
    provider            VARCHAR(64),
    recipient_count     INTEGER,
    real_email_sent     BOOLEAN DEFAULT FALSE,
    real_email_status   TEXT,
    optimal_send_time   TEXT,
    drip_sequence_json  JSONB,
    sent_at             TIMESTAMPTZ DEFAULT NOW()
);

-- ── Alert Rules ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alert_rules (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    rule_id         VARCHAR(64) UNIQUE NOT NULL,
    metric          VARCHAR(128) NOT NULL,
    condition       VARCHAR(16) NOT NULL,   -- gt | lt | gte | lte
    threshold       NUMERIC(12,4) NOT NULL,
    severity        VARCHAR(16) NOT NULL,   -- INFO | WARNING | CRITICAL
    tier            INTEGER DEFAULT 1,      -- 1=slack 2=pagerduty 3=auto-remediation
    active          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default alert rules (PRD §5.2 playbooks)
INSERT INTO alert_rules (rule_id, metric, condition, threshold, severity, tier) VALUES
    ('SPAM_RATE_HIGH',      'spam_complaint_rate',  'gt',  0.005,  'CRITICAL', 3),
    ('BOUNCE_RATE_HIGH',    'hard_bounce_rate',     'gt',  0.02,   'WARNING',  2),
    ('OPEN_RATE_LOW',       'open_rate',            'lt',  0.10,   'INFO',     1),
    ('BUDGET_OVERPACE',     'spend_vs_budget_pct',  'gt',  1.10,   'CRITICAL', 3),
    ('DELIVERY_RATE_LOW',   'delivery_rate',        'lt',  0.95,   'WARNING',  2),
    ('SMS_DELIVERY_LOW',    'sms_delivery_rate',    'lt',  0.70,   'CRITICAL', 3)
ON CONFLICT (rule_id) DO NOTHING;

-- ── Monitor Incidents ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monitor_incidents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id     VARCHAR(64) UNIQUE NOT NULL,
    campaign_id     VARCHAR(16),
    rule_id         VARCHAR(64),
    severity        VARCHAR(16),
    metric          VARCHAR(128),
    observed_value  NUMERIC(12,4),
    threshold       NUMERIC(12,4),
    status          VARCHAR(32) DEFAULT 'open',    -- open|auto_remediated|resolved
    remediation     TEXT,
    fired_at        TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

-- ── Agent Memory: Episodic (pgvector) ─────────────────────────────────────
-- Stores past campaign outcomes as vector embeddings for semantic retrieval
CREATE TABLE IF NOT EXISTS agent_episodic_memory (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    agent_name      VARCHAR(64) NOT NULL,
    event_type      VARCHAR(64),            -- campaign_completed | ab_test_winner | compliance_block
    summary         TEXT NOT NULL,          -- human-readable summary stored as embedding source
    embedding       vector(768),            -- text-embedding-004 produces 768-dim vectors
    metadata        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_episodic_workspace ON agent_episodic_memory(workspace_id, agent_name);
CREATE INDEX IF NOT EXISTS idx_episodic_embedding ON agent_episodic_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ── Agent Memory: Semantic (brand knowledge) ──────────────────────────────
CREATE TABLE IF NOT EXISTS agent_semantic_memory (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    category        VARCHAR(64),            -- brand_voice | personas | product | messaging
    key             VARCHAR(256),
    content         TEXT NOT NULL,
    embedding       vector(768),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
-- UNIQUE constraint for upsert support (ON CONFLICT)
ALTER TABLE agent_semantic_memory
    ADD CONSTRAINT uq_semantic_workspace_category_key
    UNIQUE (workspace_id, category, key);

CREATE INDEX IF NOT EXISTS idx_semantic_workspace ON agent_semantic_memory(workspace_id, category);
CREATE INDEX IF NOT EXISTS idx_semantic_embedding ON agent_semantic_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ── Add result_data to campaigns (for worker status updates) ───────────────
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS result_data JSONB;

-- ── Campaign Spend (Finance Agent) ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaign_spend (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     VARCHAR(16),
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    channel         VARCHAR(32),          -- email | sms | social | ads
    amount_inr      NUMERIC(12,2),
    conversions     INTEGER DEFAULT 0,
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── ROI Attributions (Finance Agent) ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS roi_attributions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id         VARCHAR(16) UNIQUE,
    workspace_id        VARCHAR(64) NOT NULL DEFAULT 'default',
    total_spend         NUMERIC(12,2),
    attributed_revenue  NUMERIC(12,2),
    conversions         INTEGER DEFAULT 0,
    roas                NUMERIC(8,4),
    cpa                 NUMERIC(12,2),
    attributed_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── SMS Suppressions (SMS Agent opt-out registry) ──────────────────────────
CREATE TABLE IF NOT EXISTS sms_suppressions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_normalized    VARCHAR(20) NOT NULL,
    workspace_id        VARCHAR(64) NOT NULL DEFAULT 'default',
    reason              VARCHAR(64) DEFAULT 'opt_out',
    added_at            TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (phone_normalized, workspace_id)
);

-- ── Contacts (for consent verification) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id      VARCHAR(64) UNIQUE,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    email           VARCHAR(256),
    phone           VARCHAR(20),
    first_name      VARCHAR(128),
    last_name       VARCHAR(128),
    consent_type    VARCHAR(32) DEFAULT 'implied',   -- implied | express_written
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Content Calendar (Social Media Agent) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS content_calendar (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slot_id         VARCHAR(16) UNIQUE,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    campaign_id     VARCHAR(16),
    platform        VARCHAR(32),          -- instagram | facebook | linkedin | x | tiktok
    content_text    TEXT,
    scheduled_at    TIMESTAMPTZ,
    status          VARCHAR(32) DEFAULT 'scheduled',   -- scheduled | published | failed
    published_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
