import numpy as np
import matplotlib.pyplot as plt

ROAD_VALUE = 0
CAR_VALUE = 3
BLOCKS_VALUE = 1

class Grid:
    def __init__(self, size, blocks, lane_width=2):
        self.grid = np.full((size, size), BLOCKS_VALUE, dtype=int)
        self.size = size
        self.blocks = blocks
        self.lane_width = lane_width if lane_width % 2 == 0 else lane_width + 1
        self.roads()

    def roads(self):
        """
        Add roads to the grid
        """
        for i in range(0, self.size, self.blocks):
            self.grid[max(0, i - self.lane_width + 1):i + 1, :] = ROAD_VALUE
            self.grid[:, max(0, i - self.lane_width + 1):i + 1] = ROAD_VALUE
        
        # Add lanes on the edges
        self.grid[:self.lane_width, :] = ROAD_VALUE
        self.grid[-self.lane_width:, :] = ROAD_VALUE
        self.grid[:, :self.lane_width] = ROAD_VALUE
        self.grid[:, -self.lane_width:] = ROAD_VALUE
    
    def plot(self):
        """
        Plot the grid
        """
        plt.figure(figsize=(6, 6))
        plt.imshow(self.grid, cmap='Greys', extent=[0, self.size, 0, self.size])

        plt.grid(True, which='both', axis='both', color='black', linestyle='-', linewidth=0.5)
        plt.xticks(np.arange(0, self.size, 1), labels=[])
        plt.yticks(np.arange(0, self.size, 1), labels=[])

        plt.show()

    def add_car(self, car):
        """
        Add a car to the grid
        """
        x, y = car
        self.grid[x, y] = CAR_VALUE

grid = Grid(50, 5, lane_width=2)
grid.add_car((0, 0))
grid.plot()