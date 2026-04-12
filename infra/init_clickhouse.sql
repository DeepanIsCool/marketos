-- MarketOS — ClickHouse Analytics Schema
-- All marketing events land here. Never query PostgreSQL for analytics.

-- ── Email Events ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marketos_analytics.email_events (
    event_id        String,
    campaign_id     String,
    workspace_id    String DEFAULT 'default',
    contact_id      String,
    event_type      Enum8('send'=1, 'deliver'=2, 'open'=3, 'click'=4,
                         'bounce_soft'=5, 'bounce_hard'=6, 'unsubscribe'=7,
                         'spam_complaint'=8),
    link_url        String DEFAULT '',
    user_agent      String DEFAULT '',
    ip_address      String DEFAULT '',
    provider        String DEFAULT 'sendgrid',
    timestamp       DateTime64(3, 'UTC'),
    date            Date MATERIALIZED toDate(timestamp)
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/email_events', '{replica}')
  PARTITION BY toYYYYMM(date)
  ORDER BY (campaign_id, event_type, timestamp)
  TTL date + INTERVAL 90 DAY;

-- Fallback for single-node local dev
CREATE TABLE IF NOT EXISTS marketos_analytics.email_events_local (
    event_id        String,
    campaign_id     String,
    workspace_id    String DEFAULT 'default',
    contact_id      String,
    event_type      Enum8('send'=1, 'deliver'=2, 'open'=3, 'click'=4,
                         'bounce_soft'=5, 'bounce_hard'=6, 'unsubscribe'=7,
                         'spam_complaint'=8),
    link_url        String DEFAULT '',
    provider        String DEFAULT 'sendgrid',
    timestamp       DateTime64(3, 'UTC'),
    date            Date MATERIALIZED toDate(timestamp)
) ENGINE = MergeTree()
  PARTITION BY toYYYYMM(date)
  ORDER BY (campaign_id, event_type, timestamp)
  TTL date + INTERVAL 90 DAY;

-- ── Hourly Rollup (Materialized View) ─────────────────────────────────────
CREATE MATERIALIZED VIEW IF NOT EXISTS marketos_analytics.email_hourly_mv
TO marketos_analytics.email_hourly AS
SELECT
    campaign_id,
    workspace_id,
    event_type,
    toStartOfHour(timestamp) AS hour,
    count()                  AS event_count
FROM marketos_analytics.email_events_local
GROUP BY campaign_id, workspace_id, event_type, hour;

CREATE TABLE IF NOT EXISTS marketos_analytics.email_hourly (
    campaign_id     String,
    workspace_id    String,
    event_type      Enum8('send'=1, 'deliver'=2, 'open'=3, 'click'=4,
                         'bounce_soft'=5, 'bounce_hard'=6, 'unsubscribe'=7,
                         'spam_complaint'=8),
    hour            DateTime,
    event_count     UInt64
) ENGINE = SummingMergeTree()
  ORDER BY (campaign_id, event_type, hour);

-- ── Campaign Metrics Snapshot ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marketos_analytics.campaign_metrics (
    snapshot_id     String,
    campaign_id     String,
    workspace_id    String DEFAULT 'default',
    total_sent      UInt64 DEFAULT 0,
    delivered       UInt64 DEFAULT 0,
    opens           UInt64 DEFAULT 0,
    clicks          UInt64 DEFAULT 0,
    bounces_soft    UInt64 DEFAULT 0,
    bounces_hard    UInt64 DEFAULT 0,
    unsubscribes    UInt64 DEFAULT 0,
    spam_complaints UInt64 DEFAULT 0,
    open_rate       Float64 DEFAULT 0,
    ctr             Float64 DEFAULT 0,
    bounce_rate     Float64 DEFAULT 0,
    spam_rate       Float64 DEFAULT 0,
    delivery_rate   Float64 DEFAULT 0,
    snapshotted_at  DateTime64(3, 'UTC')
) ENGINE = MergeTree()
  ORDER BY (campaign_id, snapshotted_at)
  TTL toDate(snapshotted_at) + INTERVAL 365 DAY;
