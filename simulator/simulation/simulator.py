"""
Main Simulator Class
Integrates all physics modules into a time-stepping simulation
Reference: engine_model_specification_v0.3.txt
"""

import numpy as np
import yaml
from pathlib import Path

# Import all physics modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from engine.atmosphere import AtmosphereModel
from engine.intake import IntakeModel
from engine.fuel import FuelModel
from engine.combustion import CombustionModel
from engine.mechanical import MechanicalModel
from engine.propeller import PropellerModel
from engine.energy_balance import EnergyBalanceModel
from engine.thermal import ThermalModel
from engine.lubrication import LubricationModel
from engine.vibration import VibrationModel
from sensors.sensor_model import SensorModel


class EngineSimulator:
    """
    Main UAV Piston Engine Simulator.

    Implements the complete physics chain from inputs to telemetry output.
    Based on engine_model_specification_v0.3.txt
    """

    def __init__(self, config_path=None):
        """
        Initialize simulator with configuration.

        Parameters:
        -----------
        config_path : str or Path, optional
            Path to YAML configuration file
            If None, uses default config/engine_config.yaml
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'engine_config.yaml'

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize all subsystem models
        self.atmosphere = AtmosphereModel(self.config)
        self.intake = IntakeModel(self.config)
        self.fuel = FuelModel(self.config)
        self.combustion = CombustionModel(self.config)
        self.mechanical = MechanicalModel(self.config)
        self.propeller = PropellerModel(self.config)
        self.energy_balance = EnergyBalanceModel(self.config)
        self.thermal = ThermalModel(self.config)
        self.lubrication = LubricationModel(self.config)
        self.vibration = VibrationModel(self.config)
        self.sensor = SensorModel(self.config)

        # Simulation state
        self.dt = self.config['simulation']['dt']
        self.state = None
        self.time = 0.0
        self.telemetry_history = []

    def initialize_state(self, altitude_m=0.0, T_ambient_C=15.0):
        """
        Initialize engine state at idle.

        Parameters:
        -----------
        altitude_m : float
            Initial altitude [m]
        T_ambient_C : float
            Ambient temperature [°C]

        Returns:
        --------
        state : dict
            Initial engine state

        Per v0.3 §4.6b: Engine starts already running at idle.
        No starter motor modeling - this is an explicit Phase 1 scope decision.
        """
        # Initial atmospheric conditions
        atm = self.atmosphere.compute(altitude_m, T_ambient_C)

        # Initial omega at idle
        omega_idle = self.mechanical.get_idle_omega()
        N_idle = self.mechanical.rpm_from_omega(omega_idle)

        # Initial thermal states (assume warmed up to reasonable idle temps)
        T_CHT_initial = atm['T_ambient'] + 100  # ~100°C above ambient at idle
        T_EGT_initial = atm['T_ambient'] + 200  # ~200°C above ambient
        T_oil_initial = atm['T_ambient'] + 60   # ~60°C above ambient

        self.state = {
            # Mechanical state
            'omega': omega_idle,
            'N_rpm': N_idle,

            # Thermal states
            'T_CHT': T_CHT_initial,
            'T_EGT': T_EGT_initial,
            'T_oil': T_oil_initial,

            # Operating conditions
            'altitude_m': altitude_m,
            'T_ambient': atm['T_ambient'],
            'T_ambient_C': T_ambient_C,

            # Time
            'time': 0.0
        }

        self.time = 0.0
        self.telemetry_history = []

        return self.state

    def step(self, throttle_pct, load_pct, altitude_m=None, T_ambient_C=None):
        """
        Advance simulation by one time step.

        Parameters:
        -----------
        throttle_pct : float
            Throttle position [%] (0-100)
        load_pct : float
            Engine/propeller load [%] (0-100)
        altitude_m : float, optional
            Altitude [m] (if None, uses current state)
        T_ambient_C : float, optional
            Ambient temperature offset [°C] (if None, uses current state)

        Returns:
        --------
        telemetry : dict
            Sensor measurements for this time step

        Implements the complete physics chain per v0.3:
        Inputs → Atmosphere → Intake → Fuel → Combustion → Mechanical → Thermal → Sensors
        """
        if self.state is None:
            raise RuntimeError("Simulator not initialized. Call initialize_state() first.")

        # Update operating conditions
        if altitude_m is not None:
            self.state['altitude_m'] = altitude_m
        if T_ambient_C is not None:
            self.state['T_ambient_C'] = T_ambient_C

        # Current state
        omega = self.state['omega']
        N_rpm = self.state['N_rpm']
        T_CHT = self.state['T_CHT']
        T_EGT = self.state['T_EGT']
        T_oil = self.state['T_oil']

        # 1. Atmosphere (§4.1)
        atm = self.atmosphere.compute(self.state['altitude_m'], self.state['T_ambient_C'])
        self.state['T_ambient'] = atm['T_ambient']

        # 2. Intake / Air mass flow (§4.2)
        intake_result = self.intake.compute_air_mass_flow(
            N_rpm, atm['rho_ambient'], throttle_pct)
        m_dot_air = intake_result['m_dot_air']

        # 3. Fuel (§4.3)
        fuel_result = self.fuel.compute_fuel_flow(m_dot_air)
        m_dot_fuel = fuel_result['m_dot_fuel']
        P_fuel = fuel_result['P_fuel']

        # 4. Combustion (§4.4, §4.5)
        combustion_result = self.combustion.compute(
            P_fuel, atm['T_ambient'], atm['p_ambient'])
        P_otto_ideal = combustion_result['P_otto_ideal']
        P_ind_real = combustion_result['P_ind_real']
        P_reject_cycle = combustion_result['P_reject_cycle']
        P_loss_realcycle = combustion_result['P_loss_realcycle']
        T5 = combustion_result['T5']

        # 5. Mechanical dynamics (§4.6)
        T_ind = self.mechanical.compute_indicated_torque(P_ind_real, omega)
        T_friction = self.mechanical.compute_friction_torque(omega)
        brake_result = self.mechanical.compute_brake_power(P_ind_real, omega)
        P_brake = brake_result['P_brake']
        P_friction = brake_result['P_friction']

        # 6. Propeller load (§4.7)
        T_load = self.propeller.compute_load_torque(omega, load_pct)

        # 7. Energy balance (§4.8)
        energy_result = self.energy_balance.compute_energy_split(
            P_fuel, P_otto_ideal, P_ind_real, P_brake,
            P_reject_cycle, P_loss_realcycle, P_friction)
        Q_in_CHT = energy_result['Q_in_CHT']
        Q_in_oil = energy_result['Q_in_oil']

        # 8. Update omega (integrate mechanical ODE)
        alpha = self.mechanical.compute_angular_acceleration(T_ind, T_load, T_friction)
        omega_new = self.mechanical.integrate_omega(omega, alpha, self.dt)
        N_rpm_new = self.mechanical.rpm_from_omega(omega_new)

        # 9. Thermal models (§4.9)
        T_CHT_new = self.thermal.integrate_CHT(
            T_CHT, Q_in_CHT, atm['T_ambient'], N_rpm, self.dt)
        T_EGT_new = self.thermal.integrate_EGT(T_EGT, T5, self.dt)
        T_oil_new = self.thermal.integrate_oil_temp(
            T_oil, Q_in_oil, atm['T_ambient'], self.dt)

        # 10. Lubrication (§4.10)
        lub_result = self.lubrication.compute_oil_pressure(N_rpm, T_oil)
        P_oil = lub_result['P_oil']

        # 11. Vibration (§4.11)
        vibration = self.vibration.compute_vibration(N_rpm, P_ind_real, T_load)

        # Update state
        self.state['omega'] = omega_new
        self.state['N_rpm'] = N_rpm_new
        self.state['T_CHT'] = T_CHT_new
        self.state['T_EGT'] = T_EGT_new
        self.state['T_oil'] = T_oil_new
        self.state['time'] = self.time + self.dt
        self.time = self.state['time']

        # Prepare true states for sensor model
        true_states = {
            'N_rpm': N_rpm_new,
            'T_CHT': T_CHT_new,
            'T_EGT': T_EGT_new,
            'T_oil': T_oil_new,
            'P_oil': P_oil,
            'm_dot_fuel': m_dot_fuel,
            'vibration': vibration,
            'T_ind': T_ind,
            'P_brake': P_brake,
            'throttle_pct': throttle_pct,
            'load_pct': load_pct,
            'altitude_m': self.state['altitude_m']
        }

        # 12. Sensor model (§4.12) - convert true states to telemetry
        telemetry = self.sensor.measure(true_states)

        # Add time and other useful info to telemetry
        telemetry['time'] = self.time
        telemetry['m_dot_air'] = m_dot_air
        telemetry['rho_ambient'] = atm['rho_ambient']
        telemetry['p_ambient'] = atm['p_ambient']
        telemetry['T_ambient_C'] = self.state['T_ambient_C']

        # For validation: include energy split
        telemetry['energy_split_brake_pct'] = energy_result['split_pct']['brake']
        telemetry['energy_split_exhaust_pct'] = energy_result['split_pct']['exhaust']
        telemetry['energy_split_CHT_pct'] = energy_result['split_pct']['CHT']
        telemetry['energy_split_oil_pct'] = energy_result['split_pct']['oil']
        telemetry['energy_residual_W'] = energy_result['energy_residual']

        # Store in history
        self.telemetry_history.append(telemetry)

        return telemetry

    def run_scenario(self, throttle_schedule, load_schedule, duration,
                     altitude_m=0.0, T_ambient_C=15.0, dt=None):
        """
        Run a complete simulation scenario.

        Parameters:
        -----------
        throttle_schedule : callable or float
            Either a constant throttle % or a function throttle(t) returning %
        load_schedule : callable or float
            Either a constant load % or a function load(t) returning %
        duration : float
            Simulation duration [s]
        altitude_m : float or callable
            Altitude [m] (constant or function of time)
        T_ambient_C : float or callable
            Ambient temperature [°C] (constant or function of time)
        dt : float, optional
            Time step [s] (if None, uses config default)

        Returns:
        --------
        telemetry_history : list of dict
            Complete telemetry time series
        """
        if dt is not None:
            self.dt = dt

        # Initialize
        alt_initial = altitude_m if not callable(altitude_m) else altitude_m(0)
        T_amb_initial = T_ambient_C if not callable(T_ambient_C) else T_ambient_C(0)
        self.initialize_state(alt_initial, T_amb_initial)

        # Time stepping
        num_steps = int(duration / self.dt)

        for step_idx in range(num_steps):
            t = self.time

            # Evaluate schedules
            throttle = throttle_schedule(t) if callable(throttle_schedule) else throttle_schedule
            load = load_schedule(t) if callable(load_schedule) else load_schedule
            alt = altitude_m(t) if callable(altitude_m) else altitude_m
            T_amb = T_ambient_C(t) if callable(T_ambient_C) else T_ambient_C

            # Step forward
            self.step(throttle, load, alt, T_amb)

        return self.telemetry_history

    def get_telemetry_dataframe(self):
        """
        Convert telemetry history to pandas DataFrame for analysis/export.

        Returns:
        --------
        df : pandas.DataFrame
            Telemetry as DataFrame
        """
        import pandas as pd
        return pd.DataFrame(self.telemetry_history)

    def save_telemetry_csv(self, filepath):
        """
        Save telemetry history to CSV file.

        Parameters:
        -----------
        filepath : str or Path
            Output CSV file path
        """
        df = self.get_telemetry_dataframe()
        df.to_csv(filepath, index=False)
        print(f"Telemetry saved to: {filepath}")