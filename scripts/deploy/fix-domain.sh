#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="c2c-journeys"
DOMAIN="coasttocoastjourneys.com"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Fixing Domain Mapping for $DOMAIN${NC}"

# Step 1: Check current domain mappings
echo -e "${YELLOW}Checking existing domain mappings...${NC}"
gcloud beta run domain-mappings list --region=$REGION --project=$PROJECT_ID

# Step 2: Delete existing mapping if any (to recreate)
echo -e "${YELLOW}Removing old domain mapping (if exists)...${NC}"
gcloud beta run domain-mappings delete $DOMAIN --region=$REGION --project=$PROJECT_ID --quiet 2>/dev/null || echo "No existing mapping found"

# Step 3: Map custom domain
echo -e "${YELLOW}Creating new domain mapping...${NC}"
gcloud beta run domain-mappings create \
    --service=$SERVICE_NAME \
    --domain=$DOMAIN \
    --region=$REGION \
    --project=$PROJECT_ID

# Step 4: Show DNS configuration
echo -e "${GREEN}✅ Domain mapping created!${NC}"
echo -e "${YELLOW}Please verify the following DNS records are set:${NC}"
gcloud beta run domain-mappings describe $DOMAIN --region=$REGION --project=$PROJECT_ID --format="value(status.resourceRecords)"

echo ""
echo -e "${GREEN}📝 Next Steps:${NC}"
echo "1. Go to your domain registrar (GoDaddy, Namecheap, etc.)"
echo "2. Add the DNS records shown above"
echo "3. Wait 15-30 minutes for DNS propagation"
echo "4. SSL certificate will be automatically provisioned by Google"
echo ""
echo -e "${YELLOW}To check status later, run:${NC}"
echo "gcloud beta run domain-mappings describe $DOMAIN --region=$REGION"
