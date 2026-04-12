-- MarketOS — Phase 3 Schema Additions
-- Run: docker compose exec postgres psql -U marketos -d marketos -f /path/to/init_phase3.sql

-- ── Campaign Spend Tracking (Finance Agent) ───────────────────────────────
CREATE TABLE IF NOT EXISTS campaign_spend (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     VARCHAR(16) NOT NULL,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    channel         VARCHAR(32) DEFAULT 'email',   -- email | sms | meta | google | tiktok
    amount_inr      NUMERIC(12,2) NOT NULL DEFAULT 0,
    conversions     INTEGER DEFAULT 0,
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_spend_campaign ON campaign_spend(campaign_id, workspace_id);

-- ── ROI Attributions (Finance Agent) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS roi_attributions (
    campaign_id         VARCHAR(16) PRIMARY KEY,
    workspace_id        VARCHAR(64) NOT NULL DEFAULT 'default',
    total_spend         NUMERIC(12,2) DEFAULT 0,
    attributed_revenue  NUMERIC(12,2) DEFAULT 0,
    conversions         INTEGER DEFAULT 0,
    roas                NUMERIC(8,4) DEFAULT 0,
    cpa                 NUMERIC(10,2) DEFAULT 0,
    attributed_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── A/B Variant Stats (A/B Test Agent) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS ab_variant_stats (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id     VARCHAR(16) NOT NULL,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    variant_id      VARCHAR(16) NOT NULL,
    sends           INTEGER DEFAULT 0,
    opens           INTEGER DEFAULT 0,
    clicks          INTEGER DEFAULT 0,
    conversions     INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(campaign_id, variant_id)
);

-- ── A/B Test Results (A/B Test Agent) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS ab_test_results (
    test_id         VARCHAR(32) PRIMARY KEY,
    campaign_id     VARCHAR(16) NOT NULL,
    workspace_id    VARCHAR(64) NOT NULL DEFAULT 'default',
    winner_id       VARCHAR(16),
    decision        VARCHAR(32),    -- winner_declared | inconclusive | early_stop
    confidence      NUMERIC(5,4),
    key_learning    TEXT,
    copy_insight    TEXT,
    concluded_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ── Contact Scores (Lead Scoring Agent) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS contact_scores (
    contact_id          VARCHAR(128) NOT NULL,
    workspace_id        VARCHAR(64) NOT NULL DEFAULT 'default',
    score               NUMERIC(8,2) DEFAULT 0,
    lifecycle_stage     VARCHAR(32) DEFAULT 'subscriber',
    last_activity_at    TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (contact_id, workspace_id)
);
CREATE INDEX IF NOT EXISTS idx_scores_stage ON contact_scores(workspace_id, lifecycle_stage);

-- ── Contacts Table (Personalization Agent) ────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    contact_id              VARCHAR(128) NOT NULL,
    workspace_id            VARCHAR(64) NOT NULL DEFAULT 'default',
    email                   TEXT,
    first_name              TEXT,
    last_name               TEXT,
    city                    TEXT,
    country                 CHAR(2),
    language                VARCHAR(8) DEFAULT 'en',
    segment                 VARCHAR(64),
    last_purchase_days_ago  INTEGER,
    total_orders            INTEGER DEFAULT 0,
    avg_order_value         NUMERIC(10,2),
    email_opens_30d         INTEGER DEFAULT 0,
    email_clicks_30d        INTEGER DEFAULT 0,
    preferred_time          VARCHAR(16),
    tags                    TEXT[],
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (contact_id, workspace_id)
);
CREATE INDEX IF NOT EXISTS idx_contacts_segment ON contacts(workspace_id, segment);

-- ── suppressed column on copy_variants (A/B Test loser suppression) ───────
ALTER TABLE copy_variants ADD COLUMN IF NOT EXISTS suppressed BOOLEAN DEFAULT FALSE;
