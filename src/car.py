import numpy as np

from src.grid import Grid
from src.utils import (
    CAR_BODY,
    CAR_HEAD,
    EXIT_ROTARY,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_CELLS,
    ROAD_CELLS,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)


class Car:
    def __init__(self, grid: Grid, position: tuple, car_size: int = 1):
        assert isinstance(grid, Grid)
        self.grid = grid

        # Setup movement
        assert len(position) == 2 and all(isinstance(p, int) for p in position)
        road_type = self.grid.grid[position]
        if road_type not in ROAD_CELLS and road_type not in INTERSECTION_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type
        self.grid.grid[position] = CAR_HEAD
        self.on_rotary = True if road_type in INTERSECTION_CELLS else False

        self.head_position = position
        self.flag = EXIT_ROTARY

        # Setup car size
        self.car_body_size = car_size - 1
        if self.car_body_size < 0:
            raise ValueError("Car size must be greater than 0.")
        if self.car_body_size >= 0:
            self.create_larger_car()

    def create_larger_car(self):
        pass

    def get_boundary_pos(self, x: int, y: int) -> tuple:
        """
        Get the boundary position of the grid.
        Return the position on the other side of the grid.

        Parameters:
        -----------
        - x (int): The x position of the car.
        - y (int): The y position of the car.

        Returns:
        --------
        - x (int): The new x position of the car.
        - y (int): The new y position of the car.
        """
        grid_boundary = self.grid.size

        x = x % grid_boundary
        y = y % grid_boundary

        assert 0 <= x < grid_boundary
        assert 0 <= y < grid_boundary
        return x, y

    def return_infront(self, possible_pos: tuple) -> int:
        """
        Return the cell in front of the car.

        Parameters:
        -----------
        - possible_pos (tuple): The possible position of the car.

        Returns:
        --------
        - possible_cell (int): The cell value of the cell in front of the car.
        """
        possible_cell = self.grid.grid[possible_pos]
        assert isinstance(possible_cell, np.int64)
        return possible_cell

    def return_diagonal(self, possible_pos: tuple) -> int:
        """
        Return the diagonal cell of the car.

        Parameters:
        -----------
        - possible_pos (tuple): The possible position of the car.

        Returns:
        --------
        - possible_cell (int): The cell value of the diagonal cell.
        """

        infront_x, infront_y = possible_pos

        # Get the diagonal cell
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(infront_x, infront_y + 1)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(infront_x, infront_y - 1)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(infront_x + 1, infront_y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(infront_x - 1, infront_y)

        possible_cell = self.grid.grid[possible_pos]
        assert isinstance(possible_cell, np.int64)
        return possible_cell

    def move(self):
        """
        Move the car to the next cell controller function.
        """
        # TODO write the other move functions as a subfunction of this

        if self.on_rotary and self.flag == EXIT_ROTARY:
            print("exit_rotary")
            self.exit_rotary()
        elif self.on_rotary:
            print("move_rotary")
            self.move_rotary()
        else:
            print("move_straight")
            self.move_straight()

    def move_straight(self):
        """
        Move the car straight.
        """
        current_x, current_y = self.head_position
        possible_pos = None

        # Move the car to the next cell
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x - 1, current_y)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x + 1, current_y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x, current_y + 1)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x, current_y - 1)

        assert possible_pos is not None
        possible_cell = self.return_infront(possible_pos)
        diagonal_cell = self.return_diagonal(possible_pos)

        # Check if the car is on a road
        if possible_cell not in ROAD_CELLS and possible_cell not in INTERSECTION_CELLS:
            return
        # Check if no car is in front
        if possible_cell in [CAR_HEAD, CAR_BODY]:
            return
        # Check if the car can enter the rotary
        if possible_cell in INTERSECTION_CELLS and diagonal_cell not in [
            CAR_HEAD,
            CAR_BODY,
        ]:
            self.on_rotary = True
        self.set_car_location(possible_pos)

    def move_rotary(self):
        """
        Move the car on the rotary.

        Returns:
        --------
        None if the car cannot move to the next cell.
        """
        current_x, current_y = self.head_position
        possible_pos = None

        # Move the car to the next cell and change the road type to turn
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x - 1, current_y)
            self.set_car_road_type(HORIZONTAL_ROAD_VALUE_LEFT)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x + 1, current_y)
            self.set_car_road_type(HORIZONTAL_ROAD_VALUE_RIGHT)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x, current_y + 1)
            self.set_car_road_type(VERTICAL_ROAD_VALUE_RIGHT)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x, current_y - 1)
            self.set_car_road_type(VERTICAL_ROAD_VALUE_LEFT)

        assert possible_pos is not None
        possible_cell = self.return_infront(possible_pos)

        # Check if the car is on a road
        if possible_cell not in ROAD_CELLS and possible_cell not in INTERSECTION_CELLS:
            return
        # Check if no car is in front
        if possible_cell in [CAR_HEAD, CAR_BODY]:
            return
        # Check if the car can exit the rotary
        # TODO

        self.set_car_location(possible_pos)
        self.flag = EXIT_ROTARY

    def exit_rotary(self):
        current_x, current_y = self.head_position
        possible_pos = None

        # Move the car to the next cell on the right and change the road type to straight
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x, current_y + 1)
            self.set_car_road_type(HORIZONTAL_ROAD_VALUE_RIGHT)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x, current_y - 1)
            self.set_car_road_type(HORIZONTAL_ROAD_VALUE_LEFT)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(current_x + 1, current_y)
            self.set_car_road_type(VERTICAL_ROAD_VALUE_LEFT)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(current_x - 1, current_y)
            self.set_car_road_type(VERTICAL_ROAD_VALUE_RIGHT)

        assert possible_pos is not None
        possible_cell = self.return_infront(possible_pos)

        # Check if the car is on a road
        if possible_cell not in ROAD_CELLS and possible_cell not in INTERSECTION_CELLS:
            return
        # Check if no car is in front
        if possible_cell in [CAR_HEAD, CAR_BODY]:
            return
        # Check if the car can enter the rotary
        if possible_cell not in INTERSECTION_CELLS:
            self.on_rotary = False
        self.set_car_location(possible_pos)

    def set_car_location(self, new_pos: tuple):
        """
        Set the car location to the new position.

        Parameters:
        -----------
        - new_pos (tuple): The new position of the car.
        """
        old_pos = self.head_position

        assert len(new_pos) == 2 and all(isinstance(p, int) for p in new_pos)
        self.head_position = new_pos
        self.grid.grid[new_pos] = CAR_HEAD

        self.grid.grid[old_pos] = self.grid.road_layout[old_pos]

    def set_car_road_type(self, road_type: int):
        """
        Set the road type of the car.

        Parameters:
        -----------
        - road_type (int): The new road type of the car.
        """
        assert isinstance(road_type, int)
        if road_type not in ROAD_CELLS and road_type not in INTERSECTION_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type
