"""
Lubrication Module
Implements oil pressure model
Reference: engine_model_specification_v0.3.txt §4.10
"""

import numpy as np


class LubricationModel:
    """
    Oil pressure model with RPM and temperature dependence.
    """

    def __init__(self, config):
        """
        Initialize lubrication model.

        Parameters from config:
        - k_pump: Pump coefficient [Pa·s/RPM]
        - mu_ref: Reference oil viscosity [Pa·s]
        - b: Viscosity temperature coefficient [1/K]
        - T_ref: Reference temperature [K]
        - P_oil_max: Maximum oil pressure [Pa]
        - P_oil_min: Minimum oil pressure [Pa]
        """
        lub_config = config['lubrication']
        self.k_pump = lub_config['k_pump']
        self.mu_ref = lub_config['mu_ref']
        self.b = lub_config['b']
        self.T_ref = lub_config['T_ref']
        self.P_oil_max = lub_config['P_oil_max']
        self.P_oil_min = lub_config['P_oil_min']

    def compute_oil_viscosity(self, T_oil):
        """
        Compute oil viscosity as function of temperature.

        Parameters:
        -----------
        T_oil : float
            Oil temperature [K]

        Returns:
        --------
        mu : float
            Oil viscosity [Pa·s]

        Equation (ASSUMED - exponential viscosity-temperature relationship):
        ---------------------------------------------------------------------
        μ(T) = μ_ref · exp(b·(T_ref - T))

        Viscosity decreases exponentially with increasing temperature.
        """
        mu = self.mu_ref * np.exp(self.b * (self.T_ref - T_oil))
        return mu

    def compute_oil_pressure(self, N_rpm, T_oil):
        """
        Compute oil pressure.

        Parameters:
        -----------
        N_rpm : float
            Engine speed [RPM]
        T_oil : float
            Oil temperature [K]

        Returns:
        --------
        dict with keys:
            - P_oil: Oil pressure [Pa]
            - mu_oil: Oil viscosity [Pa·s]

        Equation (ASSUMED functional form, §4.10):
        ------------------------------------------
        P_oil,uncapped = k_pump · N · μ(T_oil)
        P_oil = clamp(P_oil,uncapped, P_oil,min, P_oil,max)

        Oil pressure increases with RPM (pump speed) and viscosity.
        Capped at max pressure (relief valve) and min pressure (practical floor).
        """
        mu_oil = self.compute_oil_viscosity(T_oil)
        P_oil_uncapped = self.k_pump * N_rpm * mu_oil
        P_oil = np.clip(P_oil_uncapped, self.P_oil_min, self.P_oil_max)

        return {
            'P_oil': P_oil,
            'mu_oil': mu_oil
        }