import json
import multiprocessing as mp
import os
import time
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy import stats

from src.density import DensityTracker
from src.grid import Grid
from src.simulation import Simulation_2D_NoUI
from src.utils import FIXED_DESTINATION, FREE_MOVEMENT


def get_experiment_config() -> dict:
    """
    Central configuration for all experiments.
    Modify this function to control which experiments to run and their parameters.

    Returns:
    --------
    - config (dict): A dictionary containing all experiment parameters.
    """
    config = {
        # Global parameters
        "n_simulations": 5,  # Number of simulations per parameter combination
        "steps": 1000,  # Steps per simulation
        "lane_width": 2,
        "warmup_fraction": 0.2,  # Fraction of steps to use as warmup
        "steady_state_fraction": 1,  # Fraction of steps to use as steady state
        "log_scale": True,  # Whether to create log-log plots in addition to normal plots
        "rotary_methods": [FIXED_DESTINATION],  # Run both methods
        "density_start": 5,  # Starting density percentage
        "density_end": 105,  # Ending density percentage
        "density_step": 10,  # Step size for density
        # Which experiments to run
        "run_road_length": True,
        "run_speed_compliance": True,
        "run_max_speed": True,
        # Road length experiment parameters
        "road_length": {"road_lengths": [32, 64, 128, 256]},
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
    """
    Run all configured experiments.
    This function is the main entry point for running all experiments.
    """
    config = get_experiment_config()

    if config["run_road_length"]:
        print("\n=== Running Road Length Experiment ===")
        for rotary_method in config["rotary_methods"]:
            method_name = (
                "Free Movement"
                if rotary_method == FREE_MOVEMENT
                else "Fixed Destination"
            )
            print(f"\nRunning with {method_name} rotary method")
            run_experiment(
                n_simulations=config["n_simulations"],
                steps=config["steps"],
                warmup_fraction=config["warmup_fraction"],
                steady_state_fraction=config["steady_state_fraction"],
                lane_width=config["lane_width"],
                log_scale=config["log_scale"],
                rotary_method=rotary_method,
                **config["road_length"],
            )

    if config["run_speed_compliance"]:
        print("\n=== Running Speed Compliance Experiment ===")
        for rotary_method in config["rotary_methods"]:
            method_name = (
                "Free Movement"
                if rotary_method == FREE_MOVEMENT
                else "Fixed Destination"
            )
            print(f"\nRunning with {method_name} rotary method")
            run_speed_experiment(
                n_simulations=config["n_simulations"],
                steps=config["steps"],
                warmup_fraction=config["warmup_fraction"],
                steady_state_fraction=config["steady_state_fraction"],
                lane_width=config["lane_width"],
                log_scale=config["log_scale"],
                rotary_method=rotary_method,
                **config["speed_compliance"],
            )

    if config["run_max_speed"]:
        print("\n=== Running Maximum Speed Experiment ===")
        for rotary_method in config["rotary_methods"]:
            method_name = (
                "Free Movement"
                if rotary_method == FREE_MOVEMENT
                else "Fixed Destination"
            )
            print(f"\nRunning with {method_name} rotary method")
            run_maxspeed_experiment(
                n_simulations=config["n_simulations"],
                steps=config["steps"],
                warmup_fraction=config["warmup_fraction"],
                steady_state_fraction=config["steady_state_fraction"],
                lane_width=config["lane_width"],
                log_scale=config["log_scale"],
                rotary_method=rotary_method,
                **config["max_speed"],
            )


def calculate_grid_size(road_length: int) -> int:
    """
    Calculate appropriate grid size for a given road length.
    We want enough roads for meaningful results, but not too many to keep simulation fast.
    Grid size is scaled more aggressively for very small road lengths.

    Params:
    ------
    - road_length (int): The length of the road.

    Returns:
    -------
    - grid_size (int): The size of the grid.
    """

    # Calculate grid size based on number of roads
    grid_size = 512
    return grid_size


def run_single_simulation_generic(
    params: tuple, experiment_type: str = "road_length"
) -> dict:
    """
    Generic simulation runner for all experiment types.
    This function is used to run a single simulation with given parameters.

    Params:
    ------
    - params (tuple): The parameters for the simulation.
    - experiment_type (str): The type of experiment to run. Default is "road_length".

    Returns:
    -------
    - result (dict): The results of the simulation.
    """
    if experiment_type == "road_length":
        (
            road_length,
            density_percentage,
            steps,
            lane_width,
            rotary_method,
            sim_index,
            steady_state_fraction,
        ) = params
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
            steady_state_fraction,
        ) = params
        max_speed = 5  # Fixed max speed for speed compliance experiment
    elif experiment_type == "max_speed":
        (
            max_speed,
            density_percentage,
            steps,
            road_length,
            rotary_method,
            sim_index,
            steady_state_fraction,
        ) = params
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
        rotary_method=rotary_method,
        grid_size=grid_size,
        road_length=road_length,
        road_max_speed=max_speed,
        car_count=car_count,
        car_percentage_max_speed=speed_percentage,
        seed=42 + sim_index,
    )

    # Create density tracker and collect metrics
    density_tracker = DensityTracker(ui.grid)
    metrics_history = []  # For steady state calculation
    all_metrics_history = []  # For gridlock detection

    # Create cars and add them to the grid
    cars = ui.create_cars(ui.grid, car_count, speed_percentage)
    ui.grid.add_cars(cars)

    # Variables for gridlock detection
    gridlock_threshold = 50  # Number of steps to consider as gridlock
    zero_movement_count = 0

    # Run simulation and collect metrics
    warmup_steps = int(steps * 0.2)  # Use 20% of steps as warmup
    steady_state_start = int(
        steps * (1 - steady_state_fraction)
    )  # Calculate start of steady state period

    # Ensure we have at least one step for metrics collection
    steady_state_start = min(steady_state_start, steps - 1)
    steady_state_start = max(
        steady_state_start, warmup_steps
    )  # Don't start before warmup

    for step in range(steps):
        moved_cars = ui.grid.update_movement()
        metrics = density_tracker.update(moved_cars)

        # Only collect metrics for gridlock detection after warmup
        if step >= warmup_steps:
            all_metrics_history.append(
                metrics
            )  # Collect metrics for gridlock detection

        # Check for gridlock
        total_movement = sum(moved_cars)
        if total_movement == 0:
            zero_movement_count += 1
        else:
            zero_movement_count = 0

        # If no movement for too long after warmup, consider it gridlocked
        if step >= warmup_steps and zero_movement_count >= gridlock_threshold:
            # Calculate average velocity over all steps after warmup
            all_velocities = [m["average_velocity"] for m in all_metrics_history]
            overall_avg_velocity = np.mean(all_velocities) if all_velocities else 0.0

            result = {
                "density": density,
                "velocity": overall_avg_velocity,  # Return the overall average
                "sim_index": sim_index,
                "rotary_method": rotary_method,
                "gridlocked": True,
            }

            # Add experiment-specific parameters
            if experiment_type == "road_length":
                result["road_length"] = road_length
            elif experiment_type == "speed_compliance":
                result["speed_percentage"] = speed_percentage
            elif experiment_type == "max_speed":
                result["max_speed"] = max_speed

            return result

        if step >= steady_state_start:  # Only collect metrics in steady state period
            metrics_history.append(metrics)

    # Calculate average velocity over steady state period
    # Ensure we have at least one metric
    if not metrics_history:
        avg_velocity = 0.0  # If no metrics were collected, assume gridlock
    else:
        avg_velocity = np.mean([m["average_velocity"] for m in metrics_history])

    # Return results based on experiment type
    result = {
        "density": density,
        "velocity": avg_velocity,
        "sim_index": sim_index,
        "rotary_method": rotary_method,
        "gridlocked": False,
    }

    # Add experiment-specific parameters
    if experiment_type == "road_length":
        result["road_length"] = road_length
    elif experiment_type == "speed_compliance":
        result["speed_percentage"] = speed_percentage
    elif experiment_type == "max_speed":
        result["max_speed"] = max_speed

    return result


def aggregate_results(raw_results: list, experiment_type: str = "road_length") -> list:
    """
    Aggregate results from multiple simulations for each parameter combination.
    Performs statistical analysis including normality tests and confidence intervals.

    Params:
    ------
    - raw_results (list): The raw results from all simulations.
    - experiment_type (str): The type of experiment to aggregate results for. Default is "road_length".

    Returns:
    -------
    - aggregated_results (list): The aggregated results with statistical information.
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

    # Group results by variable value, density, and rotary method
    grouped_results = {}
    for result in raw_results:
        key = (result[var_name], result["density"], result["rotary_method"])
        if key not in grouped_results:
            grouped_results[key] = {
                "velocities": [],
                "gridlocked": 0,  # Count of gridlocked simulations
            }
        grouped_results[key]["velocities"].append(result["velocity"])
        if result.get("gridlocked", False):
            grouped_results[key]["gridlocked"] += 1

    # Calculate statistics for each group
    aggregated_results = []
    for (var_value, density, rotary_method), group_data in grouped_results.items():
        velocities = np.array(group_data["velocities"])
        n = len(velocities)
        n_gridlocked = group_data["gridlocked"]

        if n_gridlocked > 0:
            print(
                f"Warning: {n_gridlocked}/{n} simulations gridlocked for {var_name}={var_value}, "
                f"density={density:.2f}, rotary_method={rotary_method}"
            )

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

            # Skip normality test if all values are identical
            if n >= 3 and not np.allclose(velocities, velocities[0]):
                _, normality_test_p = stats.shapiro(velocities)
                if normality_test_p < 0.05:
                    print(
                        f"Warning: Non-normal distribution detected for {var_name}={var_value}, "
                        f"density={density:.2f}, rotary_method={rotary_method} (p={normality_test_p:.4f})"
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
            "rotary_method": rotary_method,
            "velocity": mean_velocity,
            "std": std_velocity,
            "std_error": std_error,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "n_samples": n,
            "n_gridlocked": n_gridlocked,
        }
        if normality_test_p is not None:
            result_dict["normality_p_value"] = normality_test_p

        aggregated_results.append(result_dict)

    return aggregated_results


def save_results_generic(
    results: list, variable_values: list, experiment_type: str = "road_length"
) -> dict:
    """
    Generic function to save results for all experiment types.

    Params:
    ------
    - results (list): The aggregated results to save.
    - variable_values (list): The values of the variable being tested.
    - experiment_type (str): The type of experiment (road_length, speed_compliance, or max_speed). Default is "road_length".

    Returns:
    -------
    - formatted_results (dict): The formatted results for plotting.
    """
    # Get timestamp in ddmmhhmm format
    timestamp = time.strftime("%d%m_%H%M")

    # Determine base paths based on experiment type
    if experiment_type == "road_length":
        base_path = "data/road_length"
        var_name = "road_length"
    elif experiment_type == "speed_compliance":
        base_path = "data/speed_compliance"
        var_name = "speed_percentage"
    elif experiment_type == "max_speed":
        base_path = "data/max_speed"
        var_name = "max_speed"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Create subdirectories for different file types
    csv_path = f"{base_path}/csv"
    json_path = f"{base_path}/json"
    os.makedirs(csv_path, exist_ok=True)
    os.makedirs(json_path, exist_ok=True)

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{csv_path}/results_{timestamp}.csv", index=False)

    # Format results for plotting
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

    with open(f"{json_path}/results_{timestamp}.json", "w") as f:
        json.dump(json_results, f, indent=4)

    return formatted_results


def create_analysis_plots_generic(
    results: dict,
    variable_values: list,
    experiment_type: str = "road_length",
    log_scale: bool = False,
    rotary_method: int = FREE_MOVEMENT,
    n_simulations: int = 1,
    steady_state_fraction: float = 1.0,
):
    """
    Generic function to create analysis plots for all experiment types.

    Params:
    -----------
    - results (dict): The formatted results for plotting.
    - variable_values (list): The values of the variable being tested.
    - experiment_type (str): The type of experiment (road_length, speed_compliance, or max_speed). Default is "road_length".
    - log_scale (bool): Whether to create log-log plots in addition to normal plots. Default is False.
    - rotary_method (str): The rotary method used in the simulation (FREE_MOVEMENT or FIXED_DESTINATION). Default is FREE_MOVEMENT.
    - n_simulations (int): Number of simulations per parameter combination. Default is 1.
    - steady_state_fraction (float): Fraction of steps to use for steady state calculation. Default is 1.0.
    """
    # Get timestamp in ddmmhhmm format
    timestamp = time.strftime("%d%m%H%M")

    # Set up plot parameters based on experiment type
    if experiment_type == "road_length":
        base_path = "data/road_length"
        label_prefix = "Road Length"
        title = "Effect of Road Length on Speed vs Density"
        param_str = f"roads_{len(variable_values)}"
    elif experiment_type == "speed_compliance":
        base_path = "data/speed_compliance"
        label_prefix = "Speed Compliance"
        title = "Effect of Speed Limit Compliance on Speed vs Density"
        param_str = f"speeds_{len(variable_values)}"
    elif experiment_type == "max_speed":
        base_path = "data/max_speed"
        label_prefix = "Max Speed"
        title = "Effect of Maximum Speed Limit on Speed vs Density"
        param_str = f"speeds_{len(variable_values)}"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    # Create rotary method label and short version for filename
    rotary_label = (
        "Free Movement" if rotary_method == FREE_MOVEMENT else "Fixed Destination"
    )
    rotary_short = "free" if rotary_method == FREE_MOVEMENT else "fixed"

    # Create plots directory
    plots_path = f"{base_path}/plots"
    os.makedirs(plots_path, exist_ok=True)

    # Create both normal and log-scale plots
    plot_types = ["normal"]
    if log_scale:
        plot_types.append("log")

    for plot_type in plot_types:
        plt.figure(figsize=(10, 7))
        has_valid_data = False  # Track if we have any valid data to plot

        # Velocity vs Density plot with confidence intervals
        colors = plt.cm.tab10(np.linspace(0, 1, len(variable_values)))
        for val, color in zip(variable_values, colors):
            densities = np.array(results[val]["densities"]) * 100
            velocities = np.array(results[val]["velocities"])

            # Only plot confidence intervals if we have multiple simulations
            has_confidence = (
                "ci_lower" in results[val]
                and "ci_upper" in results[val]
                and len(results[val]["ci_lower"]) > 0
                and len(results[val]["ci_upper"]) > 0
            )

            # Find where velocity is non-zero (allowing for small numerical errors)
            non_zero_mask = velocities > 0.001

            # Always include the last point if we have any data
            if len(densities) > 0:
                non_zero_mask[-1] = True

            # Only plot non-zero values
            plot_densities = densities[non_zero_mask]
            plot_velocities = velocities[non_zero_mask]

            if len(plot_densities) == 0:
                continue

            # For log plots, ensure all values are positive
            if plot_type == "log":
                epsilon = 1e-10
                plot_velocities = np.maximum(plot_velocities, epsilon)
                plot_densities = np.maximum(plot_densities, epsilon)

            # Plot mean line with points
            plt.plot(
                plot_densities,
                plot_velocities,
                "o-",
                color=color,
                label=f"{label_prefix} {val}",
            )
            has_valid_data = True

            # Add confidence interval shading only if we have multiple simulations
            if has_confidence and n_simulations > 1:
                ci_lower = np.array(results[val]["ci_lower"])[non_zero_mask]
                ci_upper = np.array(results[val]["ci_upper"])[non_zero_mask]
                if plot_type == "log":
                    ci_lower = np.maximum(ci_lower, epsilon)
                    ci_upper = np.maximum(ci_upper, epsilon)
                plt.fill_between(
                    plot_densities, ci_lower, ci_upper, color=color, alpha=0.2
                )

        if not has_valid_data:
            plt.close()
            continue

        plt.xlabel("Global Density (%)")
        plt.ylabel("Average Speed")
        if plot_type != "log":
            plt.ylim(0)
            plt.xlim(0, 100)
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.minorticks_on()

        if plot_type == "log":
            plt.xscale("log")
            plt.yscale("log")
            confidence_text = (
                "with 95% Confidence Intervals" if n_simulations > 1 else ""
            )
            plot_title = f"{title}\n(Log-Log Scale{', ' + confidence_text if confidence_text else ''})\nRotary Method: {rotary_label}"
            filename = f"{plots_path}/{timestamp}_{param_str}_{rotary_short}_loglog.png"
        else:
            confidence_text = (
                "with 95% Confidence Intervals" if n_simulations > 1 else ""
            )
            plot_title = f"{title}\n({confidence_text})\nRotary Method: {rotary_label}"
            filename = f"{plots_path}/{timestamp}_{param_str}_{rotary_short}.png"

        plt.title(plot_title)
        if has_valid_data:
            plt.legend()
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def run_single_simulation_with_type(args: tuple) -> dict:
    """
    Wrapper function to unpack arguments for multiprocessing.

    Params:
    -------
    - args (tuple): A tuple containing the parameters and experiment type.

    Returns:
    --------
    - result (dict): The results of the simulation.
    """
    params, experiment_type = args
    return run_single_simulation_generic(params, experiment_type)


def run_experiment_generic(
    n_simulations: int,
    steps: int,
    warmup_fraction: float,
    steady_state_fraction: float,
    experiment_type: str = "road_length",
    log_scale: bool = False,
    **kwargs,
):
    """
    Generic function to run any type of experiment.

    Params:
    -------
    - n_simulations (int): Number of simulations per parameter combination.
    - steps (int): Number of steps per simulation.
    - warmup_fraction (float): Fraction of steps to use as warmup.
    - steady_state_fraction (float): Fraction of steps to use for steady state calculation.
    - experiment_type (str): The type of experiment to run (road_length, speed_compliance, or max_speed).
    - log_scale (bool): Whether to create log-log plots in addition to normal plots. Default is False.
    - kwargs (dict): Additional keyword arguments for the experiment.
    """
    # Create parameter combinations based on experiment type
    params = []
    raw_results = []  # Initialize raw_results list
    if experiment_type == "road_length":
        total_params = (
            len(kwargs["road_lengths"]) * len(kwargs["densities"]) * n_simulations
        )
        variable_values = kwargs["road_lengths"]
        sorted_densities = sorted(kwargs["densities"])
        param_iter = kwargs["road_lengths"]
        param_name = "road length"
    elif experiment_type == "speed_compliance":
        total_params = (
            len(kwargs["speed_percentages"]) * len(kwargs["densities"]) * n_simulations
        )
        variable_values = kwargs["speed_percentages"]
        sorted_densities = sorted(kwargs["densities"])
        param_iter = kwargs["speed_percentages"]
        param_name = "speed compliance"
    elif experiment_type == "max_speed":
        total_params = (
            len(kwargs["max_speeds"]) * len(kwargs["densities"]) * n_simulations
        )
        variable_values = kwargs["max_speeds"]
        sorted_densities = sorted(kwargs["densities"])
        param_iter = kwargs["max_speeds"]
        param_name = "max speed"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    print(f"Running up to {total_params} simulations in parallel...")
    print(f"({n_simulations} simulations per parameter combination)")
    n_processes = max(1, mp.cpu_count() - 1)
    print(f"Using {n_processes} CPU cores")

    # Create progress bar for all simulations
    pbar = tqdm(total=total_params, desc="Running simulations")
    skipped_count = 0

    # Initialize gridlocked_states dictionary
    gridlocked_states = {}

    for param in param_iter:
        gridlocked_states[param] = False
        for density in sorted_densities:
            if gridlocked_states[param]:
                print(
                    f"\nSkipping density {density}% for {param_name} {param} as previous density was gridlocked"
                )
                skipped_count += n_simulations
                pbar.update(n_simulations)
                continue

            # Create parameters for this density level
            params = []
            for sim_index in range(n_simulations):
                if experiment_type == "road_length":
                    params.append(
                        (
                            (
                                param,
                                density,
                                steps,
                                kwargs["lane_width"],
                                kwargs["rotary_method"],
                                sim_index,
                                steady_state_fraction,
                            ),
                            experiment_type,
                        )
                    )
                elif experiment_type == "speed_compliance":
                    params.append(
                        (
                            (
                                density,
                                param,
                                steps,
                                kwargs["road_length"],
                                kwargs["lane_width"],
                                kwargs["rotary_method"],
                                sim_index,
                                steady_state_fraction,
                            ),
                            experiment_type,
                        )
                    )
                else:  # max_speed
                    params.append(
                        (
                            (
                                param,
                                density,
                                steps,
                                kwargs["road_length"],
                                kwargs["rotary_method"],
                                sim_index,
                                steady_state_fraction,
                            ),
                            experiment_type,
                        )
                    )

            # Run simulations for this density level
            with mp.Pool(n_processes) as pool:
                batch_results = list(pool.imap(run_single_simulation_with_type, params))
            raw_results.extend(batch_results)
            pbar.update(n_simulations)

            # Check if all simulations at this density level resulted in very low velocities
            # Look at both the average velocity and the maximum velocity achieved in any simulation
            avg_velocities = [r["velocity"] for r in batch_results]
            overall_avg_velocity = np.mean(avg_velocities)
            max_avg_velocity = np.max(avg_velocities)  # Maximum of the averages

            # Only consider it gridlocked if both the overall average and maximum average velocities are very low
            if overall_avg_velocity < 0.001:
                gridlocked_states[param] = True
                remaining_densities = len([d for d in sorted_densities if d > density])
                skipped_count += remaining_densities * n_simulations
                print(
                    f"\nGridlock detected at density {density}% for {param_name} {param}. "
                    f"Overall average velocity: {overall_avg_velocity:.6f}, "
                    f"Maximum average velocity: {max_avg_velocity:.6f}"
                )
                print(f"Skipping {remaining_densities} higher densities.")
                break  # Skip to next parameter

    pbar.close()
    if skipped_count > 0:
        print(f"\nSkipped {skipped_count} simulations due to gridlock detection")
        print(
            f"Actually ran {len(raw_results)} out of {total_params} possible simulations"
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
        n_simulations=n_simulations,
        steady_state_fraction=steady_state_fraction,
    )


def run_experiment(
    n_simulations: int,
    steps: int,
    warmup_fraction: float,
    steady_state_fraction: float,
    lane_width: int,
    road_lengths: list,
    densities: list,
    log_scale: bool = False,
    rotary_method: int = FREE_MOVEMENT,
):
    """
    Run the road length experiment.

    Params:
    -------
    - n_simulations (int): Number of simulations per parameter combination.
    - steps (int): Number of steps per simulation.
    - warmup_fraction (float): Fraction of steps to use as warmup.
    - steady_state_fraction (float): Fraction of steps to use for steady state calculation.
    - lane_width (int): Width of each lane.
    - road_lengths (list): List of road lengths to test.
    - densities (list): List of densities to test.
    - log_scale (bool): Whether to create log-log plots in addition to normal plots. Default is False.
    - rotary_method (str): The rotary method used in the simulation (FREE_MOVEMENT or FIXED_DESTINATION). Default is FREE_MOVEMENT.
    """
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        steady_state_fraction=steady_state_fraction,
        experiment_type="road_length",
        lane_width=lane_width,
        road_lengths=road_lengths,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )


def run_speed_experiment(
    n_simulations: int,
    steps: int,
    warmup_fraction: float,
    steady_state_fraction: float,
    lane_width: int,
    road_length: int,
    speed_percentages: list,
    densities: list,
    log_scale: bool = False,
    rotary_method: int = FREE_MOVEMENT,
):
    """
    Run the speed compliance experiment.

    Params:
    -------
    - n_simulations (int): Number of simulations per parameter combination.
    - steps (int): Number of steps per simulation.
    - warmup_fraction (float): Fraction of steps to use as warmup.
    - steady_state_fraction (float): Fraction of steps to use for steady state calculation.
    - lane_width (int): Width of each lane.
    - road_length (int): Length of the road.
    - speed_percentages (list): List of speed percentages to test.
    - densities (list): List of densities to test.
    - log_scale (bool): Whether to create log-log plots in addition to normal plots. Default is False.
    - rotary_method (str): The rotary method used in the simulation (FREE_MOVEMENT or FIXED_DESTINATION). Default is FREE_MOVEMENT.
    """
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        steady_state_fraction=steady_state_fraction,
        experiment_type="speed_compliance",
        lane_width=lane_width,
        road_length=road_length,
        speed_percentages=speed_percentages,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )


def run_maxspeed_experiment(
    n_simulations: int,
    steps: int,
    warmup_fraction: float,
    steady_state_fraction: float,
    lane_width: int,
    road_length: int,
    max_speeds: list,
    densities: list,
    log_scale: bool = False,
    rotary_method: int = FREE_MOVEMENT,
):
    """
    Run the maximum speed experiment.

    Params:
    -------
    - n_simulations (int): Number of simulations per parameter combination.
    - steps (int): Number of steps per simulation.
    - warmup_fraction (float): Fraction of steps to use as warmup.
    - steady_state_fraction (float): Fraction of steps to use for steady state calculation.
    - lane_width (int): Width of each lane.
    - road_length (int): Length of the road.
    - max_speeds (list): List of maximum speeds to test.
    - densities (list): List of densities to test.
    - log_scale (bool): Whether to create log-log plots in addition to normal plots. Default is False.
    - rotary_method (str): The rotary method used in the simulation (FREE_MOVEMENT or FIXED_DESTINATION). Default is FREE_MOVEMENT.
    """
    run_experiment_generic(
        n_simulations=n_simulations,
        steps=steps,
        warmup_fraction=warmup_fraction,
        steady_state_fraction=steady_state_fraction,
        experiment_type="max_speed",
        lane_width=lane_width,
        road_length=road_length,
        max_speeds=max_speeds,
        densities=densities,
        log_scale=log_scale,
        rotary_method=rotary_method,
    )
