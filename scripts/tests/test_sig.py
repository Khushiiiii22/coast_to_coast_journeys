def make_rg_signature(rg_ext):
    if not isinstance(rg_ext, dict):
        return ""
    STABLE_KEYS = {
        'balcony', 'bathroom', 'bedding', 'bedrooms', 'capacity', 
        'club', 'family', 'quality', 'class', 'sex', 'view'
    }
    parts = []
    for k in sorted(rg_ext.keys()):
        if k in STABLE_KEYS and rg_ext[k] not in (None, 0, '0', ''):
            parts.append(f"{k}:{rg_ext[k]}")
    return ",".join(parts)

static = {'balcony': 0, 'bathroom': 2, 'bedding': 3, 'bedrooms': 0, 'capacity': 2, 'club': 0, 'family': 0, 'floor': 1, 'quality': 2, 'class': 3, 'sex': 0, 'view': 0}
dynamic = {'bathroom': 2, 'bedding': 3, 'capacity': 2, 'quality': 2, 'class': 3}

print("static :", make_rg_signature(static))
print("dynamic:", make_rg_signature(dynamic))
