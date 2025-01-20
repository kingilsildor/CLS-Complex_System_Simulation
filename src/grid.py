import numpy as np
from src.utils import ROAD_VALUE, BLOCKS_VALUE, CAR_VALUE

class Grid:
    def __init__(self, grid_size: int, blocks_size: int, lane_width: int = 2):
        self.grid = np.full((grid_size, grid_size), BLOCKS_VALUE, dtype=int)
        self.size = grid_size
        self.blocks = blocks_size

        try:
            if lane_width % 2 != 0:
                raise ValueError(f"\033[91mThe lane width should be even!\033[0m")
            self.lane_width = lane_width
        except ValueError as e:
            print(e)
            self.lane_width = lane_width + 1
            print(f"Setting value to {self.lane_width}")

        self.cars = []
        self.roads()

    def roads(self):
        """
        Add roads to the grid
        """
        for i in range(0, self.size, self.blocks):
            self.grid[max(0, i - self.lane_width + 1):i + 1, :] = ROAD_VALUE
            self.grid[:, max(0, i - self.lane_width + 1):i + 1] = ROAD_VALUE
        
        # Add lanes on the edges
        self.grid[:self.lane_width, :] = ROAD_VALUE
        self.grid[-self.lane_width:, :] = ROAD_VALUE
        self.grid[:, :self.lane_width] = ROAD_VALUE
        self.grid[:, -self.lane_width:] = ROAD_VALUE

    def add_cars(self, cars: list):
        """
        Add cars to the grid.
        """
        self.cars.extend(cars)
        print(f"Added {len(cars)} cars to the grid.")

    def update_movement(self):
        """
        Update the grid and move all cars.
        """
        self.grid.fill(BLOCKS_VALUE)
        self.roads()

        for car in self.cars:
            car.move(self)
            x, y = car.position
            self.grid[x, y] = CAR_VALUE

    def display(self):
        """
        Display the grid (for testing).
        """
        print(self.grid)

