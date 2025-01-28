import tkinter as tk
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Simulation(ABC):
    def __init__(self, root):
        self.root = root

    @abstractmethod
    def start_simulation(self):
        pass

    @abstractmethod
    def pause_simulation(self):
        pass

    @abstractmethod
    def stop_simulation(self):
        pass

    @abstractmethod
    def restart_simulation(self):
        pass

    @abstractmethod
    def update_simulation(self):
        pass

    def create_plot(self, figsize: tuple = (12, 12), dpi: int = 300):
        fig = plt.Figure(figsize=figsize, dpi=dpi)
        assert isinstance(fig, plt.Figure)

        return fig

    def create_axis(
        self, figure: plt.Figure, nrows: int = 1, ncols: int = 1, index: int = 1
    ):
        """
        Create an axis in the given figure using add_gridspec and subplot.

        Params:
        -------
        - figure (plt.Figure): The figure to add the axis to.
        - nrows (int): Number of rows in the grid. Default is 1.
        - ncols (int): Number of columns in the grid. Default is 1.
        - index (int): Index of the subplot. Default is 1.

        Returns:
        --------
        - plt.Axes: The created axis.
        """
        gridspec = figure.add_gridspec(nrows, ncols)
        ax = figure.add_subplot(gridspec[index - 1])
        assert isinstance(ax, plt.Axes)

        return ax

    def create_canvas(self, figure, plot_frame, side: str = tk.TOP):
        """
        Create a canvas widget.

        Params:
        -------
        - figure: The figure to be displayed on the canvas.
        - plot_frame: The frame in which the canvas will be placed.
        - side: The side of the frame where the canvas will be placed.

        Returns:
        --------
        - tk.Canvas: The canvas widget.
        """
        canvas = FigureCanvasTkAgg(figure, plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        assert isinstance(canvas, FigureCanvasTkAgg)

        return canvas

    def create_button(
        self, control_frame: tk.Frame, text: str, command: callable, pady: int = 5
    ):
        """
        Create a button widget with a given text and command.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the button will be placed.
        - text (str): The text of the button.
        - command (callable): The function that will be called when the button is clicked.
        - Pady (int): The padding of the frame. Default is 5.

        Returns:
        --------
        - tk.Button: The button widget.
        """
        assert callable(command)
        button = tk.Button(control_frame, text=text, command=command)
        button.pack(pady=pady)
        assert isinstance(button, tk.Button)

        return button

    def create_slider(
        self,
        control_frame: tk.Frame,
        label: str,
        default_val: int | float,
        min_val: int | float,
        max_val: int | float,
        pady: int = 5,
    ):
        """
        Create a slider widget with a given label.

        Params:
        -------
        - control_frame (tk.Frame): The frame in which the slider will be placed.
        - label (str): The label of the slider.
        - default_val (int | float): The default value of the slider.
        - min_val (int | float): The minimum value of the slider.
        - max_val (int | float): The maximum value of the slider.
        - pady (int): The padding of the frame. Default is 5.

        Returns:
        --------
        - tk.Scale: The slider widget.
        """
        if (isinstance(min_val, int) and isinstance(max_val, float)) or (
            isinstance(min_val, float) and isinstance(max_val, int)
        ):
            raise ValueError("min_val and max_val must be of the same type")
        if isinstance(min_val, int) and not isinstance(default_val, int):
            raise ValueError("default_val must be an integer")
        if isinstance(min_val, float) and not isinstance(default_val, float):
            raise ValueError("default_val must be a float")

        frame = tk.Frame(control_frame)
        frame.pack(pady=pady)
        assert isinstance(frame, tk.Frame)

        label = tk.Label(frame, text=label)
        label.pack(side=tk.LEFT)
        assert isinstance(label, tk.Label)

        slider = tk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            length=200,
        )
        slider.set(default_val)
        slider.pack(side=tk.RIGHT)
        assert isinstance(slider, tk.Scale)

        return slider

    def init_metric(self):
        pass

    def save_plot(self):
        pass


class Simulation_1D(Simulation):
    def __init__(self):
        pass


class Simulation_2D(Simulation):
    def __init__(self):
        pass

    def create_cars(self):
        pass


class Simulation_2D_UI(Simulation_2D):
    def __init__(self):
        pass
