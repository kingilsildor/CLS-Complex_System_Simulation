import tkinter as tk

from src.simulation import SimulationUI

if __name__ == "__main__":
    show_ui = True
    root = tk.Tk() if show_ui else None
    ui = SimulationUI(root, show_ui=show_ui, colour_blind=False)

    if not show_ui:
        grid_states = ui.run_simulation_without_ui(
            steps=250,
            grid_size=52,
            blocks_size=10,
            lane_width=2,
            car_count=100,
        )
    else:
        root.mainloop()
