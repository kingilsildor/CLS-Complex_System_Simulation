from src.utils import HORIZONTAL_ROAD_VALUE, INTERSECTION_VALUE, VERTICAL_ROAD_VALUE


class Car:
    def __init__(self, position, direction, speed=1):
        self.position = position
        self.direction = direction
        self.speed = speed

    def move(self, grid):
        """Move the car on the grid"""
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
            if grid.grid[new_x, new_y] not in [
                VERTICAL_ROAD_VALUE,
                HORIZONTAL_ROAD_VALUE,
                INTERSECTION_VALUE,
            ]:
                raise ValueError("\033[38;5;214mCar is trying to move off-road.\033[0m")
            self.position = (new_x, new_y)
        except ValueError:
            self.direction = (-self.direction[0], -self.direction[1])
