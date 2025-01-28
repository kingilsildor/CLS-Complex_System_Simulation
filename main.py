import tkinter as tk

from src.simulation_boilerplate import (
    Simulation_1D,
    Simulation_2D_NoUI,
    Simulation_2D_UI,
)


def run_2D_NoUI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_NoUI(
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
        print("---------------------------------")


def run_1D_simulation():
    root = tk.Tk()
    Simulation_1D(root)


def run_2D_UI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_UI(root)
    sim.start_simulation()
    root.mainloop()


if __name__ == "__main__":
    # run_2D_NoUI_simulation()
    # run_2D_UI_simulation()
    run_1D_simulation()
