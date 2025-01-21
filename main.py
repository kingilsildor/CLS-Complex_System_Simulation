import tkinter as tk

from src.simulation import SimulationUI

if __name__ == "__main__":
    show_ui = True  # Running without UI
    root = tk.Tk() if show_ui else None
    ui = SimulationUI(root, show_ui=show_ui, colour_blind=True, drive_on_right=True)

    if not show_ui:
        grid_states = ui.run_simulation_without_ui(
            steps=250,  # Reduced steps for testing
            grid_size=52,  # 25x25 grid
            blocks_size=10,  # 5x5 blocks
            lane_width=2,  # 2-cell wide lanes
            car_count=100,  # Reasonable number for this grid size
        )
    else:
        root.mainloop()
