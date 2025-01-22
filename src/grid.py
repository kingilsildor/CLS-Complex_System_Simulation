import numpy as np

# import test_case as test_case
from src.utils import (
    BLOCKS_VALUE,
    HORIZONTAL_ROAD_VALUE,
    INTERSECTION_VALUE,
    VERTICAL_ROAD_VALUE,
)

# Add new constants for vertical_up and vertical_down lanes
VERTICAL_UP_LANE_VALUE = 6
VERTICAL_DOWN_LANE_VALUE = 7

# Add new constants for horizontal_left and horizontal_right lanes
HORIZONTAL_LEFT_LANE_VALUE = 8
HORIZONTAL_RIGHT_LANE_VALUE = 9


class Grid:
    """
    Represents a city grid with roads, intersections, and moving cars.

    The grid is initialized with blocks and lanes, and roads are created accordingly.
    Cars can be added to the grid and their movements updated dynamically.
    """

    def __init__(self, grid_size: int, blocks_size: int, lane_width: int = 2):
        """
        Initialize the grid with a given size, block size, and lane width.

        Params:
        -------
        - grid_size (int): The size of the grid (NxN).
        - blocks_size (int): The size of blocks between roads.
        - lane_width (int, optional): The width of each lane. Defaults to 2.
        """
        self.grid = np.full((grid_size, grid_size), BLOCKS_VALUE, dtype=int)
        self.underlying_grid = np.full(
            (grid_size, grid_size), BLOCKS_VALUE, dtype=int
        )  # Track original cell types
        self.size = grid_size
        self.blocks = blocks_size

        # Ensure the number of lanes is an even number
        try:
            if lane_width % 2 != 0:
                raise ValueError(
                    "\033[38;5;214mNumber of lanes must be an even number.\033[0m"
                )
            self.lane_width = lane_width
        except ValueError:
            self.lane_width = lane_width + 1
            print(f"\033[38;5;214mSetting lane width to {self.lane_width}.\033[0m")

        self.cars = []
        self.rotary_dict = []
        self.flag = np.zeros((grid_size, grid_size), dtype=int)
        self.roads()
        # Store the road layout
        self.road_layout = self.grid.copy()

    def roads(self):
        """
        Construct roads on the grid, including vertical, horizontal, and intersection roads.
        """
        self.create_vertical_lanes()
        self.create_horizontal_lanes()
        self.create_intersections()

    def create_edge_lanes(self):
        """
        Create lanes along the edges of the grid, ensuring connectivity.
        """
        self.grid[: self.lane_width, :] = HORIZONTAL_ROAD_VALUE
        self.grid[-self.lane_width :, :] = HORIZONTAL_ROAD_VALUE
        self.grid[:, : self.lane_width] = HORIZONTAL_ROAD_VALUE
        self.grid[:, -self.lane_width :] = HORIZONTAL_ROAD_VALUE

    def create_vertical_lanes(self):
        """
        Create vertical roads at regular intervals based on block size.
        """
        for col in range(int(self.blocks / 2), self.size, self.blocks):
            left = col
            right = min(col + self.lane_width, self.size)
            for x in range(self.size):
                for y in range(left, right):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if y == right - 1:  # Right lane
                            if x % 2 == 0:
                                self.grid[x, y] = VERTICAL_UP_LANE_VALUE
                            else:
                                self.grid[x, y] = VERTICAL_DOWN_LANE_VALUE
                        else:
                            self.grid[x, y] = VERTICAL_ROAD_VALUE
                        self.underlying_grid[x, y] = VERTICAL_ROAD_VALUE

    def create_horizontal_lanes(self):
        """
        Create horizontal roads at regular intervals based on block size.
        """
        for row in range(int(self.blocks / 2), self.size, self.blocks):
            top = row
            bottom = min(row + self.lane_width, self.size)
            for x in range(top, bottom):
                for y in range(self.size):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if x == bottom - 1:  # Bottom lane
                            if y % 2 == 0:
                                self.grid[x, y] = HORIZONTAL_LEFT_LANE_VALUE
                            else:
                                self.grid[x, y] = HORIZONTAL_RIGHT_LANE_VALUE
                        else:
                            self.grid[x, y] = HORIZONTAL_ROAD_VALUE
                        self.underlying_grid[x, y] = HORIZONTAL_ROAD_VALUE

    def create_intersections(self):
        """
        Create intersections where vertical and horizontal roads meet.
        Intersections are designed as 2x2 rotary spaces to facilitate smooth traffic flow.
        """
        for i in range(int(self.blocks / 2), self.size, self.blocks):
            for j in range(int(self.blocks / 2), self.size, self.blocks):
                x0 = i
                x1 = i + self.lane_width
                y0 = j
                y1 = j + self.lane_width

                self.grid[x0:x1, y0:y1] = INTERSECTION_VALUE
                self.underlying_grid[x0:x1, y0:y1] = INTERSECTION_VALUE

                ring = [(x0, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 1, y0)]
                self.rotary_dict.append(ring)

    def add_cars(self, cars: list):
        """
        Add cars to the grid.

        Params:
        -------
        - cars (list): A list of car objects to be added to the grid.
        """
        self.cars.extend(cars)

    def update_movement(self):
        """
        Update the grid to reflect the movement of all cars.
        """
        # Reset to road layout instead of redrawing roads
        self.grid = self.road_layout.copy()

        for car in self.cars:
            car.move_car()
