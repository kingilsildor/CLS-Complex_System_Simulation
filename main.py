import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider

from src.grid import Grid
from src.simulation import Simulate
from src.car import Car

def main():
    grid = Grid(100, 10)
    car = Car((0, 2), (1, 0))
    grid.add_cars([car])

    sim = Simulate(grid)
    sim.run()

if __name__ == "__main__":
    main()