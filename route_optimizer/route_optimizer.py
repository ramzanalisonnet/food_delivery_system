from database.database import fetch_all
import heapq

class RouteOptimizer:
    @staticmethod
    def get_graph_matrix():
        """Build adjacency list from travel_times table."""
        rows = fetch_all("SELECT from_location, to_location, travel_time FROM travel_times")
        graph = {}
        for row in rows:
            u, v, w = row['from_location'], row['to_location'], row['travel_time']
            if u not in graph:
                graph[u] = {}
            graph[u][v] = w
        return graph

    @classmethod
    def calculate_shortest_path(cls, start, end):
        """Dijkstra's algorithm for shortest path between two nodes."""
        graph = cls.get_graph_matrix()
        
        if start not in graph or end not in graph:
            return None, float('inf')
        
        # Dijkstra's algorithm
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                break
            
            if current_node in graph:
                for neighbor, weight in graph[current_node].items():
                    distance = current_dist + weight
                    if distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = distance
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        if distances.get(end, float('inf')) == float('inf'):
            return None, float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]

    @classmethod
    def calculate_optimal_path(cls, destination_nodes):
        """
        Nearest Neighbor heuristic for multi-stop delivery route.
        Starts at Restaurant 'R', visits all destination nodes.
        Falls back to Dijkstra if no direct edge exists.
        """
        if not destination_nodes:
            return ["R"], 0
        
        graph = cls.get_graph_matrix()
        current_node = "R"
        unvisited = list(set(destination_nodes))
        route = ["R"]
        total_time = 0
        
        while unvisited:
            nearest_neighbor = None
            shortest_distance = float('inf')
            best_path = None
            
            for neighbor in unvisited:
                if current_node in graph and neighbor in graph[current_node]:
                    # Direct edge exists
                    distance = graph[current_node][neighbor]
                    if distance < shortest_distance:
                        shortest_distance = distance
                        nearest_neighbor = neighbor
                        best_path = [current_node, neighbor]
                else:
                    # Use Dijkstra for indirect path
                    alt_path, alt_dist = cls.calculate_shortest_path(current_node, neighbor)
                    if alt_path and alt_dist < shortest_distance:
                        shortest_distance = alt_dist
                        nearest_neighbor = neighbor
                        best_path = alt_path
            
            # If no path found at all, use heuristic fallback
            if nearest_neighbor is None:
                nearest_neighbor = unvisited[0]
                shortest_distance = 20  # Conservative estimate
                best_path = [current_node, nearest_neighbor]
            
            # Add intermediate nodes to route (skip first as it's current)
            if best_path:
                for node in best_path[1:]:
                    route.append(node)
            
            total_time += shortest_distance
            unvisited.remove(nearest_neighbor)
            current_node = nearest_neighbor
        
        # Clean up route to show only R + destinations
        final_route = ["R"]
        for node in route[1:]:
            if node in destination_nodes or node == "R":
                final_route.append(node)
        
        return final_route, total_time