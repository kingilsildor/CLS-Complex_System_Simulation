import tkinter as tk

from src.simulation import SimulationUI

if __name__ == "__main__":
    show_ui = True
    # Set to False to run without UI
    root = tk.Tk() if show_ui else None
    ui = SimulationUI(root, show_ui=show_ui, colour_blind=False)

    if not show_ui:
        grid_states = ui.run_simulation_without_ui(
            steps=10,
            grid_size=30,
            blocks_size=10,
            lane_width=2,
            car_count=10,
            output=True,
        )
        # for grid in grid_states:
        #     print("--------------------")
        #     print(grid)
    else:
        root.mainloop()
