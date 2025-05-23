import csv

# City data: (name, latitude, longitude)
cities = [
    ("New York", 40.7128, -74.0060),
    ("Los Angeles", 34.0522, -118.2437),
    ("London", 51.5074, -0.1278),
    ("Paris", 48.8566, 2.3522),
    ("Berlin", 52.5200, 13.4050),
    ("Tokyo", 35.6895, 139.6917),
    ("Beijing", 39.9042, 116.4074),
    ("Moscow", 55.7558, 37.6173),
    ("Cairo", 30.0444, 31.2357),
    ("Sydney", -33.8688, 151.2093),
    ("São Paulo", -23.5505, -46.6333),
    ("Mexico City", 19.4326, -99.1332),
    ("Mumbai", 19.0760, 72.8777),
    ("Toronto", 43.6511, -79.3832),
    ("Istanbul", 41.0082, 28.9784)
]

# Write to CSV (no header)
with open("cities_with_header.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["name", "longitude", "latitude"])  # Header row
    for name, lat, lon in cities:
        writer.writerow([name, lon, lat])  # Order: name, longitude, latitude