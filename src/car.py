import numpy as np

from src.grid import Grid
from src.utils import (
    CAR_BODY,
    CAR_HEAD,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_VALUE,
    ROAD_CELLS,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)


class Car:
    """
    Represents a car in the city grid, with a given position and direction.

    The car can move within the grid, enter and exit rotaries, and follow road rules.
    """

    def __init__(self, grid: Grid, position: tuple, road_type: int, car_size: int = 1):
        """
        Initialize the car with a given grid, position, and direction.

        Params:
        -------
        - grid: The grid in which the car is located.
        - position (tuple): The starting position of the car on the grid (x, y).
        """

        self.grid = grid
        self.in_rotary = False
        self.flag = 0
        self.road_type = road_type

        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError(f"\033[91mInvalid position {position} for the car.\033[0m")
        if not all(isinstance(i, int) for i in position):
            raise ValueError(
                f"\033[91mPosition coordinates {position} must be integers.\033[0m"
            )

        x, y = position
        if self.grid.grid[x, y] not in ROAD_CELLS:
            raise ValueError(
                f"\033[91mInvalid starting position {position} for the car.\033[0m"
            )
        elif self.grid.grid[x, y] in [CAR_HEAD, CAR_BODY]:
            raise ValueError(
                f"\033[91mPosition {position} is already occupied by another car.\033[0m"
            )
        else:
            self.grid.grid[x, y] = CAR_HEAD
        self.head_position = position

        self.car_size = car_size
        if self.car_size > 1:
            self.create_larger_car()

    def create_larger_car(self):
        """
        Create a larger car by adding more body cells to the car.
        """
        body_positions = np.zeros((self.car_size, 2), dtype=int)
        x, y = self.head_position

        # Fill in the body positions based on the road cell and direction
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            for i in range(self.car_size):
                x, y = self.loop_boundary(x - i - 1, y)
                body_positions[i] = (x, y)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            for i in range(self.car_size):
                x, y = self.loop_boundary(x + i + 1, y)
                body_positions[i] = (x, y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            for i in range(self.car_size):
                x, y = self.loop_boundary(x, y - i - 1)
                body_positions[i] = (x, y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            for i in range(self.car_size):
                x, y = self.loop_boundary(x, y + i + 1)
                body_positions[i] = (x, y)

        for x, y in body_positions:
            self.grid.grid[x, y] = CAR_BODY

    def loop_boundary(self, x: int, y: int) -> tuple:
        """
        Move the car to the boundary of the grid based on its current position and direction.
        Also checks for cars in front of the current car on the other side of the boundary.

        Params:
        -------
        - x (int): The current x-coordinate of the car.
        - y (int): The current y-coordinate of the car.

        Returns:
        --------
        - tuple: The new x and y coordinates of the car.
        """
        grid_boundary = self.grid.size

        if x < 0:
            x = grid_boundary - 1
        elif x >= grid_boundary:
            x = 0
        if y < 0:
            y = grid_boundary - 1
        elif y >= grid_boundary:
            y = 0
        return x, y

    def move(self):
        """
        Move the car forward based on its current position and direction.
        """

        def _move_intersection():
            """
            Move the car within an intersection based on its current position and direction.
            """
            _move_straight()

        def _move_straight():
            """
            Move the car in a straight line based on its current position and direction.
            """
            x, y = self.head_position

            if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
                new_pos = (x - 1, y)
            elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
                new_pos = (x + 1, y)
            elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
                new_pos = (x, y - 1)
            elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
                new_pos = (x, y + 1)
            else:
                return  # Invalid direction, do nothing

            new_pos = self.loop_boundary(*new_pos)

            # Check if the new position is a road cell AND not occupied by another car
            if (
                self.grid.grid[new_pos] in ROAD_CELLS
                or INTERSECTION_VALUE
                and self.grid.grid[new_pos] not in [CAR_HEAD, CAR_BODY]
            ):
                # Only mark the old position as a road block if it's not already occupied by another car
                old_pos = self.head_position
                if (
                    self.grid.grid[old_pos] == CAR_HEAD
                ):  # Only clear if it's still our car's head
                    self.grid.grid[old_pos] = self.road_type
                self.head_position = new_pos
                self.grid.grid[new_pos] = CAR_HEAD

        next_cell = self.check_infront()

        if next_cell in [CAR_HEAD, CAR_BODY]:
            return

        elif next_cell == INTERSECTION_VALUE:
            if not self.grid.allow_rotary_entry:
                return
            else:
                _move_intersection()

        elif next_cell in ROAD_CELLS:
            _move_straight()

        elif self.road_type == CAR_HEAD:
            return
        else:
            raise ValueError(
                f"\033[91mInvalid road cell {self.road_type} for the car at {self.head_position}.\033[0m"
            )

    def check_infront(self) -> int:
        """
        Check if there is a car in front of the current car.

        Returns:
        --------
        - int: The value of the cell in front of the car.
        """
        x, y = self.head_position

        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x - 1, y)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x + 1, y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x, y - 1)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x, y + 1)

        return self.grid.grid[x, y]

    def set_road_type(self, road_type: int):
        """
        Set the road type for the car to move on.
        """
        if road_type not in ROAD_CELLS:
            raise ValueError(
                f"\033[91mInvalid road type {road_type} for the car.\033[0m"
            )
        self.road_type = road_type
