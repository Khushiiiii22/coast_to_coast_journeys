import sys

file_path = "backend/routes/hotel_routes.py"
with open(file_path, "r") as f:
    content = f.read()

# We need to remove the fast-path section
start_marker = "        # 1a. Quick match from popular destinations (speed optimization only)"
end_marker = "        # 1b. PRIMARY: Resolve ANY destination via RateHawk multicomplete API"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Markers not found!")
    sys.exit(1)

new_content = content[:start_idx] + content[end_idx:]

with open(file_path, "w") as f:
    f.write(new_content)

print("Patch applied successfully.")
