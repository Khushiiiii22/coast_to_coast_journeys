# RateHawk API Credential Issue

## Issue Summary
API credentials are returning "incorrect_credentials" error even though the key_id is being recognized by the server.

## Credentials Used
- **API Key ID**: 83
- **API Key Secret**: 6f9b55f6-eaea-4a82-ac1f-b4529646ce11
- **API URL**: https://api.worldota.net/api/b2b/v3

## API Response
```json
{
  "data": null,
  "debug": {
    "key_id": 83,
    "api_key_id": 0
  },
  "status": "error",
  "error": "incorrect_credentials"
}
```

## Test Request Made
```bash
curl -X POST https://api.worldota.net/api/b2b/v3/search/serp/region/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic ODM6NmY5YjU1ZjYtZWFlYS00YTgyLWFjMWYtYjQ1Mjk2NDZjZTEx" \
  -d '{
    "checkin": "2026-02-15",
    "checkout": "2026-02-18",
    "residency": "in",
    "language": "en",
    "guests": [{"adults": 2, "children": []}],
    "region_id": 6308855,
    "currency": "INR"
  }'
```

## Email to Send to RateHawk Support

**To**: apisupport@ratehawk.com  
**Subject**: Sandbox API Credentials Activation Request - Key ID: 83

```
Dear RateHawk API Support Team,

I recently received my sandbox API credentials and am trying to integrate the RateHawk API v3 for hotel bookings. However, I'm receiving an "incorrect_credentials" error when making API requests.

My credentials:
- API Key ID: 83
- API Base URL: https://api.worldota.net/api/b2b/v3

The API recognizes my key_id (returns key_id: 83 in debug info) but returns "incorrect_credentials" error.

Could you please:
1. Verify that my sandbox API key (ID: 83) is activated
2. Confirm if there are any additional steps needed for sandbox access
3. Advise if there's a different API endpoint for sandbox testing

Integration Details:
- Company: Coast to Coast Journeys
- Use Case: Hotel booking integration for travel website
- Target Markets: India (INR currency)

Thank you for your assistance.

Best regards,
[Your Name]
```
