import numpy as np
import random
import tkinter as tk

from models.nagel_schreckenberg import NagelSchreckenberg

def main():
    # Initialize the tkinter window
    root = tk.Tk()
    root.title("Nagel-Schreckenberg Simulation")

    # Simulation parameters
    length = tk.IntVar(value=100)
    num_cars = tk.IntVar(value=10)
    max_speed = tk.IntVar(value=10)
    time_steps = tk.IntVar(value=100)

    # Create sliders for adjusting parameters
    tk.Label(root, text="Length of the road").pack()
    tk.Scale(root, from_=10, to=200, orient=tk.HORIZONTAL, variable=length).pack()
    tk.Label(root, text="Number of cars").pack()
    tk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, variable=num_cars).pack()
    tk.Label(root, text="Maximum speed of cars").pack()
    tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, variable=max_speed).pack()
    tk.Label(root, text="Number of time steps").pack()
    tk.Scale(root, from_=10, to=500, orient=tk.HORIZONTAL, variable=time_steps).pack()

    # Set up the label for displaying the simulation
    label = tk.Label(root, font=("Courier", 12), justify=tk.LEFT)
    label.pack()

    # Counter for time steps
    step_counter = [0]
    output_lines = []
    running = [False]
    model = None

    def start_simulation():
        if not running[0]:
            running[0] = True
            update_simulation()

    def stop_simulation():
        running[0] = False

    def reset_simulation():
        stop_simulation()
        step_counter[0] = 0
        output_lines.clear()
        label.config(text="")
        model.initialize()

    def update_simulation():
        if running[0] and step_counter[0] < time_steps.get():
            model.update()
            output_lines.append(model.visualize())
            label.config(text="\n".join(output_lines))
            step_counter[0] += 1
            root.after(100, update_simulation)  # Schedule the next update

    def initialize_model():
        nonlocal model
        model = NagelSchreckenberg(length.get(), num_cars.get(), max_speed.get())
        reset_simulation()

    # Create buttons for starting, stopping, and resetting the simulation
    tk.Button(root, text="Start", command=start_simulation).pack()
    tk.Button(root, text="Stop", command=stop_simulation).pack()
    tk.Button(root, text="Reset", command=initialize_model).pack()

    # Initialize the model
    initialize_model()

    # Run the tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()