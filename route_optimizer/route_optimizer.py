from database.database import fetch_all
import heapq


class RouteOptimizer:
    """
    [REQUIREMENT 3: Route Planning & Delivery Optimization]
    Implements route optimization algorithms for courier delivery planning:
    - Nearest Neighbor heuristic for multi-stop delivery routes
    - Dijkstra's algorithm for shortest path between two nodes
    - Graph-based navigation using the simulated map (8 addresses A-H + restaurant R)
    """

    @staticmethod
    def get_graph_matrix():
        """
        [REQUIREMENT 3: Simulated Map Graph]
        Builds adjacency list from travel_times table.
        Returns graph as {from_location: {to_location: travel_time}}
        """
        rows = fetch_all("SELECT from_location, to_location, travel_time FROM travel_times")
        graph = {}
        for row in rows:
            u = row['from_location']
            v = row['to_location']
            w = row['travel_time']
            if u not in graph:
                graph[u] = {}
            graph[u][v] = w
        return graph

    @classmethod
    def calculate_shortest_path(cls, start, end):
        """
        [REQUIREMENT 3: Shortest Path Algorithm]
        Implements Dijkstra's algorithm for finding the optimal path between two locations.
        Returns (path_list, total_distance).
        """
        graph = cls.get_graph_matrix()

        if start not in graph or end not in graph:
            return None, float('inf')

        distances = {}
        previous = {}
        
        for node in graph:
            distances[node] = float('inf')
            previous[node] = None
        
        distances[start] = 0
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
        [REQUIREMENT 3: Multi-Stop Route Optimization]
        Implements Nearest Neighbor heuristic for multi-stop delivery route.
        Always starts from Restaurant 'R' and visits all specified destination nodes.
        
        Args:
            destination_nodes: List of destination addresses (e.g., ['A', 'D'])
        
        Returns:
            (route_list, total_time_minutes)
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
                # Check if direct edge exists
                if current_node in graph and neighbor in graph[current_node]:
                    distance = graph[current_node][neighbor]
                    if distance < shortest_distance:
                        shortest_distance = distance
                        nearest_neighbor = neighbor
                        best_path = [current_node, neighbor]
                else:
                    # Use Dijkstra for indirect paths
                    alt_path, alt_dist = cls.calculate_shortest_path(current_node, neighbor)
                    if alt_path and alt_dist < shortest_distance:
                        shortest_distance = alt_dist
                        nearest_neighbor = neighbor
                        best_path = alt_path

            # Fallback if no path found at all
            if nearest_neighbor is None:
                nearest_neighbor = unvisited[0]
                shortest_distance = 20
                best_path = [current_node, nearest_neighbor]

            # Add ALL nodes from best_path except the first one
            if best_path:
                for node in best_path[1:]:
                    route.append(node)

            total_time += shortest_distance
            unvisited.remove(nearest_neighbor)
            current_node = nearest_neighbor

        return route, total_time