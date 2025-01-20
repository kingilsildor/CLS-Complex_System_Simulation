from src.utils import ROAD_VALUE

class Car:
    def __init__(self, position, direction, speed=1):
        """
        Initialize a car.
        :param position: (x, y) tuple indicating the position of the car.
        :param direction: A tuple (dx, dy) that represents the movement direction of the car.
        :param speed: The speed at which the car moves.
        """
        self.position = position
        self.direction = direction
        self.speed = speed

    def move(self, grid):
        """
        Move the car on the grid based on its direction and speed.
        """
        new_x = self.position[0] + self.direction[0] * self.speed
        new_y = self.position[1] + self.direction[1] * self.speed

        if new_x < 0:
            new_x = grid.size - 1
        if new_x >= grid.size:
            new_x = 0
        if new_y < 0:
            new_y = grid.size - 1
        if new_y >= grid.size:
            new_y = 0

        try:
            if grid.grid[new_x, new_y] != ROAD_VALUE:
                raise ValueError(f"\033[38;5;214mCar is trying to move off-road.\033[0m")
            self.position = (new_x, new_y)
        except ValueError as e:
            print(e)
            self.direction = (-self.direction[0], -self.direction[1])

    def __str__(self):
        return f"Car at {self.position} moving in direction {self.direction}"