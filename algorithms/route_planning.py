"""
Route planning algorithm for Smart Drone Delivery Planner.

This module provides functions to plan efficient delivery routes
through multiple cities while minimizing total distance.
"""

from itertools import permutations
from .shortest_path import get_shortest_path

def plan_route(city_map, warehouse_city_name, destination_cities):
    """
    Plan an efficient route starting and ending at the warehouse and visiting all destination cities.
    
    This function uses a simple approach for small numbers of destinations:
    - For 1-3 destinations: Try all possible permutations to find the optimal route
    - For more destinations: Use a greedy nearest-neighbor approach
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        warehouse_city_name (str): Name of the warehouse city
        destination_cities (list): List of destination city names to visit
        
    Returns:
        tuple: (route, total_distance) where:
            - route is a list of city names representing the delivery route
            - total_distance is the total distance of the route
            
    Raises:
        ValueError: If any city does not exist in the map or if no feasible route exists
    """
    # Remove duplicates and warehouse from destination list if present
    unique_destinations = list(set(destination_cities))
    if warehouse_city_name in unique_destinations:
        unique_destinations.remove(warehouse_city_name)
    
    # If no destinations, return just the warehouse
    if not unique_destinations:
        return [warehouse_city_name], 0
    
    # Check if all cities exist in the map
    for city in unique_destinations + [warehouse_city_name]:
        if city not in city_map.cities:
            raise ValueError(f"City '{city}' does not exist in the map")
    
    # For small number of destinations, try all permutations
    if len(unique_destinations) <= 3:
        return _find_optimal_route(city_map, warehouse_city_name, unique_destinations)
    else:
        return _find_greedy_route(city_map, warehouse_city_name, unique_destinations)

def _find_optimal_route(city_map, warehouse_city_name, destinations):
    """
    Find the optimal route by trying all permutations of destinations.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        warehouse_city_name (str): Name of the warehouse city
        destinations (list): List of destination city names to visit
        
    Returns:
        tuple: (route, total_distance)
        
    Raises:
        ValueError: If no feasible route exists
    """
    best_route = None
    best_distance = float('infinity')
    
    # Try all permutations of destinations
    for perm in permutations(destinations):
        # Construct route: warehouse -> destinations -> warehouse
        route = [warehouse_city_name]
        route.extend(perm)
        route.append(warehouse_city_name)
        
        # Calculate total distance
        total_distance = 0
        valid_route = True
        
        for i in range(len(route) - 1):
            try:
                _, segment_distance = get_shortest_path(city_map, route[i], route[i+1])
                total_distance += segment_distance
            except ValueError:
                # No path exists between these cities
                valid_route = False
                break
        
        # Update best route if this one is better
        if valid_route and total_distance < best_distance:
            best_route = route
            best_distance = total_distance
    
    # Check if a valid route was found
    if best_route is None:
        raise ValueError("No feasible route exists through all destinations")
    
    return best_route, best_distance

def _find_greedy_route(city_map, warehouse_city_name, destinations):
    """
    Find a route using a greedy nearest-neighbor approach.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        warehouse_city_name (str): Name of the warehouse city
        destinations (list): List of destination city names to visit
        
    Returns:
        tuple: (route, total_distance)
        
    Raises:
        ValueError: If no feasible route exists
    """
    # Start at the warehouse
    route = [warehouse_city_name]
    remaining = set(destinations)
    total_distance = 0
    
    # While there are destinations to visit
    while remaining:
        current = route[-1]
        next_city = None
        min_distance = float('infinity')
        
        # Find the closest unvisited destination
        for dest in remaining:
            try:
                _, distance = get_shortest_path(city_map, current, dest)
                if distance < min_distance:
                    min_distance = distance
                    next_city = dest
            except ValueError:
                # No path exists to this destination
                continue
        
        # If no reachable destination was found
        if next_city is None:
            raise ValueError("No feasible route exists through all destinations")
        
        # Add the next city to the route
        route.append(next_city)
        remaining.remove(next_city)
        total_distance += min_distance
    
    # Return to the warehouse
    try:
        _, return_distance = get_shortest_path(city_map, route[-1], warehouse_city_name)
        route.append(warehouse_city_name)
        total_distance += return_distance
    except ValueError:
        raise ValueError("No feasible route exists back to the warehouse")
    
    return route, total_distance

def get_detailed_route(city_map, route):
    """
    Get a detailed route with all intermediate cities and segment distances.
    
    Args:
        city_map (CityMap): The city map containing cities and routes
        route (list): List of city names representing the high-level route
        
    Returns:
        tuple: (detailed_route, segment_distances, total_distance) where:
            - detailed_route is a list of city names including all intermediate cities
            - segment_distances is a list of distances for each segment
            - total_distance is the total distance of the route
            
    Raises:
        ValueError: If any segment has no feasible path
    """
    detailed_route = [route[0]]
    segment_distances = []
    total_distance = 0
    
    for i in range(len(route) - 1):
        # Get the shortest path for this segment
        segment_path, segment_distance = get_shortest_path(city_map, route[i], route[i+1])
        
        # Add intermediate cities (skip the first as it's already in the route)
        detailed_route.extend(segment_path[1:])
        segment_distances.append(segment_distance)
        total_distance += segment_distance
    
    return detailed_route, segment_distances, total_distance
