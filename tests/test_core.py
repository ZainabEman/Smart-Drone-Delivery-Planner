"""
Tests for Smart Drone Delivery Planner.

This module contains test cases for the core algorithms and data structures.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.city import City, CityMap
from models.package import Package
from models.drone import Drone
from algorithms.shortest_path import get_shortest_path, get_all_shortest_paths
from algorithms.package_selection import knapsack_package_selection
from algorithms.route_planning import plan_route, get_detailed_route


class TestCityMap(unittest.TestCase):
    """Test cases for the CityMap class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.city_map = CityMap()
        self.city_map.add_city("A", True)  # Warehouse
        self.city_map.add_city("B")
        self.city_map.add_city("C")
        self.city_map.add_city("D")
        
        self.city_map.add_route("A", "B", 10)
        self.city_map.add_route("B", "C", 15)
        self.city_map.add_route("C", "D", 20)
        self.city_map.add_route("A", "D", 30)
    
    def test_add_city(self):
        """Test adding cities."""
        self.assertEqual(len(self.city_map.cities), 4)
        self.assertTrue("A" in self.city_map.cities)
        self.assertTrue("B" in self.city_map.cities)
        self.assertTrue("C" in self.city_map.cities)
        self.assertTrue("D" in self.city_map.cities)
    
    def test_add_route(self):
        """Test adding routes."""
        self.assertEqual(len(self.city_map.routes["A"]), 2)
        self.assertEqual(len(self.city_map.routes["B"]), 2)
        self.assertEqual(len(self.city_map.routes["C"]), 2)
        self.assertEqual(len(self.city_map.routes["D"]), 2)
        
        self.assertEqual(self.city_map.routes["A"]["B"], 10)
        self.assertEqual(self.city_map.routes["B"]["C"], 15)
        self.assertEqual(self.city_map.routes["C"]["D"], 20)
        self.assertEqual(self.city_map.routes["A"]["D"], 30)
    
    def test_get_warehouse_city(self):
        """Test getting the warehouse city."""
        warehouse = self.city_map.get_warehouse_city()
        self.assertIsNotNone(warehouse)
        self.assertEqual(warehouse.name, "A")
        self.assertTrue(warehouse.is_warehouse)
    
    def test_remove_route(self):
        """Test removing a route."""
        self.city_map.remove_route("A", "B")
        self.assertFalse("B" in self.city_map.routes["A"])
        self.assertFalse("A" in self.city_map.routes["B"])


class TestShortestPath(unittest.TestCase):
    """Test cases for the shortest path algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.city_map = CityMap()
        self.city_map.add_city("A", True)  # Warehouse
        self.city_map.add_city("B")
        self.city_map.add_city("C")
        self.city_map.add_city("D")
        self.city_map.add_city("E")
        
        self.city_map.add_route("A", "B", 10)
        self.city_map.add_route("B", "C", 15)
        self.city_map.add_route("C", "D", 20)
        self.city_map.add_route("A", "E", 5)
        self.city_map.add_route("E", "D", 15)
    
    def test_shortest_path_direct(self):
        """Test finding shortest path with direct connection."""
        path, distance = get_shortest_path(self.city_map, "A", "B")
        self.assertEqual(path, ["A", "B"])
        self.assertEqual(distance, 10)
    
    def test_shortest_path_indirect(self):
        """Test finding shortest path with indirect connection."""
        path, distance = get_shortest_path(self.city_map, "A", "D")
        self.assertEqual(path, ["A", "E", "D"])
        self.assertEqual(distance, 20)
    
    def test_all_shortest_paths(self):
        """Test finding all shortest paths from a city."""
        paths = get_all_shortest_paths(self.city_map, "A")
        self.assertEqual(len(paths), 5)  # A to all cities including itself
        self.assertEqual(paths["D"][1], 20)  # Distance from A to D


class TestPackageSelection(unittest.TestCase):
    """Test cases for the package selection algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.city_map = CityMap()
        self.city_map.add_city("Warehouse", True)
        self.city_map.add_city("City1")
        self.city_map.add_city("City2")
        
        self.city_map.add_route("Warehouse", "City1", 10)
        self.city_map.add_route("Warehouse", "City2", 15)
        self.city_map.add_route("City1", "City2", 10)
        
        self.packages = [
            Package(1, 2.0, 100, "City1"),
            Package(2, 3.0, 150, "City1"),
            Package(3, 1.0, 50, "City2"),
            Package(4, 4.0, 200, "City2")
        ]
    
    def test_package_selection_weight_constraint(self):
        """Test package selection with weight constraint."""
        selected, value, weight, route = knapsack_package_selection(
            self.packages, 5.0, self.city_map, 100, "Warehouse"
        )
        
        self.assertEqual(len(selected), 2)
        self.assertEqual(weight, 5.0)
        self.assertEqual(value, 250)
    
    def test_package_selection_distance_constraint(self):
        """Test package selection with distance constraint."""
        selected, value, weight, route = knapsack_package_selection(
            self.packages, 10.0, self.city_map, 20, "Warehouse"
        )
        
        # Should only select packages for one city due to distance constraint
        self.assertTrue(all(p.destination == selected[0].destination for p in selected))


class TestRoutePlanning(unittest.TestCase):
    """Test cases for the route planning algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.city_map = CityMap()
        self.city_map.add_city("Warehouse", True)
        self.city_map.add_city("City1")
        self.city_map.add_city("City2")
        self.city_map.add_city("City3")
        
        self.city_map.add_route("Warehouse", "City1", 10)
        self.city_map.add_route("City1", "City2", 15)
        self.city_map.add_route("City2", "City3", 10)
        self.city_map.add_route("Warehouse", "City3", 30)
    
    def test_plan_route_simple(self):
        """Test planning a simple route."""
        route, distance = plan_route(self.city_map, "Warehouse", ["City1"])
        self.assertEqual(route, ["Warehouse", "City1", "Warehouse"])
        self.assertEqual(distance, 20)
    
    def test_plan_route_multiple(self):
        """Test planning a route with multiple destinations."""
        route, distance = plan_route(self.city_map, "Warehouse", ["City1", "City2"])
        self.assertEqual(len(route), 4)  # Warehouse -> City1 -> City2 -> Warehouse
        self.assertTrue(route[0] == "Warehouse" and route[-1] == "Warehouse")
    
    def test_detailed_route(self):
        """Test getting a detailed route."""
        route = ["Warehouse", "City1", "City2", "Warehouse"]
        detailed_route, segment_distances, total_distance = get_detailed_route(self.city_map, route)
        
        self.assertEqual(len(detailed_route), len(route))
        self.assertEqual(len(segment_distances), len(route) - 1)
        self.assertEqual(total_distance, 10 + 15 + 25)  # W->C1 + C1->C2 + C2->W


if __name__ == "__main__":
    unittest.main()
