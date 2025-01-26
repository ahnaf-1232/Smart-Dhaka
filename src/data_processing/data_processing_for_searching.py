import json

# Input GeoJSON file path
input_file = "C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/data/raw/emergencyLocations.geojson"

# Output JSON file path
output_file = "processed_nodes.json"

def process_geojson_nodes(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    processed_nodes = []

    # Process each feature in the GeoJSON
    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        node_data = {
            "node ID": feature.get("id", "Unknown"),
            "name": properties.get("name", "Unknown"),
            "name:en": properties.get("name:en", "Unknown"),
            "lat": coordinates[1] if len(coordinates) > 1 else None,
            "lng": coordinates[0] if len(coordinates) > 1 else None,
        }
        processed_nodes.append(node_data)

    # Save the processed nodes to a JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_nodes, f, ensure_ascii=False, indent=4)

    print(f"Processed node data saved to {output_path}")

# Run the processing function
process_geojson_nodes(input_file, output_file)
