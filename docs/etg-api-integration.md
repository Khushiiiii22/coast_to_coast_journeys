# ETG API Integration Guide

## Overview

This document describes the integration with ETG (Emerging Travel Group) API v3 for hotel booking functionality in Coast to Coast Journeys.

## API Base URL

- **Sandbox**: `https://api.worldota.net/api/b2b/v3`
- **Production**: Same URL (requires certification)

## Authentication

ETG API uses HTTP Basic Authentication:
- **Key ID**: Your API Key ID
- **Key Secret**: Your API Key Secret

```python
import base64
credentials = f"{key_id}:{key_secret}"
auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER JOURNEY                                │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   Search    │────▶│   Hotel     │────▶│   Prebook   │
    │   Hotels    │     │   Page      │     │   Rate      │
    └─────────────┘     └─────────────┘     └─────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
    /search/serp/       /search/hp/         /hotel/prebook
    region/             (hotel details)     (check availability)
          │                                       │
          └──────────────────────────────────────▶│
                                                  ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  Confirm    │◀────│   Booking   │◀────│   Create    │
    │  Booking    │     │   Status    │     │   Booking   │
    └─────────────┘     └─────────────┘     └─────────────┘
          ▲                   ▲                   │
          │                   │                   ▼
    /booking/finish/   /booking/finish/     /booking/form/
    status/ (poll)     (finalize)           (create order)
```

## Endpoints

### 1. Static Data

| Endpoint | Purpose | Frequency |
|----------|---------|-----------|
| `/hotel/info/dump/` | Download all hotels | Weekly |
| `/hotel/info/` | Get single hotel info | On-demand |
| `/hotel/info/incremental_dump/` | Daily updates | Daily |

### 2. Search

| Endpoint | Purpose |
|----------|---------|
| `/search/serp/region/` | Search by region ID |
| `/search/serp/geo/` | Search by coordinates |
| `/search/serp/hotels/` | Search specific hotels (max 300) |
| `/search/hp/` | Get hotel page with all rates |

### 3. Booking

| Endpoint | Purpose | Required |
|----------|---------|----------|
| `/hotel/prebook` | Check rate availability | ✅ Yes |
| `/hotel/order/booking/form/` | Create booking | ✅ Yes |
| `/hotel/order/booking/finish/` | Start booking | ✅ Yes |
| `/hotel/order/booking/finish/status/` | Check status | ✅ Yes |
| `/hotel/order/info/` | Get booking details | Recommended |
| `/hotel/order/cancel/` | Cancel booking | Recommended |

## Request/Response Examples

### Search by Region

**Request:**
```json
{
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "residency": "in",
    "language": "en",
    "guests": [{"adults": 2, "children": []}],
    "region_id": 6308855,
    "currency": "INR"
}
```

### Prebook Rate

**Request:**
```json
{
    "hash": "h123456789...",
    "price_increase_percent": 5
}
```

### Create Booking

**Request:**
```json
{
    "hash": "h123456789...",
    "partner_order_id": "CTC-20260201-ABC123",
    "payment_type": {"type": "now"},
    "user_ip": "192.168.1.1",
    "rooms": [{
        "guests": [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Doe"}
        ]
    }]
}
```

## Status Codes

| Status | Meaning |
|--------|---------|
| `processing` | Booking in progress, continue polling |
| `ok` | Booking confirmed |
| `cancelled` | Booking cancelled |
| `failed` | Booking failed (check error codes) |

## Error Handling

Common error codes:
- `rate_not_available` - Rate no longer available
- `insufficient_balance` - Payment issue
- `hotel_unavailable` - Hotel not available for dates
- `invalid_guest_data` - Guest information invalid

## Certification Process

1. Complete integration in sandbox environment
2. Fill APIv3 Certification Checklist
3. ETG team reviews (14-30 days)
4. Receive production access

## Support

- Email: apisupport@ratehawk.com
- Documentation: [Best Practices for APIv3](https://docs.emergingtravel.com)
