import os

filepath = 'js/auth-guard.js'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the startLoginTimer implementation to do nothing
old_timer = """
    startLoginTimer: function () {
        if (this.timer) clearTimeout(this.timer);
        
        // Skip timer if Supabase is unreachable (development/test mode fallback)
        if (window.isSupabaseConnected && !window.isSupabaseConnected()) {
            console.log('🛡️ Supabase unreachable: AuthGuard timer suspended.');
            return;
        }

        console.log('⏳ Login timer started (1 minute)');

        this.timer = setTimeout(() => {
            this.showLoginModal();
        }, this.checkInterval);
    },
"""

new_timer = """
    startLoginTimer: function () {
        // Disabled based on user request to remove login popup
        return;
    },
"""

if old_timer.strip() in content:
    content = content.replace(old_timer.strip(), new_timer.strip())
    with open(filepath, 'w') as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("Could not find old_timer exact match. Trying regex.")
    import re
    content = re.sub(r'startLoginTimer:\s*function\s*\(\)\s*\{.*?\},', new_timer.strip() + ',', content, flags=re.DOTALL)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Replaced with regex.")
