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
from src.simulation_boilerplate import Simulation_2D_NoUI


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
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.minorticks_on()
    plt.legend()
    plt.title("Effect of Block Size on Velocity vs Density")

    plt.tight_layout()
    # timecode the plot
    plt.savefig(f"data/block_size/density_analysis_{time.time()}.png")
    plt.close()


def run_experiment():
    """Run the complete experiment with different block sizes and densities in parallel."""
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


def run_single_speed_simulation(params):
    """Run a single simulation with given parameters for speed testing."""
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


def create_speed_analysis_plots(results, speed_percentages):
    """Create and save analysis plots for speed experiment."""
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


def save_speed_results(results, speed_percentages):
    """Save simulation results to CSV and JSON files."""
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
    """Run experiment testing different speed limit compliance percentages."""
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


def run_giant_component_experiment():
    """Function to calculate and plot the largest connected component size vs. car count."""

    num_simulations = 5
    mean_largest_clusters = []
    confidence_intervals = []
    z_value = 1.96  # For 95% confidence interval
    car_counts = np.arange(100, 3600, 100)

    for c in tqdm(car_counts, desc="Running simulations"):
        largest_cluster_sizes = []

        for _ in range(num_simulations):
            sim = Simulation_2D_NoUI(
                None,
                max_iter=1000,
                grid_size=100,
                road_length=8,
                road_max_speed=2,
                car_count=c,
                car_percentage_max_speed=100,
            )
            sim.start_simulation()
            largest_cluster = sim.largest_component
            if largest_cluster is not None:
                largest_cluster_sizes.append(largest_cluster)
            else:
                largest_cluster_sizes.append(0)

        print(f"Largest cluster size: {largest_cluster_sizes}")
        mean_largest_clusters.append(np.mean(largest_cluster_sizes))

        sem = np.std(largest_cluster_sizes, ddof=1) / np.sqrt(
            num_simulations
        )  # Standard error
        ci_half_width = z_value * sem  # Half-width of the 95% CI
        confidence_intervals.append(ci_half_width)

    lower_bounds = [
        m - ci for m, ci in zip(mean_largest_clusters, confidence_intervals)
    ]
    upper_bounds = [
        m + ci for m, ci in zip(mean_largest_clusters, confidence_intervals)
    ]

    plt.figure()
    plt.plot(
        car_counts, mean_largest_clusters, marker="o", label="Mean Largest Cluster Size"
    )
    plt.fill_between(
        car_counts,
        lower_bounds,
        upper_bounds,
        alpha=0.2,
        label="95% Confidence Interval",
    )
    plt.xlabel("Car Count")
    plt.ylabel("Largest Cluster Size")
    plt.title("Largest Connected Component vs. Car Count (with 95% CI)")
    plt.legend()
    plt.show()
