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
    - [UV](#uv)
    - [Conda](#conda)
- [Usage](#usage)
- [Testing](#testing)
- [File Descriptions](#file-descriptions)
- [Contributors](#contributors)
- [Git Fame](#git-fame)
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
For calling the different functionalities within the program, one can best call the functions provided in the main file.
The followings functions can be called:

- `run_2D_NoUI_simulation`: This is the fastest way to run a simulation. For this the following parameters needs to be given:
    1. `root (tk.Tk)`: The root window.
    2. `max_iter (int)`: The maximum number of iterations.
    3. `rotary_method (int)`: The method to use for rotaries.
    4. `grid_size (int)`: The size of the grid.
    5. `road_length (int)`: The length of the road.
    6. `road_max_speed (int)`: The maximum speed of cars on the road.
    7. `car_count (int)`: The number of cars to create.
    8. `car_percentage_max_speed (int)`: The percentage of cars that will drive at the maximum speed.
    9. `seed (int)`: The seed for random number generation. Default is 42.
- `run_1D_simulation`: Run the simulation based on the Nagel Schreckenberg model.
- `run_2D_UI_simulation`: Run the simulation for the 2D model inluding UI, to see the traffic behaviour visualy.
- `run_all_experiments`: Run all the experiments to generate the plots that are used in the slides.

## Testing
The repository includes **pytest-based unit tests** to ensure the correctness of the core functionalities: These tests cover:
- Grid initialization: Verifies that the grid is correctly set up with roads, intersections, and blocks
- Road Creation: Ensures that vertical and horizontal roads are generated properly.
- Collission and Interaction: Checks if cars correctly detect other vehicles in front or at intersections.

To run all tests, make sure that the imports are changed in Car.py and Grid.py from "src.utils" to "utils" for all imports and then execute:
```zsh
pytest test_simulation.py
```
The file also included asserts and raise statements to make it so that only the right value will be given to functions.

## File description
- **`data/.`**: Directory containing data files for the simulation.
- **`data/road_length/.`**: Directory for storing road length data.
- **`data/simulation.txt`**: A text file containing data results related to the simulation.
- **`slide/Complex Systems Simulation.pdf`**: PDF file of the presentation slides for the simulation project.
- **`src/car.py`**: Defines the Car class and its behavior within the simulation.
- **`src/density.py`**: Contains functions to calculate and manage density metrics in the simulation.
- **`src/experiment.py`**: Large-scale experiment framework and analysis
- **`src/grid.py`**: Implements the Grid class and associated grid operations for the simulation.
- **`src/helper.py`**: Provides helper functions used across different modules.
- **`src/nagel_schreckenberg.py`**: Implements the Nagel-Schreckenberg traffic model.
- **`src/simulation.py`**: Coordinates the overall simulation process and integrates various components.
- **`src/test_simulation.py`**: Includes unit tests for validating the functionality of the Grid and Car classes.
- **`src/utils.py`**: Provides utility functions and helpers used throughout the simulation project.
- **`main.py`**: The entry point of the project, to initiate the simulation. The different files will be called from here.
- **`requirements.txt`**: Lists Python dependencies required for the project. Can be installed using `conda`.

### Tests
- **`test_simulation.py`**: Unit tests for grid, car, and system behavior

### Data and Configuration
- **`data/`**: Experiment results (CSV, JSON) and visualizations
- **`requirements.txt`**: Python package dependencies
- **`main.py`**: Entry point with different simulation modes

## Contributors
We planed on collaborating in most parts of the assignment. We made a Trello board to structure the tasks at hand, divide them into small tickets, and distribute the workload evenly. For the presentation and documentation, we have collaborated on all parts through longer meetings.
For the presentation the work was also devided around the things we worked around.

- **Max**: Created the 1D model and the necessary analytics for it.
- **Koen**: Contributed to the system-wide analysis capabilities of the simulation by writing the `Density` class and experiment file.
- **Bart**: Worked on the Car logic, testing and network and powerlaw analyses.
- **Tycho**: Worked on the boilerplates of the code base, such as the `Car`, `Grid` and `Simulation` classes. Handeled the repository and helped with bug fixing.

All the commits can be found in main.
The branches aren't being pruned to get an idea about how the project was structured.

## Git Fame
Total commits: 156
Total ctimes: 1902
Total files: 323
Total loc: 138986
| Author       |    loc |   coms |   fils |  distribution   |
|:-------------|-------:|-------:|-------:|:----------------|
| kbverlaan    | 108369 |     27 |    265 | 78.0/17.3/82    |
| kingilsildor |  29136 |     88 |     34 | 21/56.4/10.5    |
| Bart Koedijk |   1128 |     27 |     14 | 0.8/17.3/ 4.3   |
| chappy-tm    |    328 |      3 |      8 | 0.2/ 2.0/ 2.6   |
| Tycho Stam   |     21 |      7 |      1 | 0.0/ 4.7/ 0.3   |
| brkoedijk    |     10 |      4 |      1 | 0.0/ 2.7/ 0.3   |


- Tycho Stam -> kingilsildor
- brkoedijk -> Bart Koedijk

## References
Chopard, B., Luthi, P. O., & Queloz, P. A. (1996). Cellular automata model of car traffic in a two-dimensional street network. Journal of Physics A: Mathematical and General, 29(10), 2325.

## Licence
This repository is licensed under the MIT License. You are generally free to reuse or extend upon this code as you see fit; just include the original copy of the license
