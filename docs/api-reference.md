# API Reference

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication for most endpoints. User-specific endpoints use Supabase user IDs.

---

## Health & Info

### GET /api/health

Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "service": "Coast to Coast Journeys API",
    "version": "1.0.0"
}
```

### GET /api

API information and available endpoints.

---

## Hotel Search

### POST /api/hotels/search/destination

Search hotels by destination name (geocodes automatically).

**Request Body:**
```json
{
    "destination": "Goa, India",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2,
    "children_ages": [5, 8],
    "radius": 10000,
    "currency": "INR"
}
```

**Response:**
```json
{
    "success": true,
    "location": {
        "latitude": 15.2993,
        "longitude": 74.1240,
        "formatted_address": "Goa, India"
    },
    "data": {
        "hotels": [...],
        "search_id": "abc123"
    }
}
```

### POST /api/hotels/search/region

Search hotels by ETG region ID.

**Request Body:**
```json
{
    "region_id": 6050530,
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2,
    "currency": "INR"
}
```

### POST /api/hotels/search/geo

Search hotels by coordinates.

**Request Body:**
```json
{
    "latitude": 15.2993,
    "longitude": 74.1240,
    "radius": 5000,
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2
}
```

---

## Hotel Details

### POST /api/hotels/details

Get detailed hotel information with all room rates.

**Request Body:**
```json
{
    "hotel_id": "hotel_123456",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2,
    "children_ages": []
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "hotel_123456",
        "name": "The Leela Palace",
        "star_rating": 5,
        "images": [...],
        "rates": [
            {
                "book_hash": "h1234...",
                "room_name": "Deluxe Room",
                "meal_plan": "Breakfast included",
                "price": 15999.00,
                "currency": "INR"
            }
        ]
    }
}
```

### GET /api/hotels/info/{hotel_id}

Get static hotel information (cached).

---

## Prebooking

### POST /api/hotels/prebook

Check rate availability and get final price.

**Request Body:**
```json
{
    "book_hash": "h1234567890abcdef...",
    "price_increase_percent": 5
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "hotel_id": "hotel_123456",
        "book_hash": "h1234567890abcdef...",
        "price_changed": false,
        "new_price": 15999.00,
        "original_price": 15999.00
    }
}
```

---

## Booking

### POST /api/hotels/book

Create a new booking.

**Request Body:**
```json
{
    "book_hash": "h1234567890abcdef...",
    "guests": [
        {"first_name": "John", "last_name": "Doe"},
        {"first_name": "Jane", "last_name": "Doe"}
    ],
    "user_id": "uuid-optional",
    "hotel_id": "hotel_123456",
    "hotel_name": "The Leela Palace",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "total_amount": 15999.00,
    "currency": "INR"
}
```

**Response:**
```json
{
    "success": true,
    "partner_order_id": "CTC-20260113-ABC12345",
    "booking_id": "uuid",
    "etg_response": {...}
}
```

### POST /api/hotels/book/finish

Finalize the booking.

**Request Body:**
```json
{
    "partner_order_id": "CTC-20260113-ABC12345"
}
```

### POST /api/hotels/book/status

Check booking status (manual polling).

**Request Body:**
```json
{
    "partner_order_id": "CTC-20260113-ABC12345"
}
```

### POST /api/hotels/book/poll

Poll booking status until final (recommended).

Automatically polls every 2.5 seconds until confirmed/failed.

**Request Body:**
```json
{
    "partner_order_id": "CTC-20260113-ABC12345"
}
```

**Response:**
```json
{
    "success": true,
    "status": "confirmed",
    "data": {
        "order_id": "ETG123456",
        "confirmation_number": "CONF789"
    }
}
```

---

## Post-Booking

### GET /api/hotels/booking/{partner_order_id}

Get booking details.

### POST /api/hotels/booking/cancel

Cancel a booking.

**Request Body:**
```json
{
    "partner_order_id": "CTC-20260113-ABC12345"
}
```

### GET /api/hotels/user/{user_id}/bookings

Get all bookings for a user.

---

## Maps

### POST /api/maps/geocode

Convert address to coordinates.

**Request Body:**
```json
{
    "address": "Taj Mahal, Agra, India"
}
```

### POST /api/maps/reverse-geocode

Convert coordinates to address.

**Request Body:**
```json
{
    "latitude": 27.1751,
    "longitude": 78.0421
}
```

### POST /api/maps/search

Search for places.

**Request Body:**
```json
{
    "query": "hotels in Goa",
    "latitude": 15.2993,
    "longitude": 74.1240,
    "radius": 10000,
    "type": "lodging"
}
```

### GET /api/maps/place/{place_id}

Get place details.

### POST /api/maps/distance

Calculate distance between locations.

**Request Body:**
```json
{
    "origin": "Delhi Airport",
    "destination": "The Leela Palace, Delhi",
    "mode": "driving"
}
```

### GET /api/maps/static-map

Get static map URL.

**Query Params:**
- `latitude` (required)
- `longitude` (required)
- `zoom` (optional, default: 15)
- `size` (optional, default: 600x300)

---

## Error Responses

All endpoints return errors in this format:

```json
{
    "success": false,
    "error": "Error message description",
    "status_code": 400
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (missing/invalid params) |
| 404 | Not Found |
| 408 | Timeout |
| 500 | Internal Server Error |
