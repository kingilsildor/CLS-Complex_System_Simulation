import tkinter as tk

import powerlaw

from src.grid import Grid
from src.simulation_boilerplate import (
    Simulation_1D,
    Simulation_2D_NoUI,
    Simulation_2D_UI,
)


def run_2D_NoUI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_NoUI(
        root,
        max_iter=1000,
        grid_size=100,
        road_length=8,
        road_max_speed=2,
        car_count=3200,
        car_percentage_max_speed=100,
    )
    sim.start_simulation()
    # grids = sim.get_grid_states()
    # for grid in grids:
    #     print(grid)
    #     print("---------------------------------")


def run_1D_simulation():
    root = tk.Tk()
    Simulation_1D(root)


def run_2D_UI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_UI(root)
    sim.start_simulation()
    root.mainloop()


def run_2D_NoUI_powerlaw():
    num_simulations = 20
    all_cluster_sizes = []
    for _ in range(num_simulations):
        sim = Simulation_2D_NoUI(
            None,
            max_iter=1000,
            grid_size=100,
            road_length=8,
            road_max_speed=2,
            car_count=3200,
            car_percentage_max_speed=100,
        )
        cluster_sizes = sim.start_simulation()
        all_cluster_sizes.extend(cluster_sizes)

    fit = powerlaw.Fit(all_cluster_sizes, discrete=True)

    print("alpha =", fit.alpha)
    print("xmin =", fit.xmin)

    R, p = fit.distribution_compare("power_law", "exponential")
    print("Log-likelihood ratio R=", R, ", p=", p)
    Grid.plot_powerlaw_fit(all_cluster_sizes, 100, 3200)

    return all_cluster_sizes


if __name__ == "__main__":
    # run_2D_UI_simulation()
    # run_1D_simulation()
    # run_giant_component_experiment()
    # run_2D_NoUI_powerlaw()
    run_2D_NoUI_simulation()
