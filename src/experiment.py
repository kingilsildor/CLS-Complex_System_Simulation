import json
import multiprocessing as mp
import os
import time
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm
from scipy import stats

from src.density import DensityTracker
from src.grid import Grid
from src.simulation import Simulation_2D_NoUI
from src.utils import FIXED_DESTINATION, FREE_MOVEMENT


def get_experiment_config():
    """
    Central configuration for all experiments.
    Modify this function to control which experiments to run and their parameters.
    """
    config = {
        # Global parameters
        "n_simulations": 5,  # Number of simulations per parameter combination
        "steps": 200,  # Steps per simulation
        "lane_width": 2,
        "warmup_fraction": 0.2,  # Fraction of steps to use as warmup
        "log_scale": True,  # Whether to create log-log plots in addition to normal plots
        "rotary_method": FIXED_DESTINATION,  # FREE_MOVEMENT or FIXED_DESTINATION
        "density_start": 5,  # Starting density percentage
        "density_end": 95,  # Ending density percentage
        "density_step": 5,  # Step size for density
        # Which experiments to run
        "run_road_length": True,
        "run_speed_compliance": False,
        "run_max_speed": False,
        # Road length experiment parameters
        "road_length": {
            "road_lengths": [32, 64, 128],
        },
        # Speed compliance experiment parameters
        "speed_compliance": {
            "road_length": 64,
            "speed_percentages": [50, 75, 100],
        },
        # Maximum speed experiment parameters
        "max_speed": {
            "road_length": 64,
            "max_speeds": [1, 3, 5],  # More distinct speed values
        },
    }

    # Add density range to all experiment configurations
    densities = range(
        config["density_start"], config["density_end"], config["density_step"]
    )
    config["road_length"]["densities"] = densities
    config["speed_compliance"]["densities"] = densities
    config["max_speed"]["densities"] = densities

    return config


def run_all_experiments():
    """Run all configured experiments."""
    config = get_experiment_config()

    if config["run_road_length"]:
        print("\n=== Running Road Length Experiment ===")
        run_experiment(
            n_simulations=config["n_simulations"],
            steps=config["steps"],
            warmup_fraction=config["warmup_fraction"],
            lane_width=config["lane_width"],
            log_scale=config["log_scale"],
            rotary_method=config["rotary_method"],
            **config["road_length"],
        )

    if config["run_speed_compliance"]:
        print("\n=== Running Speed Compliance Experiment ===")
        run_speed_experiment(
            n_simulations=config["n_simulations"],
            steps=config["steps"],
            warmup_fraction=config["warmup_fraction"],
            lane_width=config["lane_width"],
            log_scale=config["log_scale"],
            rotary_method=config["rotary_method"],
            **config["speed_compliance"],
        )

    if config["run_max_speed"]:
        print("\n=== Running Maximum Speed Experiment ===")
        run_maxspeed_experiment(
            n_simulations=config["n_simulations"],
            steps=config["steps"],
            warmup_fraction=config["warmup_fraction"],
            lane_width=config["lane_width"],
            log_scale=config["log_scale"],
            rotary_method=config["rotary_method"],
            **config["max_speed"],
        )


def calculate_grid_size(road_length):
    """Calculate appropriate grid size for a given road length.
    We want enough roads for meaningful results, but not too many to keep simulation fast.
    Grid size is scaled more aggressively for very small road lengths.
    """
    if road_length <= 8:
        # For very small roads, use fewer roads to keep grid size reasonable
        n_roads = 8
    elif road_length <= 32:
        # For small-medium roads, use moderate number of roads
        n_roads = 12
    else:
        # For large roads, use fewer roads
        n_roads = 8

    # Calculate grid size based on number of roads
    grid_size = road_length * n_roads
    return grid_size


def run_single_simulation_generic(params, experiment_type="road_length"):
    """Generic simulation runner for all experiment types."""
    if experiment_type == "road_length":
        road_length, density_percentage, steps, lane_width, rotary_method, sim_index = (
            params
        )
        max_speed = 2
        speed_percentage = 100
    elif experiment_type == "speed_compliance":
        (
            density_percentage,
            speed_percentage,
            steps,
            road_length,
            lane_width,
            rotary_method,
            sim_index,
        ) = params
        max_speed = 5  # Fixed max speed for speed compliance experiment
    elif experiment_type == "max_speed":
        max_speed, density_percentage, steps, road_length, rotary_method, sim_index = (
            params
        )
        speed_percentage = (
            100  # In max speed experiment, all cars should follow their speed limit
        )
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Initialize simulation
    grid_size = calculate_grid_size(road_length)

    # Calculate car count
    temp_grid = Grid(grid_size, road_length, max_speed)
    total_cells = temp_grid.road_cells + temp_grid.intersection_cells
    density = density_percentage / 100.0
    car_count = int(total_cells * density)

    # Run simulation
    ui = Simulation_2D_NoUI(
        root=None,
        max_iter=steps,
        rotary_method=rotary_method,  # Pass the rotary method
        grid_size=grid_size,
        road_length=road_length,
        road_max_speed=max_speed,
        car_count=car_count,
        car_percentage_max_speed=speed_percentage,
        seed=42 + sim_index,
    )

    # Create density tracker and collect metrics
    density_tracker = DensityTracker(ui.grid)
    metrics_history = []

    # Create cars and add them to the grid
    cars = ui.create_cars(ui.grid, car_count, speed_percentage)
    ui.grid.add_cars(cars)

    # Run simulation and collect metrics
    warmup_steps = int(steps * 0.2)  # Use 20% of steps as warmup
    for step in range(steps):
        moved_cars = ui.grid.update_movement()
        metrics = density_tracker.update(moved_cars)
        if step >= warmup_steps:  # Only collect metrics after warmup
            metrics_history.append(metrics)

    # Calculate average velocity over steady-state timesteps
    avg_velocity = np.mean([m["average_velocity"] for m in metrics_history])

    # Return results based on experiment type
    result = {"density": density, "velocity": avg_velocity, "sim_index": sim_index}

    if experiment_type == "road_length":
        result["road_length"] = road_length
    elif experiment_type == "speed_compliance":
        result["speed_percentage"] = speed_percentage
    elif experiment_type == "max_speed":
        result["max_speed"] = max_speed

    return result


def aggregate_results(raw_results, experiment_type="road_length"):
    """
    Aggregate results from multiple simulations for each parameter combination.
    Performs statistical analysis including normality tests and confidence intervals.
    """
    # Determine the variable name based on experiment type
    if experiment_type == "road_length":
        var_name = "road_length"
    elif experiment_type == "speed_compliance":
        var_name = "speed_percentage"
    elif experiment_type == "max_speed":
        var_name = "max_speed"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Group results by variable value and density
    grouped_results = {}
    for result in raw_results:
        key = (result[var_name], result["density"])
        if key not in grouped_results:
            grouped_results[key] = []
        grouped_results[key].append(result["velocity"])

    # Calculate statistics for each group
    aggregated_results = []
    for (var_value, density), velocities in grouped_results.items():
        velocities = np.array(velocities)
        n = len(velocities)

        # Basic statistics
        mean_velocity = np.mean(velocities)
        std_velocity = np.std(velocities, ddof=1) if n > 1 else 0

        # Statistical tests and confidence intervals
        if n < 2:
            # Not enough samples for statistical analysis
            ci_lower = mean_velocity
            ci_upper = mean_velocity
            normality_test_p = None
            std_error = 0
        else:
            # Standard error of the mean
            std_error = std_velocity / np.sqrt(n)

            # Normality test (if enough samples)
            if n >= 3:
                _, normality_test_p = stats.shapiro(velocities)
                if normality_test_p < 0.05:
                    print(
                        f"Warning: Non-normal distribution detected for {var_name}={var_value}, "
                        f"density={density:.2f} (p={normality_test_p:.4f})"
                    )
            else:
                normality_test_p = None

            # Confidence intervals
            if std_error == 0:
                # All values are identical
                ci_lower = mean_velocity
                ci_upper = mean_velocity
            else:
                # Use t-distribution for small sample sizes
                t_value = stats.t.ppf(0.975, df=n - 1)  # 95% CI
                margin_of_error = t_value * std_error
                ci_lower = mean_velocity - margin_of_error
                ci_upper = mean_velocity + margin_of_error

        # Store results with all statistical information
        result_dict = {
            var_name: var_value,
            "density": density,
            "velocity": mean_velocity,
            "std": std_velocity,
            "std_error": std_error,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n_samples": n,
        }
        if normality_test_p is not None:
            result_dict["normality_p_value"] = normality_test_p

        aggregated_results.append(result_dict)

    return aggregated_results


def save_results_generic(results, variable_values, experiment_type="road_length"):
    """Generic function to save results for all experiment types."""
    # Get timestamp in ddmmhhmm format
    timestamp = time.strftime("%d%m%H%M")

    # Determine file paths based on experiment type
    if experiment_type == "road_length":
        base_path = "data/road_length"
        csv_file = f"simulation_results_{timestamp}.csv"
        var_name = "road_length"
    elif experiment_type == "speed_compliance":
        base_path = "data/speed_compliance"
        csv_file = f"speed_simulation_results_{timestamp}.csv"
        var_name = "speed_percentage"
    elif experiment_type == "max_speed":
        base_path = "data/max_speed"
        csv_file = f"maxspeed_simulation_results_{timestamp}.csv"
        var_name = "max_speed"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Create directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{base_path}/{csv_file}", index=False)

    # Convert results to the format expected by create_analysis_plots
    formatted_results = {
        val: {
            "densities": [],
            "velocities": [],
            "ci_lower": [],
            "ci_upper": [],
            "std_error": [],
        }
        for val in variable_values
    }

    for result in results:
        val = result[var_name]
        formatted_results[val]["densities"].append(result["density"])
        formatted_results[val]["velocities"].append(result["velocity"])
        formatted_results[val]["ci_lower"].append(result["ci_lower"])
        formatted_results[val]["ci_upper"].append(result["ci_upper"])
        formatted_results[val]["std_error"].append(result["std_error"])

    # Save raw results to JSON with timestamp
    json_results = {
        str(k): {
            "densities": [float(x) for x in v["densities"]],
            "velocities": [float(x) for x in v["velocities"]],
            "ci_lower": [float(x) for x in v["ci_lower"]],
            "ci_upper": [float(x) for x in v["ci_upper"]],
            "std_error": [float(x) for x in v["std_error"]],
        }
        for k, v in formatted_results.items()
    }

    # Add metadata to JSON
    json_results["metadata"] = {
        "timestamp": timestamp,
        "experiment_type": experiment_type,
        "n_variables": len(variable_values),
        "variable_values": list(variable_values),
        "statistical_info": {
            "confidence_level": 0.95,
            "ci_method": "t-distribution",
            "normality_test": "Shapiro-Wilk",
            "normality_alpha": 0.05,
        },
    }

    with open(f"{base_path}/results_{timestamp}.json", "w") as f:
        json.dump(json_results, f, indent=4)

    return formatted_results


def create_analysis_plots_generic(
    results,
    variable_values,
    experiment_type="road_length",
    log_scale=False,
    rotary_method=FREE_MOVEMENT,
):
    """
    Generic function to create analysis plots for all experiment types.

    Parameters:
    -----------
    results : dict
        The results to plot
    variable_values : list
        The values of the variable being tested
    experiment_type : str
        The type of experiment (road_length, speed_compliance, or max_speed)
    log_scale : bool
        Whether to create an additional plot with log-log axes
    rotary_method : int
        The rotary method used (FREE_MOVEMENT or FIXED_DESTINATION)
    """
    # Get timestamp in ddmmhhmm format
    timestamp = time.strftime("%d%m%H%M")

    # Set up plot parameters based on experiment type
    if experiment_type == "road_length":
        base_path = "data/road_length"
        label_prefix = "Road Length"
        title = "Effect of Road Length on Speed vs Density"
    elif experiment_type == "speed_compliance":
        base_path = "data/speed_compliance"
        label_prefix = "Speed Compliance"
        title = "Effect of Speed Limit Compliance on Speed vs Density"
    elif experiment_type == "max_speed":
        base_path = "data/max_speed"
        label_prefix = "Max Speed"
        title = "Effect of Maximum Speed Limit on Speed vs Density"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Create rotary method label
    rotary_label = (
        "Free Movement" if rotary_method == FREE_MOVEMENT else "Fixed Destination"
    )

    # Create directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)

    # Create both normal and log-scale plots
    plot_types = ["normal"]
    if log_scale:
        plot_types.append("log")

    for plot_type in plot_types:
        plt.figure(figsize=(10, 7))

        # Velocity vs Density plot with confidence intervals
        colors = plt.cm.tab10(np.linspace(0, 1, len(variable_values)))
        for val, color in zip(variable_values, colors):
            densities = np.array(results[val]["densities"]) * 100
            velocities = np.array(results[val]["velocities"])
            ci_lower = np.array(results[val]["ci_lower"])
            ci_upper = np.array(results[val]["ci_upper"])

            # Plot mean line with points
            plt.plot(
                densities, velocities, "o-", color=color, label=f"{label_prefix} {val}"
            )

            # Add confidence interval shading
            plt.fill_between(densities, ci_lower, ci_upper, color=color, alpha=0.2)

        plt.xlabel("Global Density (%)")
        plt.ylabel("Average Speed")
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.minorticks_on()

        if plot_type == "log":
            plt.xscale("log")
            plt.yscale("log")
            plot_title = f"{title}\n(Log-Log Scale, with 95% Confidence Intervals, after 20% warmup)\nRotary Method: {rotary_label}"
            filename = f"{base_path}/density_analysis_loglog_{timestamp}.png"
        else:
            plot_title = f"{title}\n(with 95% Confidence Intervals, after 20% warmup)\nRotary Method: {rotary_label}"
            filename = f"{base_path}/density_analysis_{timestamp}.png"

        plt.title(plot_title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def run_single_simulation_with_type(args):
    """Wrapper function to unpack arguments for multiprocessing."""
    params, experiment_type = args
    return run_single_simulation_generic(params, experiment_type)


def run_experiment_generic(
    n_simulations,
    steps,
    warmup_fraction,
    experiment_type="road_length",
    log_scale=False,
    **kwargs,
):
    """Generic function to run any type of experiment."""
    # Create parameter combinations based on experiment type
    params = []
    if experiment_type == "road_length":
        for road_length, density in product(
            kwargs["road_lengths"], kwargs["densities"]
        ):
            for sim_index in range(n_simulations):
                params.append(
                    (
                        (
                            road_length,
                            density,
                            steps,
                            kwargs["lane_width"],
                            kwargs["rotary_method"],
                            sim_index,
                        ),
                        experiment_type,
                    )
                )
        variable_values = kwargs["road_lengths"]
    elif experiment_type == "speed_compliance":
        for density, speed in product(kwargs["densities"], kwargs["speed_percentages"]):
            for sim_index in range(n_simulations):
                params.append(
                    (
                        (
                            density,
                            speed,
                            steps,
                            kwargs["road_length"],
                            kwargs["lane_width"],
                            kwargs["rotary_method"],
                            sim_index,
                        ),
                        experiment_type,
                    )
                )
        variable_values = kwargs["speed_percentages"]
    elif experiment_type == "max_speed":
        for speed, density in product(kwargs["max_speeds"], kwargs["densities"]):
            for sim_index in range(n_simulations):
                params.append(
                    (
                        (
                            speed,
                            density,
                            steps,
                            kwargs["road_length"],
                            kwargs["rotary_method"],
                            sim_index,
                        ),
                        experiment_type,
                    )
                )
        variable_values = kwargs["max_speeds"]
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    total_simulations = len(params)
    print(f"Running {total_simulations} simulations in parallel...")
    print(f"({n_simulations} simulations per parameter combination)")
    n_processes = max(1, mp.cpu_count() - 1)
    print(f"Using {n_processes} CPU cores")

    # Run simulations in parallel with progress bar
    with mp.Pool(n_processes) as pool:
        raw_results = list(
            tqdm(
                pool.imap(run_single_simulation_with_type, params),
                total=total_simulations,
                desc="Running simulations",
            )
        )

    # Aggregate results across simulations
    results = aggregate_results(raw_results, experiment_type)

    # Save results and create plots
    formatted_results = save_results_generic(results, variable_values, experiment_type)
    create_analysis_plots_generic(
        formatted_results,
        variable_values,
        experiment_type,
        log_scale=log_scale,
        rotary_method=kwargs["rotary_method"],
    )


def run_experiment(
    n_simulations,
    steps,
    warmup_fraction,
    lane_width,
    road_lengths,
    densities,
    log_scale=False,
    rotary_method=FREE_MOVEMENT,
):
    """Run the road length experiment."""
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        experiment_type="road_length",
        lane_width=lane_width,
        road_lengths=road_lengths,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )


def run_speed_experiment(
    n_simulations,
    steps,
    warmup_fraction,
    lane_width,
    road_length,
    speed_percentages,
    densities,
    log_scale=False,
    rotary_method=FREE_MOVEMENT,
):
    """Run the speed compliance experiment."""
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        experiment_type="speed_compliance",
        lane_width=lane_width,
        road_length=road_length,
        speed_percentages=speed_percentages,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )


def run_maxspeed_experiment(
    n_simulations,
    steps,
    warmup_fraction,
    lane_width,
    road_length,
    max_speeds,
    densities,
    log_scale=False,
    rotary_method=FREE_MOVEMENT,
):
    """Run the maximum speed experiment."""
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        experiment_type="max_speed",
        lane_width=lane_width,
        road_length=road_length,
        max_speeds=max_speeds,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )
