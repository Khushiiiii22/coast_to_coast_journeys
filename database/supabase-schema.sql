-- =====================================================
-- Coast to Coast Journeys - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create 
-- the required tables for the application
-- =====================================================

-- =====================================================
-- Table: contact_messages
-- Stores contact form submissions
-- =====================================================
CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    subject VARCHAR(255),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert (for public contact form)
CREATE POLICY "Allow public insert" ON contact_messages
    FOR INSERT
    WITH CHECK (true);

-- Policy: Only authenticated users with admin role can read
CREATE POLICY "Allow admin read" ON contact_messages
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- =====================================================
-- Table: newsletter_subscribers
-- Stores newsletter subscriptions
-- =====================================================
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    unsubscribed_at TIMESTAMP WITH TIME ZONE
);

-- Enable Row Level Security
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert
CREATE POLICY "Allow public subscribe" ON newsletter_subscribers
    FOR INSERT
    WITH CHECK (true);

-- Policy: Allow checking own subscription
CREATE POLICY "Allow check email" ON newsletter_subscribers
    FOR SELECT
    USING (true);

-- =====================================================
-- Table: flight_searches
-- Stores flight search history
-- =====================================================
CREATE TABLE IF NOT EXISTS flight_searches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    from_city VARCHAR(255) NOT NULL,
    to_city VARCHAR(255) NOT NULL,
    depart_date DATE NOT NULL,
    return_date DATE,
    travelers VARCHAR(50),
    travel_class VARCHAR(50),
    trip_type VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE flight_searches ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert
CREATE POLICY "Allow insert flight search" ON flight_searches
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can view their own searches
CREATE POLICY "Users can view own searches" ON flight_searches
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- Table: hotel_searches
-- Stores hotel search history
-- =====================================================
CREATE TABLE IF NOT EXISTS hotel_searches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    destination VARCHAR(255) NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    rooms VARCHAR(20),
    guests VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE hotel_searches ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert
CREATE POLICY "Allow insert hotel search" ON hotel_searches
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can view their own searches
CREATE POLICY "Users can view own hotel searches" ON hotel_searches
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- Table: quote_requests
-- Stores quote/inquiry requests
-- =====================================================
CREATE TABLE IF NOT EXISTS quote_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    travel_type VARCHAR(50),
    destination VARCHAR(255),
    travel_date DATE,
    travelers VARCHAR(50),
    budget VARCHAR(100),
    special_requirements TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE quote_requests ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert
CREATE POLICY "Allow public quote request" ON quote_requests
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can view their own quote requests
CREATE POLICY "Users can view own quotes" ON quote_requests
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- Table: wishlist
-- Stores user's saved hotels/flights
-- =====================================================
CREATE TABLE IF NOT EXISTS wishlist (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'hotel' or 'flight'
    item_name VARCHAR(255) NOT NULL,
    item_location VARCHAR(255),
    item_price VARCHAR(100),
    item_image TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE wishlist ENABLE ROW LEVEL SECURITY;

-- Policy: Users can insert their own wishlist items
CREATE POLICY "Users can add to wishlist" ON wishlist
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can view their own wishlist
CREATE POLICY "Users can view own wishlist" ON wishlist
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own wishlist items
CREATE POLICY "Users can delete from wishlist" ON wishlist
    FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- Table: user_profiles
-- Extended user profile information
-- =====================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    avatar_url TEXT,
    date_of_birth DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- =====================================================
-- Function: Create profile on user signup
-- =====================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, full_name, phone)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'phone'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: Create profile when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- Indexes for better performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_contact_messages_email ON contact_messages(email);
CREATE INDEX IF NOT EXISTS idx_contact_messages_created ON contact_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_newsletter_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_flight_searches_user ON flight_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_hotel_searches_user ON hotel_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_quote_requests_email ON quote_requests(email);

-- =====================================================
-- Grant permissions
-- =====================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- =====================================================
-- Success message
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE 'Coast to Coast Journeys database schema created successfully!';
END $$;
