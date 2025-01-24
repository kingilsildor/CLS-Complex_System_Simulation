import numpy as np

from src.grid import Grid
from src.utils import (
    CAR_BODY,
    CAR_HEAD,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_CELLS,
    INTERSECTION_EXIT,
    INTERSECTION_INTERNAL,
    ROAD_CELLS,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)


class Car:
    """
    Represents a car in the city grid, with a given position and direction.

    The car can move within the grid, enter and exit rotaries, and follow road rules.
    """

    def __init__(self, grid: Grid, position: tuple, road_type: int, car_size: int = 2):
        """
        Initialize the car with a given grid, position, and direction.

        Params:
        -------
        - grid: The grid in which the car is located.
        - position (tuple): The starting position of the car on the grid (x, y).
        """
        assert isinstance(grid, Grid)
        self.grid = grid
        self.in_rotary = False
        self.flag = 0

        if road_type not in ROAD_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type

        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError(f"Invalid position {position} for the car.")
        if not all(isinstance(i, int) for i in position):
            raise ValueError(f"Position coordinates {position} must be integers.")

        x, y = position

        if self.grid.grid[x, y] not in ROAD_CELLS:
            raise ValueError(f"Invalid starting position {position} for the car.")
        else:
            self.grid.grid[x, y] = CAR_HEAD

        self.head_position = position

        self.car_body_size = car_size - 1
        if self.car_body_size >= 1:
            self.create_larger_car()

    def create_larger_car(self):
        """
        Create a larger car by adding more body cells to the car.
        """
        self.body_positions = np.zeros((self.car_body_size, 2), dtype=int)
        x, y = self.head_position

        # Fill in the body positions based on the road cell and direction
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            for i in range(self.car_body_size):
                x, y = self.loop_boundary(x - i - 1, y)
                self.body_positions[i] = (x, y)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            for i in range(self.car_body_size):
                x, y = self.loop_boundary(x + i + 1, y)
                self.body_positions[i] = (x, y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            for i in range(self.car_body_size):
                x, y = self.loop_boundary(x, y + i + 1)
                self.body_positions[i] = (x, y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            for i in range(self.car_body_size):
                x, y = self.loop_boundary(x, y - i - 1)
                self.body_positions[i] = (x, y)
        else:
            raise ValueError(
                f"Invalid road cell {self.road_type} for the car at {self.head_position}."
            )

        assert len(self.body_positions) == self.car_body_size
        for x, y in self.body_positions:
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

        assert 0 <= x < grid_boundary
        assert 0 <= y < grid_boundary
        return x, y

    def move(self):
        """
        Move the car forward based on its current position and direction.
        """

        def _move_intersection(x: int, y: int, car_type: int = CAR_HEAD) -> tuple:
            """
            Move the car within an intersection based on its current position and direction.

            Params:
            -------
            - x (int): The current x-coordinate of the car.
            - y (int): The current y-coordinate of the car.
            - car_type (int): The type of car to move (CAR_HEAD or CAR_BODY).

            Returns:
            --------
            - tuple: The new x and y coordinates of the car.
            """
            assert car_type in [CAR_HEAD, CAR_BODY], "Invalid car type."

            if self.grid.flag[x, y] == INTERSECTION_EXIT:
                new_pos = self.check_exit_position() or (x, y)
            else:
                new_pos = self.get_next_rotary_position(x, y)
                if new_pos == (None, None):
                    new_pos = (x, y)

            if not (
                isinstance(new_pos, tuple)
                and len(new_pos) == 2
                and all(isinstance(i, int) for i in new_pos)
            ):
                raise ValueError(f"Invalid position {new_pos} for the car.")

            self.grid.grid[new_pos] = car_type
            return new_pos

        def _move_straight(x: int, y: int, car_type: int = CAR_HEAD) -> tuple:
            """
            Move the car in a straight line based on its current position and direction.

            Params:
            -------
            - x (int): The current x-coordinate of the car.
            - y (int): The current y-coordinate of the car.
            - car_type (int): The type of car to move (CAR_HEAD or CAR_BODY).

            Returns:
            --------
            - tuple: The new x and y coordinates of the car.
            """
            if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
                new_pos = (x - 1, y)
            elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
                new_pos = (x + 1, y)
            elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
                new_pos = (x, y + 1)
            elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
                new_pos = (x, y - 1)
            else:
                return (x, y)

            new_pos = self.loop_boundary(*new_pos)

            if self.grid.grid[new_pos] in INTERSECTION_CELLS:
                self.set_road_type(INTERSECTION_INTERNAL)
            elif self.grid.grid[new_pos] not in ROAD_CELLS:
                return (x, y)

            assert car_type in [CAR_HEAD, CAR_BODY]
            self.grid.grid[new_pos] = car_type

            if not isinstance(new_pos, tuple) or len(new_pos) != 2:
                raise ValueError(f"Invalid position {new_pos} for the car.")
            if not all(isinstance(i, int) for i in new_pos):
                raise ValueError(f"Position coordinates {new_pos} must be integers.")
            return new_pos

        def _move_body(_movement_rule):
            """
            Move the car body cells based on the new head position.

            Params:
            -------
            - movement_rule (function): The movement rule to apply to the body cells.
            """
            if self.car_body_size == 0:
                return

            for i in range(self.car_body_size):
                x, y = self.body_positions[i]
                self.body_positions[i] = _movement_rule(x, y, CAR_BODY)

        if self.check_infront():
            pass  # Do nothing if there is a car in front
        elif self.road_type in ROAD_CELLS:
            temp_head = _move_straight(*self.head_position)
            self.head_position = temp_head
        elif self.road_type == INTERSECTION_INTERNAL:
            temp_head = _move_intersection(*self.head_position)
            self.head_position = temp_head
        elif self.road_type == CAR_HEAD:
            print(
                f"Car at {self.head_position} is blocked or spawned on the same cell."
            )
        else:
            raise ValueError(
                f"Invalid road cell {self.road_type} for the car at {self.head_position}."
            )

    def check_infront(self) -> bool:
        """
        Check if there is a car in front of the current car.

        Returns:
        --------
        - bool: True if there is a car in front, False otherwise.
        """
        x, y = self.head_position

        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x - 1, y)
        if self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x + 1, y)
        if self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            x, y = self.loop_boundary(x, y + 1)
        if self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            x, y = self.loop_boundary(x, y - 1)

        blocked = self.grid.grid[x, y] in [CAR_HEAD, CAR_BODY]
        return blocked

    def set_road_type(self, road_type: int):
        """
        Set the road type for the car to move on.
        """
        old_road_type = self.road_type
        if road_type not in ROAD_CELLS and road_type not in INTERSECTION_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type
        assert self.road_type != old_road_type

    def enter_rotary(self):
        x, y = self.head_position
        if (
            self.road_type == VERTICAL_ROAD_VALUE_RIGHT
            and self.grid.grid[x, y + 1] == INTERSECTION_INTERNAL
        ):
            new_pos = self.loop_boundary(x, y + 1)
        elif (
            self.road_type == VERTICAL_ROAD_VALUE_LEFT
            and self.grid.grid[x, y - 1] == INTERSECTION_INTERNAL
        ):
            new_pos = self.loop_boundary(x, y - 1)
        elif (
            self.road_type == HORIZONTAL_ROAD_VALUE_LEFT
            and self.grid.grid[x - 1, y] == INTERSECTION_INTERNAL
        ):
            new_pos = self.loop_boundary(x - 1, y)
        elif (
            self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT
            and self.grid.grid[x + 1, y] == INTERSECTION_INTERNAL
        ):
            new_pos = self.loop_boundary(x + 1, y)
        else:
            return False

        assert isinstance(new_pos, tuple) and len(new_pos) == 2
        assert isinstance(new_pos[0], int) and isinstance(new_pos[1], int)

        # Check if entrance is free
        if (
            isinstance(new_pos, tuple)
            and len(new_pos) == 2
            and all(isinstance(i, int) for i in new_pos)
        ):
            self.grid.grid[self.head_position] = ROAD_CELLS[
                self.road_type
            ]  # Restore road type
            print(f"New position: {new_pos} - Entering rotary.")
            self.head_position = new_pos
            self.grid.grid[self.head_position] = CAR_HEAD
            return True
        return False

    def check_exit_position(self) -> tuple | None:
        x, y = self.head_position
        if (
            self.grid.flag[x - 1, y]
            == INTERSECTION_EXIT & self.grid.flag[x, y - 1]
            == INTERSECTION_EXIT & self.grid.flag[x - 1, y - 1]
            == INTERSECTION_EXIT
        ):
            x, y = self.loop_boundary(x + 1, y)
        elif (
            self.grid.flag[x, y - 1]
            == INTERSECTION_EXIT & self.grid.flag[x - 1, y]
            == INTERSECTION_EXIT & self.grid.flag[x - 1, y - 1]
            == INTERSECTION_EXIT
        ):
            x, y = self.loop_boundary(x, y + 1)
        elif (
            self.grid.flag[x + 1, y]
            == INTERSECTION_EXIT & self.grid.flag[x + 1, y - 1]
            == INTERSECTION_EXIT & self.grid.flag[x, y - 1]
            == INTERSECTION_EXIT
        ):
            x, y = self.loop_boundary(x - 1, y)
        elif (
            self.grid.flag[x, y + 1]
            == INTERSECTION_EXIT & self.grid.flag[x + 1, y + 1]
            == INTERSECTION_EXIT & self.grid.flag[x + 1, y]
            == INTERSECTION_EXIT
        ):
            x, y = self.loop_boundary(x, y - 1)
        else:
            return None

        if self.grid.grid[x, y] not in [CAR_HEAD, CAR_BODY]:
            return x, y
        return None

    def get_next_rotary_position(self, x: int, y: int) -> tuple:
        for ring in self.grid.rotary_dict:
            if (x, y) in ring:
                idx = ring.index((x, y))
                next_idx = (idx + 1) % len(ring)
                next_position = ring[next_idx]

                # Check if next position is occupied by a car
                next_x, next_y = next_position
                if self.grid.grid[next_x, next_y] in [CAR_HEAD, CAR_BODY]:
                    return (None, None)

                return next_position

        return (None, None)  # Position not found in rotary
