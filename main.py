import tkinter as tk
from src.simulation import SimulationUI
from src.experiment import run_experiment

if __name__ == "__main__":
    experiment = True
    show_ui = True

    if experiment:
        run_experiment(show_ui=False)

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
