import numpy as np

from src.utils import (
    CAR_HEAD,
    INTERSECTION_VALUE,
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

        # Calculate average and max waiting times
        if self.car_wait_times:
            avg_wait = sum(self.car_wait_times.values()) / len(self.car_wait_times)
            max_wait = max(self.car_wait_times.values())
        else:
            avg_wait = max_wait = 0

        # Calculate congestion rate (percentage of cars not moving)
        congestion = 1 - (moving_cars / total_cars) if total_cars > 0 else 0

        # Count cars at intersections
        intersection_cars = sum(
            1
            for car in self.grid.cars
            if self.grid.grid[car.head_position] == INTERSECTION_VALUE
        )

        return {
            "timestamp": len(self.metrics_history),
            "total_cars": total_cars,
            "moving_cars": moving_cars,
            "average_wait_time": avg_wait,
            "max_wait_time": max_wait,
            "congestion_rate": congestion,
            "intersection_cars": intersection_cars,
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
