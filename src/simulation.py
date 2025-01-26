import tkinter as tk

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

CAR_DIRECTION = {
    1: "⬇️",
    2: "⬆️",
    3: "⬅️",
    4: "➡️",
}


class SimulationUI:
    def __init__(
        self,
        master: tk.Tk,
        show_ui: bool = True,
        colour_blind: bool = True,
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
        self.velocity_data = []  # Store velocity data for plotting

        def _init_plot():
            """Initialize the matplotlib plots"""
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
            self.ax_velocity = self.fig.add_subplot(gs[1, 1])
            self.ax_velocity.set_xlabel("Steps")
            self.ax_velocity.set_ylabel("Average Velocity")
            self.ax_velocity.set_ylim(0, 1)
            self.ax_velocity.grid(True)
            (self.velocity_line,) = self.ax_velocity.plot(
                [], [], "g-", label="Velocity"
            )
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

            title = "Welcome to SimCity 2000"
            self.ax_grid.set_title(title)

            self.canvas.draw()

        def _init_metrics_display():
            """Initialize the metrics display panel"""
            self.metrics_frame = tk.Frame(self.controls_frame)
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
                "Frame Rate", default_val=400, min_val=1, max_val=500
            )

            self.grid_size_slider = self.create_slider(
                "Grid Size", default_val=15, min_val=10, max_val=100
            )

            self.blocks_size_slider = self.create_slider(
                "Blocks Size", default_val=10, min_val=2, max_val=50
            )

            # self.lane_width_slider = self.create_slider(
            #     "Lane Width", default_val=2, min_val=2, max_val=30
            # )

            self.car_count_slider = self.create_slider(
                "Car Count", default_val=3, min_val=1, max_val=1250
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
            print("Running simulation without UI.")

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
            raise ValueError("Min and max values must be of the same type.")

        # Check if the default value is of the same type as min and max values, and convert if not
        if isinstance(min_val, int) and not isinstance(default_val, int):
            default_val = int(default_val)
            raise ValueError("Default value is set to an integer.")
        if (
            isinstance(min_val, float) or isinstance(max_val, float)
        ) and not isinstance(default_val, float):
            default_val = float(default_val)
            raise ValueError("Default value is set to a float.")

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
            """Restart the simulation if one is already running."""
            if self.animation and hasattr(self.animation, "event_source"):
                self.animation.event_source.stop()
                self.ax_grid.clear()
                self.ax_density.clear()
                self.ax_velocity.clear()
                self.ax_flow.clear()
                self.ax_queue.clear()
                self.canvas.draw()

        def _setup_plot():

            """
            Set up the plot for the simulation, including grid values and coordinates.
            """
            #Clear main plot
            self.ax.clear()
            self.fig.subplots_adjust(top=0.85)
            
            #Clear other plots
            self.ax_grid.clear()
            self.ax_density.clear()
            self.ax_velocity.clear()
            self.ax_flow.clear()
            self.ax_queue.clear()

            cmap = "Greys" if self.colour_blind else "rainbow"
            self.im = self.ax.imshow(self.grid.grid, cmap=cmap, interpolation="nearest")

            # Remove tick marks
            self.ax.set_xticks([])
            self.ax.set_yticks([])

            self.canvas.draw()

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
            self.ax_velocity.set_xlabel("Steps")
            self.ax_velocity.set_ylabel("Average Velocity")
            self.ax_velocity.set_ylim(0, 1)
            self.ax_velocity.grid(True)
            (self.velocity_line,) = self.ax_velocity.plot(
                [], [], "g-", label="Velocity"
            )
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

        _restart_simulation_if_needed()
        self.write_header()

        # Reset data arrays
        self.velocity_data = []

        # Read parameters from sliders
        steps = self.steps_slider.get()
        frame_rate = self.frame_rate_slider.get()
        grid_size = self.grid_size_slider.get()
        blocks_size = self.blocks_size_slider.get()
        lane_width = self.lane_width_slider.get()

        self.steps = steps
        self.grid = Grid(
            grid_size=grid_size, blocks_size=blocks_size, lane_width=lane_width
        )
        self.density_tracker = DensityTracker(self.grid)

        car_count = self.car_count_slider.get()
        cars = self.create_cars(car_count)
        self.grid.add_cars(cars)
        # cars[1].
        _setup_plot()

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

    def update_simulation(self, frame):
        """Update the simulation for each frame."""
        if self.is_paused:
            return [
                self.im,
                self.velocity_line,
                self.road_density_line,
                self.intersection_density_line,
                self.flow_line,
                self.queue_line,
            ]

        # Randomly switch rotary access (10% chance each frame)
        if np.random.random() < 0.1:
            self.grid.allow_rotary_entry = not self.grid.allow_rotary_entry

        # Update grid and get metrics
        moved_cars = self.grid.update_movement()
        metrics = self.density_tracker.update(moved_cars)

        # Write metrics to file
        self.write_simulation(frame, metrics)

        # Update metrics display
        if self.show_ui:
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
        if self.grid.allow_rotary_entry:
            title += " | Rotary: ✓"
        else:
            title += " | Rotary: ✗"
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
        title += f"Cars: {density_metrics['total_cars']}"
        self.ax.set_title(title)

        # Remove previous text annotations
        if hasattr(self, "text_annotations"):
            for txt in self.text_annotations:
                txt.remove()

        self.text_annotations = []

        # Add text annotations for car directions
        for car in self.grid.cars:
            i, j = car.head_position
            car_direction = CAR_DIRECTION[car.road_type]
            text = self.ax.text(
                j,
                i,
                car_direction,
                ha="center",
                va="center",
                fontsize=10,
                color="white",
            )
            self.text_annotations.append(text)


        self.canvas.draw()

        # Save plots at the end of simulation
        if frame == self.steps - 1:
            self.save_plots()

        return [
            self.im,
            self.velocity_line,
            self.road_density_line,
            self.intersection_density_line,
            self.flow_line,
            self.queue_line,
        ]

    def pause_simulation(self):
        """
        Pause or resume the simulation.
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

            car = Car(self.grid, position=(x, y))
            assert isinstance(car, Car)
            cars[i] = car

        assert isinstance(cars, np.ndarray)
        print(f"Created {car_count} cars.")
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
                "Step; Grid_State; Road_Density; Intersection_Density; Global_Density; "
                "Average_Velocity; Traffic_Flow; Queue_Length; Total_Cars; Moving_Cars\n"
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
                f"{metrics['total_cars']}; {metrics['moving_cars']}\n"
            )

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

        print("Simulation reset.")
