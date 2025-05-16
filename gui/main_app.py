"""
Main GUI application for Smart Drone Delivery Planner.

This module implements the main application window and GUI components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
from PIL import Image, ImageTk
import math

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.city import CityMap
from models.package import Package
from models.drone import Drone
from algorithms.shortest_path import get_shortest_path
from algorithms.package_selection import knapsack_package_selection
from algorithms.route_planning import plan_route, get_detailed_route
from gui.map_visualization import MapVisualization


class SmartDroneDeliveryApp(tk.Tk):
    """
    Main application window for the Smart Drone Delivery Planner.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Set window properties
        self.title("Smart Drone Delivery Planner")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        
        # Configure colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#3498db"
        self.button_color = "#2980b9"
        self.success_color = "#2ecc71"
        self.warning_color = "#e74c3c"
        
        # Configure styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        # Initialize data structures
        self.city_map = CityMap()
        self.packages = []
        self.drones = []
        self.delivery_plans = []
        
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_input_tab()
        self.create_output_tab()
        self.create_visualization_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_input_tab(self):
        """Create the input tab for data entry."""
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input Data")
        
        # Create left and right panes
        left_pane = ttk.Frame(input_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_pane = ttk.Frame(input_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # City Map Section (Left Pane)
        city_frame = ttk.LabelFrame(left_pane, text="City Map Data")
        city_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # City input
        city_input_frame = ttk.Frame(city_frame)
        city_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(city_input_frame, text="City Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.city_name_var = tk.StringVar()
        city_name_entry = ttk.Entry(city_input_frame, textvariable=self.city_name_var)
        city_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.is_warehouse_var = tk.BooleanVar()
        warehouse_check = ttk.Checkbutton(city_input_frame, text="Warehouse", variable=self.is_warehouse_var)
        warehouse_check.grid(row=0, column=2, padx=5, pady=5)
        
        add_city_btn = ttk.Button(city_input_frame, text="Add City", command=self.add_city)
        add_city_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Route input
        route_input_frame = ttk.Frame(city_frame)
        route_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(route_input_frame, text="From City:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.from_city_var = tk.StringVar()
        self.from_city_combo = ttk.Combobox(route_input_frame, textvariable=self.from_city_var, state="readonly")
        self.from_city_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(route_input_frame, text="To City:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.to_city_var = tk.StringVar()
        self.to_city_combo = ttk.Combobox(route_input_frame, textvariable=self.to_city_var, state="readonly")
        self.to_city_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(route_input_frame, text="Distance:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.distance_var = tk.StringVar()
        distance_entry = ttk.Entry(route_input_frame, textvariable=self.distance_var)
        distance_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        add_route_btn = ttk.Button(route_input_frame, text="Add Route", command=self.add_route)
        add_route_btn.grid(row=1, column=3, padx=5, pady=5)
        
        # City and route display
        display_frame = ttk.Frame(city_frame)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cities list
        cities_frame = ttk.LabelFrame(display_frame, text="Cities")
        cities_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cities_listbox = tk.Listbox(cities_frame, selectmode=tk.SINGLE)
        self.cities_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cities_scrollbar = ttk.Scrollbar(cities_frame, orient=tk.VERTICAL, command=self.cities_listbox.yview)
        cities_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cities_listbox.config(yscrollcommand=cities_scrollbar.set)
        
        # Routes list
        routes_frame = ttk.LabelFrame(display_frame, text="Routes")
        routes_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.routes_listbox = tk.Listbox(routes_frame, selectmode=tk.SINGLE)
        self.routes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        routes_scrollbar = ttk.Scrollbar(routes_frame, orient=tk.VERTICAL, command=self.routes_listbox.yview)
        routes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.routes_listbox.config(yscrollcommand=routes_scrollbar.set)
        
        # Package Section (Right Pane, Top)
        package_frame = ttk.LabelFrame(right_pane, text="Package Data")
        package_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Package input
        package_input_frame = ttk.Frame(package_frame)
        package_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(package_input_frame, text="Package ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.package_id_var = tk.StringVar()
        package_id_entry = ttk.Entry(package_input_frame, textvariable=self.package_id_var)
        package_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(package_input_frame, text="Weight (kg):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.package_weight_var = tk.StringVar()
        package_weight_entry = ttk.Entry(package_input_frame, textvariable=self.package_weight_var)
        package_weight_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(package_input_frame, text="Value:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.package_value_var = tk.StringVar()
        package_value_entry = ttk.Entry(package_input_frame, textvariable=self.package_value_var)
        package_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(package_input_frame, text="Destination:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.package_dest_var = tk.StringVar()
        self.package_dest_combo = ttk.Combobox(package_input_frame, textvariable=self.package_dest_var, state="readonly")
        self.package_dest_combo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        add_package_btn = ttk.Button(package_input_frame, text="Add Package", command=self.add_package)
        add_package_btn.grid(row=4, column=1, padx=5, pady=5, sticky=tk.E)
        
        # Package list
        package_list_frame = ttk.Frame(package_frame)
        package_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.packages_listbox = tk.Listbox(package_list_frame, selectmode=tk.SINGLE)
        self.packages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        packages_scrollbar = ttk.Scrollbar(package_list_frame, orient=tk.VERTICAL, command=self.packages_listbox.yview)
        packages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.packages_listbox.config(yscrollcommand=packages_scrollbar.set)
        
        # Drone Section (Right Pane, Bottom)
        drone_frame = ttk.LabelFrame(right_pane, text="Drone Data")
        drone_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Drone input
        drone_input_frame = ttk.Frame(drone_frame)
        drone_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(drone_input_frame, text="Drone ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.drone_id_var = tk.StringVar()
        drone_id_entry = ttk.Entry(drone_input_frame, textvariable=self.drone_id_var)
        drone_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(drone_input_frame, text="Max Weight (kg):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.drone_weight_var = tk.StringVar()
        drone_weight_entry = ttk.Entry(drone_input_frame, textvariable=self.drone_weight_var)
        drone_weight_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(drone_input_frame, text="Max Distance:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.drone_distance_var = tk.StringVar()
        drone_distance_entry = ttk.Entry(drone_input_frame, textvariable=self.drone_distance_var)
        drone_distance_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        add_drone_btn = ttk.Button(drone_input_frame, text="Add Drone", command=self.add_drone)
        add_drone_btn.grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
        
        # Drone list
        drone_list_frame = ttk.Frame(drone_frame)
        drone_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.drones_listbox = tk.Listbox(drone_list_frame, selectmode=tk.SINGLE)
        self.drones_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        drones_scrollbar = ttk.Scrollbar(drone_list_frame, orient=tk.VERTICAL, command=self.drones_listbox.yview)
        drones_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.drones_listbox.config(yscrollcommand=drones_scrollbar.set)
        
        # Control buttons at the bottom
        control_frame = ttk.Frame(input_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        load_btn = ttk.Button(control_frame, text="Load Data", command=self.load_data)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(control_frame, text="Save Data", command=self.save_data)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(control_frame, text="Clear All", command=self.clear_data)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        run_btn = ttk.Button(control_frame, text="Run Delivery Planning", command=self.run_planning)
        run_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add sample data button (for testing)
        sample_btn = ttk.Button(control_frame, text="Load Sample Data", command=self.load_sample_data)
        sample_btn.pack(side=tk.RIGHT, padx=5)
        
    def create_output_tab(self):
        """Create the output tab for displaying results."""
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="Delivery Plans")
        
        # Create results display
        results_frame = ttk.Frame(output_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split into left and right panes
        left_pane = ttk.Frame(results_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_pane = ttk.Frame(results_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Trip list (left pane)
        trip_list_frame = ttk.LabelFrame(left_pane, text="Drone Trips")
        trip_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.trips_listbox = tk.Listbox(trip_list_frame, selectmode=tk.SINGLE)
        self.trips_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trips_scrollbar = ttk.Scrollbar(trip_list_frame, orient=tk.VERTICAL, command=self.trips_listbox.yview)
        trips_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trips_listbox.config(yscrollcommand=trips_scrollbar.set)
        
        # Bind selection event
        self.trips_listbox.bind('<<ListboxSelect>>', self.on_trip_select)
        
        # Trip details (right pane)
        trip_details_frame = ttk.LabelFrame(right_pane, text="Trip Details")
        trip_details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Use a Text widget with tags for formatting
        self.trip_details_text = tk.Text(trip_details_frame, wrap=tk.WORD, padx=5, pady=5)
        self.trip_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar = ttk.Scrollbar(trip_details_frame, orient=tk.VERTICAL, command=self.trip_details_text.yview)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trip_details_text.config(yscrollcommand=details_scrollbar.set, state=tk.DISABLED)
        
        # Configure text tags for formatting
        self.trip_details_text.tag_configure('header', font=('Arial', 12, 'bold'))
        self.trip_details_text.tag_configure('subheader', font=('Arial', 11, 'bold'))
        self.trip_details_text.tag_configure('normal', font=('Arial', 10))
        self.trip_details_text.tag_configure('highlight', font=('Arial', 10, 'bold'), foreground='blue')
        
    def create_visualization_tab(self):
        """Create the visualization tab for map display."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Map Visualization")
        
        # Create visualization container
        self.map_viz_container = ttk.Frame(viz_frame)
        self.map_viz_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize map visualization
        self.map_visualization = MapVisualization(self.map_viz_container)
        self.map_visualization.pack(fill=tk.BOTH, expand=True)
        
        # Control panel for visualization
        control_panel = ttk.Frame(viz_frame)
        control_panel.pack(fill=tk.X, padx=10, pady=5)
        
        # Trip selection for visualization
        ttk.Label(control_panel, text="Select Trip to Visualize:").pack(side=tk.LEFT, padx=5)
        self.viz_trip_var = tk.StringVar()
        self.viz_trip_combo = ttk.Combobox(control_panel, textvariable=self.viz_trip_var, state="readonly")
        self.viz_trip_combo.pack(side=tk.LEFT, padx=5)
        self.viz_trip_combo.bind('<<ComboboxSelected>>', self.on_viz_trip_select)
        
        # Refresh button
        refresh_btn = ttk.Button(control_panel, text="Refresh Map", command=self.refresh_visualization)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
    def add_city(self):
        """Add a city to the map."""
        name = self.city_name_var.get().strip()
        is_warehouse = self.is_warehouse_var.get()
        
        if not name:
            messagebox.showerror("Error", "City name cannot be empty")
            return
        
        try:
            self.city_map.add_city(name, is_warehouse)
            self.update_city_display()
            self.update_city_combos()
            
            # Clear input fields
            self.city_name_var.set("")
            self.is_warehouse_var.set(False)
            
            self.status_var.set(f"Added city: {name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_route(self):
        """Add a route between two cities."""
        from_city = self.from_city_var.get()
        to_city = self.to_city_var.get()
        distance_str = self.distance_var.get().strip()
        
        if not from_city or not to_city:
            messagebox.showerror("Error", "Please select both cities")
            return
        
        if from_city == to_city:
            messagebox.showerror("Error", "Cannot add route to the same city")
            return
        
        try:
            distance = float(distance_str)
            if distance <= 0:
                raise ValueError("Distance must be positive")
            
            self.city_map.add_route(from_city, to_city, distance)
            self.update_route_display()
            
            # Clear input fields
            self.distance_var.set("")
            
            self.status_var.set(f"Added route: {from_city} to {to_city} ({distance})")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid distance: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_package(self):
        """Add a package to the list."""
        id_str = self.package_id_var.get().strip()
        weight_str = self.package_weight_var.get().strip()
        value_str = self.package_value_var.get().strip()
        destination = self.package_dest_var.get()
        
        if not id_str or not weight_str or not value_str or not destination:
            messagebox.showerror("Error", "All package fields are required")
            return
        
        try:
            id = int(id_str)
            weight = float(weight_str)
            value = float(value_str)
            
            if weight <= 0:
                raise ValueError("Weight must be positive")
            if value <= 0:
                raise ValueError("Value must be positive")
            
            # Check for duplicate ID
            if any(p.id == id for p in self.packages):
                raise ValueError(f"Package with ID {id} already exists")
            
            package = Package(id, weight, value, destination)
            self.packages.append(package)
            self.update_package_display()
            
            # Clear input fields
            self.package_id_var.set("")
            self.package_weight_var.set("")
            self.package_value_var.set("")
            
            self.status_var.set(f"Added package: {package}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid package data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_drone(self):
        """Add a drone to the list."""
        id_str = self.drone_id_var.get().strip()
        weight_str = self.drone_weight_var.get().strip()
        distance_str = self.drone_distance_var.get().strip()
        
        if not id_str or not weight_str or not distance_str:
            messagebox.showerror("Error", "All drone fields are required")
            return
        
        try:
            id = int(id_str)
            max_weight = float(weight_str)
            max_distance = float(distance_str)
            
            if max_weight <= 0:
                raise ValueError("Max weight must be positive")
            if max_distance <= 0:
                raise ValueError("Max distance must be positive")
            
            # Check for duplicate ID
            if any(d.id == id for d in self.drones):
                raise ValueError(f"Drone with ID {id} already exists")
            
            drone = Drone(id, max_weight, max_distance)
            self.drones.append(drone)
            self.update_drone_display()
            
            # Clear input fields
            self.drone_id_var.set("")
            self.drone_weight_var.set("")
            self.drone_distance_var.set("")
            
            self.status_var.set(f"Added drone: {drone}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid drone data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_city_display(self):
        """Update the cities listbox."""
        self.cities_listbox.delete(0, tk.END)
        for city in self.city_map.get_all_cities():
            self.cities_listbox.insert(tk.END, str(city))
    
    def update_route_display(self):
        """Update the routes listbox."""
        self.routes_listbox.delete(0, tk.END)
        for city_name, neighbors in self.city_map.routes.items():
            for neighbor, distance in neighbors.items():
                # Only add each route once (avoid duplicates due to bidirectional routes)
                if city_name < neighbor:
                    self.routes_listbox.insert(tk.END, f"{city_name} ↔ {neighbor}: {distance}")
    
    def update_package_display(self):
        """Update the packages listbox."""
        self.packages_listbox.delete(0, tk.END)
        for package in self.packages:
            self.packages_listbox.insert(tk.END, str(package))
    
    def update_drone_display(self):
        """Update the drones listbox."""
        self.drones_listbox.delete(0, tk.END)
        for drone in self.drones:
            self.drones_listbox.insert(tk.END, str(drone))
    
    def update_city_combos(self):
        """Update city comboboxes."""
        city_names = [city.name for city in self.city_map.get_all_cities()]
        
        self.from_city_combo['values'] = city_names
        self.to_city_combo['values'] = city_names
        self.package_dest_combo['values'] = city_names
        
        # Clear current selections if they're no longer valid
        if self.from_city_var.get() not in city_names:
            self.from_city_var.set('')
        if self.to_city_var.get() not in city_names:
            self.to_city_var.set('')
        if self.package_dest_var.get() not in city_names:
            self.package_dest_var.set('')
    
    def load_data(self):
        """Load data from a JSON file."""
        filename = filedialog.askopenfilename(
            title="Load Data",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear current data
            self.clear_data(confirm=False)
            
            # Load cities and routes
            for city_data in data.get('cities', []):
                self.city_map.add_city(city_data['name'], city_data.get('is_warehouse', False))
            
            for route_data in data.get('routes', []):
                self.city_map.add_route(
                    route_data['from_city'],
                    route_data['to_city'],
                    route_data['distance']
                )
            
            # Load packages
            for pkg_data in data.get('packages', []):
                self.packages.append(Package(
                    pkg_data['id'],
                    pkg_data['weight'],
                    pkg_data['value'],
                    pkg_data['destination']
                ))
            
            # Load drones
            for drone_data in data.get('drones', []):
                self.drones.append(Drone(
                    drone_data['id'],
                    drone_data['max_weight'],
                    drone_data['max_distance']
                ))
            
            # Update displays
            self.update_city_display()
            self.update_route_display()
            self.update_package_display()
            self.update_drone_display()
            self.update_city_combos()
            
            self.status_var.set(f"Data loaded from {os.path.basename(filename)}")
            messagebox.showinfo("Success", "Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def save_data(self):
        """Save data to a JSON file."""
        filename = filedialog.asksaveasfilename(
            title="Save Data",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Prepare data
            data = {
                'cities': [
                    {
                        'name': city.name,
                        'is_warehouse': city.is_warehouse
                    }
                    for city in self.city_map.get_all_cities()
                ],
                'routes': [
                    {
                        'from_city': city_name,
                        'to_city': neighbor,
                        'distance': distance
                    }
                    for city_name, neighbors in self.city_map.routes.items()
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
                    for package in self.packages
                ],
                'drones': [
                    {
                        'id': drone.id,
                        'max_weight': drone.max_weight,
                        'max_distance': drone.max_distance
                    }
                    for drone in self.drones
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.status_var.set(f"Data saved to {os.path.basename(filename)}")
            messagebox.showinfo("Success", "Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def clear_data(self, confirm=True):
        """Clear all data."""
        if confirm:
            if not messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
                return
        
        # Clear data structures
        self.city_map = CityMap()
        self.packages = []
        self.drones = []
        self.delivery_plans = []
        
        # Clear displays
        self.update_city_display()
        self.update_route_display()
        self.update_package_display()
        self.update_drone_display()
        self.update_city_combos()
        
        # Clear trip displays
        self.trips_listbox.delete(0, tk.END)
        self.trip_details_text.config(state=tk.NORMAL)
        self.trip_details_text.delete(1.0, tk.END)
        self.trip_details_text.config(state=tk.DISABLED)
        
        # Clear visualization
        self.viz_trip_combo['values'] = []
        self.viz_trip_var.set('')
        self.map_visualization.clear()
        
        self.status_var.set("All data cleared")
    
    def run_planning(self):
        """Run the delivery planning algorithm."""
        # Validate inputs
        if not self.city_map.get_warehouse_city():
            messagebox.showerror("Error", "No warehouse city defined")
            return
        
        if not self.packages:
            messagebox.showerror("Error", "No packages defined")
            return
        
        if not self.drones:
            messagebox.showerror("Error", "No drones defined")
            return
        
        try:
            # Clear previous results
            self.delivery_plans = []
            self.trips_listbox.delete(0, tk.END)
            self.trip_details_text.config(state=tk.NORMAL)
            self.trip_details_text.delete(1.0, tk.END)
            self.trip_details_text.config(state=tk.DISABLED)
            
            # Get warehouse city name
            warehouse_city = self.city_map.get_warehouse_city()
            warehouse_name = warehouse_city.name
            
            # Create a copy of packages to work with
            remaining_packages = self.packages.copy()
            
            # Process each drone
            for drone in self.drones:
                drone_plans = []
                
                # Continue planning trips until no more packages can be delivered
                while remaining_packages:
                    try:
                        # Select packages for this trip
                        selected_packages, total_value, total_weight, route = knapsack_package_selection(
                            remaining_packages,
                            drone.max_weight,
                            self.city_map,
                            drone.max_distance,
                            warehouse_name
                        )
                        
                        if not selected_packages:
                            # No feasible packages for this drone
                            break
                        
                        # Get detailed route
                        detailed_route, segment_distances, total_distance = get_detailed_route(
                            self.city_map,
                            route
                        )
                        
                        # Create trip plan
                        trip_plan = {
                            'drone': drone,
                            'packages': selected_packages,
                            'total_value': total_value,
                            'total_weight': total_weight,
                            'route': route,
                            'detailed_route': detailed_route,
                            'segment_distances': segment_distances,
                            'total_distance': total_distance
                        }
                        
                        drone_plans.append(trip_plan)
                        self.delivery_plans.append(trip_plan)
                        
                        # Remove delivered packages
                        for package in selected_packages:
                            remaining_packages.remove(package)
                        
                    except Exception as e:
                        messagebox.showwarning("Warning", f"Planning error: {str(e)}")
                        break
            
            # Update trips display
            for i, plan in enumerate(self.delivery_plans):
                drone = plan['drone']
                packages = plan['packages']
                self.trips_listbox.insert(
                    tk.END,
                    f"Trip {i+1}: Drone {drone.id}, {len(packages)} packages, value: {plan['total_value']}"
                )
            
            # Update visualization dropdown
            self.viz_trip_combo['values'] = [f"Trip {i+1}" for i in range(len(self.delivery_plans))]
            
            # Switch to output tab
            self.notebook.select(1)
            
            if remaining_packages:
                undelivered = len(remaining_packages)
                total = len(self.packages)
                self.status_var.set(f"Planning complete. {total - undelivered}/{total} packages deliverable.")
                messagebox.showinfo(
                    "Planning Results",
                    f"Planning complete.\n\n"
                    f"Deliverable packages: {total - undelivered}/{total}\n"
                    f"Total trips planned: {len(self.delivery_plans)}"
                )
            else:
                self.status_var.set(f"Planning complete. All {len(self.packages)} packages deliverable.")
                messagebox.showinfo(
                    "Planning Results",
                    f"Planning complete. All {len(self.packages)} packages can be delivered in "
                    f"{len(self.delivery_plans)} trips."
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Planning failed: {str(e)}")
    
    def on_trip_select(self, event):
        """Handle trip selection in the listbox."""
        selection = self.trips_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < 0 or index >= len(self.delivery_plans):
            return
        
        plan = self.delivery_plans[index]
        self.display_trip_details(plan)
        
        # Also update visualization
        self.viz_trip_var.set(f"Trip {index+1}")
        self.visualize_trip(plan)
    
    def display_trip_details(self, plan):
        """Display trip details in the text widget."""
        drone = plan['drone']
        packages = plan['packages']
        route = plan['route']
        detailed_route = plan['detailed_route']
        total_distance = plan['total_distance']
        total_value = plan['total_value']
        total_weight = plan['total_weight']
        
        # Enable editing
        self.trip_details_text.config(state=tk.NORMAL)
        self.trip_details_text.delete(1.0, tk.END)
        
        # Add header
        self.trip_details_text.insert(tk.END, f"Drone {drone.id} Trip Details\n\n", 'header')
        
        # Add drone info
        self.trip_details_text.insert(tk.END, "Drone Specifications:\n", 'subheader')
        self.trip_details_text.insert(tk.END, f"  Max Weight: {drone.max_weight} kg\n", 'normal')
        self.trip_details_text.insert(tk.END, f"  Max Distance: {drone.max_distance} units\n\n", 'normal')
        
        # Add trip summary
        self.trip_details_text.insert(tk.END, "Trip Summary:\n", 'subheader')
        self.trip_details_text.insert(tk.END, f"  Packages: {len(packages)}\n", 'normal')
        self.trip_details_text.insert(tk.END, f"  Total Weight: {total_weight:.2f} kg", 'normal')
        if total_weight > 0.9 * drone.max_weight:
            self.trip_details_text.insert(tk.END, f" (Weight Capacity: {total_weight/drone.max_weight:.1%})\n", 'highlight')
        else:
            self.trip_details_text.insert(tk.END, "\n", 'normal')
        
        self.trip_details_text.insert(tk.END, f"  Total Value: {total_value:.2f}\n", 'normal')
        self.trip_details_text.insert(tk.END, f"  Total Distance: {total_distance:.2f}", 'normal')
        if total_distance > 0.9 * drone.max_distance:
            self.trip_details_text.insert(tk.END, f" (Distance Capacity: {total_distance/drone.max_distance:.1%})\n\n", 'highlight')
        else:
            self.trip_details_text.insert(tk.END, "\n\n", 'normal')
        
        # Add package details
        self.trip_details_text.insert(tk.END, "Packages:\n", 'subheader')
        for i, package in enumerate(packages):
            self.trip_details_text.insert(tk.END, f"  {i+1}. Package {package.id}: {package.weight} kg, value {package.value}, to {package.destination}\n", 'normal')
        self.trip_details_text.insert(tk.END, "\n", 'normal')
        
        # Add route details
        self.trip_details_text.insert(tk.END, "Route:\n", 'subheader')
        self.trip_details_text.insert(tk.END, f"  High-level: {' → '.join(route)}\n\n", 'normal')
        
        self.trip_details_text.insert(tk.END, "Detailed Route:\n", 'subheader')
        self.trip_details_text.insert(tk.END, f"  {' → '.join(detailed_route)}\n", 'normal')
        
        # Disable editing
        self.trip_details_text.config(state=tk.DISABLED)
    
    def on_viz_trip_select(self, event):
        """Handle trip selection in the visualization tab."""
        trip_name = self.viz_trip_var.get()
        if not trip_name:
            return
        
        try:
            # Extract trip index (format: "Trip X")
            index = int(trip_name.split()[1]) - 1
            if index < 0 or index >= len(self.delivery_plans):
                return
            
            plan = self.delivery_plans[index]
            self.visualize_trip(plan)
        except (ValueError, IndexError):
            pass
    
    def visualize_trip(self, plan):
        """Visualize a trip on the map."""
        # Switch to visualization tab
        self.notebook.select(2)
        
        # Update visualization
        self.map_visualization.visualize_city_map(
            self.city_map,
            plan['route'],
            plan['detailed_route'],
            plan['packages']
        )
    
    def refresh_visualization(self):
        """Refresh the map visualization."""
        trip_name = self.viz_trip_var.get()
        if not trip_name:
            # Just visualize the city map without a route
            self.map_visualization.visualize_city_map(self.city_map)
            return
        
        try:
            # Extract trip index (format: "Trip X")
            index = int(trip_name.split()[1]) - 1
            if index < 0 or index >= len(self.delivery_plans):
                return
            
            plan = self.delivery_plans[index]
            self.visualize_trip(plan)
        except (ValueError, IndexError):
            pass
    
    def load_sample_data(self):
        """Load sample data for testing."""
        # Clear current data
        self.clear_data(confirm=False)
        
        # Add cities
        self.city_map.add_city("Warehouse", True)
        self.city_map.add_city("City A")
        self.city_map.add_city("City B")
        self.city_map.add_city("City C")
        self.city_map.add_city("City D")
        self.city_map.add_city("City E")
        
        # Add routes
        self.city_map.add_route("Warehouse", "City A", 10)
        self.city_map.add_route("Warehouse", "City B", 15)
        self.city_map.add_route("Warehouse", "City C", 20)
        self.city_map.add_route("City A", "City B", 12)
        self.city_map.add_route("City B", "City C", 8)
        self.city_map.add_route("City C", "City D", 10)
        self.city_map.add_route("City D", "City E", 5)
        self.city_map.add_route("City E", "Warehouse", 25)
        
        # Add packages
        self.packages.append(Package(1, 2.5, 100, "City A"))
        self.packages.append(Package(2, 1.5, 80, "City A"))
        self.packages.append(Package(3, 3.0, 120, "City B"))
        self.packages.append(Package(4, 2.0, 90, "City C"))
        self.packages.append(Package(5, 4.0, 200, "City D"))
        self.packages.append(Package(6, 1.0, 50, "City E"))
        self.packages.append(Package(7, 3.5, 150, "City B"))
        self.packages.append(Package(8, 2.8, 110, "City C"))
        
        # Add drones
        self.drones.append(Drone(1, 5.0, 50))
        self.drones.append(Drone(2, 8.0, 80))
        
        # Update displays
        self.update_city_display()
        self.update_route_display()
        self.update_package_display()
        self.update_drone_display()
        self.update_city_combos()
        
        # Update visualization
        self.map_visualization.visualize_city_map(self.city_map)
        
        self.status_var.set("Sample data loaded")
        messagebox.showinfo("Success", "Sample data loaded successfully")
    
    def on_close(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()


def main():
    """Main function to run the application."""
    app = SmartDroneDeliveryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
