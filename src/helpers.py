import matplotlib.pyplot as plt
import numpy as np


def generate_initial_state(length: int, density: int):
    """
    Generates a random initial state for the traffic simulation.

    Params:
    -------
    - length (int): Length of the road.
    - density (float): Density of the traffic.

    Returns:
    --------
    - state (ndarray): Initial state of the traffic.
    """
    return np.random.choice([0, 1], size=length, p=[1 - density, density])


def visualize_traffic(state):
    """
    Visualizes the current state of the traffic.

    Params:
    -------
    - state (ndarray): Current state of the traffic.
    """
    plt.imshow(state.reshape(1, -1), cmap="Greys", aspect="auto")
    plt.axis("off")
    plt.show()


def log_simulation_results(results, filename="simulation_results.txt"):
    """
    Logs the results of the simulation to a file.

    Params:
    -------
    - results (list): List of simulation results.
    - filename (str): Name of the file to write the results to. Default is "simulation_results.txt".
    """
    with open(filename, "w") as f:
        for result in results:
            f.write(f"{result}\n")
