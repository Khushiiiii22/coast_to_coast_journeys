# Coast to Coast Journeys

A full-stack hotel booking platform built with Flask backend and vanilla JavaScript frontend, integrated with ETG/RateHawk API v3 for real-time hotel search and booking capabilities.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Coast to Coast Journeys is a production-grade travel booking platform that enables users to:

- Search for hotels by destination, region, or geographic coordinates
- View detailed hotel information including room types, amenities, and pricing
- Book hotel rooms with real-time availability verification
- Manage bookings with confirmation tracking

The platform follows ETG API v3 certification guidelines for hotel booking integrations.

---

## Features

### Frontend
- Responsive homepage with hotel search functionality
- Location autocomplete using Google Maps API
- Hotel search results with filtering options
- Detailed hotel pages with room selection
- Booking form with guest information capture
- Booking confirmation page with order details

### Backend
- RESTful API built with Flask
- ETG/RateHawk API v3 integration for hotel data
- Google Maps integration for geocoding and location search
- Supabase integration for data persistence
- Comprehensive error handling and logging

### Security
- Environment-based configuration management
- API credentials stored securely in environment variables
- Row-level security policies in database
- CORS configuration for frontend-backend communication

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.x, Flask 3.0 |
| Database | Supabase (PostgreSQL) |
| Hotel API | ETG/RateHawk API v3 |
| Maps API | Google Maps Platform |
| Authentication | Supabase Auth |

---

## Project Structure

```
coast_to_coast_journeys/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── hotel_routes.py    # Hotel API endpoints
│   │   └── maps_routes.py     # Maps API endpoints
│   └── services/
│       ├── __init__.py
│       ├── etg_service.py     # ETG API integration
│       ├── google_maps_service.py  # Google Maps integration
│       └── supabase_service.py     # Database operations
├── css/
│   ├── style.css              # Main stylesheet
│   └── hotel-booking.css      # Booking page styles
├── js/
│   ├── main.js                # Homepage functionality
│   ├── hotel-api.js           # API client library
│   ├── hotel-results.js       # Search results page
│   ├── hotel-details.js       # Hotel details page
│   └── hotel-booking.js       # Booking form handling
├── database/
│   ├── hotel-booking-schema.sql  # Booking tables schema
│   └── supabase-schema.sql       # Base schema
├── docs/
│   ├── api-reference.md       # API documentation
│   ├── backend-setup.md       # Backend setup guide
│   ├── etg-api-integration.md # ETG integration guide
│   └── google-maps-integration.md  # Maps integration guide
├── index.html                 # Homepage
├── hotel-results.html         # Search results page
├── hotel-details.html         # Hotel details page
├── hotel-booking.html         # Booking form page
├── booking-confirmation.html  # Confirmation page
├── .env.example               # Environment variables template
└── .gitignore                 # Git ignore rules
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js (optional, for frontend tooling)
- Supabase account
- ETG/RateHawk API credentials
- Google Maps API key

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/Khushiiiii22/coast_to_coast_journeys.git
cd coast_to_coast_journeys
```

2. Create and activate a Python virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment configuration:
```bash
cd ..
cp .env.example .env
```

5. Edit `.env` with your API credentials (see Configuration section).

6. Run the database migrations in Supabase SQL Editor:
   - Execute `database/supabase-schema.sql`
   - Execute `database/hotel-booking-schema.sql`

7. Start the development server:
```bash
cd backend
python app.py
```

The application will be available at `http://localhost:5000`.

---

## Configuration

Create a `.env` file in the project root with the following variables:

```
# ETG/RateHawk API
ETG_API_KEY_ID=your_key_id
ETG_API_KEY_SECRET=your_key_secret
ETG_API_BASE_URL=https://api.worldota.net/api/b2b/v3

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Google Maps
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your_secret_key

# Server
HOST=0.0.0.0
PORT=5000
```

---

## API Documentation

### Health Check
```
GET /api/health
Response: { "status": "healthy", "service": "Coast to Coast Journeys API", "version": "1.0.0" }
```

### Hotel Search by Region
```
POST /api/hotels/search/region
Body: {
  "checkin": "2026-02-01",
  "checkout": "2026-02-03",
  "adults": 2,
  "children": 0,
  "region_id": 6308855
}
```

### Hotel Details
```
POST /api/hotels/details
Body: {
  "hotel_id": "hotel_123",
  "checkin": "2026-02-01",
  "checkout": "2026-02-03",
  "adults": 2
}
```

### Prebook Rate
```
POST /api/hotels/prebook
Body: {
  "book_hash": "hash_from_hotel_details"
}
```

### Create Booking
```
POST /api/hotels/book
Body: {
  "book_hash": "hash_from_prebook",
  "guests": [{"first_name": "John", "last_name": "Doe"}]
}
```

For complete API documentation, see `docs/api-reference.md`.

---

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `hotel_bookings` | Stores booking records and status |
| `hotel_cache` | Caches hotel static data from ETG |
| `hotel_search_history` | Analytics for search queries |
| `regions` | Location data for autocomplete |

### Row Level Security

- Users can only view their own bookings
- Service role has full access for backend operations
- Public read access for cached hotel data

---

## Testing

### Backend Health Check
```bash
curl http://localhost:5000/api/health
```

### API Endpoints List
```bash
curl http://localhost:5000/api
```

### Manual Testing
1. Navigate to `http://localhost:5000`
2. Search for hotels in a destination
3. Select a hotel and view details
4. Choose a room and proceed to booking
5. Fill guest details and confirm

---

## Deployment

### Production Considerations

1. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
2. Use a production WSGI server (Gunicorn is included)
3. Configure CORS to allow only your domain
4. Ensure HTTPS is enabled
5. Set strong `FLASK_SECRET_KEY`

### Running with Gunicorn
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ETG API Certification Workflow

This integration follows the official ETG/RateHawk API v3 certification process:

1. **Static Data** - Download hotel information dump
2. **Search (SERP)** - Search available hotels by region/geo/hotel IDs
3. **Hotel Page (HP)** - Get detailed hotel information with rates
4. **Prebook** - Verify rate availability and final pricing
5. **Create Booking** - Submit booking request with guest details
6. **Finish Booking** - Finalize the booking process
7. **Check Status** - Poll for booking confirmation
8. **Post-Booking** - Retrieve booking info or cancel if needed

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## License

This project is proprietary software developed for Coast to Coast Journeys.

---

## Contact

For support or inquiries, contact: info@coasttocoastjourneys.com
