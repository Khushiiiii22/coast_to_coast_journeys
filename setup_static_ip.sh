#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
CONNECTOR_NAME="c2c-conn"
ROUTER_NAME="c2c-router"
NAT_NAME="c2c-nat"
IP_NAME="c2c-static-ip"
SERVICE_NAME="c2c-journeys"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Static IP Setup for Project: $PROJECT_ID${NC}"

# 1. Enable Required APIs
echo "Enabling Compute and VPC Access APIs..."
gcloud services enable compute.googleapis.com vpcaccess.googleapis.com

# 2. Create Static IP
echo "Creating Static IP Address..."
gcloud compute addresses create $IP_NAME --region=$REGION --project=$PROJECT_ID --quiet

# Retrieve the IP address to show the user
STATIC_IP=$(gcloud compute addresses describe $IP_NAME --region=$REGION --format="value(address)")
echo -e "${GREEN}✅ Static IP Created: $STATIC_IP${NC}"

# 3. Create Cloud Router
echo "Creating Cloud Router..."
gcloud compute routers create $ROUTER_NAME \
    --network=default \
    --region=$REGION \
    --project=$PROJECT_ID --quiet

# 4. Create Cloud NAT
echo "Creating Cloud NAT to use the Static IP..."
gcloud compute routers nats create $NAT_NAME \
    --router=$ROUTER_NAME \
    --region=$REGION \
    --nat-all-subnet-ip-ranges \
    --nat-external-ip-pool=$IP_NAME \
    --project=$PROJECT_ID --quiet

# 5. Create VPC Access Connector (This takes a few minutes)
echo "Creating VPC Access Connector (This may take 2-3 minutes)..."
gcloud compute networks vpc-access connectors create $CONNECTOR_NAME \
    --region=$REGION \
    --range="10.8.0.0/28" \
    --network=default \
    --machine-type=e2-micro \
    --min-instances=2 \
    --max-instances=3 \
    --project=$PROJECT_ID --quiet

# 6. Redeploy Cloud Run with VPC Connector
echo "Updating Cloud Run Service to use Static IP..."
gcloud run services update $SERVICE_NAME \
    --vpc-connector=$CONNECTOR_NAME \
    --vpc-egress=all-traffic \
    --region=$REGION \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${YELLOW}Your App's Permanent Static IP is: ${GREEN}$STATIC_IP${NC}"
echo "Please whitelist this IP ($STATIC_IP) in the RateHawk dashboard."
