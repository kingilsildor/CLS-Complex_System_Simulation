# 1D Cellular Automata Traffic Simulation

This project implements a 1D cellular automata traffic simulation model based on the Nagel-Schreckenberg experiment. The simulation models traffic flow on a one-dimensional road using a set of simple rules that govern the movement of cars.

## Project Structure

- `src/main.py`: Entry point of the simulation. Initializes parameters, creates an instance of the Nagel-Schreckenberg model, and runs the simulation loop.
- `src/models/nagel_schreckenberg.py`: Contains the `NagelSchreckenberg` class that implements the cellular automata model for traffic simulation. Includes methods for initialization, updating the state, and running the simulation.
- `src/utils/helpers.py`: Utility functions for generating random initial states, visualizing traffic flow, and logging results.
- `src/types/__init__.py`: Defines custom types or data structures used throughout the project, such as constants and data classes for car states.

## Requirements

To run this project, you need to install the following dependencies:

- numpy
- matplotlib

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Running the Simulation

To run the simulation, execute the following command in your terminal:

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
    **TODO**


## File description
- **`data/simulation.txt`**: A text file containing data results related to the simulation.
- **`src/car.py`**: Contains logic and class definitions related to the car entities in the simulation.
- **`src/density.py`**: Handles calculations or logic for density in the system.
- **`src/grid.py`**: Manages grid-based operations and grid-related logic in the simulation.
- **`src/simulation.py`**: Core simulation code, to control the different components.
- **`src/utils.py`**: Utility functions used across the project for shared functionality.
- **`main.py`**: The entry point of the project, to initiate the simulation.
- **`requirements.txt`**: Lists Python dependencies required for the project.


## Contributors

We planed on collaborating in most parts of the assignment. We made a Trello board to structure the tasks at hand, divide them into small tickets, and distribute the workload evenly. For the presentation and documentation, we have collaborated on all parts through longer meetings.


- **Max**:
- **Koen**: 
- **Bart**:
- **Tycho**: Worked on the boilerplates of the code base, such as the `Car`, `Grid` and `Simulation` classes. Handeled the repository and helped with bug fixing.

```
python src/main.py
```

## Parameters

The simulation parameters can be adjusted in `main.py`. These parameters include:

- Number of cars
- Road length
- Probability of random deceleration
- Maximum speed of cars

Feel free to modify these parameters to observe different traffic behaviors.