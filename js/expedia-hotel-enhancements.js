/**
 * Expedia-Style Hotel Details Enhancements
 * Handles Property Highlights, Amenities Categorization, Accessibility, and Interactive Components
 */

// Amenity Categorization Mapping
const AMENITY_CATEGORIES = {
    internet: ['wifi', 'internet', 'wireless', 'connection', 'laptop', 'computer'],
    parking: ['parking', 'valet', 'garage', 'car', 'vehicle', 'shuttle', 'airport', 'transportation', 'bus', 'train'],
    food: ['restaurant', 'bar', 'breakfast', 'lunch', 'dinner', 'coffee', 'snack', 'kitchen', 'dining', 'room service', 'buffet'],
    activities: ['pool', 'spa', 'gym', 'fitness', 'sauna', 'massage', 'wellness', 'beach', 'water', 'sports', 'tennis', 'golf', 'yoga'],
    family: ['children', 'kids', 'child', 'crib', 'baby', 'family', 'playground', 'game', 'soundproof', 'babysitting'],
    services: ['concierge', 'front desk', '24-hour', 'reception', 'luggage', 'laundry', 'dry cleaning', 'meeting', 'business', 'tour', 'ticket', 'express check', 'atm', 'currency', 'multilingual']
};

// Accessibility Feature Mapping
const ACCESSIBILITY_FEATURES = {
    bathroom: ['accessible bathroom', 'grab bars', 'raised toilet', 'accessible sink', 'lowered sink', 'roll-under sink'],
    shower: ['roll-in shower', 'shower seat', 'hand-held shower', 'transfer shower', 'accessible shower'],
    entrance: ['wheelchair accessible', 'stair-free', 'ramp', 'accessible entrance', 'wide doorway', 'elevator', 'accessible route'],
    sensory: ['tty', 'deaf equipment', 'visual alarm', 'flashing alarm', 'vibrating alarm', 'doorbell'],
    visual: ['braille', 'raised signage', 'high-contrast', 'audio', 'visual aid'],
    service: ['service animal', 'assistance animal', 'guide dog']
};

/**
 * Generate AI-Powered Property Highlights
 */
function generatePropertyHighlights(hotelData) {
    const highlightsGrid = document.getElementById('highlightsGrid');
    if (!highlightsGrid) return;
    
    const highlights = [];
    
    // Location-based highlight
    if (hotelData.address) {
        const city = hotelData.address.city || hotelData.address.locality;
        highlights.push({
            icon: 'fa-map-marker-alt',
            title: `Prime ${city} Location`,
            description: `Conveniently located near major attractions and landmarks in ${city}`
        });
    }
    
    // WiFi highlight
    const hasWifi = checkAmenity(hotelData, ['wifi', 'internet', 'wireless']);
    if (hasWifi) {
        highlights.push({
            icon: 'fa-wifi',
            title: 'Free High-Speed WiFi',
            description: 'Stay connected with complimentary high-speed internet throughout the property'
        });
    }
    
    // Front desk highlight
    const has24HourDesk = checkAmenity(hotelData, ['24-hour', '24 hour', 'front desk']);
    if (has24HourDesk) {
        highlights.push({
            icon: 'fa-concierge-bell',
            title: '24-Hour Front Desk',
            description: 'Professional staff available around the clock to assist with your needs'
        });
    }
    
    // Parking highlight
    const hasParking = checkAmenity(hotelData, ['parking', 'valet', 'garage']);
    if (hasParking) {
        highlights.push({
            icon: 'fa-parking',
            title: 'On-Site Parking Available',
            description: 'Convenient parking options for guests with vehicles'
        });
    }
    
    // Pool/Spa highlight
    const hasPool = checkAmenity(hotelData, ['pool', 'swimming']);
    const hasSpa = checkAmenity(hotelData, ['spa', 'wellness', 'massage']);
    if (hasPool || hasSpa) {
        highlights.push({
            icon: hasPool ? 'fa-swimming-pool' : 'fa-spa',
            title: hasPool ? 'Swimming Pool' : 'Spa & Wellness',
            description: hasPool ? 'Relax and unwind in the refreshing swimming pool' : 'Indulge in rejuvenating spa treatments and wellness services'
        });
    }
    
    // Restaurant highlight
    const hasRestaurant = checkAmenity(hotelData, ['restaurant', 'dining', 'bar']);
    if (hasRestaurant) {
        highlights.push({
            icon: 'fa-utensils',
            title: 'On-Site Dining',
            description: 'Enjoy delicious meals at the hotel\'s restaurant and bar'
        });
    }
    
    // Render highlights
    highlightsGrid.innerHTML = highlights.map(h => `
        <div class="highlight-card fade-in fade-in-up">
            <div class="highlight-icon">
                <i class="fas ${h.icon}"></i>
            </div>
            <div class="highlight-content">
                <h4>${h.title}</h4>
                <p>${h.description}</p>
            </div>
        </div>
    `).join('');
}

/**
 * Helper function to check if hotel has specific amenities
 */
function checkAmenity(hotelData, keywords) {
    if (!hotelData.amenities && !hotelData.amenity_groups) return false;
    
    const amenitiesText = JSON.stringify(hotelData).toLowerCase();
    return keywords.some(keyword => amenitiesText.includes(keyword.toLowerCase()));
}

/**
 * Populate About Section
 */
function populateAboutSection(hotelData) {
    const aboutNarrative = document.getElementById('aboutNarrative');
    const summaryAmenities = document.getElementById('summaryAmenities');
    
    if (!aboutNarrative) return;
    
    // Generate narrative description
    const city = hotelData.address?.city || hotelData.address?.locality || 'the area';
    const propertyType = hotelData.property_type || 'hotel';
    const starRating = hotelData.star_rating ? `${hotelData.star_rating}-star ` : '';
    
    const narrative = `
        <p>Welcome to ${hotelData.name}, a ${starRating}${propertyType} located in the heart of ${city}. 
        This property offers a perfect blend of comfort and convenience for both business and leisure travelers.</p>
        
        <p>The hotel features well-appointed rooms and suites, designed with your comfort in mind. 
        Each accommodation includes modern amenities to ensure a pleasant stay.</p>
        
        <p>Guests can enjoy a range of facilities and services during their visit. 
        The property's prime location provides easy access to major attractions, shopping areas, and dining options in ${city}.</p>
        
        <p>Whether you're visiting for business or pleasure, ${hotelData.name} provides an ideal base 
        for exploring everything ${city} has to offer.</p>
    `;
    
    aboutNarrative.innerHTML = narrative;
    
    // Popular amenities summary
    if (summaryAmenities) {
        const topAmenities = getTopAmenities(hotelData, 6);
        summaryAmenities.innerHTML = topAmenities.map(amenity => `
            <div class="summary-amenity">
                <i class="fas ${getAmenityIcon(amenity)}"></i>
                <span>${amenity}</span>
            </div>
        `).join('');
    }
}

/**
 * Get top amenities for summary
 */
function getTopAmenities(hotelData, count = 6) {
    const amenities = [];
    const priorityAmenities = ['wifi', 'parking', 'pool', 'restaurant', 'gym', 'spa', 'bar', 'breakfast', 'air conditioning', 'room service'];
    
    if (hotelData.amenities) {
        hotelData.amenities.forEach(amenity => {
            const amenityText = amenity.toLowerCase();
            if (priorityAmenities.some(priority => amenityText.includes(priority))) {
                amenities.push(amenity);
            }
        });
    }
    
    // Add default amenities if not enough
    const defaults = ['Free WiFi', 'Air Conditioning', '24-Hour Front Desk', 'Housekeeping', 'Non-Smoking Rooms', 'Luggage Storage'];
    return [...amenities, ...defaults].slice(0, count);
}

/**
 * Categorize and Display Amenities
 */
function categorizeAndDisplayAmenities(hotelData) {
    const categorizedAmenities = {
        internet: [],
        parking: [],
        food: [],
        activities: [],
        family: [],
        services: []
    };
    
    // Get all amenities
    const allAmenities = [];
    if (hotelData.amenities) allAmenities.push(...hotelData.amenities);
    if (hotelData.amenity_groups) {
        hotelData.amenity_groups.forEach(group => {
            if (group.amenities) allAmenities.push(...group.amenities);
        });
    }
    
    // Categorize amenities
    allAmenities.forEach(amenity => {
        const amenityLower = amenity.toLowerCase();
        let categorized = false;
        
        for (const [category, keywords] of Object.entries(AMENITY_CATEGORIES)) {
            if (keywords.some(keyword => amenityLower.includes(keyword))) {
                categorizedAmenities[category].push(amenity);
                categorized = true;
                break;
            }
        }
        
        // If not categorized, add to services
        if (!categorized) {
            categorizedAmenities.services.push(amenity);
        }
    });
    
    // Display categorized amenities
    displayCategoryAmenities('amenitiesInternet', categorizedAmenities.internet);
    displayCategoryAmenities('amenitiesParking', categorizedAmenities.parking);
    displayCategoryAmenities('amenitiesFood', categorizedAmenities.food);
    displayCategoryAmenities('amenitiesActivities', categorizedAmenities.activities);
    displayCategoryAmenities('amenitiesFamily', categorizedAmenities.family);
    displayCategoryAmenities('amenitiesServices', categorizedAmenities.services);
    
    // Setup show more functionality
    setupShowMoreAmenities();
}

/**
 * Display amenities for a specific category
 */
function displayCategoryAmenities(elementId, amenities) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (amenities.length === 0) {
        element.closest('.amenity-category').style.display = 'none';
        return;
    }
    
    element.innerHTML = amenities.slice(0, 6).map(amenity => {
        const fee = amenity.toLowerCase().includes('fee') || amenity.toLowerCase().includes('surcharge');
        return `<li ${fee ? 'class="with-fee"' : ''}>
            ${amenity}
            ${fee ? '<span class="amenity-fee">Additional charge may apply</span>' : ''}
        </li>`;
    }).join('');
    
    // Store full list for "show more"
    element.dataset.fullList = JSON.stringify(amenities);
}

/**
 * Setup Show More Amenities functionality
 */
function setupShowMoreAmenities() {
    const showMoreBtn = document.getElementById('showMoreAmenities');
    if (!showMoreBtn) return;
    
    let expanded = false;
    
    showMoreBtn.addEventListener('click', () => {
        expanded = !expanded;
        
        // Toggle all amenity lists
        document.querySelectorAll('.amenity-list').forEach(list => {
            if (list.dataset.fullList) {
                const fullAmenities = JSON.parse(list.dataset.fullList);
                if (expanded) {
                    list.innerHTML = fullAmenities.map(amenity => {
                        const fee = amenity.toLowerCase().includes('fee') || amenity.toLowerCase().includes('surcharge');
                        return `<li ${fee ? 'class="with-fee"' : ''}>
                            ${amenity}
                            ${fee ? '<span class="amenity-fee">Additional charge may apply</span>' : ''}
                        </li>`;
                    }).join('');
                } else {
                    list.innerHTML = fullAmenities.slice(0, 6).map(amenity => {
                        const fee = amenity.toLowerCase().includes('fee') || amenity.toLowerCase().includes('surcharge');
                        return `<li ${fee ? 'class="with-fee"' : ''}>
                            ${amenity}
                            ${fee ? '<span class="amenity-fee">Additional charge may apply</span>' : ''}
                        </li>`;
                    }).join('');
                }
            }
        });
        
        // Update button
        showMoreBtn.innerHTML = expanded 
            ? '<i class="fas fa-chevron-up"></i> Show less amenities'
            : '<i class="fas fa-chevron-down"></i> Show all amenities';
        showMoreBtn.classList.toggle('expanded', expanded);
    });
}

/**
 * Populate Accessibility Section
 */
function populateAccessibilitySection(hotelData) {
    const accessibilityData = extractAccessibilityFeatures(hotelData);
    
    displayAccessibilityFeatures('accessibleBathroom', accessibilityData.bathroom);
    displayAccessibilityFeatures('rollInShower', accessibilityData.shower);
    displayAccessibilityFeatures('accessibleEntrance', accessibilityData.entrance);
    displayAccessibilityFeatures('sensoryEquipment', accessibilityData.sensory);
    displayAccessibilityFeatures('visualAids', accessibilityData.visual);
    displayAccessibilityFeatures('serviceAnimals', accessibilityData.service);
    
    // Hide section if no accessibility features
    const hasFeatures = Object.values(accessibilityData).some(arr => arr.length > 0);
    const accessibilitySection = document.getElementById('accessibilitySection');
    if (accessibilitySection && !hasFeatures) {
        accessibilitySection.style.display = 'none';
    }
}

/**
 * Extract accessibility features from hotel data
 */
function extractAccessibilityFeatures(hotelData) {
    const features = {
        bathroom: [],
        shower: [],
        entrance: [],
        sensory: [],
        visual: [],
        service: []
    };
    
    const allText = JSON.stringify(hotelData).toLowerCase();
    
    // Check for accessibility keywords
    for (const [category, keywords] of Object.entries(ACCESSIBILITY_FEATURES)) {
        keywords.forEach(keyword => {
            if (allText.includes(keyword.toLowerCase())) {
                const formattedFeature = keyword.charAt(0).toUpperCase() + keyword.slice(1);
                if (!features[category].includes(formattedFeature)) {
                    features[category].push(formattedFeature);
                }
            }
        });
    }
    
    // Add default accessibility features if property is accessible
    if (allText.includes('accessible') || allText.includes('wheelchair')) {
        if (features.entrance.length === 0) {
            features.entrance.push('Wheelchair accessible entrance', 'Stair-free path (minimum 36 inches wide)');
        }
        if (features.bathroom.length === 0) {
            features.bathroom.push('Accessible bathroom', 'Grab bars near toilet');
        }
        if (features.service.length === 0) {
            features.service.push('Service animals welcome');
        }
    }
    
    return features;
}

/**
 * Display accessibility features
 */
function displayAccessibilityFeatures(elementId, features) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (features.length === 0) {
        element.closest('.accessibility-feature').style.display = 'none';
        return;
    }
    
    element.innerHTML = features.map(feature => `<li>${feature}</li>`).join('');
}

/**
 * Get appropriate icon for amenity
 */
function getAmenityIcon(amenity) {
    const lower = amenity.toLowerCase();
    if (lower.includes('wifi') || lower.includes('internet')) return 'fa-wifi';
    if (lower.includes('parking')) return 'fa-parking';
    if (lower.includes('pool')) return 'fa-swimming-pool';
    if (lower.includes('restaurant') || lower.includes('dining')) return 'fa-utensils';
    if (lower.includes('gym') || lower.includes('fitness')) return 'fa-dumbbell';
    if (lower.includes('spa')) return 'fa-spa';
    if (lower.includes('bar')) return 'fa-cocktail';
    if (lower.includes('breakfast')) return 'fa-coffee';
    if (lower.includes('air conditioning') || lower.includes('ac')) return 'fa-fan';
    if (lower.includes('room service')) return 'fa-concierge-bell';
    return 'fa-check-circle';
}

/**
 * Initialize all Expedia-style enhancements
 */
function initializeExpediaEnhancements(hotelData) {
    if (!hotelData) {
        console.warn('No hotel data provided for Expedia enhancements');
        return;
    }
    
    try {
        // Add smooth scroll behavior
        document.documentElement.style.scrollBehavior = 'smooth';
        
        generatePropertyHighlights(hotelData);
        populateAboutSection(hotelData);
        categorizeAndDisplayAmenities(hotelData);
        populateAccessibilitySection(hotelData);
        
        console.log('✅ User-friendly enhancements initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing enhancements:', error);
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.ExpediaEnhancements = {
        initialize: initializeExpediaEnhancements,
        generateHighlights: generatePropertyHighlights,
        categorizeAmenities: categorizeAndDisplayAmenities,
        populateAccessibility: populateAccessibilitySection,
        populateAbout: populateAboutSection
    };
}
