import numpy as np

from src.grid import Grid
from src.utils import (
    CAR_BODY,
    CAR_HEAD,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_CELLS,
    INTERSECTION_DRIVE,
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

        # Setup car size
        self.car_body_size = car_size - 1
        if self.car_body_size < 0:
            raise ValueError("Car size must be greater than 0.")
        if self.car_body_size >= 0:
            self.create_larger_car()

    def create_larger_car(self):
        pass

    def get_boundary_pos(self, x: int, y: int) -> tuple:
        grid_boundary = self.grid.size

        x = x % grid_boundary
        y = y % grid_boundary

        assert 0 <= x < grid_boundary
        assert 0 <= y < grid_boundary
        return x, y

    def return_infront(self, possible_pos: tuple) -> int:
        possible_cell = self.grid.grid[possible_pos]
        assert isinstance(possible_cell, np.int64)
        return possible_cell

    def return_diagonal(self, possible_pos: tuple) -> int:
        infront_x, infront_y = possible_pos

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
        if self.on_rotary:
            self.move_rotary()
        else:
            self.move_straight()

    def move_straight(self):
        current_x, current_y = self.head_position
        possible_pos = None

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
        current_x, current_y = self.head_position
        possible_pos = None

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

        self.set_car_location(possible_pos)

    def set_car_location(self, new_pos: tuple):
        old_pos = self.head_position
        original_old_cell = self.road_type

        assert len(new_pos) == 2 and all(isinstance(p, int) for p in new_pos)
        self.head_position = new_pos
        self.grid.grid[new_pos] = CAR_HEAD

        if any(old_pos in ring for ring in self.grid.rotary_dict):
            self.grid.grid[old_pos] = INTERSECTION_DRIVE
        else:
            self.grid.grid[old_pos] = original_old_cell

    def set_car_road_type(self, road_type: int):
        assert isinstance(road_type, int)
        if road_type not in ROAD_CELLS and road_type not in INTERSECTION_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type
