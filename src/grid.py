import numpy as np
import matplotlib.pyplot as plt

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
    

    def plot(self):
        """
        Plot the grid
        """
        plt.imshow(self.grid, cmap='gray', interpolation='nearest')
        plt.show()

    def add_car(self, car):
        """
        Add a car to the grid
        """
        x, y = car
        self.grid[x, y] = 3

grid = Grid(25, 5, lane_width=3)
grid.add_car((0, 0))
grid.plot()
