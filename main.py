import tkinter as tk

import powerlaw

# Uncomment the line below to run the giant component experiment
# from src.experiment import run_giant_component_experiment
from src.grid import Grid
from src.simulation import (
    Simulation_1D,
    Simulation_2D_NoUI,
    Simulation_2D_UI,
)
from src.utils import FIXED_DESTINATION, FREE_MOVEMENT


def run_2D_NoUI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_NoUI(
        root,
        max_iter=100,
        rotary_method=FREE_MOVEMENT,
        grid_size=15,
        road_length=10,
        road_max_speed=2,
        car_count=3,
        car_percentage_max_speed=100,
    )
    sim.start_simulation()
    print("Simulation done")
    # grids = sim.get_grid_states()
    # for grid in grids:
    #     print(grid)
    #     print("---------------------------------")


def run_1D_simulation():
    root = tk.Tk()
    Simulation_1D(root)


def run_2D_UI_simulation():
    root = tk.Tk()
    sim = Simulation_2D_UI(root, FIXED_DESTINATION)
    sim.start_simulation()
    root.mainloop()


def run_2D_NoUI_powerlaw():
    num_simulations = 20
    all_cluster_sizes = []
    for _ in range(num_simulations):
        sim = Simulation_2D_NoUI(
            None,
            max_iter=1000,
            rotary_method=FIXED_DESTINATION,
            grid_size=10,
            road_length=8,
            road_max_speed=2,
            car_count=3200,
            car_percentage_max_speed=100,
        )
        cluster_sizes = sim.start_simulation()
        all_cluster_sizes.extend(cluster_sizes)

    print(all_cluster_sizes)
    fit = powerlaw.Fit(all_cluster_sizes, discrete=True)

    print("alpha =", fit.alpha)
    print("xmin =", fit.xmin)

    R, p = fit.distribution_compare("power_law", "exponential")
    print("Log-likelihood ratio R=", R, ", p=", p)
    Grid.plot_powerlaw_fit(all_cluster_sizes, 100, 3200)

    return all_cluster_sizes


if __name__ == "__main__":
    """
    Uncomment the functions below to run the simulation for different scenarios.
    """
    # run_2D_UI_simulation()
    # run_1D_simulation()

    # Uncomment import statement at the top to run the giant component experiment
    # run_giant_component_experiment()

    # run_2D_NoUI_powerlaw()
    run_2D_NoUI_simulation()
    # run_all_experiments()
