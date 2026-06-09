from database.database import fetch_all

class RouteOptimizer:
    @staticmethod
    def get_graph_matrix():
        rows = fetch_all("SELECT from_location, to_location, travel_time FROM travel_times")
        graph = {}
        for row in rows:
            u, v, w = row['from_location'], row['to_location'], row['travel_time']
            if u not in graph: graph[u] = {}
            graph[u][v] = w
        return graph

    @classmethod
    def calculate_optimal_path(cls, destination_nodes):
        """Calculates path sequence starting at Restaurant 'R' tracking through node strings."""
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
            
            for neighbor in unvisited:
                if current_node in graph and neighbor in graph[current_node]:
                    distance = graph[current_node][neighbor]
                    if distance < shortest_distance:
                        shortest_distance = distance
                        nearest_neighbor = neighbor
            
            # Fallback handling for disconnected topological layouts
            if nearest_neighbor is None:
                nearest_neighbor = unvisited[0]
                shortest_distance = 15 # Constant fallback value
                
            total_time += shortest_distance
            route.append(nearest_neighbor)
            unvisited.remove(nearest_neighbor)
            current_node = nearest_neighbor
            
        return route, total_time