import sys

file_path = "backend/routes/hotel_routes.py"
with open(file_path, "r") as f:
    content = f.read()

# Locate the error handling block in STEP 3
marker = """            # If it's a date validation error, return early with helpful message
            if any(kw in str(error_msg).lower() for kw in ['checkin', 'checkout', 'date']):
                return jsonify({
                    'success': False, 
                    'error': f"Search failed: {error_msg}. Please check your dates and try again."
                }), 400"""

replacement = """            # If it's a date validation error, return early with helpful message
            if any(kw in str(error_msg).lower() for kw in ['checkin', 'checkout', 'date']):
                return jsonify({
                    'success': False, 
                    'error': f"Search failed: {error_msg}. Please check your dates and try again."
                }), 400
                
            # For all other RateHawk API errors (like 403 Forbidden, 401 Unauthorized, etc.)
            # we MUST return an HTTP error so the frontend can display the actual reason
            # it failed, rather than silently pretending there are 0 hotels.
            return jsonify({
                'success': False,
                'error': f"RateHawk API Error: {error_msg}"
            }), 502  # 502 Bad Gateway (upstream error)"""

if marker not in content:
    print("Marker not found!")
    sys.exit(1)

new_content = content.replace(marker, replacement)

with open(file_path, "w") as f:
    f.write(new_content)

print("Error handling patched successfully.")
