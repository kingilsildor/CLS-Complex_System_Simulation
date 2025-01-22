from src.grid import Grid
from src.utils import (
    CAR_VALUE,
    HORIZONTAL_ROAD_VALUE,
    INTERSECTION_VALUE,
    VERTICAL_ROAD_VALUE,
)


class Car:
    """
    Represents a car in the city grid, with a given position and direction.

    The car can move within the grid, enter and exit rotaries, and follow road rules.
    """

    def __init__(self, grid: Grid, position: tuple, direction: str):
        """
        Initialize the car with a given grid, position, and direction.

        Params:
        -------
        - grid: The grid in which the car is located.
        - position (tuple): The starting position of the car on the grid (x, y).
        - direction (str): The direction the car is facing ('N', 'S', 'E', 'W').
        """

        self.grid = grid
        self.in_rotary = False
        self.flag = 0

        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("\033[91mInvalid position for the car.\033[0m")
        if not all(isinstance(i, int) for i in position):
            raise ValueError("\033[91mPosition coordinates must be integers.\033[0m")

        x, y = position
        if self.grid.grid[x, y] not in [
            VERTICAL_ROAD_VALUE,
            HORIZONTAL_ROAD_VALUE,
            INTERSECTION_VALUE,
        ]:
            raise ValueError("\033[91mInvalid starting position for the car.\033[0m")
        else:
            self.grid.grid[x, y] = CAR_VALUE
        self.position = position

        # Check if the direction is valid
        if direction not in ["N", "S", "E", "W"]:
            raise ValueError("\033[91mInvalid direction for the car.\033[0m")
        self.direction = direction

    def can_move_into(self, cell_code: int, check_rotary: bool = True) -> bool:
        """
        Check if the car can move into the specified cell based on its direction.

        Params:
        -------
        - cell_code (int): The code representing the cell the car is trying to move into.
        - check_rotary (bool, optional): Whether to check rotary cells. Defaults to True.

        Returns:
        --------
        - bool: True if the car can move into the cell, False otherwise.
        """
        if self.direction in ["N", "S"]:
            allowed = [VERTICAL_ROAD_VALUE]
            if check_rotary:
                allowed.append(INTERSECTION_VALUE)
        else:
            allowed = [HORIZONTAL_ROAD_VALUE]
            if check_rotary:
                allowed.append(INTERSECTION_VALUE)
        return cell_code in allowed

    def move_car(self) -> None:
        """
        Move the car one step based on its current direction.

        The car will move unless it is inside a rotary. If inside a rotary, it will follow the rotary movement.

        Returns:
        --------
        - None: The car moves to the next cell or stays in
        """
        if not self.in_rotary:
            new_x, new_y = self.next_position(*self.position)
            if new_x is None or new_y is None:
                self.move_boundary(new_x, new_y)
                return

            next_code = self.grid.grid[new_x, new_y]

            if next_code == INTERSECTION_VALUE:
                self.enter_rotary(new_x, new_y)
            elif self.can_move_into(next_code, check_rotary=False):
                self.move_to(new_x, new_y, old_code=self.road_code_for_direction())
        else:
            self.move_rotary()

    def next_position(self, x: int, y: int) -> tuple:
        """
        Get the next position the car will move to based on its direction.

        Params:
        -------
        - x (int): The current x-coordinate of the car.
        - y (int): The current y-coordinate of the car.

        Returns:
        --------
        - tuple: The new position (x, y) or (None, None) if out of bounds.
        """
        next_x, next_y = x, y
        if self.direction == "N":
            next_x = x - 1
        elif self.direction == "S":
            next_x = x + 1
        elif self.direction == "E":
            next_y = y + 1
        elif self.direction == "W":
            next_y = y - 1

        return (next_x, next_y) if self.is_in_bounds(next_x, next_y) else (None, None)

    def enter_rotary(self, new_x: int, new_y: int):
        """
        Enter the rotary if the car reaches an intersection.

        Params:
        -------
        - new_x (int): The x-coordinate of the intersection.
        - new_y (int): The y-coordinate of the intersection.
        """
        x, y = self.position
        if self.grid.grid[new_x, new_y] == INTERSECTION_VALUE:
            self.grid.grid[x, y] = self.road_code_for_direction()
            self.grid.grid[new_x, new_y] = CAR_VALUE
            self.position = (new_x, new_y)
            self.in_rotary = True

    def move_rotary(self) -> None:
        """
        Move the car within the rotary.

        The car moves in a circular path inside the rotary. It will exit if a suitable exit is found.
        If no exit is found, the car will rotate within the rotary.

        Returns:
        --------
        - None: The car moves to the next cell or rotates in the rotary.
        """
        x, y = self.position
        f = self.grid.flag[x, y]

        if f == 0:
            # If not flagged, exit the rotary if possible
            exit_x, exit_y = self.get_exit_position()
            if exit_x is not None and self.can_move_into(
                self.grid.grid[exit_x, exit_y], check_rotary=False
            ):
                self.grid.grid[x, y] = INTERSECTION_VALUE
                self.grid.grid[exit_x, exit_y] = CAR_VALUE
                self.position = (exit_x, exit_y)
                self.in_rotary = False
                return

            # Rotate in the rotary if no exit
            rotate_x, rotate_y = self.rotate_rotary(x, y)

            # Check if next rotary cell is free
            if (
                rotate_x is not None
                and self.grid.grid[rotate_x, rotate_y] == INTERSECTION_VALUE
            ):
                self.grid.grid[x, y] = INTERSECTION_VALUE
                self.grid.grid[rotate_x, rotate_y] = CAR_VALUE
                self.position = (rotate_x, rotate_y)
        else:
            rotate_x, rotate_y = self.rotate_rotary(x, y)
            if (
                rotate_x is not None
                and self.grid.grid[rotate_x, rotate_y] == INTERSECTION_VALUE
            ):
                self.grid.grid[x, y] = INTERSECTION_VALUE
                self.grid.grid[rotate_x, rotate_y] = CAR_VALUE
                self.position = (rotate_x, rotate_y)

    def get_next_rotary_position(self, position: tuple) -> tuple | None:
        """
        Get the next position in the rotary based on the current position.

        Params:
        -------
        - position (tuple): The current position of the car (x, y).

        Returns:
        --------
        - tuple: The next position in the rotary, or None if no valid position.
        - None: If no valid position is found.
        """
        x, y = position
        rotary_pos = [
            (x, y + 1),  # Right
            (x + 1, y),  # Down
            (x, y - 1),  # Left
            (x - 1, y),  # Up
        ]

        for pos in rotary_pos:
            if 0 <= pos[0] < self.grid.size and 0 <= pos[1] < self.grid.size:
                return pos
        return None

    def move_boundary(self, new_x: int, new_y: int) -> tuple:
        """
        Move the car to the opposite side of the grid when it reaches a boundary.
        For vertical movement (N/S), it wraps around vertically.
        For horizontal movement (E/W), it wraps around horizontally.

        Params:
        - new_x (int): The new x-coordinate of the car.
        - new_y (int): The new y-coordinate of the car.

        Returns:
        - tuple: The new position of the car (x, y).
        """
        x, y = self.position
        old_code = self.road_code_for_direction()
        self.grid.grid[x, y] = old_code

        if self.direction == "N":
            # Move to the bottom of the grid
            new_x = self.grid.size - 1
            new_y = y
        elif self.direction == "S":
            # Move to the top of the grid
            new_x = 0
            new_y = y
        elif self.direction == "E":
            # Move to the left of the grid
            new_x = x
            new_y = 0
        elif self.direction == "W":
            # Move to the right of the grid
            new_x = x
            new_y = self.grid.size - 1

        if self.can_move_into(self.grid.grid[new_x, new_y], check_rotary=False):
            self.grid.grid[new_x, new_y] = CAR_VALUE
            self.position = (new_x, new_y)
        else:
            # If can't wrap around, just remove the car
            self.grid.cars.remove(self)

    def right_of_way(self):
        """
        Check if the car has the right of way at an intersection or rotary.
        """
        pass  # TODO

    def road_rules(self):
        """
        Check the road rules for the car to follow at the current position.
        """
        pass  # TODO

    def move_to(self, new_x: int, new_y: int, old_code: int):
        """
        Move the car to a new position on the grid.

        Params:
        -------
        - new_x (int): The new x-coordinate of the car.
        - new_y (int): The new y-coordinate of the car.
        - old_code (int): The code of the previous road the car was on.
        """
        x, y = self.position
        self.grid.grid[x, y] = old_code
        self.grid.grid[new_x, new_y] = CAR_VALUE
        self.position = (new_x, new_y)

    def road_code_for_direction(self) -> int:
        """
        Get the road code based on the car's direction.

        Returns:
        --------
        - int: The road code for the direction (1 for vertical, 2 for horizontal).
        """
        if self.direction in ["N", "S"]:
            return VERTICAL_ROAD_VALUE
        else:
            return HORIZONTAL_ROAD_VALUE

    def get_exit_position(self) -> tuple:
        """
        Get the next position the car will move to when exiting the rotary.

        Returns:
        --------
        - tuple: The exit position (x, y).
        """
        return self.next_position(*self.position)

    def rotate_rotary(self, x: int, y: int) -> tuple:
        """
        Get the next position in the rotary for the car to rotate to.

        Params:
        -------
        - x (int): The current x-coordinate of the car.
        - y (int): The current y-coordinate of the car.

        Returns:
        --------
        - tuple: The next position in the rotary, or (None, None) if no valid position.
        """
        for ring in self.grid.rotary_dict:
            if (x, y) in ring:
                idx = ring.index((x, y))
                next_idx = (idx + 1) % len(ring)
                return ring[next_idx]

        return (None, None)

    def is_in_bounds(self, x: int, y: int) -> bool:
        """
        Check if a position is within the bounds of the grid.

        Params:
        -------
        - x (int): The x-coordinate of the position.
        - y (int): The y-coordinate of the position.

        Returns:
        --------
        - bool: True if the position is within the bounds, False otherwise.
        """
        return 0 <= x < self.grid.size and 0 <= y < self.grid.size
