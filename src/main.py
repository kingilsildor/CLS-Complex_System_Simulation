import numpy as np
import random
import tkinter as tk

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

    # Set up the tkinter window
    root = tk.Tk()
    root.title("Nagel-Schreckenberg Simulation")
    label = tk.Label(root, font=("Courier", 12), justify=tk.LEFT)
    label.pack()

    # Counter for time steps
    step_counter = [0]
    output_lines = []

    def update_simulation():
        if step_counter[0] < time_steps:
            model.update()
            output_lines.append(model.visualize())
            label.config(text="\n".join(output_lines))
            step_counter[0] += 1
            root.after(100, update_simulation)  # Schedule the next update

    # Run the simulation
    root.after(0, update_simulation)
    root.mainloop()

if __name__ == "__main__":
    main()