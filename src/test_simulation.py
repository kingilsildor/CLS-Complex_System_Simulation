import numpy as np

from car import Car
from grid import Grid
from utils import (
    CAR_HEAD,
    FREE_MOVEMENT,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_CELLS,
    INTERSECTION_DRIVE,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)

"""
When running the tests, you should change the import statement in the car and grid files from src.utils import {} to utils import {}.
"""


def test_car_initialization():
    """
    Test the initialization of a car on the grid.
    - Verifies that the car's head position is correctly set.
    - Ensures the car is an instance of the Car class.
    - Confirms that the car's body size starts at 0.
    - Checks that the car is not initially on a rotary.
    """
    grid = Grid(grid_size=15, blocks_size=10, rotary_method=FREE_MOVEMENT)
    car = Car(grid, (0, 5))

    assert car.head_position == (
        0,
        5,
    ), "Car head position should be initialized to (0, 5)."
    assert isinstance(car, Car), "Object should be an instance of the Car class."
    assert not car.on_rotary, "Car should not be on a rotary at initialization."


def test_car_infront():
    """
    Test the detection of the cell directly in front of the car.
    - Ensures the correct position in front of the car is calculated based on its road type.
    - Verifies that the cell in front contains the expected value, such as CAR_HEAD.
    """
    grid = Grid(grid_size=15, blocks_size=10, rotary_method=FREE_MOVEMENT)

    car = Car(grid, (1, 5))
    grid.grid[(2, 5)] = CAR_HEAD  # Set another car infront of the initiated car

    x, y = car.head_position

    # Determine the position in front based on the car's road type
    if car.road_type == VERTICAL_ROAD_VALUE_RIGHT:
        possible_pos = car.get_boundary_pos(x - 1, y)
    elif car.road_type == VERTICAL_ROAD_VALUE_LEFT:
        possible_pos = car.get_boundary_pos(x + 1, y)
    elif car.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
        possible_pos = car.get_boundary_pos(x, y + 1)
    elif car.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
        possible_pos = car.get_boundary_pos(x, y - 1)

    assert (
        car.get_infront(possible_pos) == CAR_HEAD
    ), "The position in front of the car should match CAR_HEAD because car2 is located there."


def test_car_dianogal():
    """
    Test the detection of a diagonal cell relative to a car.
    - Ensures the diagonal position is calculated correctly based on the car's road type.
    - Verifies that the diagonal cell contains the expected value.
    """
    grid = Grid(grid_size=15, blocks_size=10, rotary_method=FREE_MOVEMENT)
    car_on_rotary = Car(grid, (5, 6))  # Car already on the rotary
    car_approaching = Car(grid, (4, 5))  # Car approaching the rotary

    print(car_approaching.road_type)
    print(car_on_rotary.road_type)

    infront_x, infront_y = car_approaching.head_position
    if car_approaching.road_type == VERTICAL_ROAD_VALUE_RIGHT:
        possible_pos = car_approaching.get_boundary_pos(infront_x - 1, infront_y)
    elif car_approaching.road_type == VERTICAL_ROAD_VALUE_LEFT:
        possible_pos = car_approaching.get_boundary_pos(infront_x + 1, infront_y)
    elif car_approaching.road_type == HORIZONTAL_ROAD_VALUE_RIGHT:
        possible_pos = car_approaching.get_boundary_pos(infront_x, infront_y + 1)
    elif car_approaching.road_type == HORIZONTAL_ROAD_VALUE_LEFT:
        possible_pos = car_approaching.get_boundary_pos(infront_x, infront_y - 1)

    print(f"Possible position: {possible_pos}")
    print(f" Roadtype of possible position: {grid.grid[possible_pos]}")

    print(f"The diagonal: {car_approaching.get_diagonal(possible_pos)}")
    assert (
        car_approaching.road_type == VERTICAL_ROAD_VALUE_LEFT
    ), "Car should have the expected road type."
    assert (
        car_on_rotary.road_type in INTERSECTION_CELLS
    ), "Car on rotary should have a valid intersection road type."
    assert (
        car_approaching.get_diagonal(possible_pos) == CAR_HEAD
    ), "The diagonal cell should contain CAR_HEAD."


# Constants for test setup
grid_size = 15
block_size = 10
lane_width = 2


def test_grid_initialization():
    """
    Test if the grid initializes correctly with the specified dimensions.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)
    assert grid.grid.shape == (grid_size, grid_size), "Grid size mismatch."


def test_create_vertical_lanes():
    """
    Test if vertical lanes are created correctly.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)
    grid.create_vertical_lanes()
    vertical_lanes = grid.grid[:, block_size // 2 : block_size // 2 + lane_width]
    assert np.any(
        vertical_lanes == VERTICAL_ROAD_VALUE_LEFT
    ), "Vertical left lanes not created."
    assert np.any(
        vertical_lanes == VERTICAL_ROAD_VALUE_RIGHT
    ), "Vertical right lanes not created."


def test_create_horizontal_lanes():
    """
    Test if horizontal lanes are created correctly.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)
    grid.create_horizontal_lanes()
    horizontal_lanes = grid.grid[block_size // 2 : block_size // 2 + lane_width, :]
    assert np.any(
        horizontal_lanes == HORIZONTAL_ROAD_VALUE_LEFT
    ), "Horizontal left lanes not created."
    assert np.any(
        horizontal_lanes == HORIZONTAL_ROAD_VALUE_RIGHT
    ), "Horizontal right lanes not created."


def test_create_intersections():
    """
    Test if intersections are created correctly.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)
    grid.create_intersections()
    intersections = grid.grid[
        block_size // 2 : block_size // 2 + lane_width,
        block_size // 2 : block_size // 2 + lane_width,
    ]
    assert np.all(
        intersections == INTERSECTION_DRIVE
    ), "Intersections not created correctly."


def test_roads_combined():
    """
    Test if all roads are created correctly together.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)
    grid.roads()
    vertical_lanes = grid.grid[:, block_size // 2 : block_size // 2 + 2]
    horizontal_lanes = grid.grid[block_size // 2 : block_size // 2 + 2, :]
    intersections = grid.grid[
        block_size // 2 : block_size // 2 + 2,
        block_size // 2 : block_size // 2 + 2,
    ]

    assert np.any(
        vertical_lanes == VERTICAL_ROAD_VALUE_LEFT
    ), "Vertical left lanes not created in combined roads."
    assert np.any(
        vertical_lanes == VERTICAL_ROAD_VALUE_RIGHT
    ), "Vertical right lanes not created in combined roads."
    assert np.any(
        horizontal_lanes == HORIZONTAL_ROAD_VALUE_LEFT
    ), "Horizontal left lanes not created in combined roads."
    assert np.any(
        horizontal_lanes == HORIZONTAL_ROAD_VALUE_RIGHT
    ), "Horizontal right lanes not created in combined roads."
    assert np.all(
        intersections == INTERSECTION_DRIVE
    ), "Intersections not created correctly in combined roads."


def test_add_cars():
    """
    Test if cars can be added to the grid.
    """
    grid = Grid(grid_size, block_size, rotary_method=FREE_MOVEMENT)

    class MockCar:
        def __init__(self, position):
            self.position = position

        def move(self):
            pass

    car1 = MockCar((3, 3))
    car2 = MockCar((7, 7))

    grid.add_cars([car1, car2])
    assert len(grid.cars) == 2, "Cars not added correctly to the grid."
    assert grid.cars[0].position == (3, 3), "First car position is incorrect."
    assert grid.cars[1].position == (7, 7), "Second car position is incorrect."
