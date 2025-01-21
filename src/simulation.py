import tkinter as tk

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.grid import Grid
from src.density import DensityTracker
from src.utils import (
    FILE_EXTENSION,
    HORIZONTAL_ROAD_VALUE,
    VERTICAL_ROAD_VALUE,
    CAR_VALUE,
    INTERSECTION_VALUE,
)

matplotlib.use("TkAgg")


class SimulationUI:
    def __init__(
        self,
        master: tk.Tk,
        show_ui: bool = True,
        colour_blind: bool = False,
        drive_on_right: bool = True,
    ):
        """
        Initialize the simulation UI for controlling and visualizing the car traffic simulation.

        Params:
        -------
        master (tk.Tk): The root window for the Tkinter application.
        show_ui (bool): Flag to show the UI. Default is True.
        colour_blind (bool): Flag to use a colour-blind friendly colour map. Default is False.
        drive_on_right (bool): If True, cars drive on the right side. If False, left side.
        """
        self.show_ui = show_ui
        self.master = master
        self.is_paused = False
        self.steps = 0
        self.colour_blind = colour_blind
        self.drive_on_right = drive_on_right
        self.density_tracker = None

        def init_sliders():
            """
            Initialize the sliders for the simulation parameters.
            When adding new sliders, update the `init_sliders` method accordingly.
            """
            self.steps_slider = self.create_slider(
                "Steps", default_val=250, min_val=50, max_val=1000
            )

            self.frame_rate_slider = self.create_slider(
                "Frame Rate", default_val=40, min_val=1, max_val=500
            )

            self.grid_size_slider = self.create_slider(
                "Grid Size", default_val=52, min_val=10, max_val=100
            )

            self.blocks_size_slider = self.create_slider(
                "Blocks Size", default_val=10, min_val=2, max_val=50
            )

            self.lane_width_slider = self.create_slider(
                "Lane Width", default_val=2, min_val=2, max_val=30
            )

            self.car_count_slider = self.create_slider(
                "Car Count", default_val=100, min_val=1, max_val=1250
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

            self.reset_button = tk.Button(
                self.controls_frame,
                text="Reset Simulation",
                command=self.reset_simulation,
            )
            self.reset_button.pack(pady=5)

            self.fig, self.ax = plt.subplots(figsize=(6, 6))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
            self.canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10)

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
        if self.animation and hasattr(self.animation, "event_source"):
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
        self.density_tracker = DensityTracker(self.grid)

        car_count = self.car_count_slider.get()
        cars = self.create_cars(car_count, self.drive_on_right)
        self.grid.add_cars(cars)

        # Update button states
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

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
        density_metrics = self.density_tracker.calculate_overall_density()
        self.write_simulation(frame, density_metrics)

        self.ax.clear()
        if self.colour_blind:
            self.ax.imshow(self.grid.grid, cmap="Greys", interpolation="nearest")
        else:
            self.ax.imshow(self.grid.grid, cmap="viridis", interpolation="nearest")

        # Update title with all density metrics
        title = f"Simulation step {frame + 1}\n"
        title += f"System: {density_metrics['system_density']*100:.1f}% | "
        title += f"Roads: {density_metrics['road_density']*100:.1f}% | "
        title += f"Inter: {density_metrics['intersection_density']*100:.1f}%"
        self.ax.set_title(title)

        self.canvas.draw()

    def pause_simulation(self):
        """
        Pause or resume the simulation.
        """
        if not self.animation:
            print("\033[1;31mNo simulation running.\033[0m")
            return

        if not self.is_paused:
            self.is_paused = True
            if hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
            self.pause_button.config(text="Resume Simulation")
            print("\033[1;33mSimulation paused.\033[0m")
        else:
            self.is_paused = False
            if hasattr(self.animation, "event_source"):
                self.animation.event_source.start()
            self.pause_button.config(text="Pause Simulation")
            print("\033[1;33mSimulation resumed.\033[0m")

    def create_cars(self, car_count: int, drive_on_right: bool = True) -> list[Car]:
        """
        Create a list of cars with positions and directions based on traffic rules.
        Cars will drive on the right side by default. Cars will only spawn on regular road cells,
        not on intersections or rotaries. For vertical roads, right lane goes up and left lane
        goes down. For horizontal roads, upper lane goes right and lower lane goes left.

        Params:
        -------
        car_count (int): Number of cars to create
        drive_on_right (bool): If True, cars drive on the right side. If False, left side.
        """
        cars = []
        created_positions = set()

        # Get all valid positions and their directions based on road position
        valid_positions = []
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                cell = self.grid.grid[x, y]
                if cell == VERTICAL_ROAD_VALUE:
                    # For vertical roads:
                    # Right lane (higher y) goes North, Left lane goes South
                    lane_index = y % (
                        self.grid.lane_width * 2
                    )  # Position within the road
                    if drive_on_right:
                        # Right side of road (higher y) goes up
                        direction = "N" if lane_index >= self.grid.lane_width else "S"
                    else:
                        # Left side of road (lower y) goes up
                        direction = "S" if lane_index >= self.grid.lane_width else "N"
                    valid_positions.append((x, y, [direction]))

                elif cell == HORIZONTAL_ROAD_VALUE:
                    # For horizontal roads:
                    # Upper lane (lower x) goes East, Lower lane goes West
                    lane_index = x % (
                        self.grid.lane_width * 2
                    )  # Position within the road
                    if drive_on_right:
                        # Upper part of road (lower x) goes right
                        direction = "E" if lane_index < self.grid.lane_width else "W"
                    else:
                        # Upper part of road (lower x) goes left
                        direction = "W" if lane_index < self.grid.lane_width else "E"
                    valid_positions.append((x, y, [direction]))

        # Shuffle valid positions
        np.random.shuffle(valid_positions)

        # Place cars up to either car_count or available positions
        actual_count = min(car_count, len(valid_positions))

        print("\033[1;36mPlacing cars:")
        print(f"Requested cars: {car_count}")
        print(f"Available positions: {len(valid_positions)}")
        print(f"Cars to be placed: {actual_count}\033[0m")

        for i in range(actual_count):
            x, y, valid_directions = valid_positions[i]
            direction = valid_directions[0]  # Only one valid direction per position now

            # Skip if position is already occupied or is an intersection
            if (
                self.grid.grid[x, y] == CAR_VALUE
                or self.grid.grid[x, y] == INTERSECTION_VALUE
            ):
                print(f"\033[1;31mWarning: Position ({x}, {y}) is not available\033[0m")
                continue

            # Create and verify car
            car = Car(self.grid, position=(x, y), direction=direction)
            if self.grid.grid[x, y] != CAR_VALUE:
                print(
                    f"\033[1;31mWarning: Car not placed at ({x}, {y}). Cell value: {self.grid.grid[x, y]}\033[0m"
                )
                continue

            cars.append(car)
            created_positions.add((x, y))

        # Verify final state
        car_positions = np.where(self.grid.grid == CAR_VALUE)
        actual_cars = len(car_positions[0])
        print("\033[1;32mCar placement complete:")
        print(f"Cars placed: {len(created_positions)}")
        print(f"Cars in grid: {actual_cars}\033[0m")

        return cars

    def run_simulation_without_ui(
        self, steps=100, grid_size=25, blocks_size=5, lane_width=2, car_count=100
    ):
        """
        Run the simulation without UI for a specified number of steps.
        """
        print("\033[1;36m=== Traffic Simulation ===")
        print(
            f"Grid: {grid_size}x{grid_size} | Cars: {car_count} | Steps: {steps}\033[0m\n"
        )

        # Initialize grid and density tracker
        self.grid = Grid(grid_size, blocks_size, lane_width)
        self.density_tracker = DensityTracker(self.grid)

        # Place cars
        cars = self.create_cars(car_count, self.drive_on_right)
        self.grid.add_cars(cars)

        # Run simulation steps
        grid_states = []
        for step in range(steps):
            density = self.density_tracker.calculate_overall_density()
            print(f"\033[1;33mStep {step+1:4d}/{steps:d}\033[0m", end=" ")
            print(
                f"\033[1;32mSystem: {density['system_density']*100:4.1f}%\033[0m",
                end=" ",
            )
            print(
                f"\033[1;34mRoads: {density['road_density']*100:4.1f}%\033[0m", end=" "
            )
            print(
                f"\033[1;35mInter: {density['intersection_density']*100:4.1f}%\033[0m",
                end=" ",
            )
            print(f"\033[1;36mCars: {density['total_cars']:3d}\033[0m")

            grid_states.append(self.grid.grid.copy())
            self.grid.update_movement()

        # Final state
        density = self.density_tracker.calculate_overall_density()
        print(f"\033[1;33mStep {steps:4d}/{steps:d}\033[0m", end=" ")
        print(
            f"\033[1;32mSystem: {density['system_density']*100:4.1f}%\033[0m", end=" "
        )
        print(f"\033[1;34mRoads: {density['road_density']*100:4.1f}%\033[0m", end=" ")
        print(
            f"\033[1;35mInter: {density['intersection_density']*100:4.1f}%\033[0m",
            end=" ",
        )
        print(f"\033[1;36mCars: {density['total_cars']:3d}\033[0m")

        return grid_states

    def write_header(self):
        """
        Write the header to the simulation output file.
        """
        with open(f"data/simulation.{FILE_EXTENSION}", "w") as f:
            f.write(
                "Step; Grid_State; Road_Density; Intersection_Density; Total_Cars\n"
            )

    def write_simulation(self, step: int, density_metrics: dict):
        """
        Write the current simulation step to the output file.

        Params:
        -------
        step (int): The current step number in the simulation.
        density_metrics (dict): Dictionary containing density measurements
        """
        grid_state = str(self.grid.grid.tolist())

        with open(f"data/simulation.{FILE_EXTENSION}", "a") as f:
            f.write(
                f"{step}; {grid_state}; {density_metrics['road_density']}; {density_metrics['intersection_density']}; {density_metrics['total_cars']}\n"
            )

    def reset_simulation(self):
        """
        Reset the simulation to its initial state.
        """
        try:
            if self.animation and hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
        except Exception:
            pass  # Animation might already be stopped

        # Clear the plot
        if hasattr(self, "ax") and self.ax:
            self.ax.clear()
            self.ax.set_title("Simulation Reset")
            self.canvas.draw()

        # Reset simulation state
        self.is_paused = False
        self.grid = None
        self.simulation = None
        self.animation = None
        self.density_tracker = None

        # Reset button states
        if hasattr(self, "start_button"):
            self.start_button.config(state=tk.NORMAL)
        if hasattr(self, "pause_button"):
            self.pause_button.config(state=tk.NORMAL, text="Pause Simulation")

        print("\033[1;33mSimulation reset.\033[0m")
