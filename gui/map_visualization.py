"""
Map visualization module for Smart Drone Delivery Planner.

This module provides visualization of the city map and delivery routes.
"""

import tkinter as tk
from tkinter import ttk
import math
import random


class MapVisualization(ttk.Frame):
    """
    Provides visualization of the city map and delivery routes.
    """
    
    def __init__(self, parent):
        """Initialize the visualization frame."""
        super().__init__(parent)
        
        # Set up canvas
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set up scrollbars
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Bind events
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Initialize variables
        self.city_map = None
        self.city_positions = {}
        self.route = []
        self.detailed_route = []
        self.packages = []
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Visualization settings
        self.city_radius = 20
        self.warehouse_radius = 25
        self.city_color = "#3498db"
        self.warehouse_color = "#e74c3c"
        self.route_color = "#2ecc71"
        self.route_width = 3
        self.detailed_route_color = "#27ae60"
        self.detailed_route_width = 2
        self.city_font = ("Arial", 10, "bold")
        self.canvas_padding = 50
        
    def clear(self):
        """Clear the visualization."""
        self.canvas.delete("all")
        self.city_positions = {}
        self.route = []
        self.detailed_route = []
        self.packages = []
        
    def on_canvas_configure(self, event):
        """Handle canvas resize event."""
        if self.city_map:
            self.visualize_city_map(self.city_map, self.route, self.detailed_route, self.packages)
            
    def on_canvas_press(self, event):
        """Handle canvas mouse press event."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def on_canvas_drag(self, event):
        """Handle canvas drag event for panning."""
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.canvas.scan_mark(self.drag_start_x, self.drag_start_y)
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def visualize_city_map(self, city_map, route=None, detailed_route=None, packages=None):
        """
        Visualize the city map and optionally a delivery route.
        
        Args:
            city_map (CityMap): The city map to visualize
            route (list, optional): List of city names representing the high-level route
            detailed_route (list, optional): List of city names representing the detailed route
            packages (list, optional): List of Package objects being delivered
        """
        self.clear()
        
        self.city_map = city_map
        self.route = route or []
        self.detailed_route = detailed_route or []
        self.packages = packages or []
        
        # Get all cities
        cities = city_map.get_all_cities()
        if not cities:
            return
        
        # Calculate city positions using force-directed layout
        self.calculate_city_positions(cities)
        
        # Draw routes
        self.draw_routes()
        
        # Draw cities
        self.draw_cities(cities)
        
        # Draw route if provided
        if self.route:
            self.draw_delivery_route()
        
        # Configure canvas scrolling
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
    def calculate_city_positions(self, cities):
        """
        Calculate positions for cities using a simple force-directed layout.
        
        Args:
            cities (list): List of City objects
        """
        # If positions are already calculated, keep them
        if self.city_positions and len(self.city_positions) == len(cities):
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Initialize with random positions if needed
        if not self.city_positions:
            for city in cities:
                x = random.randint(self.canvas_padding, canvas_width - self.canvas_padding)
                y = random.randint(self.canvas_padding, canvas_height - self.canvas_padding)
                self.city_positions[city.name] = (x, y)
        
        # Apply force-directed layout algorithm
        iterations = 50
        k = math.sqrt((canvas_width * canvas_height) / len(cities))  # Optimal distance
        
        for _ in range(iterations):
            # Calculate repulsive forces between all cities
            forces = {city.name: [0, 0] for city in cities}
            
            for i, city1 in enumerate(cities):
                for j, city2 in enumerate(cities):
                    if i == j:
                        continue
                    
                    # Get positions
                    x1, y1 = self.city_positions[city1.name]
                    x2, y2 = self.city_positions[city2.name]
                    
                    # Calculate distance
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                    
                    # Repulsive force (inversely proportional to distance)
                    force = k*k / distance
                    
                    # Normalize direction
                    dx /= distance
                    dy /= distance
                    
                    # Apply force
                    forces[city1.name][0] -= dx * force
                    forces[city1.name][1] -= dy * force
            
            # Calculate attractive forces along routes
            for city_name, neighbors in self.city_map.routes.items():
                for neighbor_name in neighbors:
                    # Get positions
                    x1, y1 = self.city_positions[city_name]
                    x2, y2 = self.city_positions[neighbor_name]
                    
                    # Calculate distance
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                    
                    # Attractive force (proportional to distance)
                    force = distance*distance / k
                    
                    # Normalize direction
                    dx /= distance
                    dy /= distance
                    
                    # Apply force
                    forces[city_name][0] += dx * force
                    forces[city_name][1] += dy * force
            
            # Update positions
            for city in cities:
                fx, fy = forces[city.name]
                
                # Limit maximum movement
                mag = math.sqrt(fx*fx + fy*fy)
                if mag > 30:
                    fx = fx * 30 / mag
                    fy = fy * 30 / mag
                
                x, y = self.city_positions[city.name]
                new_x = max(self.canvas_padding, min(canvas_width - self.canvas_padding, x + fx))
                new_y = max(self.canvas_padding, min(canvas_height - self.canvas_padding, y + fy))
                self.city_positions[city.name] = (new_x, new_y)
        
        # Ensure warehouse is centered if possible
        warehouse = self.city_map.get_warehouse_city()
        if warehouse:
            warehouse_x, warehouse_y = self.city_positions[warehouse.name]
            
            # Calculate center offset
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            offset_x = center_x - warehouse_x
            offset_y = center_y - warehouse_y
            
            # Move all cities by this offset
            for city_name in self.city_positions:
                x, y = self.city_positions[city_name]
                self.city_positions[city_name] = (x + offset_x, y + offset_y)
    
    def draw_cities(self, cities):
        """
        Draw cities on the canvas.
        
        Args:
            cities (list): List of City objects
        """
        for city in cities:
            x, y = self.city_positions[city.name]
            
            # Draw city circle
            if city.is_warehouse:
                self.canvas.create_oval(
                    x - self.warehouse_radius,
                    y - self.warehouse_radius,
                    x + self.warehouse_radius,
                    y + self.warehouse_radius,
                    fill=self.warehouse_color,
                    outline="black",
                    width=2,
                    tags=("city", "warehouse")
                )
            else:
                self.canvas.create_oval(
                    x - self.city_radius,
                    y - self.city_radius,
                    x + self.city_radius,
                    y + self.city_radius,
                    fill=self.city_color,
                    outline="black",
                    width=1,
                    tags=("city",)
                )
            
            # Draw city name
            self.canvas.create_text(
                x,
                y,
                text=city.name,
                font=self.city_font,
                fill="white",
                tags=("city_label",)
            )
            
            # Draw package count if this city is a destination
            if self.packages:
                package_count = sum(1 for p in self.packages if p.destination == city.name)
                if package_count > 0:
                    self.canvas.create_text(
                        x,
                        y + self.city_radius + 15,
                        text=f"{package_count} pkg",
                        font=("Arial", 8),
                        fill="black",
                        tags=("package_count",)
                    )
    
    def draw_routes(self):
        """Draw all routes between cities."""
        for city_name, neighbors in self.city_map.routes.items():
            if city_name not in self.city_positions:
                continue
                
            x1, y1 = self.city_positions[city_name]
            
            for neighbor_name, distance in neighbors.items():
                if neighbor_name not in self.city_positions:
                    continue
                    
                # Only draw each route once (avoid duplicates due to bidirectional routes)
                if city_name < neighbor_name:
                    x2, y2 = self.city_positions[neighbor_name]
                    
                    # Draw route line
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill="gray",
                        width=1,
                        tags=("route",)
                    )
                    
                    # Draw distance label
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    
                    self.canvas.create_text(
                        mid_x, mid_y,
                        text=str(distance),
                        font=("Arial", 8),
                        fill="black",
                        tags=("distance_label",)
                    )
    
    def draw_delivery_route(self):
        """Draw the delivery route if provided."""
        # Draw high-level route
        if len(self.route) > 1:
            for i in range(len(self.route) - 1):
                city1 = self.route[i]
                city2 = self.route[i+1]
                
                if city1 in self.city_positions and city2 in self.city_positions:
                    x1, y1 = self.city_positions[city1]
                    x2, y2 = self.city_positions[city2]
                    
                    # Draw route line
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=self.route_color,
                        width=self.route_width,
                        arrow=tk.LAST,
                        tags=("delivery_route",)
                    )
        
        # Draw detailed route if different from high-level route
        if self.detailed_route and self.detailed_route != self.route and len(self.detailed_route) > 1:
            for i in range(len(self.detailed_route) - 1):
                city1 = self.detailed_route[i]
                city2 = self.detailed_route[i+1]
                
                if city1 in self.city_positions and city2 in self.city_positions:
                    x1, y1 = self.city_positions[city1]
                    x2, y2 = self.city_positions[city2]
                    
                    # Draw detailed route line (dashed)
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=self.detailed_route_color,
                        width=self.detailed_route_width,
                        dash=(5, 2),
                        tags=("detailed_route",)
                    )
