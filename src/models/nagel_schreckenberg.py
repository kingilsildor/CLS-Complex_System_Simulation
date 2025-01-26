import numpy as np
import random

class NagelSchreckenberg:
    def __init__(self, road_length, num_cars, max_speed, randomization=True):
        self.road_length = road_length
        self.num_cars = num_cars
        self.max_speed = max_speed
        self.randomization = randomization
        self.road = [0] * road_length  # 0 represents empty space, 1 represents a car
        self.speeds = [0] * num_cars  # Initialize speeds of cars
        self.total_speed = 0 # Initialize total speed
        self.flow = 0  # Initialize flow

        # Validate / Assert parameters
        if self.num_cars > self.road_length:
            raise ValueError("Number of cars cannot be greater than the length of the road")
        
        if self.num_cars < 1:
            raise ValueError("Number of cars must be at least 1")

        self.initialize()

    def initialize(self):
        # Initialize the road with cars
        self.road = [0] * self.road_length
        positions = random.sample(range(self.road_length), self.num_cars)
        for pos in positions:
            self.road[pos] = 1

    def update(self):
        new_road = [0] * self.road_length
        new_speeds = [0] * self.num_cars
        car_indices = [i for i, x in enumerate(self.road) if x == 1]
        self.total_speed = 0 # Reset total speed for time step
        self.flow = 0  # Reset flow for this time step


        for i, car_index in enumerate(car_indices):
            speed = self.speeds[i]
            # Step 1: Acceleration
            if speed < self.max_speed:
                speed += 1
            # Step 2: Slowing down due to other cars
            distance = self.distance_to_next_car(car_index)
            if speed >= distance:
                speed = distance - 1
            # Step 3: Randomization
            if self.randomization and speed > 0 and random.random() < 0.3:
                speed -= 1
            # Step 4: Car motion
            new_position = (car_index + speed) % self.road_length
            new_road[new_position] = 1
            new_speeds[i] = speed
            self.total_speed += speed # Add speed to total speed
            self.flow += 1 if speed > 0 else 0  # Increment flow if the car moved

        self.road = new_road
        self.speeds = new_speeds

    def distance_to_next_car(self, index):
        distance = 1
        while distance < self.road_length:
            next_index = (index + distance) % self.road_length
            if self.road[next_index] == 1:
                return distance
            distance += 1
        return distance

    def visualize(self):
        # Return the string representation of the road
        return ''.join(['⬛' if x == 1 else '  ' for x in self.road])
        #return ''.join(['⬛' if x == 1 else '⬜' for x in self.road])
        #return ''.join(['🚗' if x == 1 else '.' for x in self.road])