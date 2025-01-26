import json

def extract_categories(input_file, output_file):
    """
    Extracts unique categories from the input JSON file and saves them to a list.
    """
    try:
        # Load the input JSON data
        with open(input_file, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        
        features = data.get("features", [])
        unique_categories = set()

        # Extract categories from the properties
        for feature in features:
            properties = feature.get("properties", {})
            
            for key in ["amenity", "highway", "leisure", "tourism", "shop"]:
                if key in properties:
                    unique_categories.add(properties[key])
                    break

        # Save the unique categories to the output file
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(sorted(list(unique_categories)), outfile, indent=4, ensure_ascii=False)
        
        print(f"Categories extracted successfully. Output saved to {output_file}")
    
    except Exception as e:
        print(f"Error extracting categories: {e}")

# Input and output file paths
input_file = "C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/data/raw/emergencyLocations.geojson"  # Replace with your input file path
output_file = "categories.json"  # Replace with your output file path

# Run the category extraction function
extract_categories(input_file, output_file)
