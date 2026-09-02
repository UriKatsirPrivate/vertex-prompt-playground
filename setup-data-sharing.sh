#!/usr/bin/env bash
set -euo pipefail

# Enable data sharing with the Anthropic publisher for a GCP project, which is
# a prerequisite for using gated Claude models (e.g. Fable 5) via Vertex AI.
# Flips PublisherModelConfig.dataSharingEnabledProvider to ANTHROPIC.
#
# Data sharing is configured PER (location, model) via the publisher-model
# endpoint:
#   projects/{p}/locations/{loc}/publishers/anthropic/models/{model}:setPublisherModelConfig
# (The project-level :setPublisherModelConfig method is unusable: its path
#  pattern ^projects/[^/]+$ cannot carry the location its backend requires.)
#
# Safe to re-run: an already-enabled model returns HTTP 409 (ALREADY_EXISTS),
# which this script treats as success.
#
# Usage: ./setup-data-sharing.sh [PROJECT] [LOCATION] [MODEL ...]

PROJECT="${1:-${ANTHROPIC_VERTEX_PROJECT_ID:-landing-zone-demo-341118}}"
LOCATION="${2:-${CLOUD_ML_REGION:-global}}"
shift "$(( $# > 2 ? 2 : $# ))" || true
MODELS=("$@")
if [[ ${#MODELS[@]} -eq 0 ]]; then
  MODELS=(claude-fable-5 claude-opus-4-8 claude-fable-5-1)
fi

# The global location uses the global host; regional locations use a regional host.
if [[ "${LOCATION}" == "global" ]]; then
  HOST="aiplatform.googleapis.com"
else
  HOST="${LOCATION}-aiplatform.googleapis.com"
fi

TOKEN="$(gcloud auth application-default print-access-token)"

echo "Enabling Anthropic data sharing for project ${PROJECT} @ ${LOCATION}"
for MODEL in "${MODELS[@]}"; do
  url="https://${HOST}/v1beta1/projects/${PROJECT}/locations/${LOCATION}/publishers/anthropic/models/${MODEL}:setPublisherModelConfig"
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-Goog-User-Project: ${PROJECT}" \
    -H "Content-Type: application/json" \
    -d '{"publisherModelConfig":{"dataSharingEnabledProvider":"ANTHROPIC"}}' \
    "${url}")
  case "${code}" in
    200) echo "  - ${MODEL}: enabled" ;;
    409) echo "  - ${MODEL}: already enabled" ;;
    *)   echo "  - ${MODEL}: FAILED (HTTP ${code})" >&2; exit 1 ;;
  esac
done

echo
echo "Verifying via fetchPublisherModelConfig:"
for MODEL in "${MODELS[@]}"; do
  url="https://${HOST}/v1beta1/projects/${PROJECT}/locations/${LOCATION}/publishers/anthropic/models/${MODEL}:fetchPublisherModelConfig"
  provider=$(curl -sS --fail-with-body -X GET \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-Goog-User-Project: ${PROJECT}" \
    "${url}" \
    | python3 -c "import json,sys;print(json.load(sys.stdin).get('dataSharingEnabledProvider','<unset>'))")
  echo "  - ${MODEL}: dataSharingEnabledProvider=${provider}"
  if [[ "${provider}" != "ANTHROPIC" ]]; then
    echo "    WARNING: expected ANTHROPIC" >&2
    exit 1
  fi
done

# echo
# echo "Done. Retry Claude Code; the 403 on gated models should be gone."
