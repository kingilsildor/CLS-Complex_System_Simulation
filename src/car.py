from src.grid import Grid
from src.utils import (
    CAR_VALUE,
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

    def __init__(self, grid: Grid, position: tuple, car_size: int = 1):
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
        self.car_size = car_size

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
        else:
            self.grid.grid[x, y] = CAR_VALUE
        self.position = position

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
            pass

        def _move_straight():
            """
            Move the car in a straight line based on its current position and direction.
            """
            x, y = self.position
            road_value = self.get_road_cell()

            if road_value == VERTICAL_ROAD_VALUE_RIGHT:
                new_pos = (x - 1, y)
            elif road_value == VERTICAL_ROAD_VALUE_LEFT:
                new_pos = (x + 1, y)
            elif road_value == HORIZONTAL_ROAD_VALUE_LEFT:
                new_pos = (x, y - 1)
            elif road_value == HORIZONTAL_ROAD_VALUE_RIGHT:
                new_pos = (x, y + 1)
            else:
                return  # Invalid direction, do nothing

            new_pos = self.loop_boundary(*new_pos)

            if self.grid.grid[new_pos] in ROAD_CELLS:
                self.position = new_pos
                self.grid.grid[new_pos] = CAR_VALUE

        road_cell = self.get_road_cell()
        if self.check_infront():
            pass  # Do nothing if there is a car in front
        elif road_cell in ROAD_CELLS:
            _move_straight()
        elif road_cell == INTERSECTION_VALUE:
            _move_intersection()
        elif road_cell == CAR_VALUE:
            print(
                f"\033[93mCar at {self.position} is blocked or spawned on the same cell.\033[0m"
            )
        else:
            raise ValueError(
                f"\033[91mInvalid road cell {road_cell} for the car at {self.position}.\033[0m"
            )

    def get_road_cell(self):
        """
        Get the current road cell in which the car is located.
        """
        return self.grid.grid[self.position[0], self.position[1]]

    def check_infront(self) -> bool:
        """
        Check if there is a car in front of the current car.

        Returns:
        --------
        - bool: True if there is a car in front, False otherwise.
        """
        road_cell = self.get_road_cell()
        x, y = self.position

        if road_cell == VERTICAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x - 1, y)
        if road_cell == VERTICAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x + 1, y)
        if road_cell == HORIZONTAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x, y - 1)
        if road_cell == HORIZONTAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x, y + 1)

        return self.grid.grid[x, y] == CAR_VALUE
