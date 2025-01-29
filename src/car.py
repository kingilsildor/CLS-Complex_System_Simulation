import numpy as np

# from src.grid import Grid
from src.grid import Grid
from src.utils import (
    CAR_HEAD,
    EXIT_ROTARY,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_CELLS,
    MAX_SPEED,
    MIN_SPEED,
    ROAD_CELLS,
    STAY_ON_ROTARY,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)


class Car:
    def __init__(
        self, grid: Grid, position: tuple, free_rotary: True, follow_limit: bool = False
    ):
        assert isinstance(grid, Grid)

        self.grid = grid

        # Setup movement
        assert isinstance(position, tuple)
        assert len(position) == 2 and all(isinstance(p, int) for p in position)
        road_type = self.grid.grid[position]
        if road_type not in ROAD_CELLS and road_type not in INTERSECTION_CELLS:
            raise ValueError(f"Invalid road type {road_type} for the car.")
        self.road_type = road_type
        self.grid.grid[position] = CAR_HEAD
        self.on_rotary = True if road_type in INTERSECTION_CELLS else False

        self.free_rotary = free_rotary

        self.head_position = position
        self.flag = STAY_ON_ROTARY

        # Setup speed
        assert isinstance(follow_limit, bool)
        if follow_limit:
            assert hasattr(self.grid, "max_speed")
            assert isinstance(self.grid.max_speed, int)
            self.max_speed = self.grid.max_speed
        else:
            random_speed = np.random.randint(MIN_SPEED, MAX_SPEED + 1)
            assert MIN_SPEED <= random_speed <= MAX_SPEED
            self.max_speed = random_speed

    def flag_func(self):
        """
        Function to change the car flag

        Returns:
        --------
        - flag (int): The new flag of the car.
        """
        if np.random.uniform() < 0.2:
            return EXIT_ROTARY
        else:
            return STAY_ON_ROTARY

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
        # print(f"get_boundary_pos called with x={x}, y={y}")

        grid_boundary = self.grid.size

        x = x % grid_boundary
        y = y % grid_boundary

        assert 0 <= x < grid_boundary
        assert 0 <= y < grid_boundary
        return x, y

    def get_infront(self, possible_pos: tuple) -> int:
        """
        Return the cell in front of the car.

        Parameters:
        -----------
        - possible_pos (tuple): The possible position of the car.

        Returns:
        --------
        - possible_cell (int): The cell value of the cell in front of the car.
        """
        assert isinstance(possible_pos, tuple) and len(possible_pos) == 2
        possible_cell = self.grid.grid[possible_pos]
        assert isinstance(possible_cell, np.int64)
        return possible_cell

    def get_diagonal(self, possible_pos: tuple) -> int:
        """
        Return the diagonal cell of the car.

        Parameters:
        -----------
        - possible_pos (tuple): The possible position of the car.

        Returns:
        --------
        - possible_cell (int): The cell value of the diagonal cell.
        """
        assert isinstance(possible_pos, tuple) and len(possible_pos) == 2
        infront_x, infront_y = possible_pos

        # Get the diagonal cell
        if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(infront_x, infront_y - 1)
        elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(infront_x, infront_y + 1)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
            possible_pos = self.get_boundary_pos(infront_x - 1, infront_y)
        elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
            possible_pos = self.get_boundary_pos(infront_x + 1, infront_y)

        # print(f"Possible position in return diagonal: {possible_pos}")
        possible_cell = self.grid.grid[possible_pos]
        assert isinstance(possible_cell, np.int64)
        return possible_cell

    def move(self):
        """
        Move the car to the next cell controller function.
        Returns max_speed if moved straight, 1 if moved on rotary, 0 if didn't move.
        """

        def _move_straight():
            """
            Move the car straight forward.
            Returns True if moved, False otherwise.
            """
            current_x, current_y = self.head_position
            new_x, new_y = current_x, current_y
            last_open_space = (current_x, current_y)

            for move in range(self.max_speed):
                if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
                    new_x, new_y = self.get_boundary_pos(current_x - 1, current_y)
                elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
                    new_x, new_y = self.get_boundary_pos(current_x + 1, current_y)
                elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
                    new_x, new_y = self.get_boundary_pos(current_x, current_y + 1)
                elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
                    new_x, new_y = self.get_boundary_pos(current_x, current_y - 1)

                assert isinstance(new_x, int)
                assert isinstance(new_y, int)
                possible_cell = self.get_infront((new_x, new_y))
                diagonal_cell = self.get_diagonal((new_x, new_y))

                if possible_cell == CAR_HEAD:
                    break
                if possible_cell in INTERSECTION_CELLS and diagonal_cell == CAR_HEAD:
                    break

                # Update the position, so the car can move to the last open space if needed
                if possible_cell in ROAD_CELLS:
                    last_open_space = (new_x, new_y)
                current_x, current_y = new_x, new_y

                if possible_cell in INTERSECTION_CELLS:
                    self.set_car_rotary(True)
                    self.set_car_location((current_x, current_y))
                    return True

            assert isinstance(last_open_space, tuple) and len(last_open_space) == 2
            if last_open_space != self.head_position:
                self.set_car_location(last_open_space)
                return True
            return False

        def _move_rotary():
            """
            Move the car on the rotary.
            Returns True if moved, False otherwise.
            """
            current_x, current_y = self.head_position
            possible_pos = None
            possible_road_type = None

            # Move the car to the next cell and change the road type to turn
            if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
                possible_pos = self.get_boundary_pos(current_x - 1, current_y)
                possible_road_type = HORIZONTAL_ROAD_VALUE_LEFT
            elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
                possible_pos = self.get_boundary_pos(current_x + 1, current_y)
                possible_road_type = HORIZONTAL_ROAD_VALUE_RIGHT
            elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
                possible_pos = self.get_boundary_pos(current_x, current_y + 1)
                possible_road_type = VERTICAL_ROAD_VALUE_RIGHT
            elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
                possible_pos = self.get_boundary_pos(current_x, current_y - 1)
                possible_road_type = VERTICAL_ROAD_VALUE_LEFT

            assert possible_pos is not None
            possible_cell = self.get_infront(possible_pos)

            if possible_cell == CAR_HEAD:
                return False
            if possible_cell in ROAD_CELLS or possible_cell in INTERSECTION_CELLS:
                self.set_car_location(possible_pos)
                self.set_car_road_type(possible_road_type)
                return True
            return False

        def _exit_rotary():
            """
            Move the car out of the rotary.
            Returns True if moved, False otherwise.
            """
            current_x, current_y = self.head_position
            possible_pos, road_type = None, None

            # Move the car to the next cell on the right and change the road type to straight
            if self.road_type == VERTICAL_ROAD_VALUE_RIGHT:
                possible_pos = self.get_boundary_pos(current_x, current_y + 1)
                road_type = HORIZONTAL_ROAD_VALUE_RIGHT
            elif self.road_type == VERTICAL_ROAD_VALUE_LEFT:
                possible_pos = self.get_boundary_pos(current_x, current_y - 1)
                road_type = HORIZONTAL_ROAD_VALUE_LEFT
            elif self.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
                possible_pos = self.get_boundary_pos(current_x + 1, current_y)
                road_type = VERTICAL_ROAD_VALUE_LEFT
            elif self.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
                possible_pos = self.get_boundary_pos(current_x - 1, current_y)
                road_type = VERTICAL_ROAD_VALUE_RIGHT

            assert possible_pos is not None
            possible_cell = self.get_infront(possible_pos)

            if (
                possible_cell not in ROAD_CELLS
                and possible_cell not in INTERSECTION_CELLS
            ):
                return False
            if possible_cell == CAR_HEAD:
                return False

            if possible_cell not in INTERSECTION_CELLS:
                self.set_car_rotary(False)

            self.set_car_location(possible_pos)
            self.set_car_road_type(road_type)
            return True

        # Move the car according to the road type and get success status
        success = False
        # if free_rotary == True:

        if self.on_rotary and self.flag == EXIT_ROTARY:
            success = _exit_rotary()
        elif self.on_rotary:
            success = _move_rotary()
        elif not self.on_rotary:
            success = _move_straight()
        else:
            raise ValueError("Invalid car state.")

        # Randomly set the rotary flag
        flag = self.flag_func()
        self.set_car_rotary_flag(flag)

        # Return max_speed if moved straight, 1 if moved on rotary/exit, 0 if didn't move
        if not success:
            return 0
        elif self.on_rotary:
            return 1
        else:
            return self.max_speed

    #######################################################
    # Setters for the car object with error checking,     #
    # so the car object is always in a valid state        #
    #######################################################
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

    def set_car_rotary_flag(self, flag: int):
        """
        Set the rotary flag of the car.

        Parameters:
        -----------
        - flag (int): The new rotary flag of the car.
        """
        assert isinstance(flag, int)
        if flag not in [0, 1]:
            raise ValueError(f"Invalid rotary flag {flag} for the car.")
        self.flag = flag

    def set_car_rotary(self, rotary: bool):
        """
        Set the rotary flag of the car.

        Parameters:
        -----------
        - rotary (bool): The new rotary flag of the car.
        """
        assert isinstance(rotary, bool)
        self.on_rotary = rotary
