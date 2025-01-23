import numpy as np

from src.utils import (
    CAR_HEAD,
    HORIZONTAL_ROAD_VALUE_LEFT,
    INTERSECTION_INTERNAL,
    VERTICAL_ROAD_VALUE_RIGHT,
)


class DensityTracker:
    """
    Tracks various density metrics in the traffic simulation.
    """

    def __init__(self, grid):
        """
        Initialize the density tracker.

        Parameters:
        -----------
        grid : Grid
            The grid object containing the traffic simulation
        """
        self.grid = grid
        self.initial_cars = None

    def set_initial_cars(self):
        """Set the initial number of cars for percentage calculation."""
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        self.initial_cars = len(car_positions[0])

    def calculate_road_density(self):
        """
        Calculate the density of cars on road cells.

        Returns:
        --------
        float : Percentage of road cells occupied by cars (0-1)
        """
        # Get all road cells (excluding intersections)
        road_mask = (self.grid.underlying_grid == VERTICAL_ROAD_VALUE_RIGHT) | (
            self.grid.underlying_grid == HORIZONTAL_ROAD_VALUE_LEFT
        )
        total_road_cells = np.sum(road_mask)

        # Get car positions
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        cars_on_roads = 0

        # Check each car's position against the underlying grid
        for x, y in zip(*car_positions):
            if (
                self.grid.underlying_grid[x, y] == VERTICAL_ROAD_VALUE_RIGHT
                or self.grid.underlying_grid[x, y] == HORIZONTAL_ROAD_VALUE_LEFT
            ):
                cars_on_roads += 1

        return cars_on_roads / total_road_cells if total_road_cells > 0 else 0

    def calculate_intersection_density(self):
        """
        Calculate the density of cars at intersections.

        Returns:
        --------
        float : Percentage of intersection cells occupied by cars (0-1)
        """
        # Get all intersection cells
        intersection_mask = self.grid.underlying_grid == INTERSECTION_INTERNAL
        total_intersection_cells = np.sum(intersection_mask)

        # Get car positions
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        cars_at_intersections = 0

        # Check each car's position against the underlying grid
        for x, y in zip(*car_positions):
            if self.grid.underlying_grid[x, y] == INTERSECTION_INTERNAL:
                cars_at_intersections += 1

        return (
            cars_at_intersections / total_intersection_cells
            if total_intersection_cells > 0
            else 0
        )

    def calculate_overall_density(self):
        """
        Calculate the overall density of cars in the system.

        Returns:
        --------
        dict : Dictionary containing various density metrics
        """
        # Create mask for all valid positions (roads + intersections)
        system_mask = (
            (self.grid.underlying_grid == VERTICAL_ROAD_VALUE_RIGHT)
            | (self.grid.underlying_grid == HORIZONTAL_ROAD_VALUE_LEFT)
            | (self.grid.underlying_grid == INTERSECTION_INTERNAL)
        )
        total_system_cells = np.sum(system_mask)

        # Count cars in system
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        total_cars = len(car_positions[0])

        # Calculate system-wide density (as decimal, like other densities)
        system_density = (
            total_cars / total_system_cells if total_system_cells > 0 else 0
        )

        return {
            "road_density": self.calculate_road_density(),
            "intersection_density": self.calculate_intersection_density(),
            "total_cars": total_cars,
            "system_density": system_density,
        }
