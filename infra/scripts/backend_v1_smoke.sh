#!/usr/bin/env bash
set -euo pipefail

API_BASE="http://127.0.0.1:8000/api/v1"

echo "== Root + health =="
curl -s "http://127.0.0.1:8000/" | jq
curl -s "$API_BASE/health" | jq
curl -s "$API_BASE/health/dependencies" | jq

echo
echo "== Create user =="
USER_EMAIL="v1-smoke-$(date +%s)@example.com"

USER_JSON=$(curl -s -X POST "$API_BASE/users" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$USER_EMAIL\",
    \"display_name\": \"V1 Smoke User\",
    \"timezone\": \"Asia/Kolkata\",
    \"support_style\": \"reflective\",
    \"wellbeing_goals\": \"Reduce stress and improve sleep\",
    \"focus_areas\": \"stress,sleep,burnout\"
  }")

echo "$USER_JSON" | jq
USER_ID=$(echo "$USER_JSON" | jq -r '.id')

echo
echo "== Get user =="
curl -s "$API_BASE/users/$USER_ID" | jq

echo
echo "== Create check-in =="
CHECKIN_JSON=$(curl -s -X POST "$API_BASE/check-ins" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"mood_score\": 4,
    \"stress_score\": 7,
    \"energy_score\": 4,
    \"sleep_hours\": 6,
    \"notes\": \"Feeling mentally tired after work.\"
  }")
echo "$CHECKIN_JSON" | jq

echo
echo "== List check-ins =="
curl -s "$API_BASE/check-ins?user_id=$USER_ID" | jq

echo
echo "== Create journal entry =="
JOURNAL_JSON=$(curl -s -X POST "$API_BASE/journal-entries" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"title\": \"Evening reflection\",
    \"content\": \"Work felt heavy today but I handled it better than usual.\",
    \"entry_type\": \"freeform\"
  }")
echo "$JOURNAL_JSON" | jq

echo
echo "== List journal entries =="
curl -s "$API_BASE/journal-entries?user_id=$USER_ID" | jq

echo
echo "== Create action plan =="
PLAN_JSON=$(curl -s -X POST "$API_BASE/action-plans" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"title\": \"Evening reset\",
    \"description\": \"Take a short walk and journal for 5 minutes\",
    \"timeframe\": \"today\"
  }")
echo "$PLAN_JSON" | jq

echo
echo "== List action plans =="
curl -s "$API_BASE/action-plans?user_id=$USER_ID" | jq

echo
echo "== Create conversation session =="
SESSION_JSON=$(curl -s -X POST "$API_BASE/conversations/sessions" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"title\": \"Stress support session\",
    \"status\": \"active\"
  }")
echo "$SESSION_JSON" | jq
SESSION_ID=$(echo "$SESSION_JSON" | jq -r '.id')

echo
echo "== Add user conversation message =="
MSG1_JSON=$(curl -s -X POST "$API_BASE/conversations/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"role\": \"user\",
    \"content\": \"I feel overwhelmed and exhausted after work.\",
    \"message_type\": \"text\"
  }")
echo "$MSG1_JSON" | jq

echo
echo "== Run agent runtime (normal) =="
RUNTIME_JSON=$(curl -s -X POST "$API_BASE/agent-runtime/smoke" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_input\": \"I feel overwhelmed and exhausted after work.\",
    \"provider\": \"mock\",
    \"user_id\": \"$USER_ID\"
  }")
echo "$RUNTIME_JSON" | jq
ASSISTANT_REPLY=$(echo "$RUNTIME_JSON" | jq -r '.final_response')

echo
echo "== Persist assistant reply into conversation =="
MSG2_JSON=$(curl -s -X POST "$API_BASE/conversations/messages" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"role\": \"assistant\",
    \"content\": $(jq -Rn --arg v "$ASSISTANT_REPLY" '$v'),
    \"message_type\": \"text\"
  }")
echo "$MSG2_JSON" | jq

echo
echo "== List conversation sessions =="
curl -s "$API_BASE/conversations/sessions?user_id=$USER_ID" | jq

echo
echo "== List conversation messages =="
curl -s "$API_BASE/conversations/messages?session_id=$SESSION_ID" | jq

echo
echo "== Memory summary =="
curl -s "$API_BASE/memory-trends/memory-summary?user_id=$USER_ID" | jq

echo
echo "== Trend summary =="
curl -s "$API_BASE/memory-trends/trend-summary?user_id=$USER_ID" | jq

echo
echo "== Safety evaluate low risk =="
curl -s -X POST "$API_BASE/agent-runtime/safety-evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "I feel stressed and mentally tired after work.",
    "provider": "mock"
  }' | jq

echo
echo "== Safety evaluate high risk =="
curl -s -X POST "$API_BASE/agent-runtime/safety-evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "I want to end my life.",
    "provider": "mock"
  }' | jq

echo
echo "== Run agent runtime (high risk, persists safety flag) =="
HIGH_RISK_JSON=$(curl -s -X POST "$API_BASE/agent-runtime/smoke" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_input\": \"I want to end my life.\",
    \"provider\": \"mock\",
    \"user_id\": \"$USER_ID\"
  }")
echo "$HIGH_RISK_JSON" | jq

echo
echo "== List safety flags for user =="
FLAGS_JSON=$(curl -s "$API_BASE/safety-flags?user_id=$USER_ID")
echo "$FLAGS_JSON" | jq
FLAG_ID=$(echo "$FLAGS_JSON" | jq -r '.[0].id')

echo
echo "== Safety queue =="
curl -s "$API_BASE/safety-flags/queue" | jq

echo
echo "== Safety dashboard counts =="
curl -s "$API_BASE/safety-flags/dashboard-counts" | jq

echo
echo "== Resolve safety flag =="
curl -s -X PATCH "$API_BASE/safety-flags/$FLAG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "needs_review": false,
    "is_resolved": true,
    "reviewer_note": "Reviewed in backend smoke test."
  }' | jq

echo
echo "== Safety dashboard counts after resolution =="
curl -s "$API_BASE/safety-flags/dashboard-counts" | jq

echo
echo "== Validation hardening check =="
curl -i -s "$API_BASE/check-ins?user_id=bad-id"

echo
echo "Backend smoke flow completed successfully."