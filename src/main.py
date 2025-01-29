import numpy as np
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from models.nagel_schreckenberg import NagelSchreckenberg

#set random seed
random.seed(42)
np.random.seed(42)

def generate_density_vs_speed_data(length, max_speed, randomization, time_steps):

    #set random seed
    random.seed(42)
    np.random.seed(42)

    densities = []
    avg_speeds = []
    for num_cars in range(1, length + 1):  # Cover the full range of densities
        model = NagelSchreckenberg(length, num_cars, max_speed, randomization)
        total_speed = 0
        for _ in range(time_steps):
            model.update()
            total_speed += model.total_speed
        avg_speed = total_speed / (time_steps * num_cars)
        density = num_cars / length
        densities.append(density)
        avg_speeds.append(avg_speed)
    return densities, avg_speeds

def main():
    # Initialize the tkinter window
    root = tk.Tk()
    root.title("Nagel-Schreckenberg Simulation")
    root.geometry("1600x800")  # Set a fixed size for the window

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
    
    # Create a canvas for the plot frame with a scrollbar
    plot_canvas = tk.Canvas(root)
    plot_canvas.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
    plot_scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=plot_canvas.yview)
    plot_scrollbar.grid(row=0, column=3, sticky="ns")
    plot_canvas.configure(yscrollcommand=plot_scrollbar.set)

    plot_frame = tk.Frame(plot_canvas)
    plot_canvas.create_window((0, 0), window=plot_frame, anchor="nw")

    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_rowconfigure(0, weight=1)

    def on_frame_configure(event):
        plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

    plot_frame.bind("<Configure>", on_frame_configure)

    # Bind mouse wheel events to the plot_canvas for scrolling
    def on_mouse_wheel(event):
        plot_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    plot_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Simulation parameters
    length = tk.IntVar(value=200)
    num_cars = tk.IntVar(value=10)
    max_speed = tk.IntVar(value=5)
    time_steps = tk.IntVar(value=100)
    randomization = tk.BooleanVar(value=True)

    # Create sliders for adjusting parameters
    tk.Label(control_frame, text="Length of the road").pack()
    tk.Scale(control_frame, from_=10, to=100, orient=tk.HORIZONTAL, variable=length).pack()
    tk.Label(control_frame, text="Number of cars").pack()
    tk.Scale(control_frame, from_=1, to=200, orient=tk.HORIZONTAL, variable=num_cars).pack()
    tk.Label(control_frame, text="Maximum speed of cars").pack()
    tk.Scale(control_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=max_speed).pack()
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
    time_space_data = []

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

    # Set up the matplotlib figure and axis for time-space diagram
    fig3, ax3 = plt.subplots()
    ax3.set_xlim(0, length.get())
    ax3.set_ylim(time_steps.get(), 0)
    ax3.set_xlabel("Position")
    ax3.set_ylabel("Time")
    ax3.set_title("Time-Space Diagram")
    line3, = ax3.plot([], [], 'ko', markersize=1)  # Initialize line3 for scatter plot
    
    canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
    canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def init3():
        line3.set_data([], [])
        return line3,

    def update_plot3(frame):
        x_data = []
        y_data = []
        for t, positions in enumerate(time_space_data):
            x_data.extend(positions)
            y_data.extend([t] * len(positions))
        line3.set_data(x_data, y_data)
        return line3,

            #ax3.scatter(positions, [t] * len(positions), c='black', s=1)
        #return ax3,

    ani3 = FuncAnimation(fig3, update_plot3, init_func=init3, blit=True, frames=time_steps.get())
    
    def save_plots():
        # Manually update the time-space diagram plot before saving
        update_plot3(None)
        fig3.canvas.draw()
        plt.pause(0.1)  # Allow time for the canvas to update
    
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            fig1.savefig(f"{file_path}_density_vs_speed.png")
            fig2.savefig(f"{file_path}_density_vs_flow.png")
            fig3.savefig(f"{file_path}_time_space_diagram.png")
            messagebox.showinfo("Save Plots", "Plots saved successfully!")
    
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
        time_space_data.clear()
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
            positions = [i for i, x in enumerate(model.road) if x == 1]
            time_space_data.append(positions)  # Collect time-space data
            step_counter[0] += 1
            root.after(100, update_simulation)  # Schedule the next update
        #else:
        #    plot_density_vs_speed()

    def initialize_model():
        nonlocal model
        print(f"Initializing model with length={length.get()}, num_cars={num_cars.get()}, max_speed={max_speed.get()}, randomization={randomization.get()}")
        model = NagelSchreckenberg(length.get(), num_cars.get(), max_speed.get(), randomization.get())

    def on_closing():
        stop_simulation()
        ani1.event_source.stop()
        ani2.event_source.stop()
        ani3.event_source.stop()
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
    tk.Button(control_frame, text="Save Plots", command=save_plots).pack(pady=5)

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