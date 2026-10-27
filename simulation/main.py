from static_parameters import *
from simulation import *
from graphs import *
from optimization import *

def Main():

    rocket1 = Rocket(
        tank_inner_radius=0.05,
        tank_outer_radius=0.051,
        tank_height=1.5,
        nozzle_radius=0.0059,
        initial_tank_pressure=2000000,
        initial_water_ratio=0.24,
        dry_mass=2
        )
    
    standard_environment = Environment()

    """
    optimization1 = singleVariableOptimization(rocket1, standard_environment, "initial_water_ratio", [0.0, 0.80])
    optimization_result = optimization1.run(number_of_points=50)

    opt_graph = Graph("initial_water_ratio", "max_height", optimization_result)
    opt_graph.show()
    """

    sim = Simulation(rocket1, standard_environment)

    result = sim.run(["height", "thrust"])

    #thrust_graph = TimeGraph("thrust", result)
    height_graph = TimeGraph("height", result)

    height_graph.show()

    



Main()