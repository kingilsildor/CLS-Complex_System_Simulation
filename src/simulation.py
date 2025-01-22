import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.grid import Grid
from src.utils import (
    FILE_EXTENSION,
    HORIZONTAL_ROAD_VALUE,
    INTERSECTION_VALUE,
    VERTICAL_ROAD_VALUE,
)

plt.ion()


class SimulationUI:
    def __init__(self, master: tk.Tk, show_ui: bool = True, colour_blind: bool = False):
        """
        Initialize the simulation UI for controlling and visualizing the car traffic simulation.

        Params:
        -------
        master (tk.Tk): The root window for the Tkinter application.
        show_ui (bool): Flag to show the UI. Default is True.
        colour_blind (bool): Flag to use a colour-blind friendly colour map. Default is False.
        """
        self.show_ui = show_ui
        self.master = master
        self.is_paused = False
        self.steps = 0
        self.colour_blind = colour_blind

        def init_sliders():
            """
            Initialize the sliders for the simulation parameters.
            When adding new sliders, update the `init_sliders` method accordingly.
            """
            self.steps_slider = self.create_slider(
                "Steps", default_val=100, min_val=50, max_val=1000
            )

            self.frame_rate_slider = self.create_slider(
                "Frame Rate", default_val=40, min_val=1, max_val=500
            )

            self.grid_size_slider = self.create_slider(
                "Grid Size", default_val=60, min_val=10, max_val=100
            )

            self.blocks_size_slider = self.create_slider(
                "Blocks Size", default_val=10, min_val=2, max_val=50
            )

            self.lane_width_slider = self.create_slider(
                "Lane Width", default_val=2, min_val=2, max_val=30
            )

            self.car_count_slider = self.create_slider(
                "Car Count", default_val=10, min_val=1, max_val=1250
            )

        if self.show_ui:
            self.master.title("Car Traffic in a 2D street network.")
            self.controls_frame = tk.Frame(self.master)
            self.controls_frame.pack(side=tk.LEFT, padx=10)
            init_sliders()

            self.start_button = tk.Button(
                self.controls_frame,
                text="Start Simulation",
                command=self.start_simulation,
            )
            self.start_button.pack(pady=10)

            self.pause_button = tk.Button(
                self.controls_frame,
                text="Pause Simulation",
                command=self.pause_simulation,
            )
            self.pause_button.pack(pady=5)

            self.fig, self.ax = plt.subplots(figsize=(6, 6))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
            self.canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10)
            plt.ioff()
        else:
            print("\033[38;5;46mRunning simulation without UI.\033[0m")
            pass

        self.grid = None
        self.simulation = None
        self.animation = None

    def create_slider(
        self,
        label: str,
        default_val: int | float,
        min_val: int | float,
        max_val: int | float,
    ) -> tk.Scale:
        """
        Create a slider widget with a label.

        Params:
        -------
        label (str): The label for the slider.
        min_val (int | float): The minimum value of the slider.
        max_val (int | float): The maximum value of the slider.
        default_val (int | float): The default value of the slider.
        Returns:
        --------
        tk.Scale: The created slider widget.
        """
        # Check if min and max values are of the same type
        if (isinstance(min_val, int) and isinstance(max_val, float)) or (
            isinstance(min_val, float) and isinstance(max_val, int)
        ):
            raise ValueError(
                "\033[31mMin and max values must be of the same type.\033[0m"
            )

        # Check if the default value is of the same type as min and max values, and convert if not
        if isinstance(min_val, int) and not isinstance(default_val, int):
            default_val = int(default_val)
            raise ValueError("\033[38;5;214mDefault value is set to an integer.\033[0m")
        if (
            isinstance(min_val, float) or isinstance(max_val, float)
        ) and not isinstance(default_val, float):
            default_val = float(default_val)
            raise ValueError("\033[38;5;214mDefault value is set to a float.\033[0m")

        frame = tk.Frame(self.controls_frame)
        frame.pack(pady=5)

        label_widget = tk.Label(frame, text=label)
        label_widget.pack(side=tk.LEFT)

        slider = tk.Scale(
            frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200
        )
        slider.set(default_val)
        slider.pack(side=tk.RIGHT)

        assert isinstance(slider, tk.Scale)
        return slider

    def start_simulation(self):
        """
        Start the simulation based on the parameters from the UI sliders.

        If a simulation is already running, it restarts the simulation.
        """
        # Restart the simulation
        if self.animation:
            self.animation.event_source.stop()
            self.ax.clear()
            self.canvas.draw()

        self.write_header()
        steps = self.steps_slider.get()
        frame_rate = self.frame_rate_slider.get()

        grid_size = self.grid_size_slider.get()
        blocks_size = self.blocks_size_slider.get()
        lane_width = self.lane_width_slider.get()

        self.steps = 0
        self.grid = Grid(
            grid_size=grid_size, blocks_size=blocks_size, lane_width=lane_width
        )

        car_count = self.car_count_slider.get()
        cars = self.create_cars(car_count)
        self.grid.add_cars(cars)

        self.animation = FuncAnimation(
            self.fig,
            self.update_simulation,
            frames=range(steps),
            interval=frame_rate,
            repeat=False,
        )
        self.canvas.draw()

    def update_simulation(self, frame: int):
        """
        Update the simulation for the given frame.

        Params:
        -------
        frame (int): The current frame number in the simulation.
        """
        if self.is_paused:
            return

        self.grid.update_movement()
        self.write_simulation(frame)

        self.ax.clear()
        if self.colour_blind:
            self.ax.imshow(self.grid.grid, cmap="Greys", interpolation="nearest")
        else:
            self.ax.imshow(self.grid.grid, cmap="viridis", interpolation="nearest")
        self.ax.set_title(f"Simulation step {frame + 1}")

        self.canvas.draw()

    def pause_simulation(self):
        """
        Pause or resume the simulation.
        """
        if self.animation and not self.is_paused:
            self.is_paused = True
            self.animation.event_source.stop()
            print("\033[32mSimulation paused.\033[0m")

        elif self.animation and self.is_paused:
            self.is_paused = False
            self.animation.event_source.start()
            print("\033[32mSimulation resumed.\033[0m")

        elif not self.animation:
            raise RuntimeError("\033[38;5;214mNo simulation running.\033[0m")

    def create_cars(self, car_count: int) -> list[Car]:
        """
        Create a list of cars with random positions and directions.

        Params:
        -------
        car_count (int): The number of cars to create.

        Returns:
        --------
        list[Car]: A list of `Car` objects with random positions and directions.
        """

        cars = np.zeros(car_count, dtype=object)
        for i in range(car_count):
            while self.grid.grid[
                x := np.random.randint(0, self.grid.size),
                y := np.random.randint(0, self.grid.size),
            ] not in [VERTICAL_ROAD_VALUE, HORIZONTAL_ROAD_VALUE, INTERSECTION_VALUE]:
                pass

            direction = np.random.choice(["N", "S", "E", "W"])
            cars[i] = Car(self.grid, position=(x, y), direction=direction)
        print(f"\033[38;5;46mCreated {car_count} cars.\033[0m")
        return cars

    def run_simulation_without_ui(
        self,
        steps: int,
        grid_size: int,
        blocks_size: int,
        lane_width: int,
        car_count: int,
    ):
        """
        Run the simulation without displaying the UI and return the grid states.

        Params:
        -------
        steps (int): The number of steps to run the simulation.
        grid_size (int): The size of the grid (NxN).
        blocks_size (int): The size of blocks between roads.
        lane_width (int): The width of the lanes.
        car_count (int): The number of cars to simulate.
        """
        self.grid = Grid(
            grid_size=grid_size, blocks_size=blocks_size, lane_width=lane_width
        )

        cars = self.create_cars(car_count)
        self.grid.add_cars(cars)

        self.write_header()
        for step in range(steps):
            self.grid.update_movement()
            self.write_simulation(step)

    def write_header(self):
        """
        Write the header to the simulation output file.
        """
        with open(f"data/simulation.{FILE_EXTENSION}", "w") as f:
            f.write("Step; Grid_State\n")

    def write_simulation(self, step: int):
        """
        Write the current simulation step to the output file.

        Params:
        -------
        step (int): The current step number in the simulation.
        """
        grid_state = str(self.grid.grid.tolist())

        with open(f"data/simulation.{FILE_EXTENSION}", "a") as f:
            f.write(f"{step}; {grid_state}\n")
