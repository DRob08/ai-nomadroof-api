import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_true(val):
    return str(val).strip().lower() in ("true", "1", "yes")

def properties_near_universities(properties, university_coords, radius_km=5.0):
    results = {}
    for name, coords in university_coords.items():
        nearby = []
        for p in properties:
            try:
                lat = float(p.property_latitude)
                lon = float(p.property_longitude)
                distance = haversine(lat, lon, coords[0], coords[1])
                if distance <= radius_km:
                    nearby.append((p, round(distance, 2)))
            except (TypeError, ValueError):
                continue
        results[name] = nearby
    return results

def get_university_summary(universities_proximity, radius_km=5.0):
    return "\n".join(
        f"{len(props)} properties are within {radius_km} of {uni}" for uni, props in universities_proximity.items()
    )
