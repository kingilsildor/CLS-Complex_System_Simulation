import numpy as np
import random

def create_manhattan_grid_with_housing(rows, cols, lane_width, block_chance=0.2):
    # Create an empty grid filled with zeros initially
    grid = np.zeros((rows, cols), dtype=int)

    # Fill the vertical lanes with 1s and 2s
    for col in range(0, cols, lane_width * 2):
        grid[:, col:col + lane_width] = 1  # Left lane
        if col + lane_width < cols:
            grid[:, col + lane_width:col + 2 * lane_width] = 2  # Right lane

    # Fill the horizontal lanes with 1s and 2s
    for row in range(0, rows, lane_width * 2):
        grid[row:row + lane_width, :] = 1  # Left lane (horizontal)
        if row + lane_width < rows:
            grid[row + lane_width:row + 2 * lane_width, :] = 2  # Right lane (horizontal)

    # Add housing blocks (randomly set cells to 0, simulating non-driving areas)
    for i in range(rows):
        for j in range(cols):
            if random.random() < block_chance:
                grid[i, j] = 0  # Randomly set some cells as housing blocks (value 0)

    return grid

# Example usage:
rows, cols = 8, 8  # Grid size
lane_width = 2  # Lane width parameter
block_chance = 0.3  # Probability of a housing block (value 0) being added
grid = create_manhattan_grid_with_housing(rows, cols, lane_width, block_chance)
print(grid)
