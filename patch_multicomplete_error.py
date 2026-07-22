import sys

file_path = "backend/routes/hotel_routes.py"
with open(file_path, "r") as f:
    content = f.read()

# Locate the STEP 2 fallback block
marker = """        if not region_id and not hotel_ids_to_search:
            print(f"🛑 Could not resolve destination: '{data['destination']}'")
            return jsonify({
                'success': False,
                'error': f"Could not find destination '{data['destination']}'. Please check the spelling or try a different search term.",
                'hotels': [],
                'source': 'none'
            })"""

replacement = """        if not region_id and not hotel_ids_to_search:
            print(f"🛑 Could not resolve destination: '{data['destination']}'")
            # If RateHawk multicomplete actually returned an API error (like 403), surface it!
            error_msg = "Could not find destination. Please check the spelling."
            if 'suggest_result' in locals() and not suggest_result.get('success'):
                error_msg = f"RateHawk Multicomplete API Error: {suggest_result.get('error', 'Unknown Error')}"
                print(f"⚠️ {error_msg}")
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 502

            return jsonify({
                'success': False,
                'error': error_msg,
                'hotels': [],
                'source': 'none'
            }), 404"""

if marker not in content:
    print("Marker not found!")
    sys.exit(1)

new_content = content.replace(marker, replacement)

with open(file_path, "w") as f:
    f.write(new_content)

print("Multicomplete error handling patched successfully.")
