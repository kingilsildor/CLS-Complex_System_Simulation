import matplotlib.pyplot as plt
import numpy as np
from main import generate_density_vs_speed_data
import random

random.seed(42)
np.random.seed(42)

def plot_density_vs_speed(num_simulations=1):
    # Define the parameters
    length = 100  # Example value, adjust as needed
    max_speed = 2  # Example value, adjust as needed
    randomization = True  # Example value, adjust as needed
    time_steps = 100  # Example value, adjust as needed

    all_avg_speeds = []

    for _ in range(num_simulations):
        densities, avg_speeds = generate_density_vs_speed_data(length, max_speed, randomization, time_steps)
        all_avg_speeds.append(avg_speeds)

    # Calculate the mean average speeds across all simulations
    mean_avg_speeds = [sum(speeds) / num_simulations for speeds in zip(*all_avg_speeds)]
    
    # Calculate the standard deviation of the average speeds
    std_dev = [np.std(speeds) for speeds in zip(*all_avg_speeds)]
    
    # Calculate the 90% confidence interval
    ci = [1.645 * (std / np.sqrt(num_simulations)) for std in std_dev]

    # Create a figure and plot
    fig, ax = plt.subplots()
    
    # Plot the actual average speeds of each simulation
    for avg_speeds in all_avg_speeds:
        ax.plot(densities, avg_speeds, 'g-', alpha=0.3, label='Individual Simulation' if avg_speeds == all_avg_speeds[0] else "")
    
    # Plot the mean average speeds
    ax.plot(densities, mean_avg_speeds, 'b-', label='Mean Average Speed')
    
    # Fill the 90% confidence interval
    ax.fill_between(densities, 
                    [mean - ci_val for mean, ci_val in zip(mean_avg_speeds, ci)], 
                    [mean + ci_val for mean, ci_val in zip(mean_avg_speeds, ci)], 
                    color='b', alpha=0.2, label='90% Confidence Interval')
    
    ax.set_xlabel('Density')
    ax.set_ylabel('Average Speed')
    ax.set_title('Density vs Average Speed')
    ax.legend()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    plot_density_vs_speed(num_simulations=10)  # Specify the number of simulations to run