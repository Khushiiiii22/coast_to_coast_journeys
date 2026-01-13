# Backend Setup Guide

## Overview

This guide explains how to set up and run the Flask backend for Coast to Coast Journeys.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Create Virtual Environment

```bash
cd /Users/khushi22/coasttocoast/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp ../.env.example ../.env
```

Edit `.env` with your credentials:
```env
ETG_API_KEY_ID=your_etg_key_id
ETG_API_KEY_SECRET=your_etg_key_secret
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### 4. Run Database Migrations

Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/bcxkjvjchutgfuyklphx/sql) and run:

1. `database/supabase-schema.sql` (if not already done)
2. `database/hotel-booking-schema.sql`

### 5. Start the Server

```bash
python app.py
```

Server will start at `http://localhost:5000`

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Search Hotels by Destination
```bash
curl -X POST http://localhost:5000/api/hotels/search/destination \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Goa, India",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2,
    "radius": 10000
  }'
```

### Get Hotel Details
```bash
curl -X POST http://localhost:5000/api/hotels/details \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "hotel_123456",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "adults": 2
  }'
```

### Prebook Rate
```bash
curl -X POST http://localhost:5000/api/hotels/prebook \
  -H "Content-Type: application/json" \
  -d '{
    "book_hash": "h1234567890abcdef",
    "price_increase_percent": 5
  }'
```

### Create Booking
```bash
curl -X POST http://localhost:5000/api/hotels/book \
  -H "Content-Type: application/json" \
  -d '{
    "book_hash": "h1234567890abcdef",
    "guests": [{"first_name": "John", "last_name": "Doe"}],
    "hotel_name": "The Leela Palace",
    "checkin": "2026-02-01",
    "checkout": "2026-02-05",
    "total_amount": 15000.00
  }'
```

### Finish and Poll Booking
```bash
curl -X POST http://localhost:5000/api/hotels/book/poll \
  -H "Content-Type: application/json" \
  -d '{
    "partner_order_id": "CTC-20260201-ABC12345"
  }'
```

### Cancel Booking
```bash
curl -X POST http://localhost:5000/api/hotels/booking/cancel \
  -H "Content-Type: application/json" \
  -d '{
    "partner_order_id": "CTC-20260201-ABC12345"
  }'
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── routes/
│   ├── __init__.py
│   ├── hotel_routes.py   # Hotel API endpoints
│   └── maps_routes.py    # Maps API endpoints
└── services/
    ├── __init__.py
    ├── etg_service.py        # ETG API integration
    ├── supabase_service.py   # Database operations
    └── google_maps_service.py # Maps integration
```

## Running in Production

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Activate venv, reinstall deps |
| CORS errors | Check CORS config in app.py |
| Database errors | Verify Supabase credentials |
| ETG API errors | Check API key, sandbox access |

## Next Steps

1. Get ETG API sandbox credentials
2. Get Google Maps API key
3. Run database migrations
4. Test endpoints with curl
5. Connect frontend to backend
