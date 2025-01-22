# File: /1d-cellular-automata-traffic/1d-cellular-automata-traffic/src/main.py

import numpy as np
import matplotlib.pyplot as plt
import random

from models.nagel_schreckenberg import NagelSchreckenberg

def main():
    # Simulation parameters
    length = 100  # Length of the road
    num_cars = 10  # Number of cars
    max_speed = 10  # Maximum speed of cars
    time_steps = 100  # Number of time steps to simulate

    # Validate parameters
    if num_cars > length:
        raise ValueError("Number of cars cannot be greater than the length of the road")

    # Initialize the Nagel-Schreckenberg model
    model = NagelSchreckenberg(length, num_cars, max_speed)

    # Run the simulation
    for t in range(time_steps):
        model.update()
        model.visualize()

    plt.show()

if __name__ == "__main__":
    main()