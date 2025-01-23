import numpy as np
import random

class NagelSchreckenberg:
    def __init__(self, road_length, num_cars, max_speed):
        self.road_length = road_length
        self.num_cars = num_cars
        self.max_speed = max_speed
        self.road = [0] * road_length  # 0 represents empty space, 1 represents a car

        # Validate parameters
        if self.num_cars > self.road_length:
            raise ValueError("Number of cars cannot be greater than the length of the road")

        self.initialize()

    def initialize(self):
        # Initialize the road with cars
        self.road = [0] * self.road_length
        positions = random.sample(range(self.road_length), self.num_cars)
        for pos in positions:
            self.road[pos] = 1

    def update(self):
        new_road = [0] * self.road_length
        for i in range(self.road_length):
            if self.road[i] == 1:  # If there is a car
                speed = min(self.max_speed, self.distance_to_next_car(i))
                new_position = (i + speed) % self.road_length
                new_road[new_position] = 1
        self.road = new_road

    def distance_to_next_car(self, index):
        distance = 0
        for i in range(1, self.road_length):
            next_index = (index + i) % self.road_length
            if self.road[next_index] == 1:
                return distance
            distance += 1
        return distance

    def visualize(self):
        # Return the string representation of the road
        return ''.join(['🚗' if x == 1 else '.' for x in self.road])