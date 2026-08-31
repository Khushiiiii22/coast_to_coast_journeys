def match_rooms(rate_room, static_rooms):
    rate_tokens = set(rate_room.lower().replace(',', ' ').split())
    best_match = None
    best_score = 0
    
    for static_name in static_rooms:
        static_tokens = set(static_name.lower().replace(',', ' ').split())
        
        # Calculate Jaccard similarity or simple intersection
        intersection = rate_tokens.intersection(static_tokens)
        
        # If rate is "Deluxe Double room" and static is "Deluxe Room"
        # intersection = {"deluxe", "room"} (size 2)
        score = len(intersection) / len(rate_tokens.union(static_tokens))
        
        if score > best_score:
            best_score = score
            best_match = static_name
            
    return best_match, best_score

rate_name = "Deluxe Horizon Double room"
static_names = ["Deluxe Room", "Deluxe Horizon Room", "Standard Room", "Executive Suite"]
print(match_rooms(rate_name, static_names))
