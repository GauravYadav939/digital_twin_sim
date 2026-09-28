"""
Energy Balance Module
Implements full energy accounting with thermal split
Reference: engine_model_specification_v0.3.txt §4.8
"""

import numpy as np


class EnergyBalanceModel:
    """
    Energy balance and thermal routing model.
    Tracks energy flow from fuel through all loss pathways.
    """

    def __init__(self, config):
        """
        Initialize energy balance model.

        Parameters from config:
        - k_reject_to_exhaust: Fraction of ideal-cycle rejection to exhaust (NEW in v0.3)
        - k_split_exhaust: Fraction of real-cycle losses to exhaust
        - k_cyl_split: Fraction of combustion engine heat to CHT (vs oil)
        """
        engine_config = config['engine']
        self.k_reject_to_exhaust = engine_config['k_reject_to_exhaust']
        self.k_split_exhaust = engine_config['k_split_exhaust']
        self.k_cyl_split = engine_config['k_cyl_split']

    def compute_energy_split(self, P_fuel, P_otto_ideal, P_ind_real,
                            P_brake, P_reject_cycle, P_loss_realcycle, P_friction):
        """
        Compute full energy balance and thermal routing.

        Parameters:
        -----------
        P_fuel : float
            Fuel chemical energy rate [W]
        P_otto_ideal : float
            Ideal Otto cycle power [W]
        P_ind_real : float
            Real indicated power [W]
        P_brake : float
            Brake power [W]
        P_reject_cycle : float
            Ideal cycle heat rejection [W]
        P_loss_realcycle : float
            Real-cycle losses [W]
        P_friction : float
            Mechanical friction power loss [W]

        Returns:
        --------
        dict with keys:
            - P_exhaust: Power to exhaust [W]
            - P_engine_heat_combustion: Combustion-sourced engine heat [W]
            - Q_in_CHT: Heat input to CHT [W]
            - Q_in_oil: Heat input to oil [W]
            - energy_residual: Energy balance check [W] (should be ~0)
            - split_pct: Dict with percentage splits

        Equations (§4.8 v0.3 with k_reject_to_exhaust):
        ------------------------------------------------
        Energy identity (exact by construction):
        P_fuel ≡ P_brake + P_reject,cycle + P_loss,realcycle + P_friction

        Thermal routing:
        P_exhaust = k_reject_to_exhaust·P_reject,cycle + k_split_exhaust·P_loss,realcycle
        P_engine_heat,combustion = (1-k_reject_to_exhaust)·P_reject,cycle
                                   + (1-k_split_exhaust)·P_loss,realcycle

        CHT/oil split:
        Q_in,CHT = k_cyl_split · P_engine_heat,combustion
        Q_in,oil = (1-k_cyl_split)·P_engine_heat,combustion + P_friction
        """
        # Exhaust pathway
        P_exhaust = (self.k_reject_to_exhaust * P_reject_cycle +
                     self.k_split_exhaust * P_loss_realcycle)

        # Engine heat from combustion (non-exhaust portion)
        P_engine_heat_combustion = ((1.0 - self.k_reject_to_exhaust) * P_reject_cycle +
                                    (1.0 - self.k_split_exhaust) * P_loss_realcycle)

        # CHT and oil heat inputs
        Q_in_CHT = self.k_cyl_split * P_engine_heat_combustion
        Q_in_oil = ((1.0 - self.k_cyl_split) * P_engine_heat_combustion + P_friction)

        # Energy bookkeeping check (Level 1 validation target)
        energy_sum = P_brake + P_reject_cycle + P_loss_realcycle + P_friction
        energy_residual = P_fuel - energy_sum

        # Percentage splits (for Level 1.5 plausibility check)
        if P_fuel > 0:
            pct_brake = 100.0 * P_brake / P_fuel
            pct_exhaust = 100.0 * P_exhaust / P_fuel
            pct_CHT = 100.0 * Q_in_CHT / P_fuel
            pct_oil = 100.0 * Q_in_oil / P_fuel
        else:
            pct_brake = pct_exhaust = pct_CHT = pct_oil = 0.0

        return {
            'P_exhaust': P_exhaust,
            'P_engine_heat_combustion': P_engine_heat_combustion,
            'Q_in_CHT': Q_in_CHT,
            'Q_in_oil': Q_in_oil,
            'energy_residual': energy_residual,
            'split_pct': {
                'brake': pct_brake,
                'exhaust': pct_exhaust,
                'CHT': pct_CHT,
                'oil': pct_oil
            }
        }