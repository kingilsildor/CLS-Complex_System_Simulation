import numpy as np
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

from models.nagel_schreckenberg import NagelSchreckenberg

def main():
    # Initialize the tkinter window
    root = tk.Tk()
    root.title("Nagel-Schreckenberg Simulation")
    root.geometry("800x600")  # Set a fixed size for the window

    # Create frames for layout
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    output_frame = tk.Frame(root)
    output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Simulation parameters
    length = tk.IntVar(value=100)
    num_cars = tk.IntVar(value=10)
    max_speed = tk.IntVar(value=10)
    time_steps = tk.IntVar(value=100)
    randomization = tk.BooleanVar(value=True)

    # Create sliders for adjusting parameters
    tk.Label(control_frame, text="Length of the road").pack()
    tk.Scale(control_frame, from_=10, to=200, orient=tk.HORIZONTAL, variable=length).pack()
    tk.Label(control_frame, text="Number of cars").pack()
    tk.Scale(control_frame, from_=1, to=200, orient=tk.HORIZONTAL, variable=num_cars).pack()
    tk.Label(control_frame, text="Maximum speed of cars").pack()
    tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, variable=max_speed).pack()
    tk.Label(control_frame, text="Number of time steps").pack()
    tk.Scale(control_frame, from_=10, to=500, orient=tk.HORIZONTAL, variable=time_steps).pack()

    # Set up the scrollable text widget for displaying the simulation
    text_widget = scrolledtext.ScrolledText(output_frame, font=("Courier", 12), wrap=tk.NONE)
    text_widget.pack(fill=tk.BOTH, expand=True)

    # Add horizontal scrollbar
    h_scrollbar = tk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    text_widget.config(xscrollcommand=h_scrollbar.set)

    # Counter for time steps
    step_counter = [0]
    output_lines = []
    running = [False]
    model = None

    def start_simulation():
        if num_cars.get() > length.get():
            messagebox.showerror("Parameter Error", "Number of cars cannot be greater than the length of the road")
            return
        if not running[0]:
            running[0] = True
            initialize_model()
            update_simulation()

    def stop_simulation():
        running[0] = False

    def reset_simulation():
        stop_simulation()
        step_counter[0] = 0
        output_lines.clear()
        text_widget.delete(1.0, tk.END)
        initialize_model()

    def update_simulation():
        if running[0] and step_counter[0] < time_steps.get():
            model.update()
            output_lines.append(model.visualize())
            text_widget.insert(tk.END, model.visualize() + "\n")
            text_widget.see(tk.END)  # Scroll to the end
            step_counter[0] += 1
            root.after(100, update_simulation)  # Schedule the next update

    def initialize_model():
        nonlocal model
        print(f"Initializing model with length={length.get()}, num_cars={num_cars.get()}, max_speed={max_speed.get()}")
        model = NagelSchreckenberg(length.get(), num_cars.get(), max_speed.get())

    def disable_random():
        randomization.set(not randomization.get())
        print(f"Randomization set to {randomization.get()}")
    

    # Create buttons for starting, stopping, and resetting the simulation
    tk.Button(control_frame, text="Start", command=start_simulation).pack(pady=5)
    tk.Button(control_frame, text="Stop", command=stop_simulation).pack(pady=5)
    tk.Button(control_frame, text="Reset", command=reset_simulation).pack(pady=5)
    #Check Button for randomization
    randomization_checkbutton = tk.Checkbutton(control_frame, text="Randomization", variable=randomization, command=lambda: print(f"Randomization set to {randomization.get()}"))
    randomization_checkbutton.pack(pady=5)


    # Initialize the model
    initialize_model()

    # Run the tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()