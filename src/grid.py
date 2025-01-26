import numpy as np

from src.utils import (
    BLOCKS_VALUE,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_DRIVE,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
    CAR_HEAD,
    ROAD_CELLS,
)

temp = HORIZONTAL_ROAD_VALUE_LEFT + VERTICAL_ROAD_VALUE_RIGHT


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
                raise ValueError("Number of lanes must be an even number.")
            self.lane_width = lane_width
        except ValueError:
            self.lane_width = lane_width + 1
            print(f"Setting lane width to {self.lane_width}.")

        self.cars = []
        self.rotary_dict = []
        self.flag = np.full((grid_size, grid_size), INTERSECTION_DRIVE, dtype=int)
        self.roads()

        # Store the road layout
        self.road_layout = self.grid.copy()

        # Count road and intersection cells
        road_mask = np.zeros_like(self.grid, dtype=bool)
        for road_type in ROAD_CELLS:
            road_mask = road_mask | (self.grid == road_type)
        self.road_cells = np.sum(road_mask)

        self.intersection_cells = np.sum(self.grid == INTERSECTION_VALUE)

        self.allow_rotary_entry = False  # Start with rotaries blocked

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
        self.grid[: self.lane_width, :] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[-self.lane_width :, :] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[:, : self.lane_width] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[:, -self.lane_width :] = HORIZONTAL_ROAD_VALUE_RIGHT

    def create_vertical_lanes(self):
        """
        Create vertical roads at regular intervals based on block size.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for col in range(half_block, self.size, self.blocks):
            left = col
            right = min(col + self.lane_width, self.size)
            lane_devider = self.lane_width // 2

            for x in range(self.size):
                for y in range(left, right):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if (y - left) < lane_devider:
                            self.grid[x, y] = VERTICAL_ROAD_VALUE_LEFT
                        else:
                            self.grid[x, y] = VERTICAL_ROAD_VALUE_RIGHT

    def create_horizontal_lanes(self):
        """
        Create horizontal roads at regular intervals based on block size.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for row in range(half_block, self.size, self.blocks):
            top = row
            bottom = min(row + self.lane_width, self.size)
            lane_devider = self.lane_width // 2

            for x in range(top, bottom):
                for y in range(self.size):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if (x - top) < lane_devider:
                            self.grid[x, y] = HORIZONTAL_ROAD_VALUE_LEFT
                        else:
                            self.grid[x, y] = HORIZONTAL_ROAD_VALUE_RIGHT

    def create_intersections(self):
        """
        Create intersections where vertical and horizontal roads meet.
        Intersections are designed as 2x2 rotary spaces to facilitate smooth traffic flow.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for i in range(half_block, self.size, self.blocks):
            for j in range(half_block, self.size, self.blocks):
                x0, x1 = i, i + self.lane_width
                y0, y1 = j, j + self.lane_width

                self.grid[x0:x1, y0:y1] = INTERSECTION_DRIVE

                ring = [(x0, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 1, y0)]
                assert isinstance(ring, list)
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
        for car in self.cars:
            car.move()
        # print("--------------------")