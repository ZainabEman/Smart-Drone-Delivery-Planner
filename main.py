"""
Main entry point for Smart Drone Delivery Planner.

This module initializes and runs the application.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_app import SmartDroneDeliveryApp


def main():
    """Main function to run the application."""
    app = SmartDroneDeliveryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
