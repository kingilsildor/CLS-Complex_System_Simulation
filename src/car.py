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
            raise ValueError("\033[91mInvalid position for the car.\033[0m")
        if not all(isinstance(i, int) for i in position):
            raise ValueError("\033[91mPosition coordinates must be integers.\033[0m")

        x, y = position
        if self.grid.grid[x, y] not in ROAD_CELLS:
            raise ValueError("\033[91mInvalid starting position for the car.\033[0m")
        else:
            self.grid.grid[x, y] = CAR_VALUE
        self.position = position

    def move(self):
        """
        Move the car forward based on its current position and direction.
        """

        def _move_boundary(x: int, y: int) -> tuple:
            """
            Move the car to the boundary of the grid based on its current position and direction.
            """
            grid_boundary = self.grid.size

            if x < 0:
                x = 0
            elif x >= grid_boundary:
                x = grid_boundary - 1
            if y < 0:
                y = 0
            elif y >= grid_boundary:
                y = grid_boundary - 1
            return x, y

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

            new_pos = _move_boundary(*new_pos)
            if self.grid.grid[new_pos] in ROAD_CELLS:
                self.position = new_pos
                self.grid.grid[new_pos] = CAR_VALUE

        if self.get_road_cell() in ROAD_CELLS:
            _move_straight()
        elif self.get_road_cell() == INTERSECTION_VALUE:
            _move_intersection()
        else:
            raise ValueError("\033[91mInvalid road cell for the car.\033[0m")

    def get_road_cell(self):
        """
        Get the current road cell in which the car is located.
        """
        return self.grid.grid[self.position[0], self.position[1]]

    def check_infront(self):
        """
        Check if there is a car in front of the current car.
        """
        pass
