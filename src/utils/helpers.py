import numpy as np
import matplotlib.pyplot as plt

def generate_initial_state(length, density):
    """Generates a random initial state for the traffic simulation."""
    import numpy as np
    return np.random.choice([0, 1], size=length, p=[1-density, density])

def visualize_traffic(state):
    """Visualizes the current state of the traffic."""
    import matplotlib.pyplot as plt
    plt.imshow(state.reshape(1, -1), cmap='Greys', aspect='auto')
    plt.axis('off')
    plt.show()

def log_simulation_results(results, filename='simulation_results.txt'):
    """Logs the results of the simulation to a file."""
    with open(filename, 'w') as f:
        for result in results:
            f.write(f"{result}\n")