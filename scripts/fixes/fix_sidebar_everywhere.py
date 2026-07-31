import os
import re

# The sidebar HTML from index.html
sidebar_html = """
    <!-- Sidebar Menu -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
            <span>Coast To Coast</span>
            <button class="sidebar-close" id="sidebarClose">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <nav class="sidebar-nav">
            <a href="index.html" class="sidebar-link">
                <i class="fas fa-home"></i> Home
            </a>
            <a href="flight-booking.html" class="sidebar-link">
                <i class="fas fa-plane"></i> Book Flights
            </a>
            <a href="hotel-booking.html" class="sidebar-link">
                <i class="fas fa-hotel"></i> Book Hotels
            </a>
            <div class="sidebar-divider"></div>
            <a href="#contact" class="sidebar-link" id="sidebarSupport">
                <i class="fas fa-headset"></i> 24/7 Support
            </a>
            <a href="mailto:Sales@c2cjourneys.com" class="sidebar-link">
                <i class="fas fa-envelope"></i> Email Us
            </a>
            <a href="tel:+18883159768" class="sidebar-link">
                <i class="fas fa-phone"></i> Call Us
            </a>
            <div class="sidebar-divider"></div>
            <a href="#" class="sidebar-link" id="feedbackLink">
                <i class="fas fa-comment-dots"></i> Feedback
            </a>
            <a href="faqs.html" class="sidebar-link">
                <i class="fas fa-question-circle"></i> FAQs
            </a>
            <a href="about.html" class="sidebar-link">
                <i class="fas fa-info-circle"></i> About Us
            </a>
            <div class="sidebar-divider"></div>
            <a href="terms.html" class="sidebar-link">
                <i class="fas fa-file-contract"></i> Terms & Conditions
            </a>
            <a href="privacy-policy.html" class="sidebar-link">
                <i class="fas fa-user-shield"></i> Privacy Policy
            </a>
            <a href="refund-policy.html" class="sidebar-link">
                <i class="fas fa-undo-alt"></i> Refund Policy
            </a>
            <div class="sidebar-divider"></div>
            <a href="https://wa.me/18883159768" class="sidebar-link" target="_blank">
                <i class="fab fa-whatsapp"></i> WhatsApp Chat
            </a>
        </nav>
        <div class="sidebar-footer">
            <div class="sidebar-social">
                <a href="#"><i class="fab fa-facebook-f"></i></a>
                <a href="#"><i class="fab fa-instagram"></i></a>
                <a href="#"><i class="fab fa-twitter"></i></a>
            </div>
            <p>&copy; 2026 Coast To Coast</p>
        </div>
    </aside>
"""

directory = 'templates'
files_to_update = ['flight-booking.html', 'hotel-booking.html', 'faqs.html', 'about.html', 'terms.html', 'privacy-policy.html', 'refund-policy.html']

for filename in files_to_update:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only add if not already present
        if 'id="sidebarOverlay"' not in content:
            # Insert right after <body>
            content = re.sub(r'(<body[^>]*>)', r'\1\n' + sidebar_html, content, count=1)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Added sidebar HTML to {filename}")

# Now update main.js
with open('js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Revert my previous hamburgerMenu logic in toggleMobileMenu
js_content = js_content.replace("    if (DOM.hamburgerMenu) DOM.hamburgerMenu.classList.toggle('active');\n", "")
# Revert my previous hamburgerMenu logic in initEventListeners
js_content = js_content.replace("""    if (DOM.hamburgerMenu) {
        DOM.hamburgerMenu.addEventListener('click', toggleMobileMenu);
    }\n""", "")

# Add Sidebar Logic to initEventListeners
sidebar_js = """
    // ========================================
    // Sidebar Logic
    // ========================================
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');
    
    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (sidebarOverlay) sidebarOverlay.classList.add('active');
    }
    
    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
    }
    
    if (DOM.hamburgerMenu) {
        DOM.hamburgerMenu.addEventListener('click', openSidebar);
    }
    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Close sidebar if support link clicked
    const sidebarSupport = document.getElementById('sidebarSupport');
    if (sidebarSupport) {
        sidebarSupport.addEventListener('click', closeSidebar);
    }
    
    // Feedback modal from sidebar
    const feedbackLink = document.getElementById('feedbackLink');
    const feedbackModal = document.getElementById('feedbackModal');
    if (feedbackLink && feedbackModal) {
        feedbackLink.addEventListener('click', function(e) {
            e.preventDefault();
            closeSidebar();
            feedbackModal.classList.add('active');
        });
    }
"""

if "// Sidebar Logic" not in js_content:
    # Insert right before // Slider Controls in initEventListeners
    js_content = js_content.replace("    // Slider Controls", sidebar_js + "\n    // Slider Controls")

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated main.js with beautiful sidebar logic")

