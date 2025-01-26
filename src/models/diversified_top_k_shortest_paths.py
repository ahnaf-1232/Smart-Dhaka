import heapq
import googlemaps
from typing import List, Dict, Tuple
from functools import lru_cache

class DiversifiedTopKShortestPaths:
    def __init__(self, graph: Dict[str, List[Tuple[str, float]]], similarity_threshold: float, k: int):
        self.graph = graph
        self.similarity_threshold = similarity_threshold
        self.k = k
        self.gmaps = googlemaps.Client(key="AIzaSyAspJAIzFtVEWwOYAoUdJU0eLGrDssz1jk")
        self.edge_weights = {}

    def similarity(self, path1: List[str], path2: List[str]) -> float:
        # Implement a similarity function (e.g., Jaccard similarity) 
        intersection = len(set(path1) & set(path2))
        union = len(set(path1) | set(path2))
        return intersection / union if union != 0 else 0

    def find_shortest_paths(self, start: str, target: str) -> List[List[str]]:
        # Priority queue for Dijkstra's algorithm: stores tuples of (cost, path)
        min_heap = [(0, [start])]
        # List to store the k shortest paths
        paths = []
        # Dictionary to keep track of the minimum cost to reach each node
        min_cost = {start: 0}

        while min_heap and len(paths) < self.k:
            # Pop the path with the smallest cost
            cost, path = heapq.heappop(min_heap)
            node = path[-1]

            # Check if we reached the target node
            if node == target:
                paths.append(path)
                continue

            # Explore neighbors
            for neighbor, weight in self.graph.get(node, []):
                new_cost = cost + weight

                # Only consider this path if it provides a cheaper way to reach `neighbor`
                if neighbor not in min_cost or new_cost < min_cost[neighbor]:
                    min_cost[neighbor] = new_cost
                    heapq.heappush(min_heap, (new_cost, path + [neighbor]))

        return paths

    def diversified_top_k_paths(self, start: str, target: str) -> List[List[str]]:
        all_paths = self.find_shortest_paths(start, target)
        diversified_paths = []

        for path in all_paths:
            if all(self.similarity(path, p) <= self.similarity_threshold for p in diversified_paths):
                diversified_paths.append(path)
                if len(diversified_paths) == self.k:
                    break

        return diversified_paths
    
    @lru_cache(maxsize=1000)
    def get_live_data(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, float]:
        # print(f"Fetching live data for {start_coords} to {end_coords}...")
        try:
            directions = self.gmaps.directions(
                origin=start_coords,
                destination=end_coords,
                mode="driving",
                departure_time="now"
            )
            if not directions:
                return {"traffic_density": 1, "construction_zone": 0, "road_width": 2}  # Default values

            legs = directions[0]["legs"][0]
            traffic_density = legs.get("duration_in_traffic", {}).get("value", legs["duration"]["value"])
            road_width = 2  # Assume car and motorcycle-friendly by default
            construction_zone = any("construction" in step["html_instructions"].lower() for step in legs["steps"])

            return {
                "traffic_density": traffic_density,
                "construction_zone": 1 if construction_zone else 0,
                "road_width": road_width,
            }
        except Exception as e:
            print(f"Error fetching Google Maps data: {e}")
            return {"traffic_density": 1, "construction_zone": 0, "road_width": 2}  # Fallback values

    def calculate_edge_weight(self, start_node: str, end_node: str, raw_data: Dict[str, Dict]):
        if (start_node, end_node) in self.edge_weights:
            return self.edge_weights[(start_node, end_node)]

        start_coords = raw_data["nodes"][start_node]["location"]
        end_coords = raw_data["nodes"][end_node]["location"]
        live_data = self.get_live_data(tuple(start_coords), tuple(end_coords))

        weight = (live_data["traffic_density"] * 0.5 +
                  live_data["construction_zone"] * 2 +
                  (3 if live_data["road_width"] < 2 else 0))
        self.edge_weights[(start_node, end_node)] = weight
        return weight

    def calculate_path_weight(self, path: List[str], raw_data: Dict[str, Dict]):
        total_weight = 0
        for i in range(len(path) - 1):
            total_weight += self.calculate_edge_weight(path[i], path[i + 1], raw_data)
        return total_weight

    def suggest_best_path(self, paths: List[List[str]], raw_data: Dict[str, Dict]) -> List[str]:
        print("Suggesting best path...")
        weighted_paths = [(path, self.calculate_path_weight(path, raw_data)) for path in paths]
        weighted_paths.sort(key=lambda x: x[1])  # Sort by weight (ascending)
        return weighted_paths[0][0]