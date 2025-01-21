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
        self.rotary_dict = []
        self.flag = np.zeros((size, size), dtype=int)
        self.roads()

    def roads(self):
        """
        Add roads to the grid
        """
        # for i in range(0, self.size, self.blocks):
        #     self.grid[max(0, i - self.lane_width + 1):i + 1, :] = 1
        #     self.grid[:, max(0, i - self.lane_width + 1):i + 1] = 1
        
        #Add lanes on the edges
        # self.grid[:self.lane_width, :] = 2
        # self.grid[-self.lane_width:, :] = 2
        # self.grid[:, :self.lane_width] = 2
        # self.grid[:, -self.lane_width:] = 2

        for col in range(0, self.size, self.blocks):
            left = col
            right = min(col + self.lane_width, self.size)
            for x in range(self.size):
                for y in range(left, right):
                    if self.grid[x, y] == 0:
                        self.grid[x, y] = 1
        
        for row in range(0, self.size, self.blocks):
            top = row
            bottom = min(row + self.lane_width, self.size)
            for x in range(top, bottom):
                for y in range(self.size):
                    if self.grid[x, y] == 0:
                        self.grid[x, y] = 2
                    # elif self.grid[x, y] == 1:
                    #     self.grid[x, y] = 4


        for i in range(self.blocks, self.size, self.blocks):
            for j in range(self.blocks, self.size, self.blocks):
                #2x2 rotary at intersection
                x0 = i
                x1 = i + self.lane_width
                y0 = j
                y1 = j + self.lane_width

                self.grid[x0:x1, y0:y1] = 4

                ring = [(x0,y0), (x0,y0+1), (x0+1,y0+1), (x0+1,y0)]
                self.rotary_dict.append(ring)



    def plot(self):
        """
        Plot the grid
        """
        plt.imshow(self.grid, cmap='viridis', interpolation='nearest')
        plt.colorbar(label="Cell Type")
        plt.show()


grid = Grid(25, 5, lane_width=2)

cars = [
    Car(grid, position=(16,3), direction='E'),
    Car(grid, position=(17,6), direction='N')
]


for _ in range(10):
    for car in cars:
        car.move_car()
        grid.plot()

