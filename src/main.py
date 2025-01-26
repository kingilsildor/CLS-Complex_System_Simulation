import numpy as np
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from models.nagel_schreckenberg import NagelSchreckenberg

def main():
    # Initialize the tkinter window
    root = tk.Tk()
    root.title("Nagel-Schreckenberg Simulation")
    root.geometry("800x600")  # Set a fixed size for the window

    # Create frames for layout
    control_frame = tk.Frame(root)
    control_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
    output_frame = tk.Frame(root)
    output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    plot_frame = tk.Frame(root)
    plot_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    #control_frame = tk.Frame(root)
    #control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    #output_frame = tk.Frame(root)
    #output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

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
    speed_data = []
    density_data = []
    flow_data = []

    # Set up the matplotlib figure and axis for density vs speed plot
    fig1, ax1 = plt.subplots()
    line1, = ax1.plot([], [], 'bo')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, max_speed.get())
    ax1.set_xlabel("Density (cars per cell)")
    ax1.set_ylabel("Average Speed (cells per time step)")
    ax1.set_title("Density vs. Average Speed")

    canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame)
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def init1():
        line1.set_data([], [])
        return line1,

    def update_plot1(frame):
        line1.set_data(density_data, speed_data)
        return line1,

    ani1 = FuncAnimation(fig1, update_plot1, init_func=init1, blit=True, frames=time_steps.get())

    # Set up the matplotlib figure and axis for density vs flow plot
    fig2, ax2 = plt.subplots()
    line2, = ax2.plot([], [], 'ro')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, max_speed.get())
    ax2.set_xlabel("Density (cars per cell)")
    ax2.set_ylabel("Flow (cars per time step)")
    ax2.set_title("Density vs. Flow")

    canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
    canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def init2():
        line2.set_data([], [])
        return line2,

    def update_plot2(frame):
        line2.set_data(density_data, flow_data)
        return line2,

    ani2 = FuncAnimation(fig2, update_plot2, init_func=init2, blit=True, frames=time_steps.get())

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
        #speed_data.clear()
        #density_data.clear()
        #flow_data.clear()
        initialize_model()

    def update_simulation():
        if running[0] and step_counter[0] < time_steps.get():
            model.update()
            output_lines.append(model.visualize())
            text_widget.insert(tk.END, model.visualize() + "\n")
            text_widget.see(tk.END)  # Scroll to the end
            avg_speed = model.total_speed / num_cars.get() # Average speed of cars
            speed_data.append(avg_speed)
            density = num_cars.get() / length.get()
            density_data.append(density)  # Collect density data
            flow = model.flow / length.get()  # Calculate flow
            flow_data.append(flow)  # Collect flow data
            step_counter[0] += 1
            root.after(100, update_simulation)  # Schedule the next update
        #else:
        #    plot_density_vs_speed()

    def initialize_model():
        nonlocal model
        print(f"Initializing model with length={length.get()}, num_cars={num_cars.get()}, max_speed={max_speed.get()}")
        model = NagelSchreckenberg(length.get(), num_cars.get(), max_speed.get())

    def on_closing():
        stop_simulation()
        ani1.event_source.stop()
        ani2.event_source.stop()
        root.quit()
        root.destroy()

    def disable_random():
        randomization.set(not randomization.get())
        print(f"Randomization set to {randomization.get()}")
    
    def plot_density_vs_speed():
        plt.show()

    # Create buttons for starting, stopping, and resetting the simulation
    tk.Button(control_frame, text="Start", command=start_simulation).pack(pady=5)
    tk.Button(control_frame, text="Stop", command=stop_simulation).pack(pady=5)
    tk.Button(control_frame, text="Reset", command=reset_simulation).pack(pady=5)

    #Check Button for randomization
    randomization_checkbutton = tk.Checkbutton(control_frame, text="Randomization", variable=randomization, command=lambda: print(f"Randomization set to {randomization.get()}"))
    randomization_checkbutton.pack(pady=5)

    # Initialize the model
    initialize_model()

    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #show plot window
    #plt.show(block=False)
    #plt.show(block=False)

    # Run the tkinter main loop 
    root.mainloop()

if __name__ == "__main__":
    main()