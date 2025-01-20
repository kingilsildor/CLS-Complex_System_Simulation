from src.grid import Grid
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Simulate():
    def __init__(self, grid: Grid, steps: int = 100, figsize=(6, 6)):
        self.grid = grid
        self.steps = steps
        self.figsize = figsize
    
    def run(self):
        """
        Run the simulation.
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        ani = FuncAnimation(self.fig, self.update_simulation, frames=range(self.steps), interval=500, repeat=False)
        plt.show()

    def update_simulation(self, frame):
        """
        Update the simulation.
        """
        self.grid.update_movement()
        self.ax.clear()
        self.ax.imshow(self.grid.grid, cmap="Greys", interpolation="nearest")
        self.ax.set_title(f"Simulation step {frame}")