## CLS-Complex_System_Simulation
This course covers Complex System Simulation, exploring concepts like emergence, chaos, phase transitions, and complexity. Topics include Cellular Automata, Percolation, Self-Organized Criticality, Random Networks, and more. Students will develop simulations and analyze emergent phenomena in group projects..

## Getting started

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
```

4. Run code:

```zsh
uv run <PATH-TO-PYTHON-FILE>
```

## Adding new packages with uv

It's simple to add a Python package to the project with uv using `uv add`.
For instance, to install numpy and scipy, and add them to the dependency graph, run:

```zsh
uv add numpy scipy
```

To remove a package dependency, e.g., scipy, run:

```zsh
uv remove scipy
```

## Running JupyterLab with uv

uv can also be used to run Jupyter, the same way as we run Python scripts:

```zsh
# If Jupyter Lab isn't already installed, add it as a dependency
uv add jupyterlab

# Start a JupyterLab server
uv run jupyter lab
```
