import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")
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


class SimulationUI:
    def __init__(self, master: tk.Tk, show_ui: bool = True):
        self.show_ui = show_ui
        self.master = master
        self.is_paused = False
        self.steps = 0

        if self.show_ui:
            self.master.title("Car Traffic in a 2D street network.")

            self.controls_frame = tk.Frame(self.master)
            self.controls_frame.pack(side=tk.LEFT, padx=10)

            self.steps_slider = self.create_slider("Steps", 50, 200, 100)
            self.frame_rate_slider = self.create_slider("Frame Rate", 1, 500, 40)

            self.grid_size_slider = self.create_slider("Grid Size", 10, 1000, 25)
            self.blocks_size_slider = self.create_slider("Blocks Size", 2, 50, 5)
            self.lane_width_slider = self.create_slider("Lane Width", 2, 30, 2)
            self.car_count_slider = self.create_slider("Car Count", 1, 10000, 10)

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

        else:
            print("\033[38;5;46mRunning simulation without UI.\033[0m")
            pass

        self.grid = None
        self.simulation = None
        self.animation = None

    def create_slider(
        self,
        label: str,
        min_val: int | float,
        max_val: int | float,
        default_val: int | float,
    ):
        """Create a slider with a label"""
        frame = tk.Frame(self.controls_frame)
        frame.pack(pady=5)

        label_widget = tk.Label(frame, text=label)
        label_widget.pack(side=tk.LEFT)

        slider = tk.Scale(
            frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200
        )
        slider.set(default_val)
        slider.pack(side=tk.RIGHT)

        return slider

    def start_simulation(self):
        """
        Start the simulation with the parameters from the sliders
        Can also restart if previous simulation is running.
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
        # car_count = self.car_count_slider.get()

        self.steps = 0
        self.grid = Grid(
            grid_size=grid_size, blocks_size=blocks_size, lane_width=lane_width
        )
        cars = cars = [
            Car(self.grid, position=(16, 3), direction="E"),
            Car(self.grid, position=(17, 6), direction="N"),
            Car(self.grid, position=(1, 1), direction="S"),
            Car(self.grid, position=(17, 5), direction="N"),
        ]
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
        """Update the simulation"""
        if self.is_paused:
            return

        self.grid.update_movement()
        self.write_simulation(frame)

        self.ax.clear()
        self.ax.imshow(self.grid.grid, cmap="viridis", interpolation="nearest")
        # self.ax.imshow(self.grid.grid, cmap="Grays", interpolation="nearest")
        self.ax.set_title(f"Simulation step {frame + 1}")

        self.canvas.draw()

    def pause_simulation(self):
        """Pause the simulation"""
        if self.animation and not self.is_paused:
            self.is_paused = True
            self.animation.event_source.stop()
            print("Simulation paused.")

        elif self.animation and self.is_paused:
            self.is_paused = False
            self.animation.event_source.start()
            print("Simulation resumed.")

    def create_cars(self, car_count: int) -> list:
        """Create a list of cars with random positions and directions"""
        # TODO make it so that these cars are placed in a more sensible way following the road rules
        cars = np.zeros(car_count, dtype=object)
        for i in range(car_count):
            while self.grid.grid[
                x := np.random.randint(0, self.grid.size),
                y := np.random.randint(0, self.grid.size),
            ] not in [VERTICAL_ROAD_VALUE, HORIZONTAL_ROAD_VALUE, INTERSECTION_VALUE]:
                pass

            dx = np.random.choice([-1, 0, 1])
            dy = 0 if dx != 0 else np.random.choice([-1, 1])

            car = Car(self.grid, position=(x, y), direction=(dx, dy))
            cars[i] = car
        return cars

    def run_simulation_without_ui(
        self,
        steps: int,
        grid_size: int,
        blocks_size: int,
        lane_width: int,
        car_count: int,
    ):
        """Run the simulation without showing the UI and return the grid states"""
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
        """Write the header to the simulation file"""
        with open(f"data/simulation.{FILE_EXTENSION}", "w") as f:
            f.write("Step; Grid_State\n")

    def write_simulation(self, step: int):
        """Write the simulation to a file"""
        grid_state = str(self.grid.grid.tolist())

        with open(f"data/simulation.{FILE_EXTENSION}", "a") as f:
            f.write(f"{step}; {grid_state}\n")
