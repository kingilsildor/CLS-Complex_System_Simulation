import tkinter as tk
from abc import ABC
from tkinter import filedialog, messagebox, scrolledtext

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.density import DensityTracker
from src.grid import Grid
from src.nagel_schreckenberg import NagelSchreckenberg
from src.utils import (
    CAR_DIRECTION,
    FILE_EXTENSION,
    MAX_SPEED,
    MIN_SPEED,
    ROAD_CELLS,
)


class Simulation(ABC):
    def __init__(self, root: tk.Tk, seed: int = 42):
        """
        Abstract class for traffic simulations.

        Params:
        -------
        - root (tk.Tk): The root window.
        - seed (int): The seed for random number generation. Default is 42.
        """
        self.root = root
        np.random.seed(seed)

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
        - FigureCanvasTkAgg: The created canvas widget.
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

        Returns:
        --------
        - tk.Tk: The created screen.
        """
        root.title(title)
        root.geometry(geometry)
        assert isinstance(root, tk.Tk)

        return root


class Simulation_1D(Simulation):
    def generate_density_vs_speed_data(
        length, max_speed, randomization, time_steps
    ):  # function for plotting density vs speed across simulations
        # set random seed
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

    def __init__(self, root, seed=42):
        """
        Initialize the 1D traffic simulation.

        Params:
        -------
        - root (tk.Tk): The root window.
        - seed (int): The seed for random number generation. Default is 42.
        """
        super().__init__(root, seed)

        root.title("Nagel-Schreckenberg Simulation")
        root.geometry("1600x800")

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
            """
            Configure the plot frame when the window is resized.

            Params:
            -------
            - event: The event that triggered the configuration.
            """
            plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

        plot_frame.bind("<Configure>", on_frame_configure)

        # Bind mouse wheel events to the plot_canvas for scrolling
        def on_mouse_wheel(event):
            """
            Scroll the plot_canvas when the mouse wheel is moved.

            Params:
            -------
            - event: The mouse wheel event.
            """
            plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        plot_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        self.randomization = tk.BooleanVar(value=True)
        # Create sliders for adjusting parameters
        self.init_sliders(control_frame)
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
        ##############################
        n_time_steps = self.time_steps_slider.get()

        self.step_counter = 0
        self.running = False
        self.model = None

        self.output_lines = np.zeros(n_time_steps, dtype=str)

        self.speed_data = []
        self.density_data = []
        self.flow_data = []
        self.time_space_data = []
        ##############################

        # Set up the matplotlib figure and axis for density vs speed plot
        fig1, ax1 = plt.subplots()
        (line1,) = ax1.plot([], [], "bo")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, self.max_speed_slider.get())
        ax1.set_xlabel("Density (cars per cell)")
        ax1.set_ylabel("Average Speed (cells per time step)")
        ax1.set_title("Density vs. Average Speed")

        canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame)
        canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def init1():
            """
            Initialize the plot for density vs speed.

            Returns:
            --------
            - line1: The line for the plot.
            """
            line1.set_data([], [])
            return (line1,)

        def update_plot1(frame):
            """
            Update the plot for density vs speed.

            Params:
            -------
            - frame: The frame to update the plot.

            Returns:
            --------
            - line1: The line for the plot.
            """
            line1.set_data(self.density_data, self.speed_data)
            return (line1,)

        ani1 = FuncAnimation(
            fig1,
            update_plot1,
            init_func=init1,
            blit=True,
            frames=self.time_steps_slider.get(),
        )

        # Set up the matplotlib figure and axis for density vs flow plot
        fig2, ax2 = plt.subplots()
        (line2,) = ax2.plot([], [], "ro")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, self.max_speed_slider.get())
        ax2.set_xlabel("Density (cars per cell)")
        ax2.set_ylabel("Flow (cars per time step)")
        ax2.set_title("Density vs. Flow")

        canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
        canvas2.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        def init2():
            """
            Initialize the plot for density vs flow.

            Returns:
            --------
            - line2: The line for the plot.
            """
            line2.set_data([], [])
            return (line2,)

        def update_plot2(frame):
            """
            Update the plot for density vs flow.

            Params:
            -------
            - frame: The frame to update the plot.

            Returns:
            --------
            - line2: The line for the plot.
            """
            line2.set_data(self.density_data, self.flow_data)
            return (line2,)

        ani2 = FuncAnimation(
            fig2,
            update_plot2,
            init_func=init2,
            blit=True,
            frames=self.time_steps_slider.get(),
        )

        # Set up the matplotlib figure and axis for time-space diagram
        fig3, ax3 = plt.subplots()
        ax3.set_xlim(0, self.road_length_slider.get())
        ax3.set_ylim(self.time_steps_slider.get(), 0)
        ax3.set_xlabel("Position")
        ax3.set_ylabel("Time")
        ax3.set_title("Time-Space Diagram")
        (line3,) = ax3.plot(
            [], [], "ko", markersize=1
        )  # Initialize line3 for scatter plot

        canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def init3():
            """
            Initialize the plot for time-space diagram.

            Returns:
            --------
            - line3: The line for the plot.
            """
            line3.set_data([], [])
            return (line3,)

        def update_plot3(frame):
            """
            Update the plot for time-space diagram.

            Params:
            -------
            - frame: The frame to update the plot.

            Returns:
            --------
            - line3: The line for the plot.
            """
            x_data = []
            y_data = []
            for t, positions in enumerate(self.time_space_data):
                x_data.extend(positions)
                y_data.extend([t] * len(positions))
            line3.set_data(x_data, y_data)
            return (line3,)

        ani3 = FuncAnimation(
            fig3,
            update_plot3,
            init_func=init3,
            blit=True,
            frames=self.time_steps_slider.get(),
        )

        def save_plots():
            """
            Save the plots to selected file paths.
            """
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
            """
            Start the simulation with the given parameters when button is pressed.
            """
            if self.car_count_slider.get() > self.road_length_slider.get():
                messagebox.showerror(
                    "Parameter Error",
                    "Number of cars cannot be greater than the length of the road",
                )
                return
            if not self.running:
                self.running = True
                initialize_model()
                update_simulation()

        def stop_simulation():
            """
            Stop the simulation when button is pressed.
            """
            self.running = False

        def reset_simulation():
            """
            Reset the simulation when button is pressed.
            """
            stop_simulation()
            self.step_counter = 0
            self.output_lines[:] = 0
            text_widget.delete(1.0, tk.END)
            self.time_space_data.clear()
            initialize_model()

        def update_simulation():
            """
            Update the simulation at each time step.
            """
            step = self.step_counter
            if self.running and step < self.time_steps_slider.get():
                self.model.update()
                self.output_lines[step] = self.model.visualize()
                text_widget.insert(tk.END, self.model.visualize() + "\n")
                text_widget.see(tk.END)  # Scroll to the end

                avg_speed = (
                    self.model.total_speed / self.car_count_slider.get()
                )  # Average speed of cars
                self.speed_data.append(avg_speed)

                density = self.car_count_slider.get() / self.road_length_slider.get()
                self.density_data.append(density)  # Collect density data

                flow = self.model.flow / self.road_length_slider.get()  # Calculate flow
                self.flow_data.append(flow)  # Collect flow data

                positions = [i for i, x in enumerate(self.model.road) if x == 1]
                self.time_space_data.append(positions)  # Collect time-space data

                self.step_counter += 1
                root.after(100, update_simulation)  # Schedule the next update

        def initialize_model():
            """
            Initialize the model with the given parameters.
            """
            print(
                f"Initializing model with length={self.road_length_slider.get()}, num_cars={self.car_count_slider.get()}, max_speed={self.max_speed_slider.get()}"
            )
            self.model = NagelSchreckenberg(
                self.road_length_slider.get(),
                self.car_count_slider.get(),
                self.max_speed_slider.get(),
            )
            assert isinstance(self.model, NagelSchreckenberg)

        def on_closing():
            """
            Handle the window close event when the user clicks the 'X' button,
            or turn it off in the console.
            """
            stop_simulation()
            ani1.event_source.stop()
            ani2.event_source.stop()
            ani3.event_source.stop()
            root.quit()
            root.destroy()

        def disable_random():
            """
            Disable randomization of the model.
            """
            self.randomization.set(not self.randomization.get())
            print(f"Randomization set to {self.randomization.get()}")

        def plot_density_vs_speed():
            """
            Plot the density vs speed graph.
            """
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
            variable=self.randomization,
            command=lambda: print(f"Randomization set to {self.randomization.get()}"),
        )
        randomization_checkbutton.pack(pady=5)

        # Initialize the model
        initialize_model()

        # Handle window close event
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    def init_sliders(self, control_frame: tk.Frame):
        """ "
        Create sliders for adjusting the simulation parameters.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the sliders will be placed.
        """
        self.road_length_slider = tk.IntVar(value=100)
        assert isinstance(self.road_length_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Length of the Road",
            min_val=10,
            max_val=200,
            variable=self.road_length_slider,
        )

        self.car_count_slider = tk.IntVar(value=10)
        assert isinstance(self.car_count_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Number of Cars",
            min_val=1,
            max_val=200,
            variable=self.car_count_slider,
        )

        self.max_speed_slider = tk.IntVar(value=10)
        assert isinstance(self.max_speed_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Maximum Speed of Cars",
            min_val=1,
            max_val=5,
            variable=self.max_speed_slider,
        )

        self.time_steps_slider = tk.IntVar(value=100)
        assert isinstance(self.time_steps_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Number of Time Steps",
            min_val=10,
            max_val=200,
            variable=self.time_steps_slider,
        )

    def init_buttons(self, control_frame: tk.Frame):
        """
        Create buttons for starting, stopping, and resetting the simulation.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the buttons will be placed.
        """
        self.create_button(control_frame, text="Start", command=self.start_simulation)
        self.create_button(control_frame, text="Pause", command=self.pause_simulation)
        self.create_button(control_frame, text="Stop", command=self.stop_simulation)
        self.create_button(
            control_frame, text="Restart", command=self.restart_simulation
        )
        self.create_button(control_frame, text="Update", command=self.update_simulation)
        self.create_button(control_frame, text="Save", command=self.save_simulation)
        self.create_button(control_frame, text="Close", command=self.close_simulation)


class Simulation_2D(Simulation, ABC):
    def __init__(self, root: tk.Tk, rotary_method: int, seed: int = 42):
        """
        Initialize the 2D traffic simulation.

        Params:
        -------
        - root (tk.Tk): The root window.
        - rotary_method (int): The method to use for rotaries.
        - seed (int): The seed for random number generation. Default is 42.
        """
        super().__init__(root, seed)
        self.rotary_method = rotary_method

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
        - grid (Grid): The grid object.
        - car_count (int): Number of cars to create.
        - drive_on_right (bool): If True, cars drive on the right side. If False, left side.

        Returns:
        --------
        - list[Car]: List of Car objects.
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


class Simulation_2D_NoUI(Simulation_2D):
    def __init__(
        self,
        root: tk.Tk,
        max_iter: int,
        rotary_method: int,
        grid_size: int,
        road_length: int,
        road_max_speed: int,
        car_count: int,
        car_percentage_max_speed: int,
        seed: int = 42,
    ):
        """
        Initialize the 2D traffic simulation without a user interface.

        Params:
        -------
        - root (tk.Tk): The root window.
        - max_iter (int): The maximum number of iterations.
        - rotary_method (int): The method to use for rotaries.
        - grid_size (int): The size of the grid.
        - road_length (int): The length of the road.
        - road_max_speed (int): The maximum speed of cars on the road.
        - car_count (int): The number of cars to create.
        - car_percentage_max_speed (int): The percentage of cars that will drive at the maximum speed.
        - seed (int): The seed for random number generation. Default is 42.
        """
        super().__init__(root, rotary_method=rotary_method, seed=seed)
        self.grid = Grid(
            grid_size=grid_size,
            blocks_size=road_length,
            rotary_method=self.rotary_method,
        )
        self.max_iter = max_iter
        self.grid_size = grid_size
        self.road_length = road_length
        self.road_max_speed = road_max_speed
        self.car_count = car_count
        self.car_percentage_max_speed = car_percentage_max_speed

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
        G = self.grid.jammed_network()
        if G.number_of_nodes() == 0:
            print("No jammed positions found.")
            return
        else:
            self.largest_component = self.grid.get_largest_cluster(G)
            cluster_sizes = self.grid.analyze_cluster_sizes(G)
            print("Inside last step")
            return cluster_sizes

    def data_print(self, steps: int, step: int, metrics: dict):
        """
        Print the simulation data at each step.

        Params:
        -------
        - steps (int): The total number of steps.
        - step (int): The current step.
        - metrics (dict): The metrics of the simulation.
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
    def __init__(
        self,
        root: tk.Tk,
        rotary_method: int,
        seed: int = 42,
        colour_blind: bool = False,
    ):
        """
        Initialize the 2D traffic simulation with a user interface.

        Params:
        -------
        - root (tk.Tk): The root window.
        - rotary_method (int): The method to use for rotaries.
        - seed (int): The seed for random number generation. Default is 42.
        - colour_blind (bool): If True, use a colour-blind friendly palette. Default is False.
        """
        super().__init__(root, rotary_method=rotary_method, seed=seed)
        self.root.title("Car Traffic in a 2D street network.")

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, padx=10)
        assert isinstance(self.control_frame, tk.Frame)

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, padx=10)
        assert isinstance(self.plot_frame, tk.Frame)

        self.animation = None
        self.is_paused = False
        self.colour_blind = colour_blind

        self.init_sliders(self.control_frame)
        self.init_buttons()
        self.init_metrics_display()
        self.init_plot()

    def init_plot(self):
        """
        Initialize the matplotlib plots for the simulation.
        """
        self.fig = plt.Figure(figsize=(12, 12))
        gs = self.fig.add_gridspec(4, 2, width_ratios=[1, 1])

        # Grid subplot (spans all rows on the left)
        self.ax_grid = self.fig.add_subplot(gs[:, 0])
        self.ax_grid.set_xticks([])
        self.ax_grid.set_yticks([])

        # Density subplot (top right)
        self.ax_density = self.fig.add_subplot(gs[0, 1])
        self.ax_density.set_xlabel("Steps")
        self.ax_density.set_ylabel("Density (%)")
        self.ax_density.set_ylim(0, 100)
        self.ax_density.grid(True)
        (self.road_density_line,) = self.ax_density.plot([], [], "b-", label="Road")
        (self.intersection_density_line,) = self.ax_density.plot(
            [], [], "r-", label="Intersection"
        )
        self.ax_density.legend()

        # Velocity subplot (second from top)
        max_speed = self.max_speed_slider.get()
        self.ax_velocity = self.fig.add_subplot(gs[1, 1])
        self.ax_velocity.set_xlabel("Steps")
        self.ax_velocity.set_ylabel("Average Velocity")
        self.ax_velocity.set_ylim(0, max_speed)
        self.ax_velocity.grid(True)
        (self.velocity_line,) = self.ax_velocity.plot([], [], "g-", label="Velocity")
        self.ax_velocity.legend()

        # Traffic flow subplot (third from top)
        self.ax_flow = self.fig.add_subplot(gs[2, 1])
        self.ax_flow.set_xlabel("Steps")
        self.ax_flow.set_ylabel("Traffic Flow")
        self.ax_flow.set_ylim(0, 1)
        self.ax_flow.grid(True)
        (self.flow_line,) = self.ax_flow.plot([], [], "m-", label="Flow")
        self.ax_flow.legend()

        # Queue subplot (bottom right)
        self.ax_queue = self.fig.add_subplot(gs[3, 1])
        self.ax_queue.set_xlabel("Steps")
        self.ax_queue.set_ylabel("Queue Length")
        self.ax_queue.set_ylim(0, self.car_count_slider.get())
        self.ax_queue.grid(True)
        (self.queue_line,) = self.ax_queue.plot([], [], "c-", label="Queue")
        self.ax_queue.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()
        assert isinstance(self.canvas, FigureCanvasTkAgg)

        self.fig.tight_layout()

        title = "Welcome to SimCity 2000©"
        self.ax_grid.set_title(title)

        self.canvas.draw()

    def init_data_plot(self):
        """
        Set up the plot for the simulation.
        """
        # Clear previous plots
        self.ax_grid.clear()
        self.ax_density.clear()
        self.ax_velocity.clear()
        self.ax_flow.clear()
        self.ax_queue.clear()

        # Setup grid plot
        self.ax_grid.set_xticks([])
        self.ax_grid.set_yticks([])
        cmap = "Greys" if self.colour_blind else "rainbow"
        self.im = self.ax_grid.imshow(
            self.grid.grid, cmap=cmap, interpolation="nearest"
        )

        # Initialize data arrays
        self.step_data = []
        self.velocity_data = []
        self.road_density_data = []
        self.intersection_density_data = []
        self.flow_data = []
        self.queue_data = []

        # Setup density plot
        self.ax_density.set_xlabel("Steps")
        self.ax_density.set_ylabel("Density (%)")
        self.ax_density.set_ylim(0, 100)
        self.ax_density.grid(True)
        (self.road_density_line,) = self.ax_density.plot([], [], "b-", label="Road")
        (self.intersection_density_line,) = self.ax_density.plot(
            [], [], "r-", label="Intersection"
        )
        self.ax_density.legend()

        # Setup velocity plot
        max_speed = self.max_speed_slider.get()
        self.ax_velocity.set_xlabel("Steps")
        self.ax_velocity.set_ylabel("Average Velocity")
        self.ax_velocity.set_ylim(0, max_speed)
        self.ax_velocity.grid(True)
        (self.velocity_line,) = self.ax_velocity.plot([], [], "g-", label="Velocity")
        self.ax_velocity.legend()

        # Setup flow plot
        self.ax_flow.set_xlabel("Steps")
        self.ax_flow.set_ylabel("Traffic Flow")
        self.ax_flow.set_ylim(0, 1)
        self.ax_flow.grid(True)
        (self.flow_line,) = self.ax_flow.plot([], [], "m-", label="Flow")
        self.ax_flow.legend()

        # Setup queue plot
        self.ax_queue.set_xlabel("Steps")
        self.ax_queue.set_ylabel("Queue Length")
        self.ax_queue.set_ylim(0, self.car_count_slider.get())
        self.ax_queue.grid(True)
        (self.queue_line,) = self.ax_queue.plot([], [], "c-", label="Queue")
        self.ax_queue.legend()

        # Set x-axis limits based on total steps
        total_steps = self.steps_slider.get()
        self.ax_density.set_xlim(0, total_steps)
        self.ax_velocity.set_xlim(0, total_steps)
        self.ax_flow.set_xlim(0, total_steps)
        self.ax_queue.set_xlim(0, total_steps)

        self.fig.tight_layout()
        self.canvas.draw()

    def init_metrics_display(self):
        """
        Initialize the metrics display panel.
        """
        self.metrics_frame = tk.Frame(self.control_frame)
        self.metrics_frame.pack(pady=10)

        # Create labels for each metric
        self.metrics_labels = {}
        metrics = [
            "Global Density",
            "Road Density",
            "Intersection Density",
            "Average Velocity",
            "Traffic Flow",
            "Queue Length",
        ]

        for metric in metrics:
            frame = tk.Frame(self.metrics_frame)
            frame.pack(pady=2)

            label = tk.Label(frame, text=f"{metric}:", width=20, anchor="w")
            label.pack(side=tk.LEFT)

            value = tk.Label(frame, text="0", width=10)
            value.pack(side=tk.LEFT)

            self.metrics_labels[metric] = value

    def init_buttons(self):
        """
        Initialize control buttons for the simulation.
        """
        self.start_button = tk.Button(
            self.control_frame,
            text="Start Simulation",
            command=self.start_simulation,
        )
        self.start_button.pack(pady=10)

        self.pause_button = tk.Button(
            self.control_frame,
            text="Pause Simulation",
            command=self.pause_simulation,
        )
        self.pause_button.pack(pady=5)

        self.reset_button = tk.Button(
            self.control_frame,
            text="Reset Simulation",
            command=self.reset_simulation,
        )
        self.reset_button.pack(pady=5)

    def init_sliders(self, control_frame: tk.Frame):
        """
        Initialize the control sliders for the simulation.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the sliders will be placed.
        """
        self.steps_slider = tk.IntVar(value=250)
        assert isinstance(self.steps_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Steps",
            min_val=100,
            max_val=1000,
            variable=self.steps_slider,
        )

        self.frame_rate_slider = tk.IntVar(value=50)
        assert isinstance(self.frame_rate_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Frame Rate",
            min_val=1,
            max_val=400,
            variable=self.frame_rate_slider,
        )

        self.grid_size_slider = tk.IntVar(value=50)
        assert isinstance(self.grid_size_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Grid Size",
            min_val=10,
            max_val=100,
            variable=self.grid_size_slider,
        )

        self.blocks_size_slider = tk.IntVar(value=20)
        assert isinstance(self.blocks_size_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Blocks Size",
            min_val=2,
            max_val=50,
            variable=self.blocks_size_slider,
        )

        self.car_count_slider = tk.IntVar(value=100)
        assert isinstance(self.car_count_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Car Count",
            min_val=1,
            max_val=1250,
            variable=self.car_count_slider,
        )

        self.max_speed_slider = tk.IntVar(value=2)
        assert isinstance(self.max_speed_slider, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Max Speed",
            min_val=MIN_SPEED,
            max_val=MAX_SPEED,
            variable=self.max_speed_slider,
        )

        self.percentage_on_max_speed = tk.IntVar(value=100)
        assert isinstance(self.percentage_on_max_speed, tk.IntVar)
        self.create_slider(
            control_frame,
            label="Percentage on Max Speed",
            min_val=0,
            max_val=100,
            variable=self.percentage_on_max_speed,
        )

    def init_grid(self, grid_size: int, blocks_size: int, max_speed: int) -> Grid:
        """
        Initialize the grid with the given parameters.

        Params:
        -------
        - grid_size (int): The size of the grid.
        - blocks_size (int): The size of the blocks.
        - max_speed (int): The maximum speed of cars on the road.

        Returns:
        --------
        - Grid: The grid object.
        """
        return Grid(
            grid_size=grid_size,
            blocks_size=blocks_size,
            rotary_method=self.rotary_method,
            max_speed=max_speed,
        )

    def start_simulation(self):
        """
        Start the simulation with the given parameters.
        """
        self.restart_simulation_if_needed()
        self.write_header()

        # Reset data arrays
        self.velocity_data = []

        # Read parameters from sliders
        steps = self.steps_slider.get()
        frame_rate = self.frame_rate_slider.get()
        grid_size = self.grid_size_slider.get()
        blocks_size = self.blocks_size_slider.get()
        max_speed = self.max_speed_slider.get()

        self.steps = steps
        self.grid = Grid(
            grid_size=grid_size,
            blocks_size=blocks_size,
            rotary_method=self.rotary_method,
            max_speed=max_speed,
        )
        self.density_tracker = DensityTracker(self.grid)

        # Create cars
        car_count = self.car_count_slider.get()
        car_speed_percentage = self.percentage_on_max_speed.get()
        cars = self.create_cars(self.grid, car_count, car_speed_percentage)
        self.grid.add_cars(cars)
        self.init_data_plot()

        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

        # Start animation
        self.animation = FuncAnimation(
            self.fig,
            self.update_simulation,
            frames=range(steps),
            interval=frame_rate,
            repeat=False,
        )
        self.canvas.draw()

        # Keep a reference to prevent garbage collection
        self._animation_ref = self.animation

    def reset_simulation(self):
        """
        Reset the simulation to its initial state.
        """
        try:
            if self.animation and hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
            if hasattr(self, "_animation_ref"):
                del self._animation_ref
        except Exception:
            pass  # Animation might already be stopped

        # Clear the plot
        if hasattr(self, "ax_grid") and self.ax_grid:
            self.ax_grid.clear()
            self.ax_density.clear()
            self.ax_velocity.clear()
            self.ax_flow.clear()
            self.ax_queue.clear()
            self.ax_grid.set_xticks([])
            self.ax_grid.set_yticks([])

            self.canvas.draw()

        # Reset simulation state
        self.is_paused = False
        self.grid = None
        self.simulation = None
        self.animation = None
        self.density_tracker = None
        self.velocity_data = []

        # Reset button states
        if hasattr(self, "start_button"):
            self.start_button.config(state=tk.NORMAL)
        if hasattr(self, "pause_button"):
            self.pause_button.config(state=tk.NORMAL, text="Pause Simulation")

    def restart_simulation_if_needed(self):
        """
        Restart the simulation if one is already running.
        """
        if self.animation and hasattr(self.animation, "event_source"):
            self.animation.event_source.stop()
            self.ax_grid.clear()
            self.ax_density.clear()
            self.ax_velocity.clear()
            self.ax_flow.clear()
            self.ax_queue.clear()
            self.canvas.draw()

    def pause_simulation(self) -> None:
        """
        Pause or resume the simulation, based on the previous state.

        Returns:
        --------
        - None if no simulation is running.
        """
        if not self.animation:
            print("No simulation running.")
            return

        if not self.is_paused:
            self.is_paused = True
            if hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
            self.pause_button.config(text="Resume Simulation")
            print("Simulation paused.")
        else:
            self.is_paused = False
            if hasattr(self.animation, "event_source"):
                self.animation.event_source.start()
            self.pause_button.config(text="Pause Simulation")
            print("Simulation resumed.")

    def update_simulation(self, frame: int) -> list:
        """
        Update the simulation for each frame.

        Params:
        -------
        - frame (int): The current frame number.

        Returns:
        --------
        - im (matplotlib.image.AxesImage): The grid plot
        - velocity_line (matplotlib.lines.Line2D): The velocity plot
        - road_density_line (matplotlib.lines.Line2D): The road density plot
        - intersection_density_line (matplotlib.lines.Line2D): The intersection density plot
        - flow_line (matplotlib.lines.Line2D): The traffic flow plot
        - queue_line (matplotlib.lines.Line2D): The queue length plot
        """

        if self.is_paused:
            return [
                self.im,
                self.velocity_line,
                self.road_density_line,
                self.intersection_density_line,
                self.flow_line,
                self.queue_line,
            ]

        # Update grid and get metrics
        moved_cars = self.grid.update_movement()
        metrics = self.density_tracker.update(moved_cars)

        # Write metrics to file
        self.write_simulation(frame, metrics)

        # Update metrics display
        metric_mappings = {
            "Global Density": "global_density",
            "Road Density": "road_density",
            "Intersection Density": "intersection_density",
            "Average Velocity": "average_velocity",
            "Traffic Flow": "traffic_flow",
            "Queue Length": "queue_length",
        }

        for display_name, metric_key in metric_mappings.items():
            if display_name in self.metrics_labels and metric_key in metrics:
                if metric_key in [
                    "road_density",
                    "intersection_density",
                    "global_density",
                ]:
                    self.metrics_labels[display_name].config(
                        text=f"{metrics[metric_key] * 100:.1f}%"
                    )
                elif metric_key == "queue_length":
                    self.metrics_labels[display_name].config(
                        text=f"{metrics[metric_key]}"
                    )
                elif metric_key == "traffic_flow":
                    self.metrics_labels[display_name].config(
                        text=f"{metrics[metric_key]:.3f}"
                    )
                elif metric_key == "average_velocity":
                    self.metrics_labels[display_name].config(
                        text=f"{metrics[metric_key]:.2f}"
                    )

        # Update grid title
        title = f"Simulation step {frame + 1}\n"
        title += f"Cars: {metrics['total_cars']}"
        self.ax_grid.set_title(title)

        # Update all plots
        self.step_data.append(frame)
        self.velocity_data.append(metrics["average_velocity"])
        self.road_density_data.append(metrics["road_density"] * 100)
        self.intersection_density_data.append(metrics["intersection_density"] * 100)
        self.flow_data.append(metrics["traffic_flow"])
        self.queue_data.append(metrics["queue_length"])

        # Update plot lines
        self.velocity_line.set_data(self.step_data, self.velocity_data)
        self.road_density_line.set_data(self.step_data, self.road_density_data)
        self.intersection_density_line.set_data(
            self.step_data, self.intersection_density_data
        )
        self.flow_line.set_data(self.step_data, self.flow_data)
        self.queue_line.set_data(self.step_data, self.queue_data)

        # Update grid plot
        self.im.set_array(self.grid.grid)

        title = f"Simulation step {frame + 1}\n"
        title += f"Cars: {metrics['total_cars']}"
        self.ax_grid.set_title(title)

        # Remove all existing text annotations
        for text in self.ax_grid.texts[:]:
            text.remove()

        # Add text annotations for car directions
        for car in self.grid.cars:
            i, j = car.head_position
            car_direction = CAR_DIRECTION[car.road_type]
            self.ax_grid.text(
                j,
                i,
                car_direction,
                ha="center",
                va="center",
                fontsize=10,
                color="white",
            )

        self.canvas.draw()

        # Save plots at the end of simulation
        if frame == self.steps - 1:
            self.save_plots()
            print("Yo")
            G = self.grid.jammed_network()
            plt.figure(figsize=(6, 6))  # Set figure size
            pos = {
                node: node for node in G.nodes()
            }  # Use node positions as coordinates
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                edge_color="gray",
                node_size=700,
                font_size=12,
            )

            plt.show()

        return [
            self.im,
            self.velocity_line,
            self.road_density_line,
            self.intersection_density_line,
            self.flow_line,
            self.queue_line,
        ]

    def save_plots(self):
        """
        Save all plots to files in the data directory.
        """
        # Create a new figure for saving
        save_fig = plt.Figure(figsize=(12, 12))

        # Density plot
        ax1 = save_fig.add_subplot(411)
        ax1.plot(self.step_data, self.road_density_data, "b-", label="Road")
        ax1.plot(
            self.step_data, self.intersection_density_data, "r-", label="Intersection"
        )
        ax1.set_xlabel("Steps")
        ax1.set_ylabel("Density (%)")
        ax1.grid(True)
        ax1.legend()

        # Velocity plot
        ax2 = save_fig.add_subplot(412)
        ax2.plot(self.step_data, self.velocity_data, "g-", label="Velocity")
        ax2.set_xlabel("Steps")
        ax2.set_ylabel("Average Velocity")
        ax2.grid(True)
        ax2.legend()

        # Traffic flow plot
        ax3 = save_fig.add_subplot(413)
        ax3.plot(self.step_data, self.flow_data, "m-", label="Flow")
        ax3.set_xlabel("Steps")
        ax3.set_ylabel("Traffic Flow")
        ax3.grid(True)
        ax3.legend()

        # Queue plot
        ax4 = save_fig.add_subplot(414)
        ax4.plot(self.step_data, self.queue_data, "c-", label="Queue")
        ax4.set_xlabel("Steps")
        ax4.set_ylabel("Queue Length")
        ax4.grid(True)
        ax4.legend()

        save_fig.tight_layout()
        save_fig.savefig("data/metrics_plots.png")

        # Save the grid state
        grid_fig = plt.Figure(figsize=(8, 8))
        ax_grid = grid_fig.add_subplot(111)
        ax_grid.imshow(self.grid.grid, cmap="Greys" if self.colour_blind else "rainbow")
        ax_grid.set_title(f"Final Grid State\nTotal Cars: {len(self.grid.cars)}")
        grid_fig.savefig("data/final_grid_state.png")

    def write_header(self):
        """
        Write the header to the simulation output file.
        """
        with open(f"data/simulation.{FILE_EXTENSION}", "w") as f:
            f.write(
                "Step; Grid_State; Road_Density; Intersection_Density; Global_Density; "
                "Average_Velocity; Traffic_Flow; Queue_Length; Total_Cars\n"
            )

    def write_simulation(self, step: int, metrics: dict):
        """
        Write the current simulation step to the output file.

        Params:
        -------
        - step (int): The current step number in the simulation.
        - metrics (dict): Dictionary containing all metrics
        """
        grid_state = str(self.grid.grid.tolist())

        with open(f"data/simulation.{FILE_EXTENSION}", "a") as f:
            f.write(
                f"{step}; {grid_state}; "
                f"{metrics['road_density']}; {metrics['intersection_density']}; {metrics['global_density']}; "
                f"{metrics['average_velocity']}; {metrics['traffic_flow']}; {metrics['queue_length']}; "
                f"{metrics['total_cars']}\n"
            )
