"""
City/Graph model for Smart Drone Delivery Planner.

This module defines the City and CityMap classes for representing
the city network as a weighted graph.
"""

class City:
    """
    Represents a city node in the delivery network.
    
    Attributes:
        name (str): The name of the city
        is_warehouse (bool): Whether this city contains the central warehouse
    """
    
    def __init__(self, name, is_warehouse=False):
        """
        Initialize a new City object.
        
        Args:
            name (str): The name of the city
            is_warehouse (bool, optional): Whether this city contains the central warehouse. 
                                          Defaults to False.
        """
        self.name = name
        self.is_warehouse = is_warehouse
        
    def __str__(self):
        """String representation of the city."""
        warehouse_str = " (Warehouse)" if self.is_warehouse else ""
        return f"{self.name}{warehouse_str}"
    
    def __eq__(self, other):
        """Check if two cities are equal based on their names."""
        if not isinstance(other, City):
            return False
        return self.name == other.name
    
    def __hash__(self):
        """Hash function for City objects to use them in dictionaries and sets."""
        return hash(self.name)


class CityMap:
    """
    Represents the map of cities as a weighted graph.
    
    Attributes:
        cities (dict): Dictionary mapping city names to City objects
        routes (dict): Adjacency list representation of routes between cities
                      {city_name: {neighbor_name: distance}}
        warehouse (City): Reference to the warehouse city
    """
    
    def __init__(self):
        """Initialize an empty city map."""
        self.cities = {}  # name -> City object
        self.routes = {}  # name -> {neighbor_name: distance}
        self.warehouse = None
    
    def add_city(self, name, is_warehouse=False):
        """
        Add a city to the map.
        
        Args:
            name (str): The name of the city
            is_warehouse (bool, optional): Whether this city contains the central warehouse.
                                          Defaults to False.
                                          
        Returns:
            City: The created or existing City object
        """
        if name not in self.cities:
            city = City(name, is_warehouse)
            self.cities[name] = city
            self.routes[name] = {}
            
            if is_warehouse:
                self.warehouse = city
        elif is_warehouse and not self.cities[name].is_warehouse:
            # Update existing city to be a warehouse
            self.cities[name].is_warehouse = True
            self.warehouse = self.cities[name]
            
        return self.cities[name]
    
    def add_route(self, city1_name, city2_name, distance):
        """
        Add a bidirectional route between two cities.
        
        Args:
            city1_name (str): The name of the first city
            city2_name (str): The name of the second city
            distance (float): The distance between the cities
            
        Raises:
            ValueError: If either city does not exist in the map
        """
        if city1_name not in self.cities:
            raise ValueError(f"City '{city1_name}' does not exist in the map")
        if city2_name not in self.cities:
            raise ValueError(f"City '{city2_name}' does not exist in the map")
        
        # Add bidirectional route
        self.routes[city1_name][city2_name] = distance
        self.routes[city2_name][city1_name] = distance
    
    def get_neighbors(self, city_name):
        """
        Get all neighboring cities and distances for a given city.
        
        Args:
            city_name (str): The name of the city
            
        Returns:
            dict: Dictionary mapping neighbor city names to distances
            
        Raises:
            ValueError: If the city does not exist in the map
        """
        if city_name not in self.cities:
            raise ValueError(f"City '{city_name}' does not exist in the map")
        
        return self.routes[city_name]
    
    def get_all_cities(self):
        """
        Get all cities in the map.
        
        Returns:
            list: List of all City objects
        """
        return list(self.cities.values())
    
    def get_warehouse_city(self):
        """
        Get the warehouse city.
        
        Returns:
            City: The warehouse City object or None if not set
        """
        return self.warehouse
    
    def remove_route(self, city1_name, city2_name):
        """
        Remove a route between two cities (for dynamic updates).
        
        Args:
            city1_name (str): The name of the first city
            city2_name (str): The name of the second city
            
        Raises:
            ValueError: If either city does not exist in the map or there's no route
        """
        if city1_name not in self.cities:
            raise ValueError(f"City '{city1_name}' does not exist in the map")
        if city2_name not in self.cities:
            raise ValueError(f"City '{city2_name}' does not exist in the map")
        
        if city2_name not in self.routes[city1_name]:
            raise ValueError(f"No route exists between '{city1_name}' and '{city2_name}'")
        
        # Remove bidirectional route
        del self.routes[city1_name][city2_name]
        del self.routes[city2_name][city1_name]
    
    def __str__(self):
        """String representation of the city map."""
        result = "City Map:\n"
        result += "Cities: " + ", ".join([str(city) for city in self.cities.values()]) + "\n"
        result += "Routes:\n"
        
        for city_name, neighbors in self.routes.items():
            if neighbors:
                result += f"  {city_name} -> " + ", ".join([f"{neighbor}({distance})" 
                                                         for neighbor, distance in neighbors.items()]) + "\n"
        
        return result
