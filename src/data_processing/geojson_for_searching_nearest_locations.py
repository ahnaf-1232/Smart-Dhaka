import json

# Input GeoJSON file path
input_file = "C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/data/raw/emergencyLocations.geojson"

# Output JSON file path
output_file = "categorized_dataset.json"

def process_geojson_by_category(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    categorized_data = {}

    # Process each feature in the GeoJSON
    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        # Determine the category
        if "amenity" in properties:
            category = properties["amenity"]
        elif "highway" in properties:
            category = properties["highway"]
        elif "railway" in properties:
            category = properties["railway"]
        elif "leisure" in properties:
            category = properties["leisure"]
        elif "tourism" in properties:
            category = properties["tourism"]
        elif "shop" in properties:
            category = properties["shop"]
        else:
            category = "Unknown"

        # Prepare the node data
        node_data = {
            "id": feature.get("id", "Unknown"),
            "name": properties.get("name", "Unknown"),
            "name:en": properties.get("name:en", "Unknown"),
            "lat": coordinates[1] if len(coordinates) > 1 else None,
            "lng": coordinates[0] if len(coordinates) > 1 else None,
        }

        # Add the node to the appropriate category
        if category not in categorized_data:
            categorized_data[category] = []
        categorized_data[category].append(node_data)

    # Save the categorized data to a JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(categorized_data, f, ensure_ascii=False, indent=4)

    print(f"Categorized data saved to {output_path}")

# Run the processing function
process_geojson_by_category(input_file, output_file)
