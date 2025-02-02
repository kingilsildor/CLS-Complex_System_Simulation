import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import powerlaw

from src.utils import (
    BLOCKS_VALUE,
    HORIZONTAL_ROAD_VALUE_LEFT,
    HORIZONTAL_ROAD_VALUE_RIGHT,
    INTERSECTION_DRIVE,
    ROAD_CELLS,
    TRAFFIC_JAM,
    VERTICAL_ROAD_VALUE_LEFT,
    VERTICAL_ROAD_VALUE_RIGHT,
)

temp = HORIZONTAL_ROAD_VALUE_LEFT + VERTICAL_ROAD_VALUE_RIGHT


class Grid:
    """
    Represents a city grid with roads, intersections, and moving cars.

    The grid is initialized with blocks and lanes, and roads are created accordingly.
    Cars can be added to the grid and their movements updated dynamically.
    """

    def __init__(
        self, grid_size: int, blocks_size: int, rotary_method: int, max_speed: int = 2
    ):
        """
        Initialize the grid with a given size, block size, and lane width.

        Params:
        -------
        - grid_size (int): The size of the grid (NxN).
        - blocks_size (int): The size of blocks between roads.
        - rotary_method (int): The method used to handle rotaries.
        - max_speed (int): The maximum speed of cars on the grid. Default is 2.
        """
        self.grid = np.full((grid_size, grid_size), BLOCKS_VALUE, dtype=int)
        self.underlying_grid = np.full(
            (grid_size, grid_size), BLOCKS_VALUE, dtype=int
        )  # Track original cell types
        self.size = grid_size
        self.blocks = blocks_size
        self.rotary_method = rotary_method
        self.lane_width = 2

        self.cars = []
        self.rotary_dict = []
        self.flag = np.full((grid_size, grid_size), INTERSECTION_DRIVE, dtype=int)
        self.jammed = np.zeros((grid_size, grid_size))

        # Store the road layout
        self.roads()
        self.road_layout = self.grid.copy()
        self.max_speed = max_speed

        # Count road and intersection cells
        road_mask = np.zeros_like(self.grid, dtype=bool)
        for road_type in ROAD_CELLS:
            road_mask = road_mask | (self.underlying_grid == road_type)
        self.road_cells = np.sum(road_mask)

        self.intersection_cells = np.sum(self.underlying_grid == INTERSECTION_DRIVE)

        self.allow_rotary_entry = False  # Start with rotaries blocked

        self.largest_component = None

    def roads(self):
        """
        Construct roads on the grid, including vertical, horizontal, and intersection roads.
        """
        self.create_vertical_lanes()
        self.create_horizontal_lanes()
        self.create_intersections()

    def create_edge_lanes(self):
        """
        Create lanes along the edges of the grid, ensuring connectivity.
        """
        self.grid[: self.lane_width, :] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[-self.lane_width :, :] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[:, : self.lane_width] = HORIZONTAL_ROAD_VALUE_RIGHT
        self.grid[:, -self.lane_width :] = HORIZONTAL_ROAD_VALUE_RIGHT

    def create_vertical_lanes(self):
        """
        Create vertical roads at regular intervals based on block size.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for col in range(half_block, self.size, self.blocks):
            left = col
            right = min(col + self.lane_width, self.size)
            lane_devider = self.lane_width // 2

            for x in range(self.size):
                for y in range(left, right):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if (y - left) < lane_devider:
                            self.grid[x, y] = VERTICAL_ROAD_VALUE_LEFT
                            self.underlying_grid[x, y] = VERTICAL_ROAD_VALUE_LEFT
                        else:
                            self.grid[x, y] = VERTICAL_ROAD_VALUE_RIGHT
                            self.underlying_grid[x, y] = VERTICAL_ROAD_VALUE_RIGHT

    def create_horizontal_lanes(self):
        """
        Create horizontal roads at regular intervals based on block size.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for row in range(half_block, self.size, self.blocks):
            top = row
            bottom = min(row + self.lane_width, self.size)
            lane_devider = self.lane_width // 2

            for x in range(top, bottom):
                for y in range(self.size):
                    if self.grid[x, y] == BLOCKS_VALUE:
                        if (x - top) < lane_devider:
                            self.grid[x, y] = HORIZONTAL_ROAD_VALUE_LEFT
                            self.underlying_grid[x, y] = HORIZONTAL_ROAD_VALUE_LEFT
                        else:
                            self.grid[x, y] = HORIZONTAL_ROAD_VALUE_RIGHT
                            self.underlying_grid[x, y] = HORIZONTAL_ROAD_VALUE_RIGHT

    def create_intersections(self):
        """
        Create intersections where vertical and horizontal roads meet.
        Intersections are designed as 2x2 rotary spaces to facilitate smooth traffic flow.
        """
        half_block = self.blocks // 2
        assert isinstance(half_block, int)

        for i in range(half_block, self.size, self.blocks):
            for j in range(half_block, self.size, self.blocks):
                x0, x1 = i, i + self.lane_width
                y0, y1 = j, j + self.lane_width

                self.grid[x0:x1, y0:y1] = INTERSECTION_DRIVE
                self.underlying_grid[x0:x1, y0:y1] = INTERSECTION_DRIVE

                ring = [(x0, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 1, y0)]
                assert isinstance(ring, list)
                self.rotary_dict.append(ring)

    def add_cars(self, cars: list):
        """
        Add cars to the grid.

        Params:
        -------
        - cars (list): A list of car objects to be added to the grid.
        """
        self.cars.extend(cars)

    def update_movement(self):
        """
        Update the grid to reflect the movement of all cars.

        Returns:
        --------
        set: A set of distances moved by cars
        """
        moved_distances = np.zeros(len(self.cars), dtype=int)
        for id, car in enumerate(self.cars):
            distance = car.move()
            moved_distances[id] = distance
        return moved_distances

    def get_jammed_positions(self):
        """
        Get the positions of all jammed cells.

        Returns:
        --------
        list: A list of jammed cell positions

        """
        np.savetxt("jammed.txt", self.jammed, fmt="%d")
        return np.argwhere(self.jammed == TRAFFIC_JAM)

    def jammed_network(self):
        """
        Get the jammed network.

        Returns:
        --------
        list: A list of jammed cell positions
        """
        G = nx.Graph()
        jammed_positions = self.get_jammed_positions()
        # unique_jammed_positions = np.unique(jammed_positions, axis=0)
        unique_jammed_positions = set(map(tuple, jammed_positions))

        for x, y in unique_jammed_positions:
            # Assuming cars move along the y-axis (vertical roads)
            if (x, y - 1) in unique_jammed_positions:  # Back neighbor
                G.add_edge((x, y), (x, y - 1))
            if (x, y + 1) in unique_jammed_positions:  # Front neighbor
                G.add_edge((x, y), (x, y + 1))

            # If cars move along the x-axis (horizontal roads)
            if (x - 1, y) in unique_jammed_positions:  # Back neighbor
                G.add_edge((x, y), (x - 1, y))
            if (x + 1, y) in unique_jammed_positions:  # Front neighbor
                G.add_edge((x, y), (x + 1, y))

        print("G.number_of_nodes() =", G.number_of_nodes())

        return G

    def analyze_cluster_sizes(self, G):
        """
        Analyze the size of clusters in the jammed network.

        Params:
        -------
        - G (nx.Graph): The jammed network graph.

        Returns:
        --------
        list: A list of cluster sizes.
        """
        cluster_sizes = [len(c) for c in nx.connected_components(G)]
        cluster_sizes.sort(reverse=True)

        print(f"Number of clusters: {len(cluster_sizes)}")
        print(f"Cluster sizes: {cluster_sizes}")
        print(f"Sum: {sum(cluster_sizes)}")

        return cluster_sizes

    def get_largest_cluster(self, G):
        """
        Get the largest cluster in the jammed network.

        Params:
        -------
        - G (nx.Graph): The jammed network graph.

        Returns:
        --------
        set: The largest cluster in the network.
        """
        largest_cluster = max(nx.connected_components(G), key=len)
        return len(largest_cluster)

    def set_largest_cluster(self):
        self.largest_component = self.get_largest_cluster(self.jammed_network())

    @staticmethod
    def plot_powerlaw_fit(cluster_sizes, grid_size, car_count):
        fit = powerlaw.Fit(cluster_sizes, discrete=True)

        # Create a plot of the PDF
        figPDF = fit.plot_pdf(
            color="b", marker="o", linewidth=0, label="Empirical Data"
        )

        # Plot the best-fit power law on the same axes
        fit.power_law.plot_pdf(
            color="r",
            linestyle="--",
            ax=figPDF,
            label=f"Power Law Fit (α={fit.alpha:2f})",
        )

        plt.title(
            f"Cluster Size Distribution (PDF) with Power Law Fit\n Grid Size: {grid_size}, Car Count: {car_count}"
        )
        plt.xlabel("Cluster Size")
        plt.ylabel("PDF")
        plt.legend()
        plt.show()
