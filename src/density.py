import numpy as np

from src.utils import (
    CAR_HEAD,
    HORIZONTAL_ROAD_VALUE_LEFT,
    INTERSECTION_DRIVE,
    VERTICAL_ROAD_VALUE_RIGHT,

)


class DensityTracker:
    """
    Tracks various traffic metrics in the simulation.
    """

    def __init__(self, grid):
        """
        Initialize the tracker.

        Parameters:
        -----------
        grid : Grid
            The grid object containing the traffic simulation
        """
        self.grid = grid
        self.car_wait_times = {}  # Maps car to its current waiting time
        self.total_cars = len(grid.cars)
        self.metrics_history = []  # Store metrics over time

    def update(self, moved_cars):
        """
        Update metrics for this time step.

        Parameters:
        -----------
        moved_cars : set
            Set of cars that moved this time step
        """
        # Update waiting times for all cars
        for car in self.grid.cars:
            if car not in self.car_wait_times:
                self.car_wait_times[car] = 0

            if car in moved_cars:
                self.car_wait_times[car] = 0  # Reset wait time if car moved
            else:
                self.car_wait_times[car] += 1  # Increment wait time if car didn't move

        # Calculate current metrics
        metrics = self.get_metrics(moved_cars)
        self.metrics_history.append(metrics)

        return metrics

    def get_metrics(self, moved_cars):
        """
        Calculate current traffic metrics.

        Parameters:
        -----------
        moved_cars : set
            Set of cars that moved this time step

        Returns:
        --------
        dict : Dictionary containing traffic metrics
        """
        # Get all intersection cells
        intersection_mask = self.grid.underlying_grid == INTERSECTION_DRIVE
        total_intersection_cells = np.sum(intersection_mask)


        # Count cars on roads and intersections
        cars_on_roads = 0
        cars_at_intersections = 0

        # Check each car's position against the underlying grid
        for x, y in zip(*car_positions):
            if self.grid.underlying_grid[x, y] == INTERSECTION_DRIVE:
                cars_at_intersections += 1

        # Calculate densities
        road_density = cars_on_roads / (
            self.grid.road_cells + self.grid.intersection_cells
        )
        intersection_density = cars_at_intersections / (
            self.grid.road_cells + self.grid.intersection_cells
        )
        global_density = total_cars / (
            self.grid.road_cells + self.grid.intersection_cells
        )

        # Calculate velocities and flow
        average_velocity = moving_cars / total_cars if total_cars > 0 else 0
        traffic_flow = global_density * average_velocity  # J = ρ⟨v⟩
        queue_length = total_cars - moving_cars

        return {
            "timestamp": len(self.metrics_history),
            "total_cars": total_cars,
            "moving_cars": moving_cars,
            "road_density": road_density,
            "intersection_density": intersection_density,
            "global_density": global_density,
            "average_velocity": average_velocity,
            "traffic_flow": traffic_flow,
            "queue_length": queue_length,
        }

    def get_history(self):
        """
        Get the complete history of metrics.

        Returns:
        --------
        list : List of metric dictionaries over time
        """
        # Create mask for all valid positions (roads + intersections)
        system_mask = (
            (self.grid.underlying_grid == VERTICAL_ROAD_VALUE_RIGHT)
            | (self.grid.underlying_grid == HORIZONTAL_ROAD_VALUE_LEFT)
            | (self.grid.underlying_grid == INTERSECTION_DRIVE)
        )
        total_system_cells = np.sum(system_mask)


    def set_initial_cars(self):
        """Set the initial number of cars for percentage calculation."""
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        self.initial_cars = len(car_positions[0])
