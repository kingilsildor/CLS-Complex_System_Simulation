# Car Density Analysis Using Cellular Automata 🚗🏙️
Within this repository we explore how a cellular automata can be used to model and analyze car density in urban environments.
By simulating traffic on Manhattan-style grids, we compare 1D and 2D road networks and investigate how various parameters influence traffic flow and congestion.  
The 1D cellular automata models traffic based on the Nagel-Schreckenberg experiment. The simulation models traffic flow on a one-dimensional road using a set of simple rules that govern the movement of cars.

## Description
Based on the research done by Chopard, Luthi & Queloz (1996), we looked at modelling traffic for urban environments. Here, we use **cellular automata** as a lightweight and flexible approach to simulate traffic behavior. Our simulations model cars moving through streets and intersections, taking into account factors like:  

- **Grid structure**: Linear 1D roads vs. interconnected 2D Manhattan grids.  
- **Road parameters**: 
    - Road size 
    - Speed limits
    - Rotaries.  
- **Car parameters**: 
    - Number of cars in the system.
    - Whether the cars adhere to the speed limit

This study allows us to observe emergent behaviors such as traffic jams, flow bottlenecks, and the effects of road infrastructure on congestion.

## Table of Contents

- [Getting Started](#getting-started)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [Contributors](#contributors)
- [References](#references)
- [Licence](#licence)

## Getting Started

First one should clone the repository. Followed by installing the required dependencies.

### UV
This repository uses _uv_ to manage Python and its dependencies, and _pre-commit_ to run
automatic code linting & formatting.

1. Install [uv](https://github.com/astral-sh/uv)

2. Navigate to this project directory

3. Install pre-commit:

```zsh
# We can use uv to install pre-commit!
uv tool install pre-commit --with pre-commit-uv --force-reinstall

# Check that pre-commit installed alright (should say 3.8.0 or similar)
pre-commit --version

# After installing pre-commit, you'll need to initialise it.
# This installs all pre-commit hooks, the scripts which run before a commit.
pre-commit install

# It's a good idea to run pre-commit now on all files.
pre-commit run --all-files

# Before running the code sync all the packages locally
uv sync
```

4. Run code:

```zsh
uv run main.py
```
### Conda 
If _uv_ doesn't work one can install the required dependencies from `requirements.txt`. It's best to run it in python 3.12.2.

```zsh
conda install --file requirements.txt
```

## Usage
`main.py` is the main entry point for the simulation project. It can be run either with a graphical user interface (GUI) or in a headless (non-UI) mode.


1. The `show_ui` flag determines whether the simulation runs with or without a GUI:
    - **`True` (default)**: Opens a GUI using Tkinter to visualize the simulation.
    - **`False`**: Runs the simulation without a GUI and prints the grid states to the console for a specified number of steps.

2. **Non-UI Mode**:  
   If you set `show_ui` to `False`, the following parameters are passed to the simulation:
   - `steps=100`: Number of simulation steps.
   - `grid_size=15`: The size of the grid.
   - `blocks_size=10`: The size of each grid block.
   - `lane_width=2`: Width of lanes on the grid.
   - `car_count=4`: Number of cars in the simulation.  
   The resulting states of the grid will be printed to the console after each step and writen to `data/simulation.txt`.

3. **UI Mode**:  
   When `show_ui` is `True`, a Tkinter window will open, allowing you to interactively view the simulation.

4. **Testing**:
    The repository includes **pytest-based unit tests** to ensure the correctness of the core functionalities: These tests cover:
- Grid initialization: Verifies that the grid is correctly set up with roads, intersections, and blocks
- Road Creation: Ensures that vertical and horizontal roads are generated properly.
- Car Behavior: Tests car movement, intersection handling, and rotary navigation.
- Collission and Interaction: Checks if cars correctly detect other vehicles in front or at intersections.

To run all tests, make sure that the imports are changed in Car.py and Grid.py from "src.utils" to "utils" for all imports and then execute:
```zsh
pytest test_simulation.py
```

## File description
- **`data/simulation.txt`**: A text file containing data results related to the simulation.
- **`src/car.py`**: Contains logic and class definitions related to the car entities in the simulation.
- **`src/density.py`**: Handles calculations or logic for density in the system.
- **`src/grid.py`**: Manages grid-based operations and grid-related logic in the simulation.
- **`src/simulation.py`**: Core simulation code, to control the different components.
- **`src/utils.py`**: Utility functions used across the project for shared functionality.
- **`src/test_simulation.py`**: Test cases for the Grid and Car classes.
- **`main.py`**: The entry point of the project, to initiate the simulation.
- **`requirements.txt`**: Lists Python dependencies required for the project.


## Contributors

We planed on collaborating in most parts of the assignment. We made a Trello board to structure the tasks at hand, divide them into small tickets, and distribute the workload evenly. For the presentation and documentation, we have collaborated on all parts through longer meetings.


- **Max**:
- **Koen**:
- **Bart**: Worked on the Car logic in collaboration with Tycho and implemented the testing.
- **Tycho**: Worked on the boilerplates of the code base, such as the `Car`, `Grid` and `Simulation` classes. Handeled the repository and helped with bug fixing.

All the commits can be found in main.


## References
Chopard, B., Luthi, P. O., & Queloz, P. A. (1996). Cellular automata model of car traffic in a two-dimensional street network. Journal of Physics A: Mathematical and General, 29(10), 2325.

## Licence
This repository is licensed under the MIT License. You are generally free to reuse or extend upon this code as you see fit; just include the original copy of the license
