-- =====================================================
-- Coast to Coast Journeys - Complete Database Schema
-- Version 2.0 - With Admin Users & Flight Bookings
-- Run this SQL in your Supabase SQL Editor
-- =====================================================

-- =====================================================
-- Table: admin_users
-- Stores admin user accounts with roles
-- =====================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'staff',
    -- Roles: super_admin, admin, operations, sales, finance, support, readonly
    permissions JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can view all admin users
CREATE POLICY "Admin users can view admins" ON admin_users
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Policy: Super admins can manage admin users
CREATE POLICY "Super admins can manage" ON admin_users
    FOR ALL
    USING (EXISTS (
        SELECT 1 FROM admin_users 
        WHERE user_id = auth.uid() AND role = 'super_admin'
    ));

-- Insert default admin user (password: admin - user must exist in auth.users)
-- This is a placeholder - you'll need to create the auth user first
-- INSERT INTO admin_users (username, full_name, email, role) 
-- VALUES ('admin', 'Super Admin', 'admin@ctcjourneys.com', 'super_admin');

-- =====================================================
-- Table: customers
-- Stores customer accounts (extends auth.users)
-- =====================================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    nationality VARCHAR(100) DEFAULT 'Indian',
    passport_number VARCHAR(50),
    passport_expiry DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    pincode VARCHAR(20),
    customer_type VARCHAR(50) DEFAULT 'regular',
    -- Types: regular, corporate, vip, agent
    loyalty_points INTEGER DEFAULT 0,
    total_bookings INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_booking_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy: Customers can view their own data
CREATE POLICY "Customers can view own data" ON customers
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Customers can update their own data
CREATE POLICY "Customers can update own data" ON customers
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Allow insert on signup
CREATE POLICY "Allow customer insert" ON customers
    FOR INSERT
    WITH CHECK (true);

-- Policy: Admins can view all customers
CREATE POLICY "Admins can view all customers" ON customers
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- =====================================================
-- Table: flight_bookings
-- Stores flight booking records
-- =====================================================
CREATE TABLE IF NOT EXISTS flight_bookings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    booking_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Flight Details
    flight_type VARCHAR(20) NOT NULL, -- one_way, round_trip, multi_city
    trip_type VARCHAR(20) DEFAULT 'domestic', -- domestic, international
    
    -- Outbound Flight
    origin_code VARCHAR(10) NOT NULL,
    origin_city VARCHAR(100) NOT NULL,
    destination_code VARCHAR(10) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    airline_code VARCHAR(10) NOT NULL,
    airline_name VARCHAR(100) NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    departure_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    arrival_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER,
    stops INTEGER DEFAULT 0,
    cabin_class VARCHAR(50) DEFAULT 'economy',
    
    -- Return Flight (for round trips)
    return_flight_number VARCHAR(20),
    return_departure_datetime TIMESTAMP WITH TIME ZONE,
    return_arrival_datetime TIMESTAMP WITH TIME ZONE,
    
    -- Passenger Details
    passengers JSONB NOT NULL,
    -- Structure: [{name, type, age, seat, meal, baggage}]
    total_passengers INTEGER DEFAULT 1,
    
    -- Booking Reference
    pnr VARCHAR(20),
    supplier_pnr VARCHAR(50),
    supplier_name VARCHAR(100),
    
    -- Pricing
    base_fare DECIMAL(12,2) NOT NULL,
    taxes_fees DECIMAL(12,2) DEFAULT 0,
    markup_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, confirmed, ticketed, cancelled, failed, refunded
    payment_status VARCHAR(50) DEFAULT 'pending',
    -- Payment: pending, paid, failed, refunded, partial
    
    -- Payment Info
    payment_method VARCHAR(50),
    payment_id VARCHAR(100),
    payment_gateway VARCHAR(50),
    
    -- Metadata
    booking_source VARCHAR(50) DEFAULT 'website',
    -- Source: website, mobile, admin, agent
    booked_by UUID REFERENCES auth.users(id),
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    -- Cancellation
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    refund_amount DECIMAL(12,2),
    refund_status VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE flight_bookings ENABLE ROW LEVEL SECURITY;

-- Policy: Customers can view their own bookings
CREATE POLICY "Customers can view own flight bookings" ON flight_bookings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Allow insert from backend
CREATE POLICY "Allow flight booking insert" ON flight_bookings
    FOR INSERT
    WITH CHECK (true);

-- Policy: Admins can view all bookings
CREATE POLICY "Admins can view all flight bookings" ON flight_bookings
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Policy: Admins can update bookings
CREATE POLICY "Admins can update flight bookings" ON flight_bookings
    FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Indexes
CREATE INDEX IF NOT EXISTS idx_flight_bookings_customer ON flight_bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_user ON flight_bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_status ON flight_bookings(status);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_booking_id ON flight_bookings(booking_id);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_pnr ON flight_bookings(pnr);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_created ON flight_bookings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_flight_bookings_departure ON flight_bookings(departure_datetime);

-- =====================================================
-- Update hotel_bookings table with additional fields
-- =====================================================
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES customers(id) ON DELETE SET NULL;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS booking_id VARCHAR(50);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS hotel_address TEXT;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS hotel_city VARCHAR(100);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS hotel_country VARCHAR(100);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS hotel_star_rating INTEGER;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS room_type VARCHAR(255);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS meal_plan VARCHAR(100);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS base_price DECIMAL(12,2);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS markup_amount DECIMAL(12,2) DEFAULT 0;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(12,2) DEFAULT 0;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS payment_id VARCHAR(100);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS booking_source VARCHAR(50) DEFAULT 'website';
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS booked_by UUID REFERENCES auth.users(id);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS special_requests TEXT;
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2);
ALTER TABLE hotel_bookings ADD COLUMN IF NOT EXISTS refund_status VARCHAR(50);

-- Update hotel_bookings index
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_customer ON hotel_bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_hotel_bookings_booking_id ON hotel_bookings(booking_id);

-- =====================================================
-- Table: markup_rules
-- Stores markup configuration
-- =====================================================
CREATE TABLE IF NOT EXISTS markup_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- global, city, hotel, airline, route
    apply_to VARCHAR(50) NOT NULL, -- hotel, flight, all
    target_value VARCHAR(255), -- city name, hotel id, airline code, etc.
    markup_type VARCHAR(20) NOT NULL, -- percentage, flat
    markup_value DECIMAL(10,2) NOT NULL,
    min_booking_value DECIMAL(12,2) DEFAULT 0,
    max_markup_value DECIMAL(12,2),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from DATE,
    valid_until DATE,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE markup_rules ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can manage markup rules
CREATE POLICY "Admins can manage markup rules" ON markup_rules
    FOR ALL
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Policy: Public can read active rules (for price calculation)
CREATE POLICY "Public can read active markup rules" ON markup_rules
    FOR SELECT
    USING (is_active = true);

-- Insert default markup rules
INSERT INTO markup_rules (rule_name, rule_type, apply_to, markup_type, markup_value, priority, is_active)
VALUES 
    ('Default Hotel Markup', 'global', 'hotel', 'percentage', 12.00, 0, true),
    ('Default Flight Markup', 'global', 'flight', 'percentage', 10.00, 0, true),
    ('Luxury Hotels Markup', 'global', 'hotel', 'percentage', 15.00, 1, true),
    ('Goa Hotels Special', 'city', 'hotel', 'percentage', 18.00, 2, true)
ON CONFLICT DO NOTHING;

-- =====================================================
-- Table: payments
-- Stores payment transactions
-- =====================================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    order_id VARCHAR(100),
    booking_type VARCHAR(20) NOT NULL, -- hotel, flight
    booking_id UUID,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    
    payment_gateway VARCHAR(50) NOT NULL, -- razorpay, stripe, etc.
    payment_method VARCHAR(50), -- card, upi, netbanking, wallet
    
    status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, authorized, captured, failed, refunded
    
    gateway_response JSONB,
    
    refund_id VARCHAR(100),
    refund_amount DECIMAL(12,2),
    refund_status VARCHAR(50),
    refunded_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Policy: Customers can view their own payments
CREATE POLICY "Customers can view own payments" ON payments
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Allow insert
CREATE POLICY "Allow payment insert" ON payments
    FOR INSERT
    WITH CHECK (true);

-- Policy: Admins can view all payments
CREATE POLICY "Admins can view all payments" ON payments
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Indexes
CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at DESC);

-- =====================================================
-- Table: activity_logs
-- Stores admin activity for audit
-- =====================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    admin_id UUID REFERENCES admin_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- booking, customer, payment, settings
    entity_id VARCHAR(100),
    details TEXT,
    metadata JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can view activity logs
CREATE POLICY "Admins can view activity logs" ON activity_logs
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid()
    ));

-- Policy: Allow insert
CREATE POLICY "Allow activity log insert" ON activity_logs
    FOR INSERT
    WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_admin ON activity_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created ON activity_logs(created_at DESC);

-- =====================================================
-- Table: system_settings
-- Stores system configuration
-- =====================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    category VARCHAR(50),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Public settings are readable
CREATE POLICY "Public can read public settings" ON system_settings
    FOR SELECT
    USING (is_public = true);

-- Policy: Admins can manage settings
CREATE POLICY "Admins can manage settings" ON system_settings
    FOR ALL
    USING (EXISTS (
        SELECT 1 FROM admin_users WHERE user_id = auth.uid() AND role IN ('super_admin', 'admin')
    ));

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, category, description, is_public)
VALUES 
    ('company_name', 'Coast to Coast Journeys', 'string', 'company', 'Company name', true),
    ('company_email', 'info@ctcjourneys.com', 'string', 'company', 'Contact email', true),
    ('company_phone', '+91 1800 123 4567', 'string', 'company', 'Contact phone', true),
    ('currency', 'INR', 'string', 'general', 'Default currency', true),
    ('timezone', 'Asia/Kolkata', 'string', 'general', 'Default timezone', true),
    ('maintenance_mode', 'false', 'boolean', 'system', 'Maintenance mode flag', false),
    ('auto_confirm_bookings', 'true', 'boolean', 'booking', 'Auto confirm paid bookings', false),
    ('send_confirmation_emails', 'true', 'boolean', 'booking', 'Send booking confirmation emails', false)
ON CONFLICT (setting_key) DO NOTHING;

-- =====================================================
-- Function: Generate booking ID
-- =====================================================
CREATE OR REPLACE FUNCTION generate_booking_id(prefix VARCHAR, table_name VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    next_num INTEGER;
    result VARCHAR;
BEGIN
    -- Get the next number based on count
    EXECUTE format('SELECT COALESCE(MAX(id), 0) + 1 FROM %I', table_name) INTO next_num;
    result := prefix || '-' || LPAD(next_num::text, 5, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Function: Check if user is admin
-- =====================================================
CREATE OR REPLACE FUNCTION is_admin(check_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM admin_users 
        WHERE user_id = check_user_id AND is_active = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- Function: Get user role
-- =====================================================
CREATE OR REPLACE FUNCTION get_user_role(check_user_id UUID)
RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR;
BEGIN
    SELECT role INTO user_role 
    FROM admin_users 
    WHERE user_id = check_user_id AND is_active = true;
    
    IF user_role IS NOT NULL THEN
        RETURN user_role;
    END IF;
    
    IF EXISTS (SELECT 1 FROM customers WHERE user_id = check_user_id) THEN
        RETURN 'customer';
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- Trigger: Auto-update updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all relevant tables
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN 
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name IN ('admin_users', 'customers', 'flight_bookings', 'hotel_bookings', 'markup_rules', 'payments', 'system_settings')
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at();
        ', t, t, t, t);
    END LOOP;
END $$;

-- =====================================================
-- View: Dashboard Stats
-- =====================================================
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM hotel_bookings WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as hotel_bookings_30d,
    (SELECT COUNT(*) FROM flight_bookings WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as flight_bookings_30d,
    (SELECT COUNT(*) FROM customers WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as new_customers_30d,
    (SELECT COALESCE(SUM(total_amount), 0) FROM hotel_bookings WHERE status = 'confirmed' AND created_at >= CURRENT_DATE - INTERVAL '30 days') as hotel_revenue_30d,
    (SELECT COALESCE(SUM(total_amount), 0) FROM flight_bookings WHERE status = 'confirmed' AND created_at >= CURRENT_DATE - INTERVAL '30 days') as flight_revenue_30d,
    (SELECT COUNT(*) FROM hotel_bookings WHERE status = 'confirmed') as confirmed_hotel_bookings,
    (SELECT COUNT(*) FROM flight_bookings WHERE status = 'confirmed') as confirmed_flight_bookings,
    (SELECT COUNT(*) FROM hotel_bookings WHERE status = 'pending') as pending_hotel_bookings,
    (SELECT COUNT(*) FROM flight_bookings WHERE status = 'pending') as pending_flight_bookings,
    (SELECT COUNT(*) FROM hotel_bookings WHERE status = 'cancelled') as cancelled_hotel_bookings,
    (SELECT COUNT(*) FROM flight_bookings WHERE status = 'cancelled') as cancelled_flight_bookings;

-- =====================================================
-- Grant permissions
-- =====================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated, service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated, service_role;

-- =====================================================
-- Success message
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE 'Complete database schema with admin users, customers, and flight bookings created successfully!';
END $$;
