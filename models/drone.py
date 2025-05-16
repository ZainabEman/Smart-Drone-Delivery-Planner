"""
Drone model for Smart Drone Delivery Planner.

This module defines the Drone class for representing delivery drones.
"""

class Drone:
    """
    Represents a delivery drone.
    
    Attributes:
        id (int): Unique identifier for the drone
        max_weight (float): Maximum weight capacity of the drone
        max_distance (float): Maximum flight distance per trip
    """
    
    def __init__(self, id, max_weight, max_distance):
        """
        Initialize a new Drone object.
        
        Args:
            id (int): Unique identifier for the drone
            max_weight (float): Maximum weight capacity of the drone
            max_distance (float): Maximum flight distance per trip
        """
        self.id = id
        self.max_weight = max_weight
        self.max_distance = max_distance
    
    def __str__(self):
        """String representation of the drone."""
        return f"Drone {self.id}: max weight {self.max_weight} kg, max distance {self.max_distance} units"
    
    def __eq__(self, other):
        """Check if two drones are equal based on their IDs."""
        if not isinstance(other, Drone):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Hash function for Drone objects to use them in dictionaries and sets."""
        return hash(self.id)
    
    def can_carry(self, package_weight):
        """
        Check if the drone can carry a package of the given weight.
        
        Args:
            package_weight (float): Weight of the package
            
        Returns:
            bool: True if the drone can carry the package, False otherwise
        """
        return package_weight <= self.max_weight
    
    def can_travel(self, distance):
        """
        Check if the drone can travel the given distance.
        
        Args:
            distance (float): Distance to travel
            
        Returns:
            bool: True if the drone can travel the distance, False otherwise
        """
        return distance <= self.max_distance
