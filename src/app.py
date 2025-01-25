from flask import Flask, jsonify, request
from config import GRAPH_DATA, SIMILARITY_THRESHOLD, K
from models.diversified_top_k_shortest_paths import DiversifiedTopKShortestPaths
from models.node_finder import NodeGraph
from dotenv import load_dotenv
import os
import json

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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
