import numpy as np

from src.utils import (
    CAR_HEAD,
    INTERSECTION_VALUE,
    ROAD_CELLS,
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
        total_cars = len(self.grid.cars)
        moving_cars = len(moved_cars)

        # Count cars on roads and intersections
        cars_on_roads = 0
        cars_at_intersections = 0

        for car in self.grid.cars:
            x, y = car.head_position
            cell_type = self.grid.road_layout[
                x, y
            ]  # Use road_layout to check original cell type
            if cell_type in ROAD_CELLS:
                cars_on_roads += 1
            elif cell_type == INTERSECTION_VALUE:
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
        return self.metrics_history

    def set_initial_cars(self):
        """Set the initial number of cars for percentage calculation."""
        car_positions = np.where(self.grid.grid == CAR_HEAD)
        self.initial_cars = len(car_positions[0])
