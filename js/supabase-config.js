/**
 * C2C Journeys - Supabase Configuration
 * Handles database connection and authentication
 */

// Supabase Configuration
const SUPABASE_URL = 'https://bcxkjvjchutgfuyklphx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjeGtqdmpjaHV0Z2Z1eWtscGh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxOTQyNzAsImV4cCI6MjA4Mzc3MDI3MH0.qz5yreyBo5zD8x51leZDWHD6Ft_2JvutBrZF8yhjqJE';

// Initialize Supabase Client
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ========================================
// Authentication Functions
// ========================================

/**
 * Sign up a new user with email and password
 */
async function signUpUser(email, password, userData = {}) {
    try {
        const { data, error } = await supabaseClient.auth.signUp({
            email: email,
            password: password,
            options: {
                data: {
                    full_name: userData.fullName || '',
                    phone: userData.phone || ''
                }
            }
        });

        if (error) throw error;

        return {
            success: true,
            message: 'Account created successfully! Please check your email to verify.',
            user: data.user
        };
    } catch (error) {
        console.error('Sign up error:', error);
        return {
            success: false,
            message: error.message || 'Failed to create account'
        };
    }
}

/**
 * Sign in user with email and password
 */
async function signInUser(email, password) {
    try {
        const { data, error } = await supabaseClient.auth.signInWithPassword({
            email: email,
            password: password
        });

        if (error) throw error;

        return {
            success: true,
            message: 'Login successful!',
            user: data.user,
            session: data.session
        };
    } catch (error) {
        console.error('Sign in error:', error);
        return {
            success: false,
            message: error.message || 'Invalid email or password'
        };
    }
}

/**
 * Sign in with Google OAuth
 */
async function signInWithGoogle() {
    try {
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        });

        if (error) throw error;

        return { success: true };
    } catch (error) {
        console.error('Google sign in error:', error);
        return {
            success: false,
            message: error.message || 'Failed to sign in with Google'
        };
    }
}

/**
 * Sign in with Facebook OAuth
 */
async function signInWithFacebook() {
    try {
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'facebook',
            options: {
                redirectTo: window.location.origin
            }
        });

        if (error) throw error;

        return { success: true };
    } catch (error) {
        console.error('Facebook sign in error:', error);
        return {
            success: false,
            message: error.message || 'Failed to sign in with Facebook'
        };
    }
}

/**
 * Sign out the current user
 */
async function signOutUser() {
    try {
        const { error } = await supabaseClient.auth.signOut();
        if (error) throw error;

        return {
            success: true,
            message: 'Logged out successfully'
        };
    } catch (error) {
        console.error('Sign out error:', error);
        return {
            success: false,
            message: error.message || 'Failed to sign out'
        };
    }
}

/**
 * Get the current logged in user
 */
async function getCurrentUser() {
    try {
        const { data: { user }, error } = await supabaseClient.auth.getUser();
        if (error) throw error;

        return user;
    } catch (error) {
        console.error('Get user error:', error);
        return null;
    }
}

/**
 * Get current session
 */
async function getCurrentSession() {
    try {
        const { data: { session }, error } = await supabaseClient.auth.getSession();
        if (error) throw error;

        return session;
    } catch (error) {
        console.error('Get session error:', error);
        return null;
    }
}

/**
 * Reset password
 */
async function resetPassword(email) {
    try {
        const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password`
        });

        if (error) throw error;

        return {
            success: true,
            message: 'Password reset email sent! Check your inbox.'
        };
    } catch (error) {
        console.error('Reset password error:', error);
        return {
            success: false,
            message: error.message || 'Failed to send reset email'
        };
    }
}

// ========================================
// Database Functions - Contact Messages
// ========================================

/**
 * Save contact form submission to database
 */
async function saveContactMessage(formData) {
    try {
        const { data, error } = await supabaseClient
            .from('contact_messages')
            .insert([
                {
                    name: formData.name,
                    email: formData.email,
                    phone: formData.phone || null,
                    subject: formData.subject,
                    message: formData.message,
                    created_at: new Date().toISOString()
                }
            ])
            .select();

        if (error) throw error;

        return {
            success: true,
            message: 'Message sent successfully! We will get back to you soon.',
            data: data
        };
    } catch (error) {
        console.error('Save contact error:', error);
        return {
            success: false,
            message: error.message || 'Failed to send message. Please try again.'
        };
    }
}

// ========================================
// Database Functions - Newsletter
// ========================================

/**
 * Subscribe to newsletter
 */
async function subscribeNewsletter(email) {
    try {
        // Check if already subscribed
        const { data: existing } = await supabaseClient
            .from('newsletter_subscribers')
            .select('*')
            .eq('email', email)
            .single();

        if (existing) {
            return {
                success: false,
                message: 'This email is already subscribed!'
            };
        }

        const { data, error } = await supabaseClient
            .from('newsletter_subscribers')
            .insert([
                {
                    email: email,
                    subscribed_at: new Date().toISOString(),
                    is_active: true
                }
            ])
            .select();

        if (error) throw error;

        return {
            success: true,
            message: 'Successfully subscribed to our newsletter!',
            data: data
        };
    } catch (error) {
        console.error('Newsletter subscription error:', error);
        return {
            success: false,
            message: error.message || 'Failed to subscribe. Please try again.'
        };
    }
}

// ========================================
// Database Functions - Search History
// ========================================

/**
 * Save flight search to history
 */
async function saveFlightSearch(searchData) {
    try {
        const user = await getCurrentUser();

        const { data, error } = await supabaseClient
            .from('flight_searches')
            .insert([
                {
                    user_id: user ? user.id : null,
                    from_city: searchData.from,
                    to_city: searchData.to,
                    depart_date: searchData.departDate,
                    return_date: searchData.returnDate || null,
                    travelers: searchData.travelers,
                    travel_class: searchData.class,
                    trip_type: searchData.tripType,
                    created_at: new Date().toISOString()
                }
            ])
            .select();

        if (error) throw error;

        return { success: true, data: data };
    } catch (error) {
        console.error('Save flight search error:', error);
        return { success: false, message: error.message };
    }
}

/**
 * Save hotel search to history
 */
async function saveHotelSearch(searchData) {
    try {
        const user = await getCurrentUser();

        const { data, error } = await supabaseClient
            .from('hotel_searches')
            .insert([
                {
                    user_id: user ? user.id : null,
                    destination: searchData.destination,
                    check_in_date: searchData.checkIn,
                    check_out_date: searchData.checkOut,
                    rooms: searchData.rooms,
                    guests: searchData.guests,
                    created_at: new Date().toISOString()
                }
            ])
            .select();

        if (error) throw error;

        return { success: true, data: data };
    } catch (error) {
        console.error('Save hotel search error:', error);
        return { success: false, message: error.message };
    }
}

// ========================================
// Database Functions - Quote Requests
// ========================================

/**
 * Save quote request
 */
async function saveQuoteRequest(quoteData) {
    try {
        const user = await getCurrentUser();

        const { data, error } = await supabaseClient
            .from('quote_requests')
            .insert([
                {
                    user_id: user ? user.id : null,
                    name: quoteData.name,
                    email: quoteData.email,
                    phone: quoteData.phone,
                    travel_type: quoteData.travelType,
                    destination: quoteData.destination,
                    travel_date: quoteData.travelDate,
                    travelers: quoteData.travelers,
                    budget: quoteData.budget,
                    special_requirements: quoteData.requirements,
                    created_at: new Date().toISOString()
                }
            ])
            .select();

        if (error) throw error;

        return {
            success: true,
            message: 'Quote request submitted successfully! We will contact you soon.',
            data: data
        };
    } catch (error) {
        console.error('Save quote request error:', error);
        return {
            success: false,
            message: error.message || 'Failed to submit quote request.'
        };
    }
}

// ========================================
// Database Functions - Wishlist
// ========================================

/**
 * Add item to wishlist
 */
async function addToWishlist(itemType, itemData) {
    try {
        const user = await getCurrentUser();

        if (!user) {
            return {
                success: false,
                message: 'Please login to save to wishlist'
            };
        }

        const { data, error } = await supabaseClient
            .from('wishlist')
            .insert([
                {
                    user_id: user.id,
                    item_type: itemType,
                    item_name: itemData.name,
                    item_location: itemData.location,
                    item_price: itemData.price,
                    item_image: itemData.image,
                    created_at: new Date().toISOString()
                }
            ])
            .select();

        if (error) throw error;

        return {
            success: true,
            message: 'Added to wishlist!',
            data: data
        };
    } catch (error) {
        console.error('Add to wishlist error:', error);
        return {
            success: false,
            message: error.message || 'Failed to add to wishlist'
        };
    }
}

/**
 * Remove item from wishlist
 */
async function removeFromWishlist(itemId) {
    try {
        const { error } = await supabaseClient
            .from('wishlist')
            .delete()
            .eq('id', itemId);

        if (error) throw error;

        return {
            success: true,
            message: 'Removed from wishlist'
        };
    } catch (error) {
        console.error('Remove from wishlist error:', error);
        return {
            success: false,
            message: error.message || 'Failed to remove from wishlist'
        };
    }
}

/**
 * Get user's wishlist
 */
async function getWishlist() {
    try {
        const user = await getCurrentUser();

        if (!user) {
            return { success: false, data: [] };
        }

        const { data, error } = await supabaseClient
            .from('wishlist')
            .select('*')
            .eq('user_id', user.id)
            .order('created_at', { ascending: false });

        if (error) throw error;

        return { success: true, data: data };
    } catch (error) {
        console.error('Get wishlist error:', error);
        return { success: false, data: [] };
    }
}

// ========================================
// Auth State Change Listener
// ========================================
supabaseClient.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event);

    if (event === 'SIGNED_IN') {
        updateUIForLoggedInUser(session.user);
    } else if (event === 'SIGNED_OUT') {
        updateUIForLoggedOutUser();
    }
});

/**
 * Update UI for logged in user
 */
function updateUIForLoggedInUser(user) {
    const loginBtn = document.getElementById('loginBtn');
    const signUpBtn = document.querySelector('.nav-actions .btn-primary');

    if (loginBtn) {
        loginBtn.innerHTML = `<i class="fas fa-user"></i> ${user.email.split('@')[0]}`;
        loginBtn.removeEventListener('click', openLoginModal);
        loginBtn.addEventListener('click', showUserMenu);
    }

    if (signUpBtn) {
        signUpBtn.innerHTML = `<i class="fas fa-sign-out-alt"></i> Logout`;
        signUpBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await signOutUser();
            if (result.success) {
                showNotification(result.message, 'success');
                window.location.reload();
            }
        });
    }
}

/**
 * Update UI for logged out user
 */
function updateUIForLoggedOutUser() {
    const loginBtn = document.getElementById('loginBtn');
    const signUpBtn = document.querySelector('.nav-actions .btn-primary');

    if (loginBtn) {
        loginBtn.innerHTML = `<i class="fas fa-user"></i> Login`;
    }

    if (signUpBtn) {
        signUpBtn.innerHTML = `<i class="fas fa-user-plus"></i> Sign Up`;
    }
}

/**
 * Show user menu dropdown
 */
function showUserMenu(e) {
    e.preventDefault();
    // This can be expanded to show a dropdown with user options
    showNotification('User dashboard coming soon!', 'info');
}

// ========================================
// Initialize Supabase on page load
// ========================================
async function initSupabase() {
    const session = await getCurrentSession();

    if (session && session.user) {
        updateUIForLoggedInUser(session.user);
        console.log('User is logged in:', session.user.email);
    } else {
        console.log('No user logged in');
    }
}

// Export functions for use in main.js
window.SupabaseService = {
    // Auth
    signUp: signUpUser,
    signIn: signInUser,
    signInWithGoogle,
    signInWithFacebook,
    signOut: signOutUser,
    getCurrentUser,
    getCurrentSession,
    resetPassword,

    // Database
    saveContactMessage,
    subscribeNewsletter,
    saveFlightSearch,
    saveHotelSearch,
    saveQuoteRequest,
    addToWishlist,
    removeFromWishlist,
    getWishlist,

    // Init
    init: initSupabase
};

console.log('Supabase configuration loaded successfully!');
