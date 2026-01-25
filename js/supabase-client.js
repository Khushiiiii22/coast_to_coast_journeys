/**
 * C2C Journeys - Supabase Client
 * Handles all database operations and authentication
 */

// Supabase Configuration
const SUPABASE_URL = 'https://bcxkjvjchutgfuyklphx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjeGtqdmpjaHV0Z2Z1eWtscGh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxOTQyNzAsImV4cCI6MjA4Mzc3MDI3MH0.qz5yreyBo5zD8x51leZDWHD6Ft_2JvutBrZF8yhjqJE';

// Initialize Supabase Client
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * =====================================================
 * Authentication Functions
 * =====================================================
 */

// Sign up new customer
// Sign up new customer
async function signUpCustomer(email, password, fullName, phone = null) {
    try {
        // Use backend API to create user with auto-confirmation
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
                phone
            })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to create account');
        }

        // Account created successfully (and confirmed). Now sign in.
        const { data: authData, error: authError } = await supabaseClient.auth.signInWithPassword({
            email,
            password
        });

        if (authError) throw authError;

        return { success: true, data: authData };
    } catch (error) {
        console.error('Sign up error:', error);
        return { success: false, error: error.message };
    }
}

// Sign in user (customer or admin)
async function signIn(email, password) {
    try {
        const { data, error } = await supabaseClient.auth.signInWithPassword({
            email,
            password
        });

        if (error) throw error;

        // Check if user is admin
        const userRole = await getUserRole(data.user.id);

        // Log activity
        await logActivity(data.user.id, 'login', 'auth', null, `User logged in: ${email}`);

        return {
            success: true,
            data: data,
            userRole: userRole,
            isAdmin: ['super_admin', 'admin', 'operations', 'sales', 'finance', 'support', 'readonly'].includes(userRole)
        };
    } catch (error) {
        console.error('Sign in error:', error);

        // Log failed attempt
        await logActivity(null, 'login_failed', 'auth', null, `Failed login attempt: ${email}`);

        return { success: false, error: error.message };
    }
}

// Sign in with Google
async function signInWithGoogle() {
    try {
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: {
                queryParams: {
                    access_type: 'offline',
                    prompt: 'consent',
                },
                redirectTo: window.location.origin + '/auth.html'
            }
        });

        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Google sign in error:', error);
        return { success: false, error: error.message };
    }
}

// Sign out
async function signOut() {
    try {
        const { data: { user } } = await supabaseClient.auth.getUser();

        if (user) {
            await logActivity(user.id, 'logout', 'auth', null, 'User logged out');
        }

        const { error } = await supabaseClient.auth.signOut();
        if (error) throw error;

        return { success: true };
    } catch (error) {
        console.error('Sign out error:', error);
        return { success: false, error: error.message };
    }
}

// Get current user
async function getCurrentUser() {
    try {
        const { data: { user }, error } = await supabaseClient.auth.getUser();
        if (error) throw error;
        return user;
    } catch (error) {
        return null;
    }
}

// Get current session
async function getSession() {
    try {
        const { data: { session }, error } = await supabaseClient.auth.getSession();
        if (error) throw error;
        return session;
    } catch (error) {
        return null;
    }
}

// Check if user is admin
async function isAdmin(userId = null) {
    try {
        if (!userId) {
            const user = await getCurrentUser();
            if (!user) return false;
            userId = user.id;
        }

        const { data, error } = await supabaseClient
            .from('admin_users')
            .select('id, role, is_active')
            .eq('user_id', userId)
            .eq('is_active', true)
            .single();

        return !!data;
    } catch (error) {
        return false;
    }
}

// Get user role
async function getUserRole(userId = null) {
    try {
        if (!userId) {
            const user = await getCurrentUser();
            if (!user) return null;
            userId = user.id;
        }

        // Check if admin
        const { data: adminData } = await supabaseClient
            .from('admin_users')
            .select('role')
            .eq('user_id', userId)
            .eq('is_active', true)
            .single();

        if (adminData) {
            return adminData.role;
        }

        // Check if customer
        const { data: customerData } = await supabaseClient
            .from('customers')
            .select('id')
            .eq('user_id', userId)
            .single();

        if (customerData) {
            return 'customer';
        }

        return null;
    } catch (error) {
        return null;
    }
}

// Get admin user details
async function getAdminDetails(userId = null) {
    try {
        if (!userId) {
            const user = await getCurrentUser();
            if (!user) return null;
            userId = user.id;
        }

        const { data, error } = await supabaseClient
            .from('admin_users')
            .select('*')
            .eq('user_id', userId)
            .single();

        if (error) throw error;
        return data;
    } catch (error) {
        return null;
    }
}

// Get customer details
async function getCustomerDetails(userId = null) {
    try {
        if (!userId) {
            const user = await getCurrentUser();
            if (!user) return null;
            userId = user.id;
        }

        const { data, error } = await supabaseClient
            .from('customers')
            .select('*')
            .eq('user_id', userId)
            .single();

        if (error) throw error;
        return data;
    } catch (error) {
        return null;
    }
}

/**
 * =====================================================
 * Hotel Booking Functions
 * =====================================================
 */

// Get all hotel bookings (admin)
async function getHotelBookings(filters = {}) {
    try {
        let query = supabaseClient
            .from('hotel_bookings')
            .select(`
                *,
                customers (full_name, email, phone)
            `)
            .order('created_at', { ascending: false });

        // Apply filters
        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.fromDate) {
            query = query.gte('check_in', filters.fromDate);
        }
        if (filters.toDate) {
            query = query.lte('check_in', filters.toDate);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get hotel bookings error:', error);
        return { success: false, error: error.message };
    }
}

// Create hotel booking
async function createHotelBooking(bookingData) {
    try {
        const user = await getCurrentUser();
        const bookingId = 'HTL-' + Date.now().toString().slice(-5) + Math.random().toString(36).substr(2, 4).toUpperCase();

        const { data, error } = await supabaseClient
            .from('hotel_bookings')
            .insert({
                ...bookingData,
                booking_id: bookingId,
                user_id: user?.id,
                partner_order_id: bookingId
            })
            .select()
            .single();

        if (error) throw error;

        // Log activity
        await logActivity(user?.id, 'create', 'hotel_booking', data.id, `Created hotel booking: ${bookingId}`);

        return { success: true, data };
    } catch (error) {
        console.error('Create hotel booking error:', error);
        return { success: false, error: error.message };
    }
}

// Update hotel booking status
async function updateHotelBookingStatus(bookingId, status) {
    try {
        const { data, error } = await supabaseClient
            .from('hotel_bookings')
            .update({ status, updated_at: new Date().toISOString() })
            .eq('id', bookingId)
            .select()
            .single();

        if (error) throw error;

        const user = await getCurrentUser();
        await logActivity(user?.id, 'update', 'hotel_booking', bookingId, `Updated status to: ${status}`);

        return { success: true, data };
    } catch (error) {
        console.error('Update hotel booking error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Flight Booking Functions
 * =====================================================
 */

// Get all flight bookings (admin)
async function getFlightBookings(filters = {}) {
    try {
        let query = supabaseClient
            .from('flight_bookings')
            .select(`
                *,
                customers (full_name, email, phone)
            `)
            .order('created_at', { ascending: false });

        // Apply filters
        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.tripType) {
            query = query.eq('trip_type', filters.tripType);
        }
        if (filters.airline) {
            query = query.eq('airline_code', filters.airline);
        }
        if (filters.fromDate) {
            query = query.gte('departure_datetime', filters.fromDate);
        }
        if (filters.toDate) {
            query = query.lte('departure_datetime', filters.toDate);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get flight bookings error:', error);
        return { success: false, error: error.message };
    }
}

// Create flight booking
async function createFlightBooking(bookingData) {
    try {
        const user = await getCurrentUser();
        const bookingId = 'FLT-' + Date.now().toString().slice(-5) + Math.random().toString(36).substr(2, 4).toUpperCase();
        const pnr = Math.random().toString(36).substr(2, 6).toUpperCase();

        const { data, error } = await supabaseClient
            .from('flight_bookings')
            .insert({
                ...bookingData,
                booking_id: bookingId,
                pnr: pnr,
                user_id: user?.id,
                booked_by: user?.id
            })
            .select()
            .single();

        if (error) throw error;

        // Log activity
        await logActivity(user?.id, 'create', 'flight_booking', data.id, `Created flight booking: ${bookingId}`);

        return { success: true, data };
    } catch (error) {
        console.error('Create flight booking error:', error);
        return { success: false, error: error.message };
    }
}

// Update flight booking status
async function updateFlightBookingStatus(bookingId, status) {
    try {
        const { data, error } = await supabaseClient
            .from('flight_bookings')
            .update({ status, updated_at: new Date().toISOString() })
            .eq('id', bookingId)
            .select()
            .single();

        if (error) throw error;

        const user = await getCurrentUser();
        await logActivity(user?.id, 'update', 'flight_booking', bookingId, `Updated status to: ${status}`);

        return { success: true, data };
    } catch (error) {
        console.error('Update flight booking error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Customer Functions
 * =====================================================
 */

// Get all customers (admin)
async function getCustomers(filters = {}) {
    try {
        let query = supabaseClient
            .from('customers')
            .select('*')
            .order('created_at', { ascending: false });

        if (filters.search) {
            query = query.or(`full_name.ilike.%${filters.search}%,email.ilike.%${filters.search}%,phone.ilike.%${filters.search}%`);
        }
        if (filters.customerType) {
            query = query.eq('customer_type', filters.customerType);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get customers error:', error);
        return { success: false, error: error.message };
    }
}

// Update customer profile
async function updateCustomerProfile(customerId, updates) {
    try {
        const { data, error } = await supabaseClient
            .from('customers')
            .update({ ...updates, updated_at: new Date().toISOString() })
            .eq('id', customerId)
            .select()
            .single();

        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Update customer error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Dashboard Stats Functions
 * =====================================================
 */

// Get dashboard statistics
async function getDashboardStats() {
    try {
        const now = new Date();
        const thirtyDaysAgo = new Date(now.setDate(now.getDate() - 30)).toISOString();
        const today = new Date().toISOString().split('T')[0];

        // Get hotel bookings stats
        const { data: hotelStats } = await supabaseClient
            .from('hotel_bookings')
            .select('status, total_amount')
            .gte('created_at', thirtyDaysAgo);

        // Get flight bookings stats
        const { data: flightStats } = await supabaseClient
            .from('flight_bookings')
            .select('status, total_amount')
            .gte('created_at', thirtyDaysAgo);

        // Get customer count
        const { count: newCustomers } = await supabaseClient
            .from('customers')
            .select('*', { count: 'exact', head: true })
            .gte('created_at', thirtyDaysAgo);

        // Calculate stats
        const totalHotelBookings = hotelStats?.length || 0;
        const totalFlightBookings = flightStats?.length || 0;
        const totalBookings = totalHotelBookings + totalFlightBookings;

        const hotelRevenue = hotelStats?.filter(b => b.status === 'confirmed').reduce((sum, b) => sum + (parseFloat(b.total_amount) || 0), 0) || 0;
        const flightRevenue = flightStats?.filter(b => b.status === 'confirmed').reduce((sum, b) => sum + (parseFloat(b.total_amount) || 0), 0) || 0;
        const totalRevenue = hotelRevenue + flightRevenue;

        const pendingBookings = (hotelStats?.filter(b => b.status === 'pending').length || 0) +
            (flightStats?.filter(b => b.status === 'pending').length || 0);
        const confirmedBookings = (hotelStats?.filter(b => b.status === 'confirmed').length || 0) +
            (flightStats?.filter(b => b.status === 'confirmed').length || 0);
        const cancelledBookings = (hotelStats?.filter(b => b.status === 'cancelled').length || 0) +
            (flightStats?.filter(b => b.status === 'cancelled').length || 0);

        return {
            success: true,
            data: {
                totalBookings,
                totalHotelBookings,
                totalFlightBookings,
                totalRevenue,
                hotelRevenue,
                flightRevenue,
                newCustomers: newCustomers || 0,
                pendingBookings,
                confirmedBookings,
                cancelledBookings
            }
        };
    } catch (error) {
        console.error('Get dashboard stats error:', error);
        return { success: false, error: error.message };
    }
}

// Get recent bookings for dashboard
async function getRecentBookings(limit = 10) {
    try {
        const { data: hotelBookings } = await supabaseClient
            .from('hotel_bookings')
            .select(`
                id, booking_id, hotel_name, total_amount, status, created_at,
                customers (full_name)
            `)
            .order('created_at', { ascending: false })
            .limit(limit);

        const { data: flightBookings } = await supabaseClient
            .from('flight_bookings')
            .select(`
                id, booking_id, origin_city, destination_city, airline_name, total_amount, status, created_at,
                customers (full_name)
            `)
            .order('created_at', { ascending: false })
            .limit(limit);

        // Combine and sort
        const allBookings = [
            ...(hotelBookings || []).map(b => ({ ...b, type: 'hotel' })),
            ...(flightBookings || []).map(b => ({ ...b, type: 'flight' }))
        ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, limit);

        return { success: true, data: allBookings };
    } catch (error) {
        console.error('Get recent bookings error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Markup Rules Functions
 * =====================================================
 */

// Get markup rules
async function getMarkupRules(filters = {}) {
    try {
        let query = supabaseClient
            .from('markup_rules')
            .select('*')
            .order('priority', { ascending: false });

        if (filters.applyTo) {
            query = query.eq('apply_to', filters.applyTo);
        }
        if (filters.ruleType) {
            query = query.eq('rule_type', filters.ruleType);
        }
        if (filters.activeOnly) {
            query = query.eq('is_active', true);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get markup rules error:', error);
        return { success: false, error: error.message };
    }
}

// Create markup rule
async function createMarkupRule(ruleData) {
    try {
        const user = await getCurrentUser();

        const { data, error } = await supabaseClient
            .from('markup_rules')
            .insert({
                ...ruleData,
                created_by: user?.id
            })
            .select()
            .single();

        if (error) throw error;
        await logActivity(user?.id, 'create', 'markup_rule', data.id, `Created markup rule: ${ruleData.rule_name}`);
        return { success: true, data };
    } catch (error) {
        console.error('Create markup rule error:', error);
        return { success: false, error: error.message };
    }
}

// Update markup rule
async function updateMarkupRule(ruleId, updates) {
    try {
        const { data, error } = await supabaseClient
            .from('markup_rules')
            .update({ ...updates, updated_at: new Date().toISOString() })
            .eq('id', ruleId)
            .select()
            .single();

        if (error) throw error;

        const user = await getCurrentUser();
        await logActivity(user?.id, 'update', 'markup_rule', ruleId, `Updated markup rule`);
        return { success: true, data };
    } catch (error) {
        console.error('Update markup rule error:', error);
        return { success: false, error: error.message };
    }
}

// Delete markup rule
async function deleteMarkupRule(ruleId) {
    try {
        const { error } = await supabaseClient
            .from('markup_rules')
            .delete()
            .eq('id', ruleId);

        if (error) throw error;

        const user = await getCurrentUser();
        await logActivity(user?.id, 'delete', 'markup_rule', ruleId, `Deleted markup rule`);
        return { success: true };
    } catch (error) {
        console.error('Delete markup rule error:', error);
        return { success: false, error: error.message };
    }
}

// Calculate markup for a price
async function calculateMarkup(basePrice, itemType = 'hotel', targetValue = null) {
    try {
        const { data: rules } = await supabaseClient
            .from('markup_rules')
            .select('*')
            .eq('apply_to', itemType)
            .eq('is_active', true)
            .order('priority', { ascending: false });

        if (!rules || rules.length === 0) {
            return { basePrice, markupAmount: 0, finalPrice: basePrice };
        }

        // Find the best matching rule
        let applicableRule = rules.find(r => r.rule_type === 'global');

        // Check for more specific rules
        if (targetValue) {
            const specificRule = rules.find(r =>
                (r.rule_type === 'city' || r.rule_type === 'hotel' || r.rule_type === 'airline') &&
                r.target_value?.toLowerCase() === targetValue.toLowerCase()
            );
            if (specificRule) {
                applicableRule = specificRule;
            }
        }

        if (!applicableRule) {
            return { basePrice, markupAmount: 0, finalPrice: basePrice };
        }

        let markupAmount = 0;
        if (applicableRule.markup_type === 'percentage') {
            markupAmount = (basePrice * applicableRule.markup_value) / 100;
        } else {
            markupAmount = applicableRule.markup_value;
        }

        // Apply max markup cap if set
        if (applicableRule.max_markup_value && markupAmount > applicableRule.max_markup_value) {
            markupAmount = applicableRule.max_markup_value;
        }

        const finalPrice = basePrice + markupAmount;

        return {
            basePrice,
            markupAmount,
            finalPrice,
            appliedRule: applicableRule.rule_name
        };
    } catch (error) {
        console.error('Calculate markup error:', error);
        return { basePrice, markupAmount: 0, finalPrice: basePrice };
    }
}

/**
 * =====================================================
 * Activity Logs Functions
 * =====================================================
 */

// Log activity
async function logActivity(userId, action, entityType = null, entityId = null, details = null, metadata = null) {
    try {
        // Get admin ID if user is admin
        let adminId = null;
        if (userId) {
            const { data: adminData } = await supabaseClient
                .from('admin_users')
                .select('id')
                .eq('user_id', userId)
                .single();
            adminId = adminData?.id;
        }

        await supabaseClient
            .from('activity_logs')
            .insert({
                user_id: userId,
                admin_id: adminId,
                action,
                entity_type: entityType,
                entity_id: entityId,
                details,
                metadata
            });
    } catch (error) {
        console.error('Log activity error:', error);
    }
}

// Get activity logs
async function getActivityLogs(filters = {}) {
    try {
        let query = supabaseClient
            .from('activity_logs')
            .select(`
                *,
                admin_users (username, full_name)
            `)
            .order('created_at', { ascending: false });

        if (filters.action) {
            query = query.eq('action', filters.action);
        }
        if (filters.entityType) {
            query = query.eq('entity_type', filters.entityType);
        }
        if (filters.userId) {
            query = query.eq('user_id', filters.userId);
        }
        if (filters.fromDate) {
            query = query.gte('created_at', filters.fromDate);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get activity logs error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Settings Functions
 * =====================================================
 */

// Get system settings
async function getSystemSettings(category = null) {
    try {
        let query = supabaseClient
            .from('system_settings')
            .select('*');

        if (category) {
            query = query.eq('category', category);
        }

        const { data, error } = await query;
        if (error) throw error;

        // Convert to key-value object
        const settings = {};
        data?.forEach(s => {
            let value = s.setting_value;
            if (s.setting_type === 'boolean') {
                value = s.setting_value === 'true';
            } else if (s.setting_type === 'number') {
                value = parseFloat(s.setting_value);
            } else if (s.setting_type === 'json') {
                try { value = JSON.parse(s.setting_value); } catch { }
            }
            settings[s.setting_key] = value;
        });

        return { success: true, data: settings };
    } catch (error) {
        console.error('Get settings error:', error);
        return { success: false, error: error.message };
    }
}

// Update system setting
async function updateSystemSetting(key, value) {
    try {
        const user = await getCurrentUser();

        const { data, error } = await supabaseClient
            .from('system_settings')
            .update({
                setting_value: String(value),
                updated_by: user?.id,
                updated_at: new Date().toISOString()
            })
            .eq('setting_key', key)
            .select()
            .single();

        if (error) throw error;
        await logActivity(user?.id, 'update', 'setting', key, `Updated setting: ${key}`);
        return { success: true, data };
    } catch (error) {
        console.error('Update setting error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Payments Functions
 * =====================================================
 */

// Get payments
async function getPayments(filters = {}) {
    try {
        let query = supabaseClient
            .from('payments')
            .select(`
                *,
                customers (full_name, email)
            `)
            .order('created_at', { ascending: false });

        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.bookingType) {
            query = query.eq('booking_type', filters.bookingType);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Get payments error:', error);
        return { success: false, error: error.message };
    }
}

// Create payment record
async function createPayment(paymentData) {
    try {
        const user = await getCurrentUser();
        const paymentId = 'PAY-' + Date.now().toString().slice(-8);

        const { data, error } = await supabaseClient
            .from('payments')
            .insert({
                ...paymentData,
                payment_id: paymentId,
                user_id: user?.id
            })
            .select()
            .single();

        if (error) throw error;
        return { success: true, data };
    } catch (error) {
        console.error('Create payment error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * =====================================================
 * Auth State Listener
 * =====================================================
 */

// Subscribe to auth state changes
function onAuthStateChange(callback) {
    return supabaseClient.auth.onAuthStateChange((event, session) => {
        callback(event, session);
    });
}

// Export all functions for use
window.SupabaseDB = {
    // Auth
    signUpCustomer,
    signIn,
    signInWithGoogle,
    signOut,
    getCurrentUser,
    getSession,
    isAdmin,
    getUserRole,
    getAdminDetails,
    getCustomerDetails,
    onAuthStateChange,

    // Hotel Bookings
    getHotelBookings,
    createHotelBooking,
    updateHotelBookingStatus,

    // Flight Bookings
    getFlightBookings,
    createFlightBooking,
    updateFlightBookingStatus,

    // Customers
    getCustomers,
    updateCustomerProfile,

    // Dashboard
    getDashboardStats,
    getRecentBookings,

    // Markup
    getMarkupRules,
    createMarkupRule,
    updateMarkupRule,
    deleteMarkupRule,
    calculateMarkup,

    // Activity Logs
    logActivity,
    getActivityLogs,

    // Settings
    getSystemSettings,
    updateSystemSetting,

    // Payments
    getPayments,
    createPayment,

    // Supabase client direct access
    client: supabaseClient
};
