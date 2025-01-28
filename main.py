import tkinter as tk

from src.simulation_boilerplate import Simulation_1D, Simulation_2D


def run_2D_simulation():
    root = tk.Tk()
    sim = Simulation_2D(
        root,
        max_iter=100,
        grid_size=15,
        road_length=10,
        road_max_speed=2,
        car_count=4,
        car_percentage_max_speed=50,
    )
    sim.start_simulation()
    grids = sim.get_grid_states()
    for grid in grids:
        print(grid)
        print("--------------------")


def run_1D_simulation():
    root = tk.Tk()
    Simulation_1D(root)


if __name__ == "__main__":
    # run_2D_simulation()
    run_1D_simulation()
