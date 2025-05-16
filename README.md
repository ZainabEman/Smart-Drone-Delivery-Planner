# Smart Drone Delivery Planner

![Project Banner](https://via.placeholder.com/1200x300/3498db/ffffff?text=Smart+Drone+Delivery+Planner)

## Introduction

The Smart Drone Delivery Planner is a comprehensive Python application designed to optimize package delivery operations using drones. This system implements advanced algorithms to solve the complex logistics challenges of drone-based delivery services, including route planning, package selection, and resource allocation.

The application provides an intuitive graphical user interface that allows logistics managers to input city maps, package details, and drone specifications, then automatically generates optimized delivery plans that maximize value while respecting weight and distance constraints.

## Objectives

- Create a complete delivery planning system with an interactive GUI
- Implement efficient algorithms for shortest path finding and package selection
- Provide visualization tools for routes and delivery plans
- Support data persistence through save/load functionality
- Enable dynamic updates to handle route closures and changes
- Maximize delivery value while respecting drone constraints

## Tech Stack

- **Language**: Python 3.x
- **GUI Framework**: Tkinter (Python standard library)
- **Data Structures**: Custom implementations for city maps (weighted graphs), packages, and drones
- **Algorithms**: 
  - Dijkstra's algorithm for shortest path finding
  - Modified Knapsack algorithm for package selection
  - Route planning with optimization for multiple destinations
- **File Formats**: JSON for data persistence
- **Testing**: Python's unittest framework

## System Requirements

### Software Requirements
- Python 3.6 or higher
- Operating System: Windows, macOS, or Linux
- Visual Studio Code (recommended IDE)

### Hardware Requirements
- Processor: 1.6 GHz or faster
- RAM: 2 GB or more
- Disk Space: 50 MB for application and data
- Display: 1280x720 or higher resolution

## Project Structure

```
smart_drone_delivery_planner/
├── algorithms/                # Algorithm implementations
│   ├── __init__.py
│   ├── package_selection.py   # Knapsack algorithm for package selection
│   ├── route_planning.py      # Route planning algorithms
│   └── shortest_path.py       # Dijkstra's algorithm implementation
├── data/                      # Directory for sample data files
├── gui/                       # GUI components
│   ├── __init__.py
│   ├── main_app.py            # Main application window and interface
│   └── map_visualization.py   # Map visualization component
├── models/                    # Data structure definitions
│   ├── __init__.py
│   ├── city.py                # City and CityMap classes
│   ├── drone.py               # Drone class
│   └── package.py             # Package class
├── tests/                     # Unit tests
│   └── test_core.py           # Tests for core functionality
├── utils/                     # Utility functions
│   └── data_utils.py          # Data validation and file operations
├── __init__.py                # Package initialization
├── main.py                    # Application entry point
└── README.md                  # This file
```

## Setup Guide

### Installation

1. **Clone or download the repository**
   ```
   git clone https://github.com/yourusername/smart-drone-delivery-planner.git
   ```
   Or download and extract the ZIP file provided.

2. **Verify Python installation**
   Ensure Python 3.6+ is installed on your system:
   ```
   python --version
   ```
   If not installed, download from [python.org](https://www.python.org/downloads/).

3. **Open the project in VSCode**
   - Launch Visual Studio Code
   - Go to File > Open Folder
   - Navigate to the extracted project directory
   - Click "Select Folder"

### Running the Application

1. **Open the terminal in VSCode** (Terminal > New Terminal)

2. **Run the main script**
   ```
   python main.py
   ```
   
3. **Alternative methods**:
   - Right-click on `main.py` in the Explorer panel and select "Run Python File in Terminal"
   - Use the Run button in VSCode when `main.py` is open in the editor

## Usage Guide

### Main Interface

The application is organized into three main tabs:
1. **Input Data**: For entering city map, package, and drone information
2. **Delivery Plans**: For viewing the generated delivery plans and trip details
3. **Map Visualization**: For visualizing the city map and delivery routes

### Step-by-Step Usage

#### 1. Input Data Tab

**Adding Cities**:
- Enter a city name in the "City Name" field
- Check the "Warehouse" box if this city contains the central warehouse
- Click "Add City"
- Note: One city must be designated as the warehouse

**Adding Routes**:
- Select the "From City" and "To City" from the dropdown menus
- Enter the distance between the cities
- Click "Add Route"
- Note: Routes are bidirectional by default

**Adding Packages**:
- Enter the package ID, weight, value, and select a destination city
- Click "Add Package"

**Adding Drones**:
- Enter the drone ID, maximum weight capacity, and maximum flight distance
- Click "Add Drone"

#### 2. Running the Planning Algorithm

- After entering all required data, click "Run Delivery Planning"
- The system will calculate optimal delivery plans for each drone
- Results will be displayed in the "Delivery Plans" tab

#### 3. Viewing Delivery Plans

- Select a trip from the list on the left to view its details
- The details panel shows:
  - Drone specifications
  - Trip summary (packages, weight, value, distance)
  - List of packages included in the trip
  - Route information

#### 4. Map Visualization

- Select a trip from the dropdown to visualize its route on the map
- The map shows:
  - Cities as circles (warehouse in red, other cities in blue)
  - Routes as lines between cities
  - The selected delivery route highlighted in green
  - Package counts at destination cities

#### 5. Additional Features

**Save/Load Data**:
- Click "Save Data" to save the current city map, packages, and drones to a JSON file
- Click "Load Data" to load previously saved data

**Sample Data**:
- Click "Load Sample Data" to populate the application with example data for testing

**Dynamic Updates**:
- To simulate a route closure, select a route from the routes list and delete it
- Run the planning algorithm again to generate new routes avoiding the closed path

## Demo Scenarios

### Scenario 1: Simple Delivery Network

**Setup**:
- Create a small network with 3-4 cities including a warehouse
- Add 5-6 packages of varying weights and values
- Configure a drone with moderate capacity

**Expected Results**:
- The system should generate a simple, efficient delivery route
- All packages should be deliverable in one or two trips

### Scenario 2: Complex Network with Constraints

**Setup**:
- Create a larger network with 6-8 cities
- Add 10-15 packages distributed across different destinations
- Configure multiple drones with different capacities and range limitations

**Expected Results**:
- The system should prioritize high-value packages within constraints
- Multiple trips may be required to deliver all packages
- Different drones may be assigned different routes based on their capabilities

### Scenario 3: Edge Cases and Limitations

**Setup**:
- Include some very heavy packages that approach drone capacity limits
- Create some distant cities that test the range limits of drones
- Remove some routes to create "islands" or longer paths

**Expected Results**:
- The system should identify packages that cannot be delivered
- Routes should be optimized to handle distance constraints
- The planner should find alternative paths when direct routes are unavailable

## Algorithm Details

### Shortest Path Finding

The application uses Dijkstra's algorithm to find the shortest path between cities:

1. Initialize distances from the start city to all other cities as infinity
2. Set distance to the start city as 0
3. Create a priority queue with the start city
4. While the queue is not empty:
   - Get the city with the smallest distance
   - For each neighbor, calculate the distance through the current city
   - If this distance is smaller than the known distance, update it
5. Return the distances and predecessors for path reconstruction

### Package Selection

The package selection uses a variation of the 0/1 Knapsack algorithm:

1. Group packages by destination city
2. Sort packages within each destination by value-to-weight ratio
3. Use dynamic programming to find the optimal combination of packages
4. Check if the selected packages can be delivered within the drone's distance limit
5. If not, use a greedy approach based on closest destinations first

### Route Planning

The route planning algorithm optimizes the sequence of city visits:

1. For small numbers of destinations (≤3), try all permutations to find the optimal route
2. For larger numbers, use a greedy nearest-neighbor approach
3. Always start and end at the warehouse
4. Calculate the total distance using the shortest paths between consecutive cities

## Conclusion

The Smart Drone Delivery Planner demonstrates how algorithmic approaches can solve complex logistics problems in drone delivery systems. By combining graph theory, dynamic programming, and heuristic methods, the application provides an efficient solution for maximizing delivery value while respecting physical constraints.

The modular design of the application allows for easy extension and modification, making it adaptable to various delivery scenarios and requirements. The intuitive GUI makes it accessible to users without technical expertise in algorithms or optimization.

This project serves as both a practical tool for drone delivery planning and an educational resource for understanding the application of classic algorithms to real-world logistics problems.

## License

This project is released under the MIT License. See the LICENSE file for details.

## Acknowledgments

- The project was developed as a demonstration of applying algorithmic solutions to logistics problems
- Thanks to all contributors and testers who provided valuable feedback
