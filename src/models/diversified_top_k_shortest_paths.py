import heapq
import googlemaps
from typing import List, Dict, Tuple

class DiversifiedTopKShortestPaths:
    def __init__(self, graph: Dict[str, List[Tuple[str, float]]], similarity_threshold: float, k: int):
        self.graph = graph
        self.similarity_threshold = similarity_threshold
        self.k = k
        self.gmaps = googlemaps.Client(key="AIzaSyAspJAIzFtVEWwOYAoUdJU0eLGrDssz1jk")

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
    
    def get_live_data(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, float]:
        """
        Fetch live traffic and road data from Google Maps.
        """
        print(f"Fetching live data for {start_coords} to {end_coords}...")
        try:
            directions = self.gmaps.directions(
                origin=start_coords,
                destination=end_coords,
                mode="driving",
                departure_time="now"  # For live traffic
            )
            if not directions:
                return {"traffic_density": 1, "construction_zone": 0, "road_width": 2}  # Default values

            # Parse traffic density and check for construction zones
            legs = directions[0]["legs"][0]
            traffic_density = legs.get("duration_in_traffic", {}).get("value", legs["duration"]["value"])
            road_width = 2  # Assume car and motorcycle-friendly by default (adjust as needed)

            # Example: Identify construction zones from warnings (if available in the API)
            construction_zone = any("construction" in step["html_instructions"].lower()
                                     for step in legs["steps"])

            return {
                "traffic_density": traffic_density,
                "construction_zone": 1 if construction_zone else 0,
                "road_width": road_width,
            }
        except Exception as e:
            print(f"Error fetching Google Maps data: {e}")
            return {"traffic_density": 1, "construction_zone": 0, "road_width": 2}  # Default fallback

    def calculate_path_weight(self, path: List[str], raw_data: Dict[str, Dict]):
        """
        Calculate the weight for a path based on live data.
        """
        print(f"Calculating weight for path: {path}")
        total_weight = 0
        for i in range(len(path) - 1):
            start_node = raw_data["nodes"][path[i]]
            end_node = raw_data["nodes"][path[i + 1]]

            # Fetch live data for the edge
            live_data = self.get_live_data(
                start_coords=(start_node["location"][0], start_node["location"][1]),
                end_coords=(end_node["location"][0], end_node["location"][1])
            )

            # Example weight calculation
            weight = (live_data["traffic_density"] * 0.5 +
                      live_data["construction_zone"] * 2 +
                      (3 if live_data["road_width"] < 2 else 0))  # Penalize narrow roads

            total_weight += weight

        return total_weight

    def suggest_best_path(self, paths: List[List[str]], raw_data: Dict[str, Dict]) -> List[str]:
        """
        Suggest the best path based on calculated weights.
        """
        print("Suggesting best path...")
        weighted_paths = [
            (path, self.calculate_path_weight(path, raw_data)) for path in paths
        ]
        # Sort paths by weight (ascending order for best suggestion)
        weighted_paths.sort(key=lambda x: x[1])
        return weighted_paths[0][0]
