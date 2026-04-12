#!/bin/bash

BROKER="localhost:9092"
RPK_CMD=(docker compose exec -T redpanda rpk)
TOPICS=(
  "agent.supervisor.tasks:3:1"
  "agent.supervisor.results:1:1"
  "agent.copy_agent.tasks:3:1"
  "agent.copy_agent.results:1:1"
  "agent.image_agent.tasks:3:1"
  "agent.image_agent.results:1:1"
  "agent.compliance_agent.tasks:3:1"
  "agent.compliance_agent.results:1:1"
  "agent.finance_agent.tasks:3:1"
  "agent.finance_agent.results:1:1"
  "agent.email_agent.tasks:3:1"
  "agent.email_agent.results:1:1"
  "agent.sms_agent.tasks:3:1"
  "agent.sms_agent.results:1:1"
  "agent.social_media_agent.tasks:3:1"
  "agent.social_media_agent.results:1:1"
  "agent.analytics_agent.tasks:3:1"
  "agent.analytics_agent.results:1:1"
  "agent.monitor_agent.tasks:3:1"
  "agent.monitor_agent.results:1:1"
  "agent.ab_test_agent.tasks:3:1"
  "agent.ab_test_agent.results:1:1"
  "agent.lead_scoring_agent.tasks:3:1"
  "agent.lead_scoring_agent.results:1:1"
  "agent.competitor_agent.tasks:3:1"
  "agent.competitor_agent.results:1:1"
  "agent.seo_agent.tasks:3:1"
  "agent.seo_agent.results:1:1"
  "agent.reporting_agent.tasks:3:1"
  "agent.reporting_agent.results:1:1"
  "agent.onboarding_agent.tasks:3:1"
  "agent.onboarding_agent.results:1:1"
  "campaign.events:3:1"
  "contact.events:6:1"
  "system.alerts:1:1"
  "system.metrics:3:1"
  "campaign.send.stats:3:1"
)

for ENTRY in "${TOPICS[@]}"; do
  IFS=':' read -r TOPIC PARTITIONS REPLICAS <<< "$ENTRY"
  "${RPK_CMD[@]}" topic create "$TOPIC" \
    --brokers "$BROKER" \
    --partitions "$PARTITIONS" \
    --replicas "$REPLICAS" \
    --topic-config retention.ms=604800000 \
    --topic-config cleanup.policy=delete 2>/dev/null || echo "Topic $TOPIC already exists"
done

"${RPK_CMD[@]}" topic create "agent.dlq" \
  --brokers "$BROKER" \
  --partitions 1 \
  --replicas 1 \
  --topic-config retention.ms=-1 \
  --topic-config cleanup.policy=delete 2>/dev/null || echo "Topic agent.dlq already exists"

echo "All topics created."
