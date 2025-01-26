from flask import Flask, jsonify, request
from config import GRAPH_DATA, SIMILARITY_THRESHOLD, K
from models.diversified_top_k_shortest_paths import DiversifiedTopKShortestPaths
from models.node_finder import NodeGraph
from dotenv import load_dotenv
import os
import json
from geopy.distance import geodesic

# Load environment variables from .env file
load_dotenv()

# Get the API key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = Flask(__name__)

# Load the graph and node data
def load_graph(file_path: str):
    with open(file_path) as f:
        data = json.load(f)

    node_graph = NodeGraph()
    graph = {}

    for node, edges in data['edges'].items():
        graph[node] = [(neighbor, weight) for neighbor, weight in edges.items()]

    for node_id, node_info in data['nodes'].items():
        node_graph.add_node(node_id, node_info['name'], node_info['location'])

    return graph, node_graph, data

graph, node_graph, raw_data = load_graph(GRAPH_DATA)

with open('C:/Users/Ahnaf-1466/Documents/GitHub/Smart-Dhaka/data/raw/categorized_dataset.json', 'r', encoding='utf-8') as f:
    category_data = json.load(f)

class NearestEntityFinder:
    def __init__(self, data):
        self.data = data

    def find_nearest_entity(self, lat, lon, category):
        if category not in self.data:
            return None

        entities = self.data[category]
        current_location = (lat, lon)
        
        nearest_entity = None
        nearest_distance = float('inf')

        for entity in entities:
            entity_location = (entity['lat'], entity['lng'])
            distance = geodesic(current_location, entity_location).meters

            if distance < nearest_distance:
                nearest_entity = entity
                nearest_distance = distance

        return nearest_entity

# Initialize the finder with the category data
entity_finder = NearestEntityFinder(category_data)

@app.route('/map-data', methods=['GET'])
def map_data():
    """
    Endpoint to serve nodes and edges in a format suitable for visualization
    """
    nodes = [
        {"id": node_id, "name": node_data["name"], "latitude": node_data["location"][0], "longitude": node_data["location"][1]}
        for node_id, node_data in raw_data["nodes"].items()
    ]

    edges = [
        {"start": start_node, "end": end_node, "distance": weight}
        for start_node, connections in raw_data["edges"].items()
        for end_node, weight in connections.items()
    ]

    return jsonify({"nodes": nodes, "edges": edges})


@app.route('/shortest-paths', methods=['GET'])
def shortest_paths():
    """
    Endpoint to get the best shortest path based on live data from OpenStreetMap
    """
    print("Fetching shortest path...")
    try:
        # Get the origin and destination from query params
        origin_lat = float(request.args.get('origin_lat'))
        origin_lon = float(request.args.get('origin_lon'))
        target_lat = float(request.args.get('target_lat'))
        target_lon = float(request.args.get('target_lon'))

        # Find nearest nodes
        start_node = node_graph.find_nearest_node(origin_lat, origin_lon)
        target_node = node_graph.find_nearest_node(target_lat, target_lon)

        # Compute diversified top-k shortest paths
        dtksp = DiversifiedTopKShortestPaths(graph, SIMILARITY_THRESHOLD, K)
        paths = dtksp.diversified_top_k_paths(start_node, target_node)

        if not paths:
            return jsonify({"error": "No paths found"}), 404

        # Suggest the best path based on weights
        best_path = dtksp.suggest_best_path(paths, raw_data)

        # Format the path with coordinates
        formatted_path = [
            {
                "id": node_id,
                "name": raw_data["nodes"][node_id]["name"],
                "latitude": raw_data["nodes"][node_id]["location"][0],
                "longitude": raw_data["nodes"][node_id]["location"][1],
            }
            for node_id in best_path
            if node_id in raw_data["nodes"]
        ]

        return jsonify({"path": formatted_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/nearest-entity', methods=['GET'])
def get_nearest_entity_and_shortest_path():
    try:
        # Get latitude, longitude, and category from the request
        origin_lat = float(request.args.get('lat'))
        origin_lon = float(request.args.get('lon'))
        category = request.args.get('category').lower()

        # Find the nearest entity
        nearest_entity = entity_finder.find_nearest_entity(origin_lat, origin_lon, category)

        print(f"Nearest entity: {nearest_entity}")

        if not nearest_entity:
            return jsonify({"error": "No entities found for the given category."}), 404

        # Extract target latitude and longitude from the nearest entity
        target_lat = nearest_entity['lat']
        target_lon = nearest_entity['lng']

        print(f"Target location: ({target_lat}, {target_lon})")
        print("Fetching shortest path...")

        # Find nearest nodes for origin and target
        start_node = node_graph.find_nearest_node(origin_lat, origin_lon)
        target_node = node_graph.find_nearest_node(target_lat, target_lon)

        # Compute diversified top-k shortest paths
        dtksp = DiversifiedTopKShortestPaths(graph, SIMILARITY_THRESHOLD, K)
        paths = dtksp.diversified_top_k_paths(start_node, target_node)

        print(f"Found {len(paths)} paths")

        if not paths:
            return jsonify({"error": "No paths found"}), 404

        # Suggest the best path based on weights
        best_path = dtksp.suggest_best_path(paths, raw_data)

        # Format the path with coordinates
        formatted_path = [
            {
                "id": node_id,
                "name": raw_data["nodes"][node_id]["name"],
                "latitude": raw_data["nodes"][node_id]["location"][0],
                "longitude": raw_data["nodes"][node_id]["location"][1],
            }
            for node_id in best_path
            if node_id in raw_data["nodes"]
        ]

        # Return the nearest entity and the shortest path
        return jsonify({
            "nearest_entity": nearest_entity,
            "path": formatted_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/find-nearest-entity-only', methods=['GET'])
def get_nearest_entity_only():
    try:
        # Get latitude, longitude, and category from the request
        origin_lat = float(request.args.get('lat'))
        origin_lon = float(request.args.get('lon'))
        category = request.args.get('category').lower()

        # Find the nearest entity
        nearest_entity = entity_finder.find_nearest_entity(origin_lat, origin_lon, category)

        print(f"Nearest entity: {nearest_entity}")

        if not nearest_entity:
            return jsonify({"error": "No entities found for the given category."}), 404

        # Return the nearest entity and the shortest path
        return jsonify({
            "nearest_entity": nearest_entity,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
