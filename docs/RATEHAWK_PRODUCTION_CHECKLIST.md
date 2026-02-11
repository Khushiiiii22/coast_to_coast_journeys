# RateHawk Production API - Quick Start Checklist

## 🎯 Goal
Get your static IP and configure RateHawk production API access

---

## ✅ Step-by-Step Checklist

### Phase 1: Setup Static IP (15 minutes)

- [ ] **1.1** Go to https://www.quotaguard.com/static-ip
- [ ] **1.2** Sign up for QuotaGuard Static account
- [ ] **1.3** Choose "Starter" plan ($9/month - 250k requests)
- [ ] **1.4** After signup, go to dashboard and note:
  - Proxy URL: `http://username:password@proxy-url:port`
  - Static IP addresses (1-2 IPs provided)

**Example:**
```
Proxy URL: http://quotaguard12345:secret-pass@us-east-static-01.quotaguard.com:9293
Static IPs: 54.243.63.45, 54.243.63.46
```

### Phase 2: Configure Render (5 minutes)

- [ ] **2.1** Login to Render: https://dashboard.render.com
- [ ] **2.2** Select your web service: `coast-to-coast-journeys`
- [ ] **2.3** Go to "Environment" tab
- [ ] **2.4** Click "Add Environment Variable"
- [ ] **2.5** Add these variables:

```
QUOTAGUARDSTATIC_URL = http://username:password@proxy-url:port
STATIC_IP_ENABLED = true
```

- [ ] **2.6** Click "Save Changes"
- [ ] **2.7** Wait for automatic redeploy (~2 minutes)

### Phase 3: Verify Static IP (2 minutes)

- [ ] **3.1** After deploy completes, visit:
```
https://your-app.onrender.com/api/test/static-ip
```

- [ ] **3.2** You should see JSON response like:
```json
{
  "proxy_configured": true,
  "ip_with_proxy": "54.243.63.45",
  "static_ip_working": true,
  "message": "✅ Static IP configured: 54.243.63.45"
}
```

- [ ] **3.3** **COPY THIS IP ADDRESS** - you'll need it for RateHawk

### Phase 4: Request RateHawk Production Access (5 minutes)

- [ ] **4.1** Open your email client
- [ ] **4.2** Compose email to: `b2b@ratehawk.com`
- [ ] **4.3** Subject: `Production API Access Request - Coast to Coast Journeys`
- [ ] **4.4** Use this template:

```
Hello RateHawk Team,

I would like to request production API credentials for our travel booking platform.

Company Information:
- Company Name: Coast to Coast Journeys
- Website: https://coast-to-coast-journeys.onrender.com (update with your URL)
- Business Type: Online Travel Agency
- Expected Monthly Bookings: 50-200 bookings
- Countries of Operation: India, USA

Technical Information:
- Application Server: Render (US-West)
- Static IP Address: 54.243.63.45 (update with YOUR IP from step 3.3)
- Integration Type: REST API v3
- Current Environment: Sandbox (Key ID: 83)

We have completed integration testing in the sandbox environment and are ready for production access.

Attached Documents:
- Business registration (if available)
- Tax ID / Business license (if available)

Please let me know if you need any additional information or documentation.

Best regards,
[Your Name]
[Your Title]
Coast to Coast Journeys
[Your Phone]
[Your Email]
```

- [ ] **4.5** Send email
- [ ] **4.6** Check your email for RateHawk response (usually 1-3 business days)

### Phase 5: Configure Production Credentials (2 minutes)

**⏳ Wait for RateHawk approval email with production credentials**

Once you receive:
```
Production Key ID: [your_prod_key_id]
Production Key Secret: [your_prod_secret]
```

- [ ] **5.1** Go to Render dashboard
- [ ] **5.2** Go to "Environment" tab
- [ ] **5.3** Update these variables:

```
ETG_API_KEY_ID = [your_prod_key_id]
ETG_API_KEY_SECRET = [your_prod_secret]
ETG_API_BASE_URL = https://api.worldota.net/api/b2b/v3
```

- [ ] **5.4** Save changes (will auto-redeploy)
- [ ] **5.5** Update local `.env` file with same credentials

### Phase 6: Test Production API (5 minutes)

- [ ] **6.1** After redeploy, test hotel search:
```bash
curl -X POST https://your-app.onrender.com/api/hotels/search/destination \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "New Delhi",
    "checkin": "2026-03-15",
    "checkout": "2026-03-17",
    "guests": [{"adults": 2, "children": []}]
  }'
```

- [ ] **6.2** Verify response shows hotels (not sandbox data)
- [ ] **6.3** Test booking flow end-to-end
- [ ] **6.4** Check that static IP is being used in logs

---

## 📊 Cost Breakdown

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Render Web Service | Starter | $7 |
| QuotaGuard Static | Starter (250k req) | $9 |
| **Total** | | **$16/month** |

**Note:** You can upgrade QuotaGuard if you exceed 250k requests/month

---

## 🔍 Verification Commands

### Check your static IP from terminal:
```bash
curl https://your-app.onrender.com/api/test/static-ip
```

### Check RateHawk API working:
```bash
curl https://your-app.onrender.com/api/health
```

### Test hotel search (after production configured):
```bash
curl -X POST https://your-app.onrender.com/api/hotels/search/destination \
  -H "Content-Type: application/json" \
  -d '{"destination":"Mumbai","checkin":"2026-03-15","checkout":"2026-03-17","guests":[{"adults":2}]}'
```

---

## ⚠️ Important Notes

### Security
- ✅ Never commit proxy credentials to git
- ✅ Never commit production API keys to git
- ✅ All sensitive data goes in Render environment variables
- ✅ Your `.env` file is already in `.gitignore`

### Testing
- ✅ Always test in sandbox first
- ✅ Verify static IP is working before requesting production
- ✅ Test production API in staging environment before going live

### Monitoring
- ✅ Monitor QuotaGuard usage dashboard
- ✅ Set up Render alerts for downtime
- ✅ Check ETG API logs in `logs/etg_api_logs.json`

---

## 🆘 Troubleshooting

### Problem: Static IP test shows "proxy not configured"
**Solution:** 
1. Check Render environment has `QUOTAGUARDSTATIC_URL`
2. Verify format: `http://user:pass@proxy:port`
3. Redeploy service

### Problem: RateHawk not responding after production setup
**Solution:**
1. Verify IP whitelist with RateHawk
2. Wait 24 hours for propagation
3. Check credentials are correct
4. Check `ETG_API_BASE_URL` is production URL (not sandbox)

### Problem: QuotaGuard 429 errors (rate limit)
**Solution:**
1. Check usage in QuotaGuard dashboard
2. Upgrade to higher plan
3. Implement request caching

### Problem: "Authorization failed" errors
**Solution:**
1. Verify production credentials are correct
2. Check base64 encoding is working
3. Test with sandbox credentials first to isolate issue

---

## 📞 Support Contacts

- **QuotaGuard Support:** https://www.quotaguard.com/support
- **Render Support:** https://render.com/docs/support
- **RateHawk Support:** b2b@ratehawk.com
- **Your Backend Logs:** https://dashboard.render.com → Your Service → Logs

---

## 🎉 Success Criteria

You're ready for production when:
- ✅ Static IP test endpoint returns your QuotaGuard IP
- ✅ RateHawk has confirmed your IP is whitelisted
- ✅ Production credentials are configured in Render
- ✅ Hotel search returns real (non-sandbox) results
- ✅ Booking flow completes successfully
- ✅ Payment integration is tested

---

## 📚 Additional Resources

- Full setup guide: `docs/RENDER_STATIC_IP_SETUP.md`
- Backend configuration: `backend/config.py`
- ETG API service: `backend/services/etg_service.py`
- Render blueprint: `render.yaml`

---

## ⏱️ Timeline

| Phase | Time | Can Start |
|-------|------|-----------|
| 1. Setup QuotaGuard | 15 min | Now |
| 2. Configure Render | 5 min | After Phase 1 |
| 3. Verify Static IP | 2 min | After Phase 2 |
| 4. Request Production | 5 min | After Phase 3 |
| 5. Wait for Approval | 1-3 days | After Phase 4 |
| 6. Configure & Test | 10 min | After Phase 5 |

**Total Active Time:** ~40 minutes
**Total Elapsed Time:** 1-3 business days (waiting for RateHawk)

---

Good luck! 🚀
