#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud Project found."
    echo "Please run 'gcloud init' to set up your project first."
    exit 1
fi

REGION="us-central1"
SERVICE_NAME="c2c-journeys"
REPO_NAME="c2c-repo"
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Deployment for Project: $PROJECT_ID${NC}"

# 1. Check if Artifact Registry repo exists
echo -e "${YELLOW}Checking/Creating Artifact Registry Repository...${NC}"
gcloud artifacts repositories describe $REPO_NAME \
    --location=$REGION \
    --project=$PROJECT_ID > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Creating repository '$REPO_NAME'..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Coast to Coast Journeys Docker Repository"
else
    echo -e "${GREEN}Repository '$REPO_NAME' exists.${NC}"
fi

# 2. Prepare Environment
echo -e "${YELLOW}Preparing Environment Configuration...${NC}"
python3 scripts/prepare_gcp_env.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to prepare environment."
    exit 1
fi

# 3. Build and Push Image
echo -e "${YELLOW}Building and Submiting Image to Cloud Build...${NC}"
gcloud builds submit --tag $IMAGE_TAG .

if [ $? -ne 0 ]; then
    echo "❌ Build failed."
    exit 1
fi

# 4. Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
# Deploy with environment variables from env.yaml

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --env-vars-file env.yaml \
    --project $PROJECT_ID

if [ $? -ne 0 ]; then
    echo "❌ Deployment to Cloud Run failed."
    exit 1
fi

echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${YELLOW}Service URL:${NC} https://$SERVICE_NAME-xxxxxx-uc.a.run.app (Check output above for exact URL)"
echo "To see your service, run: gcloud run services list --region $REGION"
