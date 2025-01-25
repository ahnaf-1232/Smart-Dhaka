import json
from geopy.geocoders import Nominatim
from time import sleep

# Initialize the geocoder
geolocator = Nominatim(user_agent="geo-enrichment")

# File paths
input_file = "C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/data/raw/dhaka_osmnx_data.json"  # Input relative path
output_file = "../../data/dhaka_enriched_data.json"  # Output relative path

# Function to fetch the place name using geocoding
def get_place_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else "Unknown"
    except Exception as e:
        print(f"Error fetching place name for ({lat}, {lon}): {e}")
        return "Unknown"

# Load the input data
try:
    with open(input_file, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"File not found: {input_file}")
    exit(1)

# Process nodes to add place names
for node_id, node_info in data["nodes"].items():
    lat, lon = node_info["location"]
    print(f"Processing Node: {node_id}, Location: ({lat}, {lon})")
    
    # Fetch the place name
    place_name = get_place_name(lat, lon)
    
    # Add place name to the node info
    node_info["place_name"] = place_name
    
    # To avoid hitting API rate limits, add a delay
    sleep(1)  # Adjust delay as needed

# Save the enriched data back to a file
with open(output_file, "w") as f:
    json.dump(data, f, indent=4)

print(f"Enriched data saved to {output_file}")
