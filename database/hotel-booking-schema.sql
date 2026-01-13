-- =====================================================
-- Coast to Coast Journeys - Hotel Booking Schema
-- Additional tables for ETG API integration
-- Run this SQL in your Supabase SQL Editor
-- =====================================================

-- =====================================================
-- Table: hotel_bookings
-- Stores hotel booking records
-- =====================================================
CREATE TABLE IF NOT EXISTS hotel_bookings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    partner_order_id VARCHAR(255) UNIQUE NOT NULL,
    etg_order_id VARCHAR(255),
    hotel_id VARCHAR(100) NOT NULL,
    hotel_name VARCHAR(500),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    rooms INTEGER NOT NULL DEFAULT 1,
    guests JSONB NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(50) DEFAULT 'pending',
    -- Status values: pending, created, processing, confirmed, failed, cancelled
    booking_response JSONB,
    cancellation_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE hotel_bookings ENABLE ROW LEVEL SECURITY;

-- Policy: Allow backend (service role) full access
CREATE POLICY "Service role full access" ON hotel_bookings
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Policy: Users can view their own bookings
CREATE POLICY "Users can view own bookings" ON hotel_bookings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Allow insert from backend
CREATE POLICY "Allow insert booking" ON hotel_bookings
    FOR INSERT
    WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_user ON hotel_bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_status ON hotel_bookings(status);
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_partner_order ON hotel_bookings(partner_order_id);
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_created ON hotel_bookings(created_at DESC);

-- =====================================================
-- Table: hotel_cache
-- Caches hotel static data from ETG
-- =====================================================
CREATE TABLE IF NOT EXISTS hotel_cache (
    hotel_id VARCHAR(100) PRIMARY KEY,
    hotel_data JSONB NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE hotel_cache ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read
CREATE POLICY "Allow public read hotel cache" ON hotel_cache
    FOR SELECT
    USING (true);

-- Policy: Allow backend to manage cache
CREATE POLICY "Allow service role manage cache" ON hotel_cache
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Index
CREATE INDEX IF NOT EXISTS idx_hotel_cache_updated ON hotel_cache(last_updated);

-- =====================================================
-- Table: hotel_search_history
-- Stores hotel search history for analytics
-- =====================================================
CREATE TABLE IF NOT EXISTS hotel_search_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    search_type VARCHAR(50) NOT NULL, -- 'region', 'geo', 'destination', 'hotels'
    search_params JSONB NOT NULL,
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE hotel_search_history ENABLE ROW LEVEL SECURITY;

-- Policy: Allow insert from backend
CREATE POLICY "Allow insert search history" ON hotel_search_history
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can view their own search history
CREATE POLICY "Users can view own search history" ON hotel_search_history
    FOR SELECT
    USING (auth.uid() = user_id OR user_id IS NULL);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_search_history_user ON hotel_search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created ON hotel_search_history(created_at DESC);

-- =====================================================
-- Table: regions
-- Stores ETG regions for autocomplete
-- =====================================================
CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country_code VARCHAR(10),
    region_type VARCHAR(50), -- 'city', 'airport', 'poi', 'island', etc.
    coordinates JSONB, -- {"latitude": 0.0, "longitude": 0.0}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE regions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read
CREATE POLICY "Allow public read regions" ON regions
    FOR SELECT
    USING (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_regions_name ON regions(name);
CREATE INDEX IF NOT EXISTS idx_regions_name_search ON regions USING gin(to_tsvector('simple', name));
CREATE INDEX IF NOT EXISTS idx_regions_country ON regions(country_code);

-- =====================================================
-- Function: Update updated_at timestamp
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update hotel_bookings updated_at
DROP TRIGGER IF EXISTS update_hotel_bookings_updated_at ON hotel_bookings;
CREATE TRIGGER update_hotel_bookings_updated_at
    BEFORE UPDATE ON hotel_bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Sample regions data for India (insert initial data)
-- You should import full region data from ETG dump
-- =====================================================
INSERT INTO regions (id, name, country_code, region_type) VALUES
    (6308855, 'New Delhi', 'IN', 'city'),
    (6308873, 'Mumbai', 'IN', 'city'),
    (6308879, 'Bangalore', 'IN', 'city'),
    (6050530, 'Goa', 'IN', 'state'),
    (6054412, 'Jaipur', 'IN', 'city'),
    (6057034, 'Udaipur', 'IN', 'city'),
    (6054466, 'Agra', 'IN', 'city'),
    (6054468, 'Varanasi', 'IN', 'city'),
    (6057040, 'Shimla', 'IN', 'city'),
    (6057042, 'Manali', 'IN', 'city'),
    (2114, 'Dubai', 'AE', 'city'),
    (70, 'Singapore', 'SG', 'city'),
    (2734, 'Bangkok', 'TH', 'city'),
    (3270, 'Paris', 'FR', 'city'),
    (2196, 'London', 'GB', 'city')
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Grant permissions
-- =====================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON hotel_bookings TO anon, authenticated, service_role;
GRANT ALL ON hotel_cache TO anon, authenticated, service_role;
GRANT ALL ON hotel_search_history TO anon, authenticated, service_role;
GRANT ALL ON regions TO anon, authenticated, service_role;

-- =====================================================
-- Success message
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE 'Hotel booking schema created successfully!';
END $$;
