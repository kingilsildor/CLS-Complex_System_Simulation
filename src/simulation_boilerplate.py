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
    def __init__(self, root: tk.Tk, seed: int = 42):
        # Create the root window
        root = self.create_screen(root, "Nagel-Schreckenberg Simulation", "1600x800")
        super().__init__(root, seed)

        control_frame = self.create_frames(root, 0, 0, tk.NS)
        output_frame = self.create_frames(root, 0, 2, tk.NSEW)

        # Initialize a canvas for the plot
        plot_canvas = tk.Canvas(self.root)
        plot_canvas.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Add a scrollbar to the plot canvas
        plot_scrollbar = tk.Scrollbar(
            self.root, orient=tk.VERTICAL, command=plot_canvas.yview
        )
        plot_scrollbar.grid(row=0, column=3, sticky="ns")

        plot_frame = self.create_frames(plot_canvas, 0, 1, tk.NSEW)
        plot_canvas.create_window((0, 0), window=plot_frame, anchor="nw")

        # Enable scrolling for the plot canvas
        def _on_frame_configure(event):
            """
            Configure the plot canvas to scroll.
            """
            plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

        plot_frame.bind("<Configure>", _on_frame_configure)

        def _on_mouse_wheel(event):
            plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        plot_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        self.text_widget = scrolledtext.ScrolledText(
            output_frame, font=("Courier", 12), wrap=tk.NONE
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        h_scrollbar = tk.Scrollbar(
            output_frame, orient=tk.HORIZONTAL, command=self.text_widget.xview
        )
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget.config(xscrollcommand=h_scrollbar.set)

        # Config root window
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.init_sliders(control_frame)
        self.init_metrics()
        self.init_plots(plot_frame)

        self.init_buttons(control_frame)
        self.initialize_model()

        root.protocol("WM_DELETE_WINDOW", self.close_simulation)
        root.mainloop()

    def init_sliders(self, control_frame: tk.Frame):
        """
        Initialize the sliders for the simulation.
        """
        self.road_length_slider = tk.IntVar(value=100)
        self.create_slider(
            control_frame,
            label="Length of the Road",
            min_val=10,
            max_val=200,
            variable=self.road_length_slider,
        )

        self.car_count_slider = tk.IntVar(value=10)
        self.create_slider(
            control_frame,
            label="Number of Cars",
            min_val=1,
            max_val=200,
            variable=self.car_count_slider,
        )

        self.max_speed_slider = tk.IntVar(value=10)
        self.create_slider(
            control_frame,
            label="Maximum Speed of Cars",
            min_val=1,
            max_val=5,
            variable=self.max_speed_slider,
        )

        self.time_steps_slider = tk.IntVar(value=100)
        self.create_slider(
            control_frame,
            label="Number of Time Steps",
            min_val=10,
            max_val=200,
            variable=self.time_steps_slider,
        )

    def init_buttons(self, control_frame: tk.Frame):
        """
        Initialize the buttons for the simulation.
        """
        self.create_button(control_frame, "Start", self.start_simulation)
        self.create_button(control_frame, "Stop", self.stop_simulation)
        self.create_button(control_frame, "Restart", self.restart_simulation)
        self.create_button(control_frame, "Save Plots", self.save_simulation)

        self.randomization = tk.BooleanVar(value=True)
        randomization_checkbutton = tk.Checkbutton(
            control_frame,
            text="Randomization",
            variable=self.randomization,
            command=lambda: print(f"Randomization set to {self.randomization.get()}"),
        )
        randomization_checkbutton.pack(pady=5)

    def init_metrics(self):
        """
        Initialize the metrics for the simulation.
        """
        self.step_counter = 0
        self.running = False
        self.model = None

        time_steps = self.time_steps_slider.get()
        self.output_lines = np.zeros(time_steps, dtype=str)
        self.speed_data = np.zeros(time_steps, dtype=float)
        self.density_data = np.zeros(time_steps, dtype=float)
        self.flow_data = np.zeros(time_steps, dtype=float)
        self.time_space_data = np.zeros(
            (time_steps, self.road_length_slider.get()), dtype=int
        )

    def init_plots(self, frame: tk.Frame):
        self.speed_animation = self.create_plot(
            frame,
            title="Density vs Average Speed",
            format_string="bo",
            xlabel="Density (cars per cell)",
            ylabel="Average Speed (cells per time step)",
            xlim=(0, 1),
            ylim=(0, self.max_speed_slider.get()),
        )

        self.flow_animation = self.create_plot(
            frame,
            title="Density vs Flow",
            format_string="ro",
            xlabel="Density (cars per cell)",
            ylabel="Flow (cars per time step)",
            xlim=(0, 1),
            ylim=(0, self.max_speed_slider.get()),
        )

        def update_time_space_plot(frame, line):
            """
            Update the time-space plot with the given data.
            """
            x_data = []
            y_data = []
            for t, positions in enumerate(self.time_space_data):
                x_data.extend(positions)
                y_data.extend([t] * len(positions))
            line.set_data(x_data, y_data)
            return (line,)

        # self.time_space_animation = self.create_plot(
        #     "Time-Space Diagram",
        #     "k0.",
        #     "Position",
        #     "Time",
        #     frame,
        #     update_time_space_plot,
        # )
        # TODO

    def create_plot(
        self,
        frame: tk.Frame,
        title: str,
        format_string: str,
        xlabel: str,
        ylabel: str,
        xlim: tuple = (0, 1),
        ylim: tuple = (0, 1),
        update_func=None,
        kwargs: dict = {},
    ) -> FuncAnimation:
        """
        Create a plot with given parameters.

        Params:
        -------
        - title (str): The title of the plot.
        - format_string (str): The format string for the plot.
        - xlabel (str): The label of the x-axis.
        - ylabel (str): The label of the y-axis.
        - frame (tk.Frame): The frame in which the plot will be placed.
        - update_func (callable): The function that will be called to update the plot. Default is None.
        - kwargs (dict): The keyword arguments for the plot. Default is {}.

        Returns:
        --------
        - FuncAnimation: The animation of the plot.
        """
        fig, ax = plt.subplots()
        (line,) = ax.plot([], [], format_string)

        assert isinstance(xlim, tuple) and len(xlim) == 2
        ax.set_xlim(*xlim)
        assert isinstance(ylim, tuple) and len(ylim) == 2
        ax.set_ylim(*ylim)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        self.create_canvas(fig, frame)

        def _init():
            """
            Initialize the plot.
            """
            line.set_data([], [])
            return (line,)

        def _update_plot(frame):
            """
            Update the plot with the given data.
            """
            line.set_data(self.density_data, self.speed_data)
            return (line,)

        if update_func is None:
            update_func = _update_plot
        else:
            assert callable(update_func)

        animation = FuncAnimation(
            fig,
            update_func,
            init_func=_init,
            blit=True,
            frames=self.time_steps_slider.get(),
            **kwargs,
        )

        assert isinstance(animation, FuncAnimation)
        return animation

    def save_simulation(self):
        """
        Save the simulation data to img files.
        """
        # TODO time-space diagram

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if file_path:
            self.speed_animation.save(f"{file_path}_density_vs_speed.png")
            self.flow_animation.save(f"{file_path}_density_vs_flow.png")
            self.time_space_animation.save(f"{file_path}_time_space_diagram.png")
            messagebox.showinfo("Save Plots", "Plots saved successfully!")
            return
        else:
            raise ValueError("File path not provided")

    def start_simulation(self):
        """
        Start the simulation by initializing the model and updating the plots.
        """
        if self.car_count_slider.get() > self.road_length_slider.get():
            raise ValueError(
                "Number of cars cannot be greater than the length of the road"
            )
        if not self.running:
            self.running = True
            self.initialize_model()
            self.update_simulation()
            print("Simulation started")
        else:
            print("Simulation is already running")

    def stop_simulation(self):
        """
        Stop the simulation.
        """
        if not self.running:
            print("Simulation is not running")
            return
        self.running = False
        print("Simulation stopped")

    def restart_simulation(self):
        """
        Restart the simulation by stopping it and resetting the step counter and output lines.
        """
        self.stop_simulation()
        self.step_counter = 0
        self.output_lines.clear()
        self.text_widget.delete(1.0, tk.END)

        self.time_space_data.clear()

        self.initialize_model()
        print("Simulation restarted")

    def update_simulation(self):
        """
        Update the simulation by updating the model and visualizing the output.
        """
        step_counter = self.step_counter
        max_time_steps = self.time_steps_slider.get()

        if self.running and step_counter < max_time_steps:
            self.model.update()
            self.output_lines[step_counter] = self.model.visualize()
            self.text_widget.insert(tk.END, self.model.visualize() + "\n")
            self.text_widget.see(tk.END)

            avg_speed = self.model.total_speed / self.car_count_slider.get()
            assert isinstance(avg_speed, float)
            self.speed_data[step_counter] = avg_speed

            density = self.car_count_slider.get() / self.road_length_slider.get()
            assert isinstance(density, float)
            self.density_data[step_counter] = density

            flow = self.model.flow / self.road_length_slider.get()
            assert isinstance(flow, float)
            self.flow_data[step_counter] = flow

            positions = [i for i, x in enumerate(self.model.road) if x == 1]
            assert isinstance(positions, list)
            # self.time_space_data[step_counter] = positions

            self.step_counter += 1
            self.root.after(100, self.update_simulation)
        elif step_counter >= max_time_steps:
            print("Simulation completed")
        else:
            print("Simulation is not running")

    def close_simulation(self):
        """
        Close the simulation by stopping the simulation and closing the root window.
        """
        self.stop_simulation()
        self.speed_animation.event_source.stop()
        self.flow_animation.event_source.stop()
        # self.time_space_animation.event_source.stop()

        self.root.quit()
        self.root.destroy()
        print("Simulation closed")

    def initialize_model(self):
        """
        Initialize the model with the given parameters.
        """
        # assert self.model is not None

        length = self.road_length_slider.get()
        num_cars = self.car_count_slider.get()
        max_speed = self.max_speed_slider.get()
        print(
            f"Initializing model with length={length}, num_cars={num_cars}, max_speed={max_speed}"
        )
        self.model = NagelSchreckenberg(length, num_cars, max_speed)


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
