import tkinter as tk

from src.simulation import SimulationUI


def main():
    show_ui = True  # Set to False to run without UI
    root = tk.Tk() if show_ui else None
    ui = SimulationUI(root, show_ui=show_ui, colour_blind=False)

    if not show_ui:
        grid_states = ui.run_simulation_without_ui(
            steps=100,
            grid_size=15,
            blocks_size=10,
            lane_width=2,
            car_count=4,
        )
        for state in grid_states:
            print(state)
            print("--------------------")
    else:
        root.mainloop()


if __name__ == "__main__":
    main()
