"""
Utility functions for Smart Drone Delivery Planner.

This module provides utility functions for file operations, data validation,
and other helper functions.
"""

import json
import os


def validate_city_map(city_map):
    """
    Validate the city map data.
    
    Args:
        city_map (CityMap): The city map to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if there's at least one city
    if not city_map.cities:
        return False, "City map must contain at least one city"
    
    # Check if there's a warehouse
    if not city_map.get_warehouse_city():
        return False, "City map must contain a warehouse city"
    
    # Check if all cities are connected
    warehouse = city_map.get_warehouse_city()
    if not warehouse:
        return False, "No warehouse city defined"
    
    # Check if there are any routes
    if not any(city_map.routes.values()):
        return False, "City map must contain at least one route"
    
    return True, ""


def validate_packages(packages):
    """
    Validate the package data.
    
    Args:
        packages (list): List of Package objects to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if there's at least one package
    if not packages:
        return False, "There must be at least one package"
    
    # Check for duplicate IDs
    ids = [p.id for p in packages]
    if len(ids) != len(set(ids)):
        return False, "Package IDs must be unique"
    
    # Check for valid weights and values
    for package in packages:
        if package.weight <= 0:
            return False, f"Package {package.id} has invalid weight: {package.weight}"
        if package.value <= 0:
            return False, f"Package {package.id} has invalid value: {package.value}"
    
    return True, ""


def validate_drones(drones):
    """
    Validate the drone data.
    
    Args:
        drones (list): List of Drone objects to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if there's at least one drone
    if not drones:
        return False, "There must be at least one drone"
    
    # Check for duplicate IDs
    ids = [d.id for d in drones]
    if len(ids) != len(set(ids)):
        return False, "Drone IDs must be unique"
    
    # Check for valid capacities
    for drone in drones:
        if drone.max_weight <= 0:
            return False, f"Drone {drone.id} has invalid max weight: {drone.max_weight}"
        if drone.max_distance <= 0:
            return False, f"Drone {drone.id} has invalid max distance: {drone.max_distance}"
    
    return True, ""


def save_data_to_file(filename, city_map, packages, drones):
    """
    Save data to a JSON file.
    
    Args:
        filename (str): Path to the file
        city_map (CityMap): The city map to save
        packages (list): List of Package objects to save
        drones (list): List of Drone objects to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare data
        data = {
            'cities': [
                {
                    'name': city.name,
                    'is_warehouse': city.is_warehouse
                }
                for city in city_map.get_all_cities()
            ],
            'routes': [
                {
                    'from_city': city_name,
                    'to_city': neighbor,
                    'distance': distance
                }
                for city_name, neighbors in city_map.routes.items()
                for neighbor, distance in neighbors.items()
                if city_name < neighbor  # Only include each route once
            ],
            'packages': [
                {
                    'id': package.id,
                    'weight': package.weight,
                    'value': package.value,
                    'destination': package.destination
                }
                for package in packages
            ],
            'drones': [
                {
                    'id': drone.id,
                    'max_weight': drone.max_weight,
                    'max_distance': drone.max_distance
                }
                for drone in drones
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception:
        return False


def load_data_from_file(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename (str): Path to the file
        
    Returns:
        tuple: (city_map, packages, drones) or (None, None, None) if failed
    """
    from models.city import CityMap
    from models.package import Package
    from models.drone import Drone
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Create city map
        city_map = CityMap()
        
        # Load cities
        for city_data in data.get('cities', []):
            city_map.add_city(city_data['name'], city_data.get('is_warehouse', False))
        
        # Load routes
        for route_data in data.get('routes', []):
            city_map.add_route(
                route_data['from_city'],
                route_data['to_city'],
                route_data['distance']
            )
        
        # Load packages
        packages = []
        for pkg_data in data.get('packages', []):
            packages.append(Package(
                pkg_data['id'],
                pkg_data['weight'],
                pkg_data['value'],
                pkg_data['destination']
            ))
        
        # Load drones
        drones = []
        for drone_data in data.get('drones', []):
            drones.append(Drone(
                drone_data['id'],
                drone_data['max_weight'],
                drone_data['max_distance']
            ))
        
        return city_map, packages, drones
    except Exception:
        return None, None, None
