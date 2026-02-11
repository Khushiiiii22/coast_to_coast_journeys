# Render Static IP Setup for RateHawk Production

## Overview
RateHawk requires a static IP address to whitelist your application for production API access. Render doesn't provide static IPs directly, but you can use proxy services to get one.

## Solution Options

### Option 1: QuotaGuard Static (Recommended for Render)
**Best for**: Simple setup, reliable, Render-friendly
**Cost**: $9-79/month depending on requests
**Setup Time**: 10 minutes

### Option 2: Fixie Socks
**Best for**: More control, Heroku-like experience
**Cost**: $5-149/month
**Setup Time**: 15 minutes

### Option 3: Google Cloud Run with Reserved IP
**Best for**: Full control, enterprise needs
**Cost**: ~$8-20/month + compute costs
**Setup Time**: 30-60 minutes

---

## RECOMMENDED: QuotaGuard Static Setup

### Step 1: Sign Up for QuotaGuard Static
1. Go to https://www.quotaguard.com/static-ip
2. Create an account
3. Choose a plan (Start with "Starter" - $9/month for testing)
4. You'll receive a proxy URL like: `http://username:password@us-east-static-01.quotaguard.com:9293`

### Step 2: Add to Render Environment Variables
1. Go to your Render dashboard: https://dashboard.render.com
2. Select your web service
3. Go to "Environment" tab
4. Add these variables:

```
QUOTAGUARDSTATIC_URL=http://username:password@us-east-static-01.quotaguard.com:9293
STATIC_IP_ENABLED=true
```

### Step 3: Update Backend Code
Your code is already configured! The `config.py` has:
```python
PROXY_URL = os.getenv('QUOTAGUARDSTATIC_URL', os.getenv('FIXIE_URL'))
```

### Step 4: Get Your Static IP Address
QuotaGuard will provide 1-2 static IPs. To find them:

**Method 1: QuotaGuard Dashboard**
- Login to https://www.quotaguard.com
- Go to "My IPs"
- Copy the static IP addresses (e.g., `54.243.63.45`)

**Method 2: From Your App**
Add this test endpoint to your backend:

```python
# Add to backend/app.py
@app.route('/api/test/my-ip')
def test_static_ip():
    import requests
    
    # Without proxy
    response_no_proxy = requests.get('https://api.ipify.org?format=json')
    
    # With proxy
    proxies = None
    if Config.PROXY_URL:
        proxies = {
            'http': Config.PROXY_URL,
            'https': Config.PROXY_URL
        }
    
    response_with_proxy = requests.get('https://api.ipify.org?format=json', proxies=proxies)
    
    return {
        'without_proxy': response_no_proxy.json(),
        'with_proxy': response_with_proxy.json(),
        'proxy_configured': Config.PROXY_URL is not None
    }
```

### Step 5: Update ETG/RateHawk Service to Use Proxy

I'll update your code now to use the proxy for RateHawk requests.

---

## Alternative: Google Cloud Platform Static IP

### If You Want to Use Google Cloud:

#### Step 1: Create a Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create a new project: "coast-to-coast-journeys"
3. Enable billing

#### Step 2: Reserve a Static IP
```bash
# Install Google Cloud SDK first
# Then run:
gcloud compute addresses create coast-to-coast-static-ip \
    --region=us-central1
```

#### Step 3: Deploy to Cloud Run with Static IP
```bash
# Deploy your backend
gcloud run deploy coast-to-coast-backend \
    --source ./backend \
    --region us-central1 \
    --allow-unauthenticated
```

**Note**: Cloud Run doesn't support static outbound IPs directly. You need to:
1. Use Cloud NAT with reserved external IP
2. Or use Serverless VPC Access Connector

This is more complex and costs more than QuotaGuard.

---

## Recommended Approach: Stay on Render + QuotaGuard

**Why this is best:**
1. ✅ Your existing Render setup works
2. ✅ No migration needed
3. ✅ QuotaGuard is designed for this use case
4. ✅ 10-minute setup
5. ✅ Costs less than Google Cloud NAT
6. ✅ Reliable and maintained

**Steps:**
1. Sign up for QuotaGuard Static
2. Add `QUOTAGUARDSTATIC_URL` to Render environment
3. Get your static IP from QuotaGuard dashboard
4. Send that IP to RateHawk for whitelisting
5. Update your `.env` with production credentials when approved

---

## RateHawk Production Application Process

### Step 1: Get Your Static IP
Follow QuotaGuard setup above to get your IP (e.g., `54.243.63.45`)

### Step 2: Request Production Credentials
Email RateHawk support:
- **To**: b2b@ratehawk.com
- **Subject**: Production API Access Request - Coast to Coast Journeys

**Email Template**:
```
Hello RateHawk Team,

I would like to request production API credentials for our travel booking platform.

Company Information:
- Company Name: Coast to Coast Journeys
- Website: https://coasttocoastjourneys.com (or your Render URL)
- Business Type: Online Travel Agency
- Expected Monthly Bookings: [Your estimate, e.g., 50-100]

Technical Information:
- Application Server: Render (US)
- Static IP Address: [Your QuotaGuard IP, e.g., 54.243.63.45]
- Integration Type: REST API
- Current Environment: Sandbox (Key ID: 83)

We have completed integration testing in the sandbox environment and are ready for production access.

Please let me know if you need any additional information or documentation.

Best regards,
[Your Name]
[Your Title]
Coast to Coast Journeys
```

### Step 3: After Approval
Once RateHawk approves and provides production credentials:

1. Update Render environment variables:
```
ETG_API_KEY_ID=[production_key_id]
ETG_API_KEY_SECRET=[production_secret]
ETG_API_BASE_URL=https://api.worldota.net/api/b2b/v3
```

2. Update local `.env` for testing

---

## Cost Breakdown

### QuotaGuard Static + Render
- **Render Web Service**: $7/month (Starter plan)
- **QuotaGuard Static**: $9/month (Starter - 250k requests)
- **Total**: ~$16/month

### Google Cloud Run + NAT
- **Cloud Run**: $0 (generous free tier) + usage
- **Reserved IP**: $7.30/month
- **Cloud NAT**: $0.045/hour (~$32/month) + data transfer
- **Total**: ~$40-60/month

**Winner**: Render + QuotaGuard = Half the cost, easier setup

---

## Testing Your Static IP Setup

### Test 1: Verify Proxy Connection
```bash
curl -x http://username:password@proxy-url:port https://api.ipify.org
```

### Test 2: Python Test Script
```python
import requests
import os

proxy_url = os.getenv('QUOTAGUARDSTATIC_URL')

if proxy_url:
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    response = requests.get('https://api.ipify.org?format=json', proxies=proxies)
    print(f"Your static IP: {response.json()['ip']}")
else:
    print("No proxy configured")
```

### Test 3: RateHawk API Test
Once configured, test with:
```bash
curl -H "Authorization: Basic [base64_key]" \
     -x http://proxy-url:port \
     https://api.worldota.net/api/b2b/v3/hotel/search/
```

---

## Troubleshooting

### Issue: Proxy not working
**Solution**: Check that `QUOTAGUARDSTATIC_URL` is set in Render environment

### Issue: RateHawk still blocking requests
**Solution**: 
1. Verify your static IP with `curl -x proxy https://api.ipify.org`
2. Confirm RateHawk has whitelisted the exact IP
3. Wait 24 hours for whitelisting to propagate

### Issue: Slow requests
**Solution**: 
- QuotaGuard has multiple regions, request US-East if your Render is in US
- Upgrade QuotaGuard plan for better performance

---

## Next Steps

1. ✅ **Sign up for QuotaGuard Static** (10 min)
2. ✅ **Add to Render environment** (2 min)
3. ✅ **Update backend code to use proxy** (I'll do this now)
4. ✅ **Get static IP from QuotaGuard** (instant)
5. ✅ **Email RateHawk with IP** (5 min)
6. ⏳ **Wait for approval** (1-3 business days)
7. ✅ **Update production credentials** (2 min)
8. 🚀 **Go live!**

---

## Support Links

- **QuotaGuard**: https://www.quotaguard.com/support
- **Render Docs**: https://render.com/docs
- **RateHawk Support**: b2b@ratehawk.com
- **Your Backend**: https://dashboard.render.com

---

## Important Notes

⚠️ **Do not commit proxy credentials to git**
⚠️ **Keep production API keys secure**
⚠️ **Test thoroughly in sandbox before switching to production**
✅ **QuotaGuard provides automatic failover between IPs**
✅ **Your code is already configured to use proxy via `PROXY_URL`**
