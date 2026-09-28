"""
Fuel Module
Computes fuel flow based on air flow and target AFR
Reference: engine_model_specification_v0.3.txt §4.3
"""

import numpy as np


class FuelModel:
    """
    Fuel flow model based on target air-fuel ratio.
    """

    def __init__(self, config):
        """
        Initialize fuel model.

        Parameters from config:
        - LHV: Lower heating value of fuel [J/kg] (REF: 43.5e6 for AVGAS)
        - AFR_target: Target air-fuel ratio [dimensionless] (CONFIG)
        """
        fuel_config = config['fuel']
        self.LHV = float(fuel_config['LHV'])
        self.AFR_target = float(fuel_config['AFR_target'])

    def compute_fuel_flow(self, m_dot_air):
        """
        Compute fuel mass flow rate and fuel energy rate.

        Parameters:
        -----------
        m_dot_air : float
            Air mass flow rate [kg/s]

        Returns:
        --------
        dict with keys:
            - m_dot_fuel: Fuel mass flow rate [kg/s]
            - f: Fuel-air ratio (dimensionless)
            - P_fuel: Fuel energy rate (chemical energy input) [W]

        Equations (CONFIG + REF):
        -------------------------
        AFR = ṁ_air / ṁ_fuel
        Therefore: ṁ_fuel = ṁ_air / AFR_target

        Fuel-air ratio: f = 1 / AFR

        Fuel energy rate: P_fuel = ṁ_fuel · LHV

        Note: AFR_target = 13.0 is rich of stoichiometric (AFR_stoich ≈ 14.6 for AVGAS)
        This corresponds to λ ≈ 0.89, in the best-power mixture region per FOCA data.
        """
        m_dot_fuel = m_dot_air / self.AFR_target
        f = 1.0 / self.AFR_target
        P_fuel = m_dot_fuel * self.LHV

        return {
            'm_dot_fuel': m_dot_fuel,
            'f': f,
            'P_fuel': P_fuel
        }