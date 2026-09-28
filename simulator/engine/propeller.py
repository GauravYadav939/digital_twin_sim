"""
Propeller/Load Module
Implements propeller load torque model
Reference: engine_model_specification_v0.3.txt §4.7
"""

import numpy as np


class PropellerModel:
    """
    Propeller/load model.
    Simplified quadratic load characteristic.
    """

    def __init__(self, config):
        """
        Initialize propeller model.

        Parameters from config:
        - k_load: Load coefficient [N·m·s²/rad²]
        """
        propeller_config = config['propeller']
        self.k_load = propeller_config['k_load']

    def compute_load_torque(self, omega, load_pct):
        """
        Compute load torque from propeller.

        Parameters:
        -----------
        omega : float
            Crankshaft angular velocity [rad/s]
        load_pct : float
            Load setting [%] (0-100)

        Returns:
        --------
        T_load : float
            Load torque [N·m]

        Equation (ASSUMED - simplified propeller characteristic):
        ----------------------------------------------------------
        T_load = k_load · (load_pct/100) · ω²

        This represents the squared relationship between propeller torque
        and RPM at a given pitch/load setting.

        For a fixed-pitch propeller: torque ∝ ω²
        load_pct represents effective blade pitch or flight condition.
        """
        T_load = self.k_load * (load_pct / 100.0) * (omega ** 2)
        return T_load