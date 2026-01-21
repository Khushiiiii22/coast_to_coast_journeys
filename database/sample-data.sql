-- =====================================================
-- Coast to Coast Journeys - Sample Data for Demo
-- Run this after creating the schema
-- =====================================================

-- =====================================================
-- Insert Sample Admin User
-- Note: You need to first create this user in Supabase Auth
-- Email: admin@ctcjourneys.com, Password: Admin@123
-- =====================================================
-- After creating the auth user, get their UUID and run:
-- INSERT INTO admin_users (user_id, username, full_name, email, role)
-- VALUES ('YOUR_AUTH_USER_UUID', 'admin', 'Super Admin', 'admin@ctcjourneys.com', 'super_admin');

-- =====================================================
-- Insert Sample Customers
-- =====================================================
INSERT INTO customers (user_id, full_name, email, phone, city, customer_type, total_bookings, total_spent)
VALUES 
    (NULL, 'Rajesh Kumar', 'rajesh.kumar@email.com', '+91 98765 43210', 'New Delhi', 'regular', 5, 125000),
    (NULL, 'Priya Sharma', 'priya.sharma@email.com', '+91 87654 32109', 'Mumbai', 'regular', 3, 89000),
    (NULL, 'Mohammed Ali', 'mohammed.ali@email.com', '+91 99887 76655', 'Chennai', 'corporate', 12, 450000),
    (NULL, 'Anita Desai', 'anita.desai@email.com', '+91 95678 12345', 'Bangalore', 'regular', 2, 45000),
    (NULL, 'Vikram Mehta', 'vikram.mehta@email.com', '+91 88776 54321', 'Pune', 'vip', 18, 780000),
    (NULL, 'Suresh Patel', 'suresh.patel@email.com', '+91 91234 56789', 'Hyderabad', 'regular', 4, 95000),
    (NULL, 'Neha Gupta', 'neha.gupta@email.com', '+91 92345 67890', 'Jaipur', 'regular', 1, 28000),
    (NULL, 'Amit Singh', 'amit.singh@email.com', '+91 93456 78901', 'Kolkata', 'corporate', 8, 320000)
ON CONFLICT DO NOTHING;

-- =====================================================
-- Insert Sample Hotel Bookings
-- =====================================================
INSERT INTO hotel_bookings (
    partner_order_id, hotel_id, hotel_name, hotel_city, hotel_country,
    check_in, check_out, rooms, guests, room_type, meal_plan,
    base_price, markup_amount, total_amount, currency, status, payment_status,
    booking_source, created_at
)
VALUES 
    ('HTL-50001', 'leela-goa-001', 'The Leela Goa', 'Goa', 'India', 
     CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '8 days', 2, 
     '[{"name": "Rajesh Kumar", "type": "adult"}, {"name": "Meera Kumar", "type": "adult"}]'::jsonb,
     'Deluxe Sea View', 'Breakfast Included',
     35000, 6300, 41300, 'INR', 'confirmed', 'paid', 'website', NOW() - INTERVAL '2 days'),
     
    ('HTL-50002', 'taj-mumbai-001', 'Taj Mahal Palace', 'Mumbai', 'India',
     CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '12 days', 1,
     '[{"name": "Priya Sharma", "type": "adult"}]'::jsonb,
     'Heritage Room', 'Breakfast & Dinner',
     28000, 4200, 32200, 'INR', 'confirmed', 'paid', 'website', NOW() - INTERVAL '1 day'),
     
    ('HTL-50003', 'oberoi-udaipur-001', 'Oberoi Udaivilas', 'Udaipur', 'India',
     CURRENT_DATE + INTERVAL '15 days', CURRENT_DATE + INTERVAL '18 days', 1,
     '[{"name": "Mohammed Ali", "type": "adult"}, {"name": "Fatima Ali", "type": "adult"}]'::jsonb,
     'Premier Lake View Room', 'All Meals',
     65000, 11700, 76700, 'INR', 'pending', 'pending', 'admin', NOW() - INTERVAL '12 hours'),
     
    ('HTL-50004', 'itc-delhi-001', 'ITC Maurya', 'New Delhi', 'India',
     CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE, 1,
     '[{"name": "Vikram Mehta", "type": "adult"}]'::jsonb,
     'Executive Suite', 'Breakfast Included',
     18000, 2700, 20700, 'INR', 'confirmed', 'paid', 'mobile', NOW() - INTERVAL '5 days'),
     
    ('HTL-50005', 'marriott-bangalore-001', 'JW Marriott Bangalore', 'Bangalore', 'India',
     CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '9 days', 2,
     '[{"name": "Anita Desai", "type": "adult"}, {"name": "Rahul Desai", "type": "adult"}, {"name": "Arjun Desai", "type": "child"}]'::jsonb,
     'Premium Room', 'Room Only',
     22000, 3300, 25300, 'INR', 'cancelled', 'refunded', 'website', NOW() - INTERVAL '3 days'),
     
    ('HTL-50006', 'hyatt-chennai-001', 'Grand Hyatt Chennai', 'Chennai', 'India',
     CURRENT_DATE + INTERVAL '20 days', CURRENT_DATE + INTERVAL '22 days', 1,
     '[{"name": "Suresh Patel", "type": "adult"}]'::jsonb,
     'Grand Room', 'Breakfast Included',
     15000, 2250, 17250, 'INR', 'processing', 'paid', 'website', NOW() - INTERVAL '6 hours')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Insert Sample Flight Bookings
-- =====================================================
INSERT INTO flight_bookings (
    booking_id, flight_type, trip_type,
    origin_code, origin_city, destination_code, destination_city,
    airline_code, airline_name, flight_number,
    departure_datetime, arrival_datetime, duration_minutes, stops, cabin_class,
    passengers, total_passengers, pnr, supplier_name,
    base_fare, taxes_fees, markup_amount, total_amount, currency,
    status, payment_status, booking_source, created_at
)
VALUES 
    ('FLT-50001', 'one_way', 'domestic',
     'DEL', 'New Delhi', 'BOM', 'Mumbai',
     '6E', 'IndiGo', '6E-2158',
     NOW() + INTERVAL '5 days' + INTERVAL '6 hours 30 minutes',
     NOW() + INTERVAL '5 days' + INTERVAL '8 hours 45 minutes',
     135, 0, 'economy',
     '[{"name": "Rajesh Kumar", "type": "adult", "seat": "14A"}]'::jsonb, 1,
     'ABC123', 'TBO',
     6500, 1150, 850, 8500, 'INR',
     'confirmed', 'paid', 'website', NOW() - INTERVAL '3 days'),
     
    ('FLT-50002', 'one_way', 'domestic',
     'BLR', 'Bangalore', 'DEL', 'New Delhi',
     'AI', 'Air India', 'AI-505',
     NOW() + INTERVAL '6 days' + INTERVAL '10 hours 15 minutes',
     NOW() + INTERVAL '6 days' + INTERVAL '12 hours 45 minutes',
     150, 0, 'business',
     '[{"name": "Priya Sharma", "type": "adult", "seat": "2B"}]'::jsonb, 1,
     'XYZ789', 'TBO',
     10500, 1800, 1230, 12300, 'INR',
     'confirmed', 'paid', 'website', NOW() - INTERVAL '2 days'),
     
    ('FLT-50003', 'one_way', 'international',
     'MAA', 'Chennai', 'DXB', 'Dubai',
     'EK', 'Emirates', 'EK-545',
     NOW() + INTERVAL '8 days' + INTERVAL '14 hours',
     NOW() + INTERVAL '8 days' + INTERVAL '18 hours 30 minutes',
     270, 0, 'economy',
     '[{"name": "Mohammed Ali", "type": "adult", "seat": "22F"}]'::jsonb, 1,
     'EK7H2P', 'DirectAPI',
     24000, 4500, 2850, 28500, 'INR',
     'pending', 'pending', 'admin', NOW() - INTERVAL '1 day'),
     
    ('FLT-50004', 'one_way', 'domestic',
     'DEL', 'New Delhi', 'GOI', 'Goa',
     'UK', 'Vistara', 'UK-857',
     NOW() + INTERVAL '10 days' + INTERVAL '8 hours',
     NOW() + INTERVAL '10 days' + INTERVAL '10 hours 30 minutes',
     150, 0, 'premium_economy',
     '[{"name": "Anita Desai", "type": "adult", "seat": "8C"}]'::jsonb, 1,
     'VT4K9L', 'TBO',
     8200, 1600, 980, 9800, 'INR',
     'cancelled', 'refunded', 'website', NOW() - INTERVAL '4 days'),
     
    ('FLT-50005', 'round_trip', 'international',
     'BOM', 'Mumbai', 'SIN', 'Singapore',
     'SQ', 'Singapore Airlines', 'SQ-423',
     NOW() + INTERVAL '12 days' + INTERVAL '7 hours',
     NOW() + INTERVAL '12 days' + INTERVAL '14 hours',
     420, 0, 'business',
     '[{"name": "Vikram Mehta", "type": "adult", "seat": "4A"}, {"name": "Sunita Mehta", "type": "adult", "seat": "4B"}]'::jsonb, 2,
     'SQ8F3M', 'DirectAPI',
     72000, 14400, 8640, 86400, 'INR',
     'confirmed', 'paid', 'website', NOW() - INTERVAL '5 days'),
     
    ('FLT-50006', 'one_way', 'domestic',
     'HYD', 'Hyderabad', 'CCU', 'Kolkata',
     'SG', 'SpiceJet', 'SG-245',
     NOW() + INTERVAL '3 days' + INTERVAL '11 hours 30 minutes',
     NOW() + INTERVAL '3 days' + INTERVAL '14 hours',
     150, 0, 'economy',
     '[{"name": "Suresh Patel", "type": "adult", "seat": "18D"}]'::jsonb, 1,
     'SJ2N8P', 'TBO',
     4500, 1100, 560, 5600, 'INR',
     'processing', 'paid', 'website', NOW() - INTERVAL '8 hours'),
     
    ('FLT-50007', 'one_way', 'domestic',
     'DEL', 'New Delhi', 'JAI', 'Jaipur',
     '6E', 'IndiGo', '6E-678',
     NOW() + INTERVAL '2 days' + INTERVAL '9 hours',
     NOW() + INTERVAL '2 days' + INTERVAL '10 hours',
     60, 0, 'economy',
     '[{"name": "Neha Gupta", "type": "adult", "seat": "12A"}]'::jsonb, 1,
     'IG3M5N', 'TBO',
     3200, 650, 400, 4250, 'INR',
     'confirmed', 'paid', 'website', NOW() - INTERVAL '10 hours'),
     
    ('FLT-50008', 'round_trip', 'domestic',
     'CCU', 'Kolkata', 'DEL', 'New Delhi',
     'AI', 'Air India', 'AI-780',
     NOW() + INTERVAL '7 days' + INTERVAL '6 hours',
     NOW() + INTERVAL '7 days' + INTERVAL '8 hours 30 minutes',
     150, 0, 'economy',
     '[{"name": "Amit Singh", "type": "adult", "seat": "16C"}]'::jsonb, 1,
     'AI5K9R', 'TBO',
     9800, 1800, 1160, 12760, 'INR',
     'confirmed', 'paid', 'mobile', NOW() - INTERVAL '15 hours')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Insert Sample Payments
-- =====================================================
INSERT INTO payments (
    payment_id, order_id, booking_type, amount, currency,
    payment_gateway, payment_method, status, created_at
)
VALUES 
    ('PAY-10000001', 'HTL-50001', 'hotel', 41300, 'INR', 'razorpay', 'card', 'captured', NOW() - INTERVAL '2 days'),
    ('PAY-10000002', 'HTL-50002', 'hotel', 32200, 'INR', 'razorpay', 'upi', 'captured', NOW() - INTERVAL '1 day'),
    ('PAY-10000003', 'HTL-50004', 'hotel', 20700, 'INR', 'razorpay', 'netbanking', 'captured', NOW() - INTERVAL '5 days'),
    ('PAY-10000004', 'HTL-50006', 'hotel', 17250, 'INR', 'razorpay', 'card', 'captured', NOW() - INTERVAL '6 hours'),
    ('PAY-10000005', 'FLT-50001', 'flight', 8500, 'INR', 'razorpay', 'upi', 'captured', NOW() - INTERVAL '3 days'),
    ('PAY-10000006', 'FLT-50002', 'flight', 12300, 'INR', 'razorpay', 'card', 'captured', NOW() - INTERVAL '2 days'),
    ('PAY-10000007', 'FLT-50005', 'flight', 86400, 'INR', 'razorpay', 'card', 'captured', NOW() - INTERVAL '5 days'),
    ('PAY-10000008', 'FLT-50006', 'flight', 5600, 'INR', 'razorpay', 'upi', 'captured', NOW() - INTERVAL '8 hours'),
    ('PAY-10000009', 'FLT-50007', 'flight', 4250, 'INR', 'razorpay', 'upi', 'captured', NOW() - INTERVAL '10 hours'),
    ('PAY-10000010', 'FLT-50008', 'flight', 12760, 'INR', 'razorpay', 'netbanking', 'captured', NOW() - INTERVAL '15 hours'),
    ('PAY-10000011', 'HTL-50005', 'hotel', 25300, 'INR', 'razorpay', 'card', 'refunded', NOW() - INTERVAL '3 days'),
    ('PAY-10000012', 'FLT-50004', 'flight', 9800, 'INR', 'razorpay', 'card', 'refunded', NOW() - INTERVAL '4 days')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Insert Sample Activity Logs
-- =====================================================
INSERT INTO activity_logs (action, entity_type, details, created_at)
VALUES 
    ('login', 'auth', 'Admin logged in successfully', NOW() - INTERVAL '2 hours'),
    ('create', 'hotel_booking', 'Created hotel booking HTL-50006', NOW() - INTERVAL '6 hours'),
    ('update', 'flight_booking', 'Updated flight booking FLT-50003 status to pending', NOW() - INTERVAL '1 day'),
    ('create', 'customer', 'New customer registration: Neha Gupta', NOW() - INTERVAL '10 hours'),
    ('view', 'report', 'Generated monthly revenue report', NOW() - INTERVAL '3 hours'),
    ('update', 'settings', 'Updated markup rules', NOW() - INTERVAL '1 day'),
    ('login', 'auth', 'Admin logged in successfully', NOW() - INTERVAL '1 day'),
    ('create', 'flight_booking', 'Created flight booking FLT-50007', NOW() - INTERVAL '10 hours')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Update customer booking counts (if customers have IDs)
-- =====================================================
-- This would be done via triggers in production

-- =====================================================
-- Success message
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE 'Sample data inserted successfully!';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '- 8 sample customers';
    RAISE NOTICE '- 6 sample hotel bookings';
    RAISE NOTICE '- 8 sample flight bookings';
    RAISE NOTICE '- 12 sample payments';
    RAISE NOTICE '- 8 sample activity logs';
END $$;
