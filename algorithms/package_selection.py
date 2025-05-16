"""
Package selection algorithm using a variation of the Knapsack algorithm.

This module provides functions to select packages for drone delivery
based on weight constraints and value optimization.
"""

def knapsack_package_selection(packages, max_weight, city_map, drone_max_distance, warehouse_city_name):
    """
    Select packages for delivery to maximize value while respecting weight and distance constraints.
    
    This is a variation of the 0/1 Knapsack algorithm that also considers route feasibility.
    
    Args:
        packages (list): List of Package objects to select from
        max_weight (float): Maximum weight capacity of the drone
        city_map (CityMap): The city map containing cities and routes
        drone_max_distance (float): Maximum flight distance of the drone
        warehouse_city_name (str): Name of the warehouse city
        
    Returns:
        tuple: (selected_packages, total_value, total_weight, feasible_route) where:
            - selected_packages is a list of selected Package objects
            - total_value is the sum of values of selected packages
            - total_weight is the sum of weights of selected packages
            - feasible_route is a list of city names representing the delivery route
    """
    from .shortest_path import get_shortest_path
    from .route_planning import plan_route
    
    # Group packages by destination city
    packages_by_destination = {}
    for package in packages:
        if package.destination not in packages_by_destination:
            packages_by_destination[package.destination] = []
        packages_by_destination[package.destination].append(package)
    
    # Sort packages within each destination by value-to-weight ratio (descending)
    for destination, pkg_list in packages_by_destination.items():
        pkg_list.sort(key=lambda p: p.value / p.weight, reverse=True)
    
    # Get all destinations
    destinations = list(packages_by_destination.keys())
    
    # Initialize dynamic programming table
    # dp[i][w] = (value, packages, route) for considering first i destinations with weight limit w
    n = len(destinations)
    w_max = int(max_weight * 10)  # Scale up for integer weights
    dp = [[(0, [], None) for _ in range(w_max + 1)] for _ in range(n + 1)]
    
    # Fill the dp table
    for i in range(1, n + 1):
        destination = destinations[i-1]
        dest_packages = packages_by_destination[destination]
        
        for w in range(1, w_max + 1):
            # Default: don't include any package from this destination
            dp[i][w] = dp[i-1][w]
            
            # Try including packages from this destination
            for k in range(len(dest_packages) + 1):
                # Take first k packages from this destination
                selected = dest_packages[:k]
                total_weight = sum(p.weight for p in selected)
                scaled_weight = int(total_weight * 10)
                
                if scaled_weight <= w:
                    prev_value, prev_packages, _ = dp[i-1][w - scaled_weight]
                    current_value = prev_value + sum(p.value for p in selected)
                    
                    if current_value > dp[i][w][0]:
                        dp[i][w] = (current_value, prev_packages + selected, None)
    
    # Get the optimal solution
    best_value, selected_packages, _ = dp[n][w_max]
    total_weight = sum(p.weight for p in selected_packages)
    
    # If no packages were selected, return empty result
    if not selected_packages:
        return [], 0, 0, []
    
    # Get unique destinations of selected packages
    selected_destinations = set(p.destination for p in selected_packages)
    
    # Plan a feasible route through these destinations
    try:
        route, total_distance = plan_route(
            city_map, 
            warehouse_city_name, 
            list(selected_destinations)
        )
        
        # Check if route is feasible given drone's max distance
        if total_distance <= drone_max_distance:
            return selected_packages, best_value, total_weight, route
    except ValueError:
        # No feasible route exists
        pass
    
    # If we reach here, the optimal solution by weight is not feasible by distance
    # Try a greedy approach based on destinations
    selected_packages = []
    total_value = 0
    total_weight = 0
    
    # Sort destinations by shortest distance from warehouse
    from .shortest_path import get_shortest_path
    destinations_with_distance = []
    
    for dest in destinations:
        try:
            _, distance = get_shortest_path(city_map, warehouse_city_name, dest)
            destinations_with_distance.append((dest, distance))
        except ValueError:
            # Skip unreachable destinations
            continue
    
    destinations_with_distance.sort(key=lambda x: x[1])
    
    # Try adding packages from closest destinations first
    route = [warehouse_city_name]
    current_route_distance = 0
    
    for dest, _ in destinations_with_distance:
        # Check if we can add this destination to the route
        temp_route = route + [dest, warehouse_city_name]
        try:
            temp_route, temp_distance = plan_route(city_map, warehouse_city_name, [d for d in temp_route if d != warehouse_city_name])
            
            if temp_distance <= drone_max_distance:
                # We can add this destination
                route = temp_route
                current_route_distance = temp_distance
                
                # Add packages from this destination, sorted by value-to-weight ratio
                for package in packages_by_destination[dest]:
                    if total_weight + package.weight <= max_weight:
                        selected_packages.append(package)
                        total_value += package.value
                        total_weight += package.weight
        except ValueError:
            # Skip if no feasible route
            continue
    
    return selected_packages, total_value, total_weight, route
