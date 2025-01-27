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