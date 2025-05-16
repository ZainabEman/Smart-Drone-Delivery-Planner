"""
Shortest path algorithm implementation using Dijkstra's algorithm.

This module provides functions to find the shortest path between cities
in the city map using Dijkstra's algorithm.
"""

import heapq
from collections import defaultdict

def dijkstra(city_map, start_city_name):
    """
    Implements Dijkstra's algorithm to find shortest paths from a start city to all other cities.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        start_city_name (str): The name of the starting city
        
    Returns:
        tuple: (distances, predecessors) where:
            - distances is a dict mapping city names to their shortest distance from start
            - predecessors is a dict mapping city names to their predecessor in the shortest path
            
    Raises:
        ValueError: If the start city does not exist in the map
    """
    if start_city_name not in city_map.cities:
        raise ValueError(f"City '{start_city_name}' does not exist in the map")
    
    # Initialize distances with infinity for all cities except the start city
    distances = {city_name: float('infinity') for city_name in city_map.cities}
    distances[start_city_name] = 0
    
    # Initialize predecessors dictionary
    predecessors = {city_name: None for city_name in city_map.cities}
    
    # Priority queue for cities to visit (distance, city_name)
    pq = [(0, start_city_name)]
    
    # Set to keep track of visited cities
    visited = set()
    
    while pq:
        # Get city with smallest distance
        current_distance, current_city = heapq.heappop(pq)
        
        # Skip if already visited
        if current_city in visited:
            continue
        
        # Mark as visited
        visited.add(current_city)
        
        # If we've visited all cities, we can stop
        if len(visited) == len(city_map.cities):
            break
        
        # Check all neighbors
        for neighbor, weight in city_map.get_neighbors(current_city).items():
            if neighbor in visited:
                continue
                
            # Calculate new distance
            distance = current_distance + weight
            
            # If we found a shorter path, update distance and predecessor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_city
                heapq.heappush(pq, (distance, neighbor))
    
    return distances, predecessors

def get_shortest_path(city_map, start_city_name, end_city_name):
    """
    Find the shortest path between two cities.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        start_city_name (str): The name of the starting city
        end_city_name (str): The name of the destination city
        
    Returns:
        tuple: (path, distance) where:
            - path is a list of city names representing the shortest path
            - distance is the total distance of the path
            
    Raises:
        ValueError: If either city does not exist in the map or if no path exists
    """
    if start_city_name not in city_map.cities:
        raise ValueError(f"City '{start_city_name}' does not exist in the map")
    if end_city_name not in city_map.cities:
        raise ValueError(f"City '{end_city_name}' does not exist in the map")
    
    # If start and end are the same, return a path with just that city
    if start_city_name == end_city_name:
        return [start_city_name], 0
    
    # Run Dijkstra's algorithm
    distances, predecessors = dijkstra(city_map, start_city_name)
    
    # Check if a path exists
    if distances[end_city_name] == float('infinity'):
        raise ValueError(f"No path exists from '{start_city_name}' to '{end_city_name}'")
    
    # Reconstruct the path
    path = []
    current = end_city_name
    
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    # Reverse the path to get it from start to end
    path.reverse()
    
    return path, distances[end_city_name]

def get_all_shortest_paths(city_map, start_city_name):
    """
    Find shortest paths from a start city to all other cities.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        start_city_name (str): The name of the starting city
        
    Returns:
        dict: Dictionary mapping destination city names to (path, distance) tuples
        
    Raises:
        ValueError: If the start city does not exist in the map
    """
    if start_city_name not in city_map.cities:
        raise ValueError(f"City '{start_city_name}' does not exist in the map")
    
    # Run Dijkstra's algorithm
    distances, predecessors = dijkstra(city_map, start_city_name)
    
    # Construct paths to all cities
    paths = {}
    
    for end_city_name in city_map.cities:
        # Skip unreachable cities
        if distances[end_city_name] == float('infinity'):
            continue
        
        # Reconstruct the path
        path = []
        current = end_city_name
        
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        # Reverse the path to get it from start to end
        path.reverse()
        
        paths[end_city_name] = (path, distances[end_city_name])
    
    return paths
