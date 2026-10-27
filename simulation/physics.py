from math import *
import numpy as np
from static_parameters import *
from scipy.integrate import solve_ivp


class FlightPhase:
    def __init__(self, rocket: Rocket, environment: Environment):
        self.rocket = rocket
        self.environment = environment

    def airResistance(self, current_velocity):
        return (0.5 * self.environment.air_density * self.rocket.tank_cross_section_area 
                    * self.rocket.drag_coefficient * (current_velocity * abs(current_velocity)))
    

class WaterPhase(FlightPhase):

    def __init__(self, rocket: Rocket, environment: Environment):
        super().__init__(rocket, environment)

        self.air_mass = (self.rocket.initial_tank_pressure * self.rocket.initial_air_volume 
                         / (self.environment.air_gas_constant * self.environment.temperature))

    def totalMass(self, current_air_volume):
        return (self.rocket.dry_mass + 
                self.environment.water_density * (self.rocket.tank_volume - current_air_volume) + 
                self.air_mass)

    def tankPressure(self, current_air_volume):
        return (self.rocket.initial_tank_pressure * 
                (self.rocket.initial_air_volume / current_air_volume)**(self.environment.air_adiabatic_constant))

    def exhaustVelocity(self, current_air_volume):
        pressure_difference = self.tankPressure(current_air_volume) - self.environment.air_pressure
        if pressure_difference >= 0:
            return sqrt(2*(pressure_difference) / self.environment.water_density)
        else: return 0.0

    def airFlowRate(self, current_air_volume):
        return self.rocket.nozzle_area * self.exhaustVelocity(current_air_volume) * self.environment.flow_loss_coefficient

    def airMassFlowRate(self, current_air_volume):
        return self.environment.water_density * self.airFlowRate(current_air_volume)

    def thrust(self, current_air_volume):
        return self.airMassFlowRate(current_air_volume) * self.exhaustVelocity(current_air_volume)

    def gravity(self, current_air_volume):
        return self.totalMass(current_air_volume) * self.environment.gravitational_acceleration

    def derivatives(self, t, state):
        height, velocity, air_volume = state

        # Derivative of the air volume / air volume flow rate
        air_volume_derivative = self.airFlowRate(air_volume)

        acceleration = ((self.thrust(air_volume) - self.gravity(air_volume) - self.airResistance(velocity)) 
                        / self.totalMass(air_volume))

        return [velocity, acceleration, air_volume_derivative]

    def waterIsOut(self, t, state):
        return self.rocket.tank_volume - state[2]
    waterIsOut.terminal = True
    waterIsOut.direction = -1

    def run(self, initial_state: list, initial_time):

        result = solve_ivp(
            fun=self.derivatives,
            t_span=[initial_time, 1000.0],
            y0=initial_state,
            events=self.waterIsOut,
            max_step=0.001
        )
        return result

class AirPhase(FlightPhase):
    def isChocked(self, current_air_mass, current_air_temperature): 
        return self.exhaustPressure(current_air_mass, current_air_temperature) > self.environment.air_pressure

    def tankPressure(self, current_air_mass, current_air_temperature):
        return current_air_mass * current_air_temperature * self.environment.air_gas_constant / self.rocket.tank_volume

    def exhaustPressure(self, current_air_mass, current_air_temperature):
        return (self.tankPressure(current_air_mass, current_air_temperature) 
                * (2 / (self.environment.air_adiabatic_constant + 1))**(self.environment.air_adiabatic_constant 
                                                                        / (self.environment.air_adiabatic_constant - 1)))

    def exhaustTemperature(self, current_air_mass, current_air_temperature):
        if self.isChocked(current_air_mass, current_air_temperature): 
            return 2 * current_air_temperature / (self.environment.air_adiabatic_constant + 1)
        else: 
            return (current_air_temperature * (self.tankPressure(current_air_mass, current_air_temperature) / self.environment.air_pressure)**((1 - self.environment.air_adiabatic_constant) / self.environment.air_adiabatic_constant))

    def mach_number(self, current_air_mass, current_air_temperature):
        inside_sqrt = ((2 * ((self.environment.air_pressure / self.tankPressure(current_air_mass, current_air_temperature))**((1 - self.environment.air_adiabatic_constant) / self.environment.air_adiabatic_constant) - 1)) 
                            / (self.environment.air_adiabatic_constant - 1))
        if inside_sqrt <= 0: return 0.0
        else:
            return sqrt(inside_sqrt)

    def exhaustVelocity(self, current_air_mass, current_air_temperature):
        if self.isChocked(current_air_mass, current_air_temperature):
            return sqrt(self.environment.air_adiabatic_constant * self.environment.air_gas_constant 
                                * self.exhaustTemperature(current_air_mass, current_air_temperature))
        else:
            return (self.mach_number(current_air_mass, current_air_temperature) 
                            * sqrt(self.environment.air_adiabatic_constant * self.environment.air_gas_constant 
                                * self.exhaustTemperature(current_air_mass, current_air_temperature)))

    def exhaustDensity(self, current_air_mass, current_air_temperature):
        if self.isChocked(current_air_mass, current_air_temperature):
            return (self.exhaustPressure(current_air_mass, current_air_temperature) 
                            / (self.environment.air_gas_constant * self.exhaustTemperature(current_air_mass, current_air_temperature)))
        else:
            return (self.environment.air_pressure / (self.environment.air_gas_constant 
                                                                * self.exhaustTemperature(current_air_mass, current_air_temperature)))

    def airMassFlowRate(self, current_air_mass, current_air_temperature):
        return (self.environment.flow_loss_coefficient 
                                * self.rocket.nozzle_area 
                                * self.exhaustDensity(current_air_mass, current_air_temperature)
                                * self.exhaustVelocity(current_air_mass, current_air_temperature))

    def thrust(self, current_air_mass, current_air_temperature):
        if self.isChocked(current_air_mass, current_air_temperature):
            return (self.airMassFlowRate(current_air_mass, current_air_temperature) 
                    * self.exhaustVelocity(current_air_mass, current_air_temperature) 
                            + (self.exhaustPressure(current_air_mass, current_air_temperature) - self.environment.air_pressure) 
                            * self.rocket.nozzle_area)
        else: 
            return (self.airMassFlowRate(current_air_mass, current_air_temperature) 
                    * self.exhaustVelocity(current_air_mass, current_air_temperature))

    def derivatives(self, t, state):
        height, velocity, air_temperature, air_mass = state

        if self.tankPressure(air_mass, air_temperature) <= self.environment.air_pressure:
            acceleration = ((-self.airResistance(velocity)) / (self.rocket.dry_mass + air_mass)) - self.environment.gravitational_acceleration
            return [velocity, acceleration, 0.0, 0.0]

        air_mass_flow_rate = self.airMassFlowRate(air_mass, air_temperature)

        air_temperature_derivative = -air_mass_flow_rate * air_temperature * (self.environment.air_adiabatic_constant - 1) / air_mass

        acceleration = ((self.thrust(air_mass, air_temperature) - self.airResistance(velocity)) / (self.rocket.dry_mass + air_mass)) - self.environment.gravitational_acceleration

        return [velocity, acceleration, air_temperature_derivative, -air_mass_flow_rate]

    def equalPressure(self, t, state):
        return self.tankPressure(state[3], state[2]) - self.environment.air_pressure

    equalPressure.terminal = True
    equalPressure.direction = -1


    def run(self, initial_state: list, initial_time):
        result = solve_ivp(
            fun=self.derivatives,
            t_span=[initial_time, 1000.0],
            y0=initial_state,
            events=self.equalPressure,
            max_step=0.001
        )

        return result

class BallisticPhase(FlightPhase):
    def derivatives(self, t, state):
        height, velocity = state

        acceleration = -self.airResistance(velocity) / self.rocket.dry_mass - self.environment.gravitational_acceleration

        return [velocity, acceleration]

    def hitGround(self, t, state):
        return state[0]

    hitGround.terminal = True
    hitGround.direction = -1

    def run(self, initial_state: list, initial_time):
        result = solve_ivp(
            fun=self.derivatives,
            t_span=[initial_time, 1000.0],
            y0=initial_state,
            events=self.hitGround,
            max_step=0.1
        )
        return result