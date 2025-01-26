import json

# Load the JSON data
with open('C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/src/data_processing/bd_datas.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Filter upazillas with district_id = 47
selected_upazillas = [
    upazilla for upazilla in data["upazillas"]["data"] if upazilla["district_id"] == "47"
]

# Extract the IDs of the selected upazillas
selected_upazilla_ids = {upazilla["id"] for upazilla in selected_upazillas}

# Filter unions corresponding to the selected upazillas
selected_unions = [
    union for union in data["unions"]["data"] if union["upazilla_id"] in selected_upazilla_ids
]

# Create the filtered output structure
filtered_data = {
    "upazillas": {
        "type": data["upazillas"]["type"],
        "name": data["upazillas"]["name"],
        "database": data["upazillas"]["database"],
        "data": selected_upazillas,
    },
    "unions": {
        "type": data["unions"]["type"],
        "name": data["unions"]["name"],
        "database": data["unions"]["database"],
        "data": selected_unions,
    },
}

# Save the filtered data to a new JSON file
with open('filtered_bd_datas.json', 'w', encoding='utf-8') as file:
    json.dump(filtered_data, file, ensure_ascii=False, indent=4)

print("Filtered data saved to 'filtered_data.json'")
