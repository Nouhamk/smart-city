import csv

# City data: (name, latitude, longitude)
cities = [
    ("new york", 40.7128, -74.0060),
    ("los angeles", 34.0522, -118.2437),
    ("london", 51.5074, -0.1278),
    ("paris", 48.8566, 2.3522),
    ("berlin", 52.5200, 13.4050),
    ("tokyo", 35.6895, 139.6917),
    ("beijing", 39.9042, 116.4074),
    ("moscow", 55.7558, 37.6173),
    ("cairo", 30.0444, 31.2357),
    ("sydney", -33.8688, 151.2093),
    ("sao paulo", -23.5505, -46.6333),
    ("mexico city", 19.4326, -99.1332),
    ("mumbai", 19.0760, 72.8777),
    ("tronto", 43.6511, -79.3832),
    ("istanbul", 41.0082, 28.9784)
]

# Write to CSV (no header)
with open("cities_with_header.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["name", "longitude", "latitude"])  # Header row
    for name, lat, lon in cities:
        writer.writerow([name, lon, lat])  # Order: name, longitude, latitude