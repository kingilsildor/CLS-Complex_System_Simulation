import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.car import Car
from src.density import DensityTracker
from src.grid import Grid
from src.utils import (
    FILE_EXTENSION,
    ROAD_CELLS,
)


class SimulationUI:
    def __init__(
        self,
        master: tk.Tk,
        show_ui: bool = True,
        colour_blind: bool = True,
        drive_on_right: bool = True,
    ):
        """
        Initialize the simulation UI for controlling and visualizing the car traffic simulation.

        Params:
        -------
        - master (tk.Tk): The root window for the Tkinter application.
        - show_ui (bool): Flag to show the UI. Default is True.
        - colour_blind (bool): Flag to use a colour-blind friendly colour map. Default is False.
        - drive_on_right (bool): If True, cars drive on the right side. If False, left side.
        """
        self.show_ui = show_ui
        self.master = master
        self.is_paused = False
        self.steps = 0
        self.colour_blind = colour_blind
        self.density_tracker = None
        self.grid = None
        self.simulation = None
        self.animation = None

        def _init_plot():
            """Initialize the matplotlib plot"""
            self.fig = plt.Figure(figsize=(6, 6))
            self.ax = self.fig.add_subplot(111)

            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.get_tk_widget().pack()
            assert isinstance(self.canvas, FigureCanvasTkAgg)

            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.fig.tight_layout()
            self.fig.subplots_adjust(top=0.85)

            title = "Welcome to SimCity 2000"
            self.ax.set_title(title)

            self.canvas.draw()

        def _init_metrics_display():
            """Initialize the metrics display panel"""
            self.metrics_frame = tk.Frame(self.controls_frame)
            self.metrics_frame.pack(pady=10)

            # Create labels for each metric
            self.metrics_labels = {}
            metrics = [
                "Moving Cars",
                "Total Cars",
                "Average Wait",
                "Max Wait",
                "Congestion Rate",
                "Cars at Intersections",
            ]

            for metric in metrics:
                frame = tk.Frame(self.metrics_frame)
                frame.pack(pady=2)

                label = tk.Label(frame, text=f"{metric}:", width=20, anchor="w")
                label.pack(side=tk.LEFT)

                value = tk.Label(frame, text="0", width=10)
                value.pack(side=tk.LEFT)

                self.metrics_labels[metric] = value

        def _init_buttons():
            """Initialize control buttons"""
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

        def _init_sliders():
            """Initialize the control sliders"""
            self.steps_slider = self.create_slider(
                "Steps", default_val=250, min_val=50, max_val=1000
            )

            self.frame_rate_slider = self.create_slider(
                "Frame Rate", default_val=40, min_val=1, max_val=500
            )

            self.grid_size_slider = self.create_slider(
                "Grid Size", default_val=50, min_val=10, max_val=100
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
            assert isinstance(self.controls_frame, tk.Frame)

            self.plot_frame = tk.Frame(self.master)
            self.plot_frame.pack(side=tk.RIGHT, padx=10)
            assert isinstance(self.plot_frame, tk.Frame)

            _init_sliders()
            _init_buttons()
            _init_metrics_display()
            _init_plot()

        else:
            print("\033[38;5;46mRunning simulation without UI.\033[0m")

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
        - label (str): The label for the slider.
        - min_val (int | float): The minimum value of the slider.
        - max_val (int | float): The maximum value of the slider.
        - default_val (int | float): The default value of the slider.

        Returns:
        --------
        - tk.Scale: The created slider widget.
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
        assert isinstance(frame, tk.Frame)

        label_widget = tk.Label(frame, text=label)
        label_widget.pack(side=tk.LEFT)
        assert isinstance(label_widget, tk.Label)

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

        def _restart_simulation_if_needed():
            """
            Restart the simulation if one is already running.
            """
            if self.animation and hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
                self.ax.clear()
                self.canvas.draw()

        def _initialize_grid(grid_size: int, blocks_size: int, lane_width: int) -> Grid:
            """
            Initialize the grid with the given parameters.
            """
            return Grid(
                grid_size=grid_size, blocks_size=blocks_size, lane_width=lane_width
            )

        def _setup_plot():
            """
            Set up the plot for the simulation.
            """
            self.ax.clear()
            self.fig.subplots_adjust(top=0.85)
            cmap = "Greys" if self.colour_blind else "rainbow"
            self.im = self.ax.imshow(self.grid.grid, cmap=cmap, interpolation="nearest")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()

        def _start_animation(steps, frame_rate: int):
            """
            Start the animation for the simulation.
            """
            self.animation = FuncAnimation(
                self.fig,
                self.update_simulation,
                frames=range(steps),
                interval=frame_rate,
                repeat=False,
            )
            self.canvas.draw()

        _restart_simulation_if_needed()
        self.write_header()

        # Read parameters from sliders
        steps = self.steps_slider.get()
        frame_rate = self.frame_rate_slider.get()

        grid_size = self.grid_size_slider.get()
        blocks_size = self.blocks_size_slider.get()
        lane_width = self.lane_width_slider.get()

        self.steps = 0
        self.grid = _initialize_grid(grid_size, blocks_size, lane_width)
        assert isinstance(self.grid, Grid)

        self.density_tracker = DensityTracker(self.grid)

        car_count = self.car_count_slider.get()
        cars = self.create_cars(car_count)
        self.grid.add_cars(cars)

        _setup_plot()

        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        _start_animation(steps, frame_rate)

        # Keep a reference to prevent garbage collection
        assert isinstance(self.animation, FuncAnimation)
        self._animation_ref = self.animation

    def update_simulation(self, frame: int):
        """
        Update the simulation for the given frame.

        Params:
        -------
        - frame (int): The current frame number in the simulation.
        """
        if self.is_paused:
            return [self.im, self.title]

        # Randomly switch rotary access (1% chance each frame)
        if np.random.random() < 0.1:
            self.grid.allow_rotary_entry = not self.grid.allow_rotary_entry
            state = "allowed" if self.grid.allow_rotary_entry else "blocked"
            print(f"\033[1;36mRotary access is now {state}\033[0m")

        # Update movement and get metrics
        moved_cars = self.grid.update_movement()
        metrics = self.density_tracker.update(moved_cars)

        self.im.set_array(self.grid.grid)

        # Update metrics display
        if self.show_ui:
            self.metrics_labels["Moving Cars"].config(text=f"{metrics['moving_cars']}")
            self.metrics_labels["Total Cars"].config(text=f"{metrics['total_cars']}")
            self.metrics_labels["Average Wait"].config(
                text=f"{metrics['average_wait_time']:.1f}"
            )
            self.metrics_labels["Max Wait"].config(text=f"{metrics['max_wait_time']}")
            self.metrics_labels["Congestion Rate"].config(
                text=f"{metrics['congestion_rate']:.1%}"
            )
            self.metrics_labels["Cars at Intersections"].config(
                text=f"{metrics['intersection_cars']}"
            )

        title = f"Simulation step {frame + 1}\n"
        title += f"Cars: {metrics['total_cars']}"
        if self.grid.allow_rotary_entry:
            title += " | Rotary: ✓"
        else:
            title += " | Rotary: ✗"
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

    def create_cars(self, car_count: int) -> list[Car]:
        """
        Create a list of cars with positions and directions based on traffic rules.
        Cars will drive on the right side by default. Cars will only spawn on regular road cells,
        not on intersections or rotaries. For vertical roads, right lane goes up and left lane
        goes down. For horizontal roads, upper lane goes right and lower lane goes left.

        Params:
        -------
        - car_count (int): Number of cars to create
        - drive_on_right (bool): If True, cars drive on the right side. If False, left side.

        Returns:
        --------
        - list[Car]: List of Car objects

        """
        np.random.seed(42)

        cars = np.zeros(car_count, dtype=object)
        for i in range(car_count):
            while (
                self.grid.grid[
                    x := np.random.randint(0, self.grid.size),
                    y := np.random.randint(0, self.grid.size),
                ]
                not in ROAD_CELLS
            ):
                pass

            road_type = self.grid.grid[x, y]
            car = Car(self.grid, position=(x, y), road_type=road_type)
            assert isinstance(car, Car)
            cars[i] = car

        assert isinstance(cars, np.ndarray)
        print(f"\033[38;5;46mCreated {car_count} cars.\033[0m")
        return cars

    def run_simulation_without_ui(
        self,
        steps=100,
        grid_size=25,
        blocks_size=5,
        lane_width=2,
        car_count=100,
        output=False,
    ):
        """
        Run the simulation without UI for a specified number of steps.

        Params:
        -------
        - steps (int): The number of steps to run the simulation.
        - grid_size (int): The size of the grid.
        - blocks_size (int): The size of the blocks in the grid.
        - lane_width (int): The width of the lanes in the grid.
        - car_count (int): The number of cars to create in the simulation.
        """

        assert isinstance(steps, int), f"Steps must be an integer, got {type(steps)}"

        # Initialize grid and density tracker
        self.grid = Grid(grid_size, blocks_size, lane_width)
        assert isinstance(self.grid, Grid)
        self.density_tracker = DensityTracker(self.grid)

        cars = self.create_cars(car_count)
        self.grid.add_cars(cars)

        # Run simulation steps
        grid_states = []

        if output:
            print("\033[1;36m=== Traffic Simulation ===")
            print(
                f"Grid: {grid_size}x{grid_size} | Cars: {car_count} | Steps: {steps}\033[0m\n"
            )

        for step in range(steps):
            if output:
                density = self.density_tracker.calculate_overall_density()
                print(f"\033[1;33mStep {step + 1:4d}/{steps:d}\033[0m", end=" ")
                print(
                    f"\033[1;32mSystem: {density['system_density'] * 100:4.1f}%\033[0m",
                    end=" ",
                )
                print(
                    f"\033[1;34mRoads: {density['road_density'] * 100:4.1f}%\033[0m",
                    end=" ",
                )
                print(
                    f"\033[1;35mInter: {density['intersection_density'] * 100:4.1f}%\033[0m",
                    end=" ",
                )
                print(f"\033[1;36mCars: {density['total_cars']:3d}\033[0m")

            grid_states.append(self.grid.grid.copy())
            self.grid.update_movement()

        # Final state
        # density = self.density_tracker.calculate_overall_density()
        # print(f"\033[1;33mStep {steps:4d}/{steps:d}\033[0m", end=" ")
        # print(
        #     f"\033[1;32mSystem: {density['system_density'] * 100:4.1f}%\033[0m", end=" "
        # )
        # print(f"\033[1;34mRoads: {density['road_density'] * 100:4.1f}%\033[0m", end=" ")
        # print(
        #     f"\033[1;35mInter: {density['intersection_density'] * 100:4.1f}%\033[0m",
        #     end=" ",
        # )
        # print(f"\033[1;36mCars: {density['total_cars']:3d}\033[0m")

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
        - step (int): The current step number in the simulation.
        - density_metrics (dict): Dictionary containing density measurements
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
            if hasattr(self, "_animation_ref"):
                del self._animation_ref
        except Exception:
            pass  # Animation might already be stopped

        # Clear the plot
        if hasattr(self, "ax") and self.ax:
            self.ax.clear()
            self.ax.set_xticks([])
            self.ax.set_yticks([])

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
