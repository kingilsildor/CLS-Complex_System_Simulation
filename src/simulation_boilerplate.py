import tkinter as tk
from abc import ABC
from tkinter import filedialog, messagebox, scrolledtext

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.density import DensityTracker
from src.grid import Grid
from src.nagel_schreckenberg import NagelSchreckenberg
from src.utils import ROAD_CELLS


class Simulation(ABC):
    def __init__(self, root: tk.Tk, seed: int = 42):
        self.root = root
        np.random.seed(seed)

    def start_simulation(self):
        print(f"Simulation started from {self.__class__.__name__}")
        return

    def pause_simulation(self):
        print(f"Simulation paused from {self.__class__.__name__}")
        return

    def stop_simulation(self):
        print(f"Simulation stopped from {self.__class__.__name__}")
        return

    def restart_simulation(self):
        print(f"Simulation restarted from {self.__class__.__name__}")
        return

    def update_simulation(self):
        print(f"Simulation updated from {self.__class__.__name__}")
        return

    def save_simulation(self):
        print(f"Simulation saved from {self.__class__.__name__}")
        return

    def close_simulation(self):
        print(f"Simulation closed from {self.__class__.__name__}")
        return

    def create_plot(self, figsize: tuple = (12, 12), dpi: int = 300) -> plt.Figure:
        """
        Create a plot with given parameters.

        Params:
        -------
        - figsize (tuple): The size of the figure. Default is (12, 12).
        - dpi (int): The resolution of the figure. Default is 300.

        Returns:
        --------
        - plt.Figure: The created figure.
        """
        fig = plt.Figure(figsize=figsize, dpi=dpi)
        assert isinstance(fig, plt.Figure)

        return fig

    def create_axis(
        self, figure: plt.Figure, nrows: int = 1, ncols: int = 1, index: int = 1
    ) -> plt.Axes:
        """
        Create an axis in the given figure using add_gridspec and subplot.

        Params:
        -------
        - figure (plt.Figure): The figure to add the axis to.
        - nrows (int): Number of rows in the grid. Default is 1.
        - ncols (int): Number of columns in the grid. Default is 1.
        - index (int): Index of the subplot. Default is 1.

        Returns:
        --------
        - plt.Axes: The created axis.
        """
        gridspec = figure.add_gridspec(nrows, ncols)
        ax = figure.add_subplot(gridspec[index - 1])
        assert isinstance(ax, plt.Axes)

        return ax

    def create_canvas(
        self, figure, plot_frame, side: str = tk.TOP
    ) -> FigureCanvasTkAgg:
        """
        Create a canvas widget.

        Params:
        -------
        - figure: The figure to be displayed on the canvas.
        - plot_frame: The frame in which the canvas will be placed.
        - side: The side of the frame where the canvas will be placed. Default is tk.TOP.

        Returns:
        --------
        - tk.Canvas: The canvas widget.
        """
        canvas = FigureCanvasTkAgg(figure, plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=side, fill=tk.BOTH, expand=True)
        assert isinstance(canvas, FigureCanvasTkAgg)

        return canvas

    def create_button(
        self, control_frame: tk.Frame, text: str, command: callable, pady: int = 5
    ) -> tk.Button:
        """
        Create a button widget with a given text and command.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the button will be placed.
        - text (str): The text of the button.
        - command (callable): The function that will be called when the button is clicked.
        - Pady (int): The padding of the frame. Default is 5.

        Returns:
        --------
        - tk.Button: The button widget.
        """
        assert callable(command)
        button = tk.Button(control_frame, text=text, command=command)
        button.pack(pady=pady)
        assert isinstance(button, tk.Button)

        return button

    def create_slider(
        self,
        control_frame: tk.Frame,
        label: str,
        min_val: int | float,
        max_val: int | float,
        variable: tk.IntVar | tk.DoubleVar,
        pady: int = 5,
    ) -> tk.Scale:
        """
        Create a slider widget with a given label.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the slider will be placed.
        - label (str): The label of the slider.
        - min_val (int | float): The minimum value of the slider.
        - max_val (int | float): The maximum value of the slider.
        - variable (tk.IntVar | tk.DoubleVar): The variable that will be updated when the slider is moved.
        - pady (int): The padding of the frame. Default is 5.

        Returns:
        --------
        - tk.Scale: The slider widget.
        """
        if (isinstance(min_val, int) and isinstance(max_val, float)) or (
            isinstance(min_val, float) and isinstance(max_val, int)
        ):
            raise ValueError("min_val and max_val must be of the same type")

        if isinstance(min_val, int) and isinstance(max_val, int):
            assert isinstance(variable, tk.IntVar)
        if isinstance(min_val, float) and isinstance(max_val, float):
            assert isinstance(variable, tk.DoubleVar)

        frame = tk.Frame(control_frame)
        frame.pack(pady=pady)
        assert isinstance(frame, tk.Frame)

        label = tk.Label(frame, text=label)
        label.pack(side=tk.LEFT)
        assert isinstance(label, tk.Label)

        slider = tk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            length=200,
            variable=variable,
        )
        slider.pack(side=tk.RIGHT)
        assert isinstance(slider, tk.Scale)

        return slider

    def create_frames(
        self,
        root: tk.Tk,
        row: int,
        column: int,
        sticky: str,
        padx: int = 10,
        pady: int = 10,
    ) -> tk.Frame:
        """
        Create a frame with given parameters.

        Params:
        -------
        - root (tk.Tk): The root window.
        - row (int): The row of the frame.
        - column (int): The column of the frame.
        - sticky (str): The sticky parameter of the frame.
        - padx (int): The padding in the x-direction. Default is 10.
        - pady (int): The padding in the y-direction. Default is 10.

        Returns:
        --------
        - tk.Frame: The created frame.
        """
        frame = tk.Frame(root)
        frame.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        assert isinstance(frame, tk.Frame)

        return frame

    def create_screen(self, root: tk.Tk, title: str, geometry: str) -> tk.Tk:
        """
        Create a screen with given parameters.

        Params:
        -------
        - root (tk.Tk): The root window.
        - title (str): The title of the screen.
        - geometry (str): The geometry of the screen.
        """
        root.title(title)
        root.geometry(geometry)
        assert isinstance(root, tk.Tk)

        return root


class Simulation_1D(Simulation):
    def __init__(self, root, seed=42):
        super().__init__(root, seed)

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
        plot_scrollbar = tk.Scrollbar(
            root, orient=tk.VERTICAL, command=plot_canvas.yview
        )
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
            plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        plot_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # Simulation parameters
        length = tk.IntVar(value=100)
        num_cars = tk.IntVar(value=10)
        max_speed = tk.IntVar(value=10)
        time_steps = tk.IntVar(value=100)
        randomization = tk.BooleanVar(value=True)

        # Create sliders for adjusting parameters
        tk.Label(control_frame, text="Length of the road").pack()
        tk.Scale(
            control_frame, from_=10, to=200, orient=tk.HORIZONTAL, variable=length
        ).pack()
        tk.Label(control_frame, text="Number of cars").pack()
        tk.Scale(
            control_frame, from_=1, to=200, orient=tk.HORIZONTAL, variable=num_cars
        ).pack()
        tk.Label(control_frame, text="Maximum speed of cars").pack()
        tk.Scale(
            control_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=max_speed
        ).pack()
        tk.Label(control_frame, text="Number of time steps").pack()
        tk.Scale(
            control_frame, from_=10, to=500, orient=tk.HORIZONTAL, variable=time_steps
        ).pack()

        # Set up the scrollable text widget for displaying the simulation
        text_widget = scrolledtext.ScrolledText(
            output_frame, font=("Courier", 12), wrap=tk.NONE
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Add horizontal scrollbar
        h_scrollbar = tk.Scrollbar(
            output_frame, orient=tk.HORIZONTAL, command=text_widget.xview
        )
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
        (line1,) = ax1.plot([], [], "bo")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, max_speed.get())
        ax1.set_xlabel("Density (cars per cell)")
        ax1.set_ylabel("Average Speed (cells per time step)")
        ax1.set_title("Density vs. Average Speed")

        canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame)
        canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def init1():
            line1.set_data([], [])
            return (line1,)

        def update_plot1(frame):
            line1.set_data(density_data, speed_data)
            return (line1,)

        ani1 = FuncAnimation(
            fig1, update_plot1, init_func=init1, blit=True, frames=time_steps.get()
        )

        # Set up the matplotlib figure and axis for density vs flow plot
        fig2, ax2 = plt.subplots()
        (line2,) = ax2.plot([], [], "ro")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, max_speed.get())
        ax2.set_xlabel("Density (cars per cell)")
        ax2.set_ylabel("Flow (cars per time step)")
        ax2.set_title("Density vs. Flow")

        canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
        canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        def init2():
            line2.set_data([], [])
            return (line2,)

        def update_plot2(frame):
            line2.set_data(density_data, flow_data)
            return (line2,)

        ani2 = FuncAnimation(
            fig2, update_plot2, init_func=init2, blit=True, frames=time_steps.get()
        )

        # Set up the matplotlib figure and axis for time-space diagram
        fig3, ax3 = plt.subplots()
        ax3.set_xlim(0, length.get())
        ax3.set_ylim(time_steps.get(), 0)
        ax3.set_xlabel("Position")
        ax3.set_ylabel("Time")
        ax3.set_title("Time-Space Diagram")
        (line3,) = ax3.plot(
            [], [], "ko", markersize=1
        )  # Initialize line3 for scatter plot

        canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def init3():
            line3.set_data([], [])
            return (line3,)

        # def init3():
        # ax3.set_xlim(0, length.get())
        # ax3.set_ylim(time_steps.get(), 0)  # Flip the y-axis
        # ax3.set_xlabel("Position")
        # ax3.set_ylabel("Time")
        # ax3.set_title("Time-Space Diagram")
        # return ax3,

        def update_plot3(frame):
            x_data = []
            y_data = []
            for t, positions in enumerate(time_space_data):
                x_data.extend(positions)
                y_data.extend([t] * len(positions))
            line3.set_data(x_data, y_data)
            return (line3,)

            # ax3.scatter(positions, [t] * len(positions), c='black', s=1)
            # return ax3,

        ani3 = FuncAnimation(
            fig3, update_plot3, init_func=init3, blit=True, frames=time_steps.get()
        )

        def save_plots():
            # Manually update the time-space diagram plot before saving
            update_plot3(None)
            fig3.canvas.draw()
            plt.pause(0.1)  # Allow time for the canvas to update

            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            )
            if file_path:
                fig1.savefig(f"{file_path}_density_vs_speed.png")
                fig2.savefig(f"{file_path}_density_vs_flow.png")
                fig3.savefig(f"{file_path}_time_space_diagram.png")
                messagebox.showinfo("Save Plots", "Plots saved successfully!")

        def start_simulation():
            if num_cars.get() > length.get():
                messagebox.showerror(
                    "Parameter Error",
                    "Number of cars cannot be greater than the length of the road",
                )
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
            # speed_data.clear()
            # density_data.clear()
            # flow_data.clear()
            time_space_data.clear()
            initialize_model()

        def update_simulation():
            if running[0] and step_counter[0] < time_steps.get():
                model.update()
                output_lines.append(model.visualize())
                text_widget.insert(tk.END, model.visualize() + "\n")
                text_widget.see(tk.END)  # Scroll to the end
                avg_speed = model.total_speed / num_cars.get()  # Average speed of cars
                speed_data.append(avg_speed)
                density = num_cars.get() / length.get()
                density_data.append(density)  # Collect density data
                flow = model.flow / length.get()  # Calculate flow
                flow_data.append(flow)  # Collect flow data
                positions = [i for i, x in enumerate(model.road) if x == 1]
                time_space_data.append(positions)  # Collect time-space data
                step_counter[0] += 1
                root.after(100, update_simulation)  # Schedule the next update
            # else:
            #    plot_density_vs_speed()

        def initialize_model():
            nonlocal model
            print(
                f"Initializing model with length={length.get()}, num_cars={num_cars.get()}, max_speed={max_speed.get()}"
            )
            model = NagelSchreckenberg(length.get(), num_cars.get(), max_speed.get())

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

        # Check Button for randomization
        randomization_checkbutton = tk.Checkbutton(
            control_frame,
            text="Randomization",
            variable=randomization,
            command=lambda: print(f"Randomization set to {randomization.get()}"),
        )
        randomization_checkbutton.pack(pady=5)

        # Initialize the model
        initialize_model()

        # Handle window close event
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()


class Simulation_2D(Simulation):
    def __init__(
        self,
        root: tk.Tk,
        max_iter: int,
        grid_size: int,
        road_length: int,
        road_max_speed: int,
        car_count: int,
        car_percentage_max_speed: int,
        seed: int = 42,
    ):
        super().__init__(root, seed)
        self.grid = Grid(grid_size, road_length)
        self.max_iter = max_iter
        self.grid_size = grid_size
        self.road_length = road_length
        self.road_max_speed = road_max_speed
        self.car_count = car_count
        self.car_percentage_max_speed = car_percentage_max_speed

    def create_cars(
        self, grid: Grid, car_count: int, car_percentage_max_speed: int
    ) -> list[Car]:
        """
        Create a list of cars with positions and directions based on traffic rules.
        Cars will drive on the right side by default. Cars will only spawn on regular road cells,
        not on intersections or rotaries. For vertical roads, right lane goes up and left lane
        goes down. For horizontal roads, upper lane goes right and lower lane goes left.

        Params:
        -------
        - grid (Grid): The grid object
        - car_count (int): Number of cars to create
        - drive_on_right (bool): If True, cars drive on the right side. If False, left side.

        Returns:
        --------
        - list[Car]: List of Car objects

        """
        cars = np.zeros(car_count, dtype=object)

        follow_limit_count = int(car_count * (car_percentage_max_speed / 100))
        follow_limit_indices = set(
            np.random.choice(car_count, follow_limit_count, replace=False)
        )

        for i in range(car_count):
            while (
                grid.grid[
                    x := np.random.randint(0, grid.size),
                    y := np.random.randint(0, grid.size),
                ]
                not in ROAD_CELLS
            ):
                pass

            # Set "follow the speed limit" for cars
            follow_limit = True if i in follow_limit_indices else False
            car = Car(grid, position=(x, y), follow_limit=follow_limit)
            assert isinstance(car, Car)
            cars[i] = car

        assert isinstance(cars, np.ndarray)
        return cars

    def start_simulation(self, output: bool = True):
        """
        Start the simulation by creating cars and updating the grid at each step.

        Params:
        -------
        - output (bool): If True, print the simulation steps. Default is True.
        """
        density_tracter = DensityTracker(self.grid)

        # Init cars
        cars = self.create_cars(
            self.grid, self.car_count, self.car_percentage_max_speed
        )
        self.grid.add_cars(cars)

        # Init grid states
        self.grid_states = np.zeros(
            (self.max_iter, self.grid_size, self.grid_size), dtype=int
        )

        # Init data collection
        total_velocity = 0
        total_road_density = 0
        total_intersection_density = 0

        # Init metrics
        grid_size = self.grid.size
        car_count = self.car_count
        steps = self.max_iter

        if output:
            print("\033[1;36m=== Traffic Simulation ===")
            print(
                f"Grid: {grid_size}x{grid_size} | Cars: {car_count} | Steps: {steps}\033[0m\n"
            )

        for step in range(steps):
            moved_cars = self.grid.update_movement()
            metrics = density_tracter.update(moved_cars)

            total_velocity += metrics["average_velocity"]
            total_road_density += metrics["road_density"]
            total_intersection_density += metrics["intersection_density"]

            if output:
                self.data_print(steps, step, metrics)

            new_grid = self.grid.grid.copy()
            assert isinstance(new_grid, np.ndarray)
            self.grid_states[step] = new_grid
        print("-------------------")

    def data_print(self, steps: int, step: int, metrics: dict):
        """
        Print the simulation data at each step.
        """
        print(f"\033[1;33mStep {step + 1:4d}/{steps:d}\033[0m", end=" ")
        print(
            f"\033[1;32mSystem: {metrics['global_density'] * 100:4.1f}%\033[0m",
            end=" ",
        )
        print(
            f"\033[1;34mRoads: {metrics['road_density'] * 100:4.1f}%\033[0m",
            end=" ",
        )
        print(
            f"\033[1;35mInter: {metrics['intersection_density'] * 100:4.1f}%\033[0m",
            end=" ",
        )
        print(f"\033[1;36mCars: {metrics['total_cars']:3d}\033[0m")

    def get_grid_states(self) -> np.ndarray:
        """
        Get the grid states at each step of the simulation.

        Returns:
        --------
        - np.ndarray: The grid states at each step of the simulation.
        """
        return self.grid_states


class Simulation_2D_UI(Simulation_2D):
    def __init__(self):
        pass
