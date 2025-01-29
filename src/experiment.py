import json
import multiprocessing as mp
import time
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from src.density import DensityTracker
from src.grid import Grid
from src.simulation import SimulationUI


def calculate_grid_size(blocks_size) -> int:
    """
    Calculate appropriate grid size for a given block size.
    We want enough blocks for meaningful results, but not too many to keep simulation fast.
    Grid size is scaled more aggressively for very small block sizes.

    Params:
    -------
    - blocks_size (int): Size of blocks in the grid.

    Returns:
    --------
    - grid_size (int): Size of the grid based on the block size
    """
    if blocks_size <= 8:
        # For very small blocks, use fewer blocks to keep grid size reasonable
        n_blocks = 8
    elif blocks_size <= 32:
        # For small-medium blocks, use moderate number of blocks
        n_blocks = 12
    else:
        # For large blocks, use fewer blocks
        n_blocks = 8

    # Calculate grid size based on number of blocks
    grid_size = blocks_size * n_blocks
    return grid_size


def run_single_simulation(params) -> dict:
    """
    Run a single simulation with given parameters.

    Params:
    -------
    - params (tuple): Tuple of simulation parameters (blocks_size, density_percentage, steps, lane_width).

    Returns:
    --------
    - results (dict): Dictionary of simulation results.
    """
    blocks_size, density_percentage, steps, lane_width = params

    # Initialize simulation
    ui = SimulationUI(None, show_ui=False, colour_blind=False)
    grid_size = calculate_grid_size(blocks_size)

    # Calculate car count
    temp_grid = Grid(grid_size, blocks_size, lane_width)
    total_cells = temp_grid.road_cells + temp_grid.intersection_cells
    density = density_percentage / 100.0
    car_count = int(total_cells * density)

    # Run simulation
    ui.run_simulation_without_ui(
        steps=steps,
        grid_size=grid_size,
        blocks_size=blocks_size,
        lane_width=lane_width,
        car_count=car_count,
        output=False,
    )

    # Calculate metrics
    avg_velocity = np.mean(
        [m["average_velocity"] for m in ui.density_tracker.metrics_history]
    )

    return {"blocks_size": blocks_size, "density": density, "velocity": avg_velocity}


def save_results(results: list, block_sizes: list) -> dict:
    """
    Save simulation results to CSV and JSON files.

    Params:
    -------
    - results (list): List of simulation results.
    - block_sizes (list): List of block sizes used in the experiment.

    Returns:
    --------
    - formatted_results (dict): Dictionary of formatted simulation results.
    """
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("data/block_size/simulation_results.csv", index=False)

    # Convert results to the format expected by create_analysis_plots
    formatted_results = {
        block_size: {"densities": [], "velocities": []} for block_size in block_sizes
    }

    for result in results:
        block_size = result["blocks_size"]
        formatted_results[block_size]["densities"].append(result["density"])
        formatted_results[block_size]["velocities"].append(result["velocity"])

    # Save raw results to JSON
    json_results = {
        str(k): {
            "densities": [float(x) for x in v["densities"]],
            "velocities": [float(x) for x in v["velocities"]],
        }
        for k, v in formatted_results.items()
    }
    with open("data/block_size/raw_results.json", "w") as f:
        json.dump(json_results, f, indent=4)

    return formatted_results


def create_analysis_plots(results: dict, block_sizes: list):
    """
    Create and save analysis plots.

    Params:
    -------
    - results (dict): Dictionary of formatted simulation results.
    - block_sizes (list): List of block sizes used in the experiment.
    """
    plt.figure(figsize=(8, 6))

    # Velocity vs Density plot
    for blocks_size in block_sizes:
        plt.plot(
            np.array(results[blocks_size]["densities"]) * 100,
            results[blocks_size]["velocities"],
            "o-",
            label=f"Block Size {blocks_size}",
        )
    plt.xlabel("Global Density (%)")
    plt.ylabel("Average Velocity")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.minorticks_on()
    plt.legend()
    plt.title("Effect of Block Size on Velocity vs Density")

    plt.tight_layout()
    # timecode the plot
    plt.savefig(f"data/block_size/density_analysis_{time.time()}.png")
    plt.close()


def run_experiment():
    """
    Run the complete experiment with different block sizes and densities in parallel.
    """
    # Configuration
    lane_width = 2
    block_sizes = [32, 64, 128, 256]
    densities = range(5, 95, 1)
    steps = 100

    # Create parameter combinations for parallel processing
    params = list(product(block_sizes, densities, [steps], [lane_width]))
    total_simulations = len(params)

    print(f"Running {total_simulations} simulations in parallel...")
    n_processes = max(1, mp.cpu_count() - 1)
    print(f"Using {n_processes} CPU cores")

    # Run simulations in parallel with progress bar
    with mp.Pool(n_processes) as pool:
        results = list(
            tqdm(
                pool.imap(run_single_simulation, params),
                total=total_simulations,
                desc="Running simulations",
            )
        )

    # Save results and create plots
    formatted_results = save_results(results, block_sizes)
    create_analysis_plots(formatted_results, block_sizes)


def run_single_speed_simulation(params) -> dict:
    """
    Run a single simulation with given parameters for speed testing.

    Params:
    -------
    - params (tuple): Tuple of simulation parameters (density_percentage, car_speed_percentage, steps, blocks_size, lane_width).

    Returns:
    --------
    - speed_percentage (float): Percentage of cars following speed limit.
    - density (float): Density of the traffic.
    - velocity (float): Average velocity of cars in the simulation.
    """
    density_percentage, car_speed_percentage, steps, blocks_size, lane_width = params

    # Initialize simulation
    ui = SimulationUI(None, show_ui=False, colour_blind=False)
    grid_size = calculate_grid_size(blocks_size)

    # Calculate car count
    temp_grid = Grid(grid_size, blocks_size, lane_width)
    total_cells = temp_grid.road_cells + temp_grid.intersection_cells
    density = density_percentage / 100.0
    car_count = int(total_cells * density)

    # Initialize grid and density tracker
    ui.grid = Grid(grid_size, blocks_size, lane_width)
    ui.density_tracker = DensityTracker(ui.grid)

    # Create cars with specified speed percentage
    cars = ui.create_cars(car_count, car_speed_percentage=car_speed_percentage)
    ui.grid.add_cars(cars)

    # Run simulation steps
    for _ in range(steps):
        moved_cars = ui.grid.update_movement()
        ui.density_tracker.update(moved_cars)

    # Calculate metrics
    avg_velocity = np.mean(
        [m["average_velocity"] for m in ui.density_tracker.metrics_history]
    )

    return {
        "speed_percentage": car_speed_percentage,
        "density": density,
        "velocity": avg_velocity,
    }


def create_speed_analysis_plots(results: dict, speed_percentages: list):
    """
    Create and save analysis plots for speed experiment.

    Params:
    -------
    - results (dict): Dictionary of formatted simulation results.
    - speed_percentages (list): List of speed percentages used in the experiment.
    """
    plt.figure(figsize=(8, 6))

    # Sort speed percentages for better visualization
    speed_percentages = sorted(speed_percentages)

    # Velocity vs Density plot
    for speed in speed_percentages:
        plt.plot(
            np.array(results[speed]["densities"]) * 100,
            results[speed]["velocities"],
            "o-",
            label=f"{speed}% Speed Compliance",
        )
    plt.xlabel("Global Density (%)")
    plt.ylabel("Average Velocity")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.minorticks_on()
    plt.legend()
    plt.title("Effect of Speed Limit Compliance on Velocity vs Density")

    plt.tight_layout()
    plt.savefig(f"data/speed/density_analysis_{time.time()}.png")
    plt.close()


def save_speed_results(results: list, speed_percentages: list):
    """
    Save simulation results to CSV and JSON files.

    Params:
    -------
    - results (list): List of simulation results.
    - speed_percentages (list): List of speed percentages used in the experiment.
    """
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("data/speed/speed_simulation_results.csv", index=False)

    # Convert results to the format expected by create_analysis_plots
    formatted_results = {
        speed: {"densities": [], "velocities": []} for speed in speed_percentages
    }

    for result in results:
        speed = result["speed_percentage"]
        formatted_results[speed]["densities"].append(result["density"])
        formatted_results[speed]["velocities"].append(result["velocity"])

    # Save raw results to JSON
    json_results = {
        str(k): {
            "densities": [float(x) for x in v["densities"]],
            "velocities": [float(x) for x in v["velocities"]],
        }
        for k, v in formatted_results.items()
    }
    with open("data/speed/speed_raw_results.json", "w") as f:
        json.dump(json_results, f, indent=4)

    return formatted_results


def run_speed_experiment():
    """
    Run experiment testing different speed limit compliance percentages.
    """
    # Configuration
    blocks_size = 64  # Fixed block size
    lane_width = 2
    speed_percentages = [
        0,
        25,
        50,
        75,
        100,
    ]  # Different percentages of cars following speed limit
    densities = range(10, 95, 5)  # Test densities from 5% to 50%
    steps = 250

    # Create parameter combinations for parallel processing
    params = list(
        product(densities, speed_percentages, [steps], [blocks_size], [lane_width])
    )
    total_simulations = len(params)

    print(f"Running {total_simulations} simulations in parallel...")
    n_processes = max(1, mp.cpu_count() - 1)
    print(f"Using {n_processes} CPU cores")

    # Run simulations in parallel with progress bar
    with mp.Pool(n_processes) as pool:
        results = list(
            tqdm(
                pool.imap(run_single_speed_simulation, params),
                total=total_simulations,
                desc="Running simulations",
            )
        )

    # Save results and create plots
    formatted_results = save_speed_results(results, speed_percentages)
    create_speed_analysis_plots(formatted_results, speed_percentages)
