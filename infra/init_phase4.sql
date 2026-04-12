-- MarketOS — Phase 4 Schema Additions
-- Run: docker compose exec postgres psql -U marketos -d marketos -f /docker-entrypoint-initdb.d/init_phase4.sql

-- ── SMS Suppressions ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sms_suppressions (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_normalized VARCHAR(20) NOT NULL,
    workspace_id     VARCHAR(64) NOT NULL DEFAULT 'default',
    reason           VARCHAR(64) DEFAULT 'opt_out',
    added_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(phone_normalized, workspace_id)
);

-- ── Content Calendar ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_calendar (
    slot_id          VARCHAR(32) PRIMARY KEY,
    workspace_id     VARCHAR(64) NOT NULL DEFAULT 'default',
    campaign_id      VARCHAR(16),
    platform         VARCHAR(32) NOT NULL,
    content_text     TEXT,
    image_url        TEXT,
    scheduled_at     TIMESTAMPTZ NOT NULL,
    published_at     TIMESTAMPTZ,
    status           VARCHAR(32) DEFAULT 'scheduled',
    platform_post_id TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cal_workspace ON content_calendar(workspace_id, platform, scheduled_at);

-- ── Social Post Engagement ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS social_engagement (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id     VARCHAR(64) NOT NULL DEFAULT 'default',
    platform         VARCHAR(32),
    post_id          TEXT,
    campaign_id      VARCHAR(16),
    likes            INTEGER DEFAULT 0,
    comments         INTEGER DEFAULT 0,
    shares           INTEGER DEFAULT 0,
    reach            INTEGER DEFAULT 0,
    impressions      INTEGER DEFAULT 0,
    recorded_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Onboarding Plans ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS onboarding_plans (
    onboarding_id    VARCHAR(32) PRIMARY KEY,
    workspace_id     VARCHAR(64) NOT NULL,
    workspace_type   VARCHAR(32),
    user_email       TEXT,
    drip_json        JSONB,
    tasks_json       JSONB,
    churn_risk       TEXT,
    status           VARCHAR(32) DEFAULT 'active',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── Workspace Milestones ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workspace_milestones (
    workspace_id     VARCHAR(64) NOT NULL,
    milestone        VARCHAR(64) NOT NULL,
    completed        BOOLEAN DEFAULT FALSE,
    completed_at     TIMESTAMPTZ,
    PRIMARY KEY(workspace_id, milestone)
);

-- ── Reports Store ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaign_reports (
    report_id        VARCHAR(32) PRIMARY KEY,
    campaign_id      VARCHAR(16),
    workspace_id     VARCHAR(64) DEFAULT 'default',
    report_type      VARCHAR(32) DEFAULT 'campaign',
    grade            VARCHAR(4),
    html_path        TEXT,
    xlsx_path        TEXT,
    emailed_to       TEXT,
    insights_json    JSONB,
    generated_at     TIMESTAMPTZ DEFAULT NOW()
);
