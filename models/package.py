"""
Package model for Smart Drone Delivery Planner.

This module defines the Package class for representing delivery packages.
"""

class Package:
    """
    Represents a package to be delivered.
    
    Attributes:
        id (int): Unique identifier for the package
        weight (float): Weight of the package
        value (float): Value/priority of the package
        destination (str): Name of the destination city
    """
    
    def __init__(self, id, weight, value, destination):
        """
        Initialize a new Package object.
        
        Args:
            id (int): Unique identifier for the package
            weight (float): Weight of the package
            value (float): Value/priority of the package
            destination (str): Name of the destination city
        """
        self.id = id
        self.weight = weight
        self.value = value
        self.destination = destination
    
    def __str__(self):
        """String representation of the package."""
        return f"Package {self.id}: {self.weight} kg, value {self.value}, to {self.destination}"
    
    def __eq__(self, other):
        """Check if two packages are equal based on their IDs."""
        if not isinstance(other, Package):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Hash function for Package objects to use them in dictionaries and sets."""
        return hash(self.id)
