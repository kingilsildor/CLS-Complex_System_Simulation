import tkinter as tk

from src.experiment import run_speed_experiment
from src.simulation import SimulationUI

if __name__ == "__main__":
    experiment = False
    show_ui = True

    if experiment:
        run_speed_experiment()
        # run_experiment()

    elif not show_ui:
        ui = SimulationUI(None, show_ui=False)
        grid_states = ui.run_simulation_without_ui(
            steps=100,
            grid_size=15,
            blocks_size=10,
            lane_width=2,
            car_count=4,
            output=False,
        )
        for state in grid_states:
            print(state)
            print("--------------------")
    else:
        root = tk.Tk()
        ui = SimulationUI(root, show_ui=True, colour_blind=False)
        root.mainloop()
