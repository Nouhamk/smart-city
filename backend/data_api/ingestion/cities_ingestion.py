from data_api.supabase.database import save_cities

cities = [
    {"name": "new york", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "los angeles", "latitude": 34.0522, "longitude": -118.2437},
    {"name": "london", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "paris", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "berlin", "latitude": 52.5200, "longitude": 13.4050},
    {"name": "tokyo", "latitude": 35.6895, "longitude": 139.6917},
    {"name": "beijing", "latitude": 39.9042, "longitude": 116.4074},
    {"name": "moscow", "latitude": 55.7558, "longitude": 37.6173},
    {"name": "cairo", "latitude": 30.0444, "longitude": 31.2357},
    {"name": "sydney", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "sao paulo", "latitude": -23.5505, "longitude": -46.6333},
    {"name": "mexico city", "latitude": 19.4326, "longitude": -99.1332},
    {"name": "mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "toronto", "latitude": 43.6511, "longitude": -79.3832},
    {"name": "istanbul", "latitude": 41.0082, "longitude": 28.9784}
]

def get_all_regions(): # On peut améliorer redondance
    return list(map(lambda x: x["name"].lower(), cities))

def get_coorindates(city_name):
    city = filter(lambda x: x["name"] == city_name, cities)[0]

    return city["latitude"], city["longitude"]

def save_cities_to_supabase():
    save_cities(cities)