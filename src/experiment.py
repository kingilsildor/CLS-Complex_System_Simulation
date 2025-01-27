import numpy as np
from tqdm import tqdm
import multiprocessing as mp
from itertools import product

from src.simulation import SimulationUI
from src.grid import Grid
import matplotlib.pyplot as plt
import pandas as pd
import json


def calculate_grid_size(blocks_size):
    """Calculate appropriate grid size for a given block size.
    We want enough blocks for meaningful results, but not too many to keep simulation fast.
    Grid size is scaled more aggressively for very small block sizes.
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


def run_single_simulation(params):
    """Run a single simulation with given parameters."""
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


def save_results(results, block_sizes):
    """Save simulation results to CSV and JSON files."""
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("data/simulation_results.csv", index=False)

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
    with open("data/raw_results.json", "w") as f:
        json.dump(json_results, f, indent=4)

    return formatted_results


def create_analysis_plots(results, block_sizes):
    """Create and save analysis plots."""
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
    plt.yscale("log")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.minorticks_on()
    plt.legend()
    plt.title("Effect of Block Size on Velocity vs Density")

    plt.tight_layout()
    plt.savefig("data/density_analysis.png")
    plt.close()


def run_experiment():
    """Run the complete experiment with different block sizes and densities in parallel."""
    # Configuration
    lane_width = 2
    block_sizes = [32, 64, 128, 256]
    densities = range(5, 100, 5)
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
