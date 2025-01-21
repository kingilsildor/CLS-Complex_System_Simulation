import numpy as np

from src.utils import (
    BLOCKS_VALUE,
    HORIZONTAL_ROAD_VALUE,
    INTERSECTION_VALUE,
    VERTICAL_ROAD_VALUE,
)


class Grid:
    def __init__(self, grid_size: int, blocks_size: int, lane_width: int = 2):
        self.grid = np.full((grid_size, grid_size), BLOCKS_VALUE, dtype=int)
        self.size = grid_size
        self.blocks = blocks_size
        self.lane_width = lane_width
        self.cars = []
        self.rotary_dict = []
        self.flag = np.zeros((grid_size, grid_size), dtype=int)
        self.roads()

    def roads(self):
        """
        Add roads to the grid
        """

        # Add lanes on the edges
        # self.grid[: self.lane_width, :] = HORIZONTAL_ROAD_VALUE
        # self.grid[-self.lane_width :, :] = HORIZONTAL_ROAD_VALUE
        # self.grid[:, : self.lane_width] = HORIZONTAL_ROAD_VALUE
        # self.grid[:, -self.lane_width :] = HORIZONTAL_ROAD_VALUE

        self.create_vertical_lanes()
        self.create_horizontal_lanes()
        self.create_intersections()

    def create_vertical_lanes(self):
        for col in range(0, self.size, self.blocks):
            left = col
            right = min(col + self.lane_width, self.size)
            for x in range(self.size):
                for y in range(left, right):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        self.grid[x, y] = VERTICAL_ROAD_VALUE

    def create_horizontal_lanes(self):
        for row in range(0, self.size, self.blocks):
            top = row
            bottom = min(row + self.lane_width, self.size)
            for x in range(top, bottom):
                for y in range(self.size):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        self.grid[x, y] = HORIZONTAL_ROAD_VALUE

    def create_intersections(self):
        for i in range(self.blocks, self.size, self.blocks):
            for j in range(self.blocks, self.size, self.blocks):
                # 2x2 rotary at intersection
                x0 = i
                x1 = i + self.lane_width
                y0 = j
                y1 = j + self.lane_width

                self.grid[x0:x1, y0:y1] = INTERSECTION_VALUE

                ring = [(x0, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 1, y0)]
                self.rotary_dict.append(ring)

    def add_cars(self, cars: list):
        """Add cars to the grid"""
        self.cars.extend(cars)

    def update_movement(self):
        """Update the grid and move all cars"""
        self.grid.fill(BLOCKS_VALUE)
        self.roads()

        for car in self.cars:
            car.move_car()
