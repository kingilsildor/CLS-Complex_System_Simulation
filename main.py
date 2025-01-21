import tkinter as tk

from src.simulation import SimulationUI

if __name__ == "__main__":
    show_ui = False  # Change to True to simulate with UI
    root = tk.Tk() if show_ui else None
    ui = SimulationUI(root, show_ui=show_ui)

    if not show_ui:
        grid_states = ui.run_simulation_without_ui(
            steps=100,
            grid_size=25,
            blocks_size=5,
            lane_width=2,
            car_count=50,
        )
    else:
        root.mainloop()
