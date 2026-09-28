"""
Vibration Module
Implements vibration proxy model
Reference: engine_model_specification_v0.3.txt §4.11
"""

import numpy as np


class VibrationModel:
    """
    Vibration proxy model.
    Simplified representation of engine vibration based on operating state.
    """

    def __init__(self, config):
        """
        Initialize vibration model.

        Parameters from config:
        - k_v1: Vibration coefficient 1 (ASSUMED)
        - k_v2: Vibration coefficient 2 (ASSUMED)
        """
        vib_config = config['vibration']
        self.k_v1 = vib_config['k_v1']
        self.k_v2 = vib_config['k_v2']

    def compute_vibration(self, N_rpm, P_ind_real, T_load):
        """
        Compute vibration proxy.

        Parameters:
        -----------
        N_rpm : float
            Engine speed [RPM]
        P_ind_real : float
            Real indicated power [W]
        T_load : float
            Load torque [N·m]

        Returns:
        --------
        vibration : float
            Vibration proxy [dimensionless RMS-like value]

        Equation (ASSUMED proxy, §4.11):
        ---------------------------------
        vibration = k_v1·N + k_v2·P_ind,real·T_load

        This is a simplified proxy representing:
        - Base vibration from reciprocating/rotating mass (∝ RPM)
        - Load-dependent vibration from combustion/torque variation

        NOT a resolved frequency spectrum or physical acceleration.
        Trend only: higher RPM and higher load → higher vibration.
        """
        vibration = self.k_v1 * N_rpm + self.k_v2 * P_ind_real * T_load
        return vibration