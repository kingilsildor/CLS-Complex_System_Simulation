import tkinter as tk
from abc import ABC

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.density import DensityTracker
from src.grid import Grid
from src.utils import ROAD_CELLS


class Simulation(ABC):
    def __init__(self, root: tk.Tk, seed: int = 42):
        self.root = root
        np.random.seed(seed)

    def start_simulation(self):
        pass

    def pause_simulation(self):
        pass

    def stop_simulation(self):
        pass

    def restart_simulation(self):
        pass

    def update_simulation(self):
        pass

    def create_plot(self, figsize: tuple = (12, 12), dpi: int = 300):
        fig = plt.Figure(figsize=figsize, dpi=dpi)
        assert isinstance(fig, plt.Figure)

        return fig

    def create_axis(
        self, figure: plt.Figure, nrows: int = 1, ncols: int = 1, index: int = 1
    ):
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

    def create_canvas(self, figure, plot_frame, side: str = tk.TOP):
        """
        Create a canvas widget.

        Params:
        -------
        - figure: The figure to be displayed on the canvas.
        - plot_frame: The frame in which the canvas will be placed.
        - side: The side of the frame where the canvas will be placed.

        Returns:
        --------
        - tk.Canvas: The canvas widget.
        """
        canvas = FigureCanvasTkAgg(figure, plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        assert isinstance(canvas, FigureCanvasTkAgg)

        return canvas

    def create_button(
        self, control_frame: tk.Frame, text: str, command: callable, pady: int = 5
    ):
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
        default_val: int | float,
        min_val: int | float,
        max_val: int | float,
        pady: int = 5,
    ):
        """
        Create a slider widget with a given label.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the slider will be placed.
        - label (str): The label of the slider.
        - default_val (int | float): The default value of the slider.
        - min_val (int | float): The minimum value of the slider.
        - max_val (int | float): The maximum value of the slider.
        - pady (int): The padding of the frame. Default is 5.

        Returns:
        --------
        - tk.Scale: The slider widget.
        """
        if (isinstance(min_val, int) and isinstance(max_val, float)) or (
            isinstance(min_val, float) and isinstance(max_val, int)
        ):
            raise ValueError("min_val and max_val must be of the same type")
        if isinstance(min_val, int) and not isinstance(default_val, int):
            raise ValueError("default_val must be an integer")
        if isinstance(min_val, float) and not isinstance(default_val, float):
            raise ValueError("default_val must be a float")

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
        )
        slider.set(default_val)
        slider.pack(side=tk.RIGHT)
        assert isinstance(slider, tk.Scale)

        return slider

    def init_metric(self):
        pass

    def save_plot(self):
        pass


class Simulation_1D(Simulation):
    def __init__(self):
        pass


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
    ):
        super().__init__(root)
        self.grid = Grid(grid_size, road_length)
        self.max_iter = max_iter
        self.grid_size = grid_size
        self.road_length = road_length
        self.road_max_speed = road_max_speed
        self.car_count = car_count
        self.car_percentage_max_speed = car_percentage_max_speed

    def create_cars(self, grid: Grid, car_count: int, car_percentage_max_speed: int):
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

    def start_simulation(self):
        """
        Start the simulation by creating cars and updating the grid at each step.
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

        print("\033[1;36m=== Traffic Simulation ===")
        print(
            f"Grid: {grid_size}x{grid_size} | Cars: {car_count} | Steps: {steps}\033[0m\n"
        )

        for step in range(self.max_iter):
            moved_cars = self.grid.update_movement()
            metrics = density_tracter.update(moved_cars)

            total_velocity += metrics["average_velocity"]
            total_road_density += metrics["road_density"]
            total_intersection_density += metrics["intersection_density"]

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

            new_grid = self.grid.grid.copy()
            assert isinstance(new_grid, np.ndarray)
            self.grid_states[step] = new_grid
            print("-------------------")

    def data_write(self):
        pass

    def get_grid_states(self):
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
