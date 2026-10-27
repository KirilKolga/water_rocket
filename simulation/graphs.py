from static_parameters import *
from simulation import *

import matplotlib.pyplot as plt


class Graph:
    def __init__(self, quantity_x: str, quantity_y: str, result: SimulationResult):
        self.result = result
        self.quantity_x_string = quantity_x
        self.quantity_y_string = quantity_y
        self.quantity_x = getattr(result, quantity_x)
        self.quantity_y = getattr(result, quantity_y)

    def show(self):
        plt.plot(self.quantity_x, self.quantity_y)
        plt.xlabel(valid_cols[self.quantity_x_string] if self.quantity_x_string in valid_cols else self.quantity_x_string)
        plt.ylabel(valid_cols[self.quantity_y_string] if self.quantity_y_string in valid_cols else self.quantity_y_string)
        plt.title(self.quantity_y_string + " vs. " + self.quantity_x_string)

        plt.show()


class TimeGraph:
    def __init__(self, quantity: str, result: SimulationResult):
        self.result = result
        self.quantity_string = quantity
        self.quantity = getattr(result, quantity)

    def show(self):
        plt.plot(self.result.time, self.quantity)
        plt.xlabel("Time (s)")
        plt.ylabel(valid_cols[self.quantity_string] if self.quantity_string in valid_cols else self.quantity_string)
        plt.title(f"{self.quantity_string} vs. time \n (max value: {self.quantity.max():.1f})")

        plt.show()


