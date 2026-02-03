---
description: Integration workflow for ETG / RateHawk Hotel API
---

# ETG (RateHawk) API Integration Workflow

This workflow documents the integration with ETG (RateHawk) API v3 for hotel searching and booking.

## 1. Prerequisites

Ensure your `.env` file contains the correct API credentials.

**Sandbox (Test) Credentials:**
```env
ETG_API_KEY_ID=2849
ETG_API_KEY_SECRET=6fb86629-9d5e-45dc-a61f-178550170a4a
ETG_API_BASE_URL=https://api.worldota.net/api/b2b/v3
```

**Production Credentials:**
To go live, obtain production credentials from your RateHawk account manager and update the `.env` file.

## 2. Service Implementation

The core logic is located in `backend/services/etg_service.py`.

### Key Methods:

*   **Initialization**: `ETGApiService()` - Sets up Basic Auth using Key ID and Secret.
*   **Search**:
    *   `search_by_geo()`: Search hotels by latitude/longitude (used for "Near Me" or City search). (Endpoint 10)
    *   `search_by_hotels()`: Search by specific Hotel IDs. (Endpoint 9)
    *   `get_hotel_page()`: Get detailed rate data for a specific hotel. (Endpoint 14)
*   **Static Data**:
    *   `suggest()`: Autocomplete for destinations/hotels.
    *   `get_hotel_content()`: Get images, description, amenities. (Endpoint 8)
*   **Booking Flow**:
    *   `prebook()`: Validate price and availability before booking. (Endpoint 15)
    *   `create_booking()`: Create the booking order. (Endpoint 18)
    *   `finish_booking()`: Confirm payment and finalize booking. (Endpoint 19)

## 3. Testing the Integration

### Step 1: Verify Connectivity
Run the test script to verify credentials and basic connectivity.

```bash
cd backend
python test_etg_auth.py
```
*(Note: If `test_etg_auth.py` doesn't exist, you can create a simple script calling `etg_service.get_overview()`)*

### Step 2: Test Search
Perform a hotel search for a test city (e.g., "MOW" for Moscow in Sandbox).

```bash
# Example curl command for local API
curl -X POST http://localhost:5000/api/hotels/search \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Paris",
    "checkin": "2024-06-01",
    "checkout": "2024-06-03",
    "rooms": 1,
    "guests": 2
  }'
```

### Step 3: Test Booking Flow (Sandbox)
1.  **Search** -> Get `hotel_id`
2.  **Get Details** -> Get `book_hash` from a rate
3.  **Prebook** -> Verify `book_hash`
4.  **Book** -> Call booking endpoint

## 4. Troubleshooting

*   **Invalid Login Credentials**:
    *   Check if `ETG_API_KEY_ID` and `ETG_API_KEY_SECRET` are correct in `.env`.
    *   Ensure there are no leading/trailing spaces in the `.env` values.
    *   Verify you are hitting the correct Base URL (Sandbox vs Production).

*   **No Availability**:
    *   Sandbox environment has limited inventory. Try searching for major cities like "Rome", "Paris", or "Dubai".
    *   Dates must be in the future.

*   **Rate Hash Expired**:
    *   `book_hash` is temporary. If it expires, you must perform the search again.

## 5. Switching to Production

1.  Update `.env` with Production Credentials.
2.  Update `ETG_API_BASE_URL` to the production URL (usually `https://api.worldota.net/api/b2b/v3`).
3.  Restart the backend server.
