"""
Combustion Module
Implements ideal Otto cycle and real-cycle corrections
Reference: engine_model_specification_v0.3.txt §4.4, §4.5
"""

import numpy as np


class CombustionModel:
    """
    Combustion model using ideal Otto-cycle approximation with real-cycle corrections.
    """

    def __init__(self, config):
        """
        Initialize combustion model.

        Parameters from config:
        - r: Compression ratio (CONFIG)
        - gamma: Ratio of specific heats for combustion products (ASSUMED)
        - eta_ind_real: Real indicated efficiency (ASSUMED - requires calibration)
        """
        engine_config = config['engine']
        self.r = engine_config['r']
        self.gamma = engine_config['gamma']
        self.eta_ind_real = engine_config['eta_ind_real']

        # Compute ideal Otto cycle efficiency (DERIVED from thermodynamics)
        self.eta_otto_ideal = 1.0 - (1.0 / self.r ** (self.gamma - 1.0))

    def compute_ideal_otto_cycle(self, P_fuel, T_intake, p_intake):
        """
        Compute ideal Otto cycle temperatures and ideal power.

        Parameters:
        -----------
        P_fuel : float
            Fuel energy rate [W]
        T_intake : float
            Intake air temperature [K]
        p_intake : float
            Intake pressure [Pa]

        Returns:
        --------
        dict with keys:
            - eta_otto_ideal: Ideal Otto cycle efficiency
            - P_otto_ideal: Ideal Otto cycle power output [W]
            - P_reject_cycle: Ideal cycle heat rejection [W]
            - T1: State 1 temperature (intake) [K]
            - T2: State 2 temperature (after compression) [K]
            - T3: State 3 temperature (after combustion) [K]
            - T4: State 4 temperature (after expansion) [K]
            - T5: State 5 temperature (after heat rejection, exhaust proxy) [K]

        Equations (DERIVED - ideal Otto cycle):
        ---------------------------------------
        η_otto,ideal = 1 - 1/r^(γ-1)  [NASA GRC, standard thermodynamics]

        P_otto,ideal = η_otto,ideal · P_fuel
        P_reject,cycle = (1 - η_otto,ideal) · P_fuel

        Otto cycle state temperatures:
        T1 = T_intake
        T2 = T1 · r^(γ-1)           [isentropic compression]
        T3 = T2 + Q_in/(m_cv)       [const-volume heat addition, simplified]
        T4 = T3 / r^(γ-1)           [isentropic expansion]
        T5 = T1                     [const-volume heat rejection back to T1]

        For lumped-parameter purposes, we approximate T3 scaling with fuel input.
        """
        # Ideal cycle efficiency (already computed in __init__)
        eta_otto_ideal = self.eta_otto_ideal

        # Ideal power and rejection
        P_otto_ideal = eta_otto_ideal * P_fuel
        P_reject_cycle = (1.0 - eta_otto_ideal) * P_fuel

        # Cycle temperatures (simplified lumped model)
        T1 = T_intake
        T2 = T1 * (self.r ** (self.gamma - 1.0))

        # T3 estimation: empirical scaling
        # For a real engine, T3 depends on fuel quantity and mixture
        # Approximate peak cycle temp ~2000-2500 K at full load
        # Scale with fuel energy input
        T3_base = 2200.0  # Representative peak combustion temp [K]
        T3 = T2 + (T3_base - T2) * min(1.0, P_fuel / 100000.0)  # Scale with power

        T4 = T3 / (self.r ** (self.gamma - 1.0))
        T5 = T1  # Idealized return to intake temp

        return {
            'eta_otto_ideal': eta_otto_ideal,
            'P_otto_ideal': P_otto_ideal,
            'P_reject_cycle': P_reject_cycle,
            'T1': T1,
            'T2': T2,
            'T3': T3,
            'T4': T4,
            'T5': T5
        }

    def compute_real_indicated_power(self, P_otto_ideal):
        """
        Compute real indicated power with efficiency losses.

        Parameters:
        -----------
        P_otto_ideal : float
            Ideal Otto cycle power [W]

        Returns:
        --------
        dict with keys:
            - P_ind_real: Real indicated power [W]
            - P_loss_realcycle: Real-cycle losses [W]
            - eta_ind_real: Real indicated efficiency

        Equations (ASSUMED efficiency correction):
        -------------------------------------------
        P_ind,real = η_ind,real · P_otto,ideal
        P_loss,realcycle = (1 - η_ind,real) · P_otto,ideal

        Real-cycle losses account for:
        - Incomplete combustion
        - Heat transfer during compression/expansion
        - Valve timing effects
        - Pumping losses
        - Other non-ideal effects
        """
        P_ind_real = self.eta_ind_real * P_otto_ideal
        P_loss_realcycle = (1.0 - self.eta_ind_real) * P_otto_ideal

        return {
            'P_ind_real': P_ind_real,
            'P_loss_realcycle': P_loss_realcycle,
            'eta_ind_real': self.eta_ind_real
        }

    def compute(self, P_fuel, T_intake, p_intake):
        """
        Complete combustion calculation.

        Returns:
        --------
        dict with all cycle parameters
        """
        otto = self.compute_ideal_otto_cycle(P_fuel, T_intake, p_intake)
        real = self.compute_real_indicated_power(otto['P_otto_ideal'])

        return {**otto, **real}