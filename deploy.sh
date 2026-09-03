#!/bin/bash
# ==============================================================================
# Cloud Run deployment for The Prompt Playground (Next.js + FastAPI, combined
# container). Builds via Cloud Build (Dockerfile) and deploys to Cloud Run.
#
# Targets the PRODUCTION service (fronted by the load balancer / myprompt.online).
# Ingress is restricted to the load balancer + internal, matching the original.
# ==============================================================================
set -euo pipefail

PROJECT_ID="landing-zone-demo-341118"
REGION="me-west1"
REPOSITORY="vertex-prompt-playground"
SERVICE_NAME="vertex-prompt-playground"
SERVICE_ACCOUNT_EMAIL="experts-hub-demo@landing-zone-demo-341118.iam.gserviceaccount.com"
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest"

echo "-------------------------------------"
echo "Deploying ${SERVICE_NAME} to Cloud Run"
echo "Project: ${PROJECT_ID}  Region: ${REGION}"
echo "Image:   ${IMAGE_PATH}"
echo "-------------------------------------"

echo "[1/4] Setting project..."
gcloud config set project "${PROJECT_ID}"

echo "[2/4] Ensuring required services are enabled..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com

echo "[2b/4] Ensuring Artifact Registry repo exists..."
gcloud artifacts repositories describe "${REPOSITORY}" --location="${REGION}" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format=docker --location="${REGION}" \
    --description="Docker repo for the Prompt Playground"

echo "[3/4] Building image via Cloud Build (Dockerfile)..."
gcloud builds submit --config cloudbuild.yaml \
  --substitutions "_IMAGE=${IMAGE_PATH}" .

echo "[4/4] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_PATH}" \
  --platform=managed \
  --region="${REGION}" \
  --allow-unauthenticated \
  --ingress=internal-and-cloud-load-balancing \
  --min-instances=0 \
  --concurrency=20 \
  --service-account="${SERVICE_ACCOUNT_EMAIL}" \
  --execution-environment=gen2 \
  --cpu-boost \
  --cpu=2 \
  --memory=4Gi \
  --set-env-vars "PG_GCP_PROJECT_ID=${PROJECT_ID},PG_GCP_REGION=global,PG_DEFAULT_MODEL=gemini-3.8-flash"

echo "-------------------------------------"
echo "Done. Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)'
