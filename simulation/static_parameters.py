from dataclasses import dataclass

from math import pi


# Rocket dataclass is used to hold the rocket parameters that don't change.

@dataclass
class Rocket:
    tank_inner_radius: float # m
    tank_outer_radius: float # m
    tank_height: float # m
    nozzle_radius: float # m
    initial_tank_pressure: float # Pa
    initial_water_ratio: float
    dry_mass: float = 1.5
    drag_coefficient: float = 0.2

    def __post_init__(self):
        self.tank_volume = pi * (self.tank_inner_radius)**2 * ((self.tank_height - 2*self.tank_outer_radius) + (4/3) * self.tank_inner_radius)
        self.initial_water_volume = self.tank_volume * self.initial_water_ratio 
        self.initial_air_volume = self.tank_volume * (1 - self.initial_water_ratio)
        self.nozzle_area = pi * (self.nozzle_radius)**2
        self.tank_cross_section_area = pi * (self.tank_outer_radius)**2
        self.dry_mass = self.dry_mass

# Environment dataclass is used to set up the environment in which the simulation is performed.

@dataclass(frozen = True)
class Environment:
    gravitational_acceleration: float = 9.81 # m/s^2
    temperature: float = 273.15 + 20 # Kelvin
    air_pressure: float = 101325 # Pa
    air_density: float = 1.225 # kg/m^3
    water_density: float = 1000 # kg/m^3
    air_adiabatic_constant: float = 1.40
    air_gas_constant: float = 287
    flow_loss_coefficient: float = 0.8