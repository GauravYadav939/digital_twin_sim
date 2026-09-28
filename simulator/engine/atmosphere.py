"""
Atmosphere Module
Implements ISA (International Standard Atmosphere) model
Reference: engine_model_specification_v0.3.txt §4.1
"""

import numpy as np


class AtmosphereModel:
    """
    International Standard Atmosphere (ISA) model.
    Computes atmospheric pressure, temperature, and density as a function of altitude.
    """

    def __init__(self, config):
        """
        Initialize atmosphere model with ISA parameters.

        Parameters from config:
        - T_sl: Sea-level temperature [K] (REF: 288.15 K)
        - p_sl: Sea-level pressure [Pa] (REF: 101325 Pa)
        - L: Temperature lapse rate [K/m] (REF: 0.0065 K/m)
        - R: Specific gas constant for air [J/(kg·K)] (REF: 287.05)
        - g: Gravitational acceleration [m/s²] (REF: 9.80665)
        """
        atm_config = config['atmosphere']
        self.T_sl = atm_config['T_sl']
        self.p_sl = atm_config['p_sl']
        self.L = atm_config['L']
        self.R = atm_config['R']
        self.g = atm_config['g']

    def compute(self, altitude_m, T_ambient_offset_C=0.0):
        """
        Compute atmospheric properties at given altitude.

        Parameters:
        -----------
        altitude_m : float
            Altitude above sea level [m]
        T_ambient_offset_C : float
            Ambient temperature offset from ISA [°C]

        Returns:
        --------
        dict with keys:
            - T_ambient: Ambient temperature [K]
            - p_ambient: Ambient pressure [Pa]
            - rho_ambient: Ambient air density [kg/m³]

        Equations (REF - ISA standard):
        -------------------------------
        T(h) = T_sl - L·h
        p(h) = p_sl · (T(h)/T_sl)^(g/(R·L))
        ρ(h) = p(h) / (R·T(h))
        """
        # ISA temperature at altitude
        T_ISA = self.T_sl - self.L * altitude_m

        # Apply ambient temperature offset
        T_ambient = T_ISA + T_ambient_offset_C  # offset already in K equivalent

        # Atmospheric pressure (barometric formula)
        # Note: This uses ISA temperature for pressure calculation,
        # then actual ambient temperature for density
        if altitude_m < 11000:  # Troposphere
            p_ambient = self.p_sl * (T_ISA / self.T_sl) ** (self.g / (self.R * self.L))
        else:
            # Simplified - for typical UAV altitudes, troposphere formula suffices
            p_ambient = self.p_sl * (T_ISA / self.T_sl) ** (self.g / (self.R * self.L))

        # Air density from ideal gas law
        rho_ambient = p_ambient / (self.R * T_ambient)

        return {
            'T_ambient': T_ambient,
            'p_ambient': p_ambient,
            'rho_ambient': rho_ambient
        }

    def get_intake_conditions(self, altitude_m, T_ambient_offset_C=0.0):
        """
        Get intake air conditions (convenience wrapper).

        Returns:
        --------
        dict with keys:
            - T_intake: Intake air temperature [K]
            - p_intake: Intake air pressure [Pa]
            - rho_intake: Intake air density [kg/m³]
        """
        atm = self.compute(altitude_m, T_ambient_offset_C)
        return {
            'T_intake': atm['T_ambient'],
            'p_intake': atm['p_ambient'],
            'rho_intake': atm['rho_ambient']
        }