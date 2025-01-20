import numpy as np
import matplotlib.pyplot as plt
from car import Car

class Grid:
    def __init__(self, size, blocks, lane_width=2):
        self.size = size
        self.blocks = blocks
        self.lane_width = lane_width if lane_width % 2 == 0 else lane_width + 1
        print(self.lane_width)
        self.grid = np.zeros((size, size))
        self.roads()

    def roads(self):
        """
        Add roads to the grid
        """
        for i in range(0, self.size, self.blocks):
            self.grid[max(0, i - self.lane_width + 1):i + 1, :] = 1
            self.grid[:, max(0, i - self.lane_width + 1):i + 1] = 1
        
        # Add lanes on the edges
        self.grid[:self.lane_width, :] = 1
        self.grid[-self.lane_width:, :] = 1
        self.grid[:, :self.lane_width] = 1
        self.grid[:, -self.lane_width:] = 1

        
        # for i in range(self.blocks, self.size, self.blocks):
        #     for j in range(self.blocks, self.size, self.blocks):
        #         #2x2 rotary at intersection
        #         x0 = max(0, i - 1)
        #         y0 = max(0, j - 1)
        #         x1 = min(self.size, i + 1)  # slicing end index is exclusive
        #         y1 = min(self.size, j + 1)
        #         # This creates a 2x2 block in [x0:x1, y0:y1]
        #         self.grid[x0:x1, y0:y1] = 2

    def plot(self):
        """
        Plot the grid
        """
        plt.imshow(self.grid, cmap='viridis', interpolation='nearest')
        plt.colorbar(label="Cell Type")
        plt.show()

    def add_car(self, car):
        """
        Add a car to the grid
        """
        x, y = car
        self.grid[x, y] = 3

grid = Grid(25, 5, lane_width=2)
grid.plot()
cars = [
    Car(grid, position=(0,0), direction='E'),
    Car(grid, position=(0,10), direction='S'),
    Car(grid, position=(10,0), direction='N')
]


for _ in range(10):
    for car in cars:
        car.move_car()
        grid.plot()
