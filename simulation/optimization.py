from static_parameters import *
from simulation import *
from graphs import *


class singleVariableOptimization:
    def __init__(self, rocket: Rocket, environment: Environment, parameter: str, span: list):
        self.rocket = rocket
        self.environment = environment
        self.parameter_string = parameter
        self.parameter_attribute = getattr(rocket, self.parameter_string)
        self.first = span[0]
        self.last = span[-1]

    def run(self, number_of_points):

        maximum_heights = []
        parameter_values = []

        for value in np.linspace(self.first, self.last, number_of_points):
            setattr(self.rocket, self.parameter_string, value)
            self.rocket.__post_init__()

            simulation = Simulation(self.rocket, self.environment)
            simulation_result = simulation.run(["height"])

            maximum_heights.append(simulation_result.height.max())
            parameter_values.append(value)

        result = OptimizationResult()

        result.addQuantity("max_height")
        result.addValues("max_height", maximum_heights)

        result.addQuantity(self.parameter_string)
        result.addValues(self.parameter_string, parameter_values)

        return result

