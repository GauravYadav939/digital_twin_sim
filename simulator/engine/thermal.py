"""
Thermal Module
Implements CHT, EGT, and oil temperature models
Reference: engine_model_specification_v0.3.txt §4.9
"""

import numpy as np


class ThermalModel:
    """
    Thermal model for cylinder head temperature (CHT),
    exhaust gas temperature (EGT), and oil temperature.
    """

    def __init__(self, config):
        """
        Initialize thermal model.

        Parameters from config:
        - C_CHT: CHT thermal capacitance [J/K]
        - h_cool_base: Base cooling coefficient [W/(m²·K)]
        - A_fin: Effective finned cooling area [m²]
        - tau_EGT: EGT time constant [s]
        - C_oil: Oil thermal capacitance [J/K]
        - h_oilcool: Oil cooler heat transfer coefficient [W/(m²·K)]
        - A_oilcooler: Oil cooler effective area [m²]
        - T_ambient_offset: Offset for temperature conversions
        """
        thermal_config = config['thermal']
        self.C_CHT = thermal_config['C_CHT']
        self.h_cool_base = thermal_config['h_cool_base']
        self.A_fin = thermal_config['A_fin']
        self.tau_EGT = thermal_config['tau_EGT']
        self.C_oil = thermal_config['C_oil']
        self.h_oilcool = thermal_config['h_oilcool']
        self.A_oilcooler = thermal_config['A_oilcooler']

    def compute_cooling_coefficient(self, N_rpm):
        """
        Compute cooling heat transfer coefficient as function of RPM.

        Parameters:
        -----------
        N_rpm : float
            Engine speed [RPM]

        Returns:
        --------
        h_cool : float
            Cooling coefficient [W/(m²·K)]

        Equation (ASSUMED - convective cooling increases with airflow/RPM):
        -------------------------------------------------------------------
        h_cool = h_cool_base · (1 + k_cool·N/N_ref)

        Simplified: use linear scaling for now
        """
        # Simple RPM-dependent cooling (more RPM -> more cooling air flow)
        h_cool = self.h_cool_base * (1.0 + 0.5 * N_rpm / 2400.0)
        return h_cool

    def compute_CHT_derivative(self, T_CHT, Q_in_CHT, T_ambient, N_rpm):
        """
        Compute CHT rate of change.

        Parameters:
        -----------
        T_CHT : float
            Current CHT [K]
        Q_in_CHT : float
            Heat input to cylinder head [W]
        T_ambient : float
            Ambient temperature [K]
        N_rpm : float
            Engine speed [RPM]

        Returns:
        --------
        dT_CHT_dt : float
            CHT rate of change [K/s]

        Equation (lumped thermal ODE, §4.9):
        ------------------------------------
        C_CHT · dT_CHT/dt = Q_in,CHT - Q_cool
        Q_cool = h_cool(N) · A_fin · (T_CHT - T_ambient)

        dT_CHT/dt = (Q_in,CHT - h_cool·A_fin·(T_CHT - T_ambient)) / C_CHT
        """
        h_cool = self.compute_cooling_coefficient(N_rpm)
        Q_cool = h_cool * self.A_fin * (T_CHT - T_ambient)
        dT_CHT_dt = (Q_in_CHT - Q_cool) / self.C_CHT
        return dT_CHT_dt

    def integrate_CHT(self, T_CHT_current, Q_in_CHT, T_ambient, N_rpm, dt):
        """
        Integrate CHT forward one time step (Euler).

        Parameters:
        -----------
        T_CHT_current : float
            Current CHT [K]
        Q_in_CHT : float
            Heat input [W]
        T_ambient : float
            Ambient temperature [K]
        N_rpm : float
            Engine speed [RPM]
        dt : float
            Time step [s]

        Returns:
        --------
        T_CHT_new : float
            New CHT [K]
        """
        dT_CHT_dt = self.compute_CHT_derivative(T_CHT_current, Q_in_CHT, T_ambient, N_rpm)
        T_CHT_new = T_CHT_current + dT_CHT_dt * dt
        return T_CHT_new

    def compute_EGT_derivative(self, T_EGT_current, T5):
        """
        Compute EGT rate of change (first-order lag).

        Parameters:
        -----------
        T_EGT_current : float
            Current EGT measurement [K]
        T5 : float
            Otto cycle exhaust temperature (target) [K]

        Returns:
        --------
        dT_EGT_dt : float
            EGT rate of change [K/s]

        Equation (first-order lag, §4.9):
        ----------------------------------
        τ_EGT · dT_EGT/dt = T5 - T_EGT
        dT_EGT/dt = (T5 - T_EGT) / τ_EGT

        This represents sensor/transport lag, not the true instantaneous
        exhaust gas temperature.
        """
        dT_EGT_dt = (T5 - T_EGT_current) / self.tau_EGT
        return dT_EGT_dt

    def integrate_EGT(self, T_EGT_current, T5, dt):
        """
        Integrate EGT forward one time step.

        Returns:
        --------
        T_EGT_new : float
            New EGT [K]
        """
        dT_EGT_dt = self.compute_EGT_derivative(T_EGT_current, T5)
        T_EGT_new = T_EGT_current + dT_EGT_dt * dt
        return T_EGT_new

    def compute_oil_temp_derivative(self, T_oil, Q_in_oil, T_ambient):
        """
        Compute oil temperature rate of change.

        Parameters:
        -----------
        T_oil : float
            Current oil temperature [K]
        Q_in_oil : float
            Heat input to oil [W]
        T_ambient : float
            Ambient temperature [K]

        Returns:
        --------
        dT_oil_dt : float
            Oil temperature rate of change [K/s]

        Equation (lumped thermal ODE, §4.9):
        ------------------------------------
        C_oil · dT_oil/dt = Q_in,oil - Q_oilcool
        Q_oilcool = h_oilcool · A_oilcooler · (T_oil - T_ambient)

        dT_oil/dt = (Q_in,oil - h_oilcool·A_oilcooler·(T_oil - T_ambient)) / C_oil
        """
        Q_oilcool = self.h_oilcool * self.A_oilcooler * (T_oil - T_ambient)
        dT_oil_dt = (Q_in_oil - Q_oilcool) / self.C_oil
        return dT_oil_dt

    def integrate_oil_temp(self, T_oil_current, Q_in_oil, T_ambient, dt):
        """
        Integrate oil temperature forward one time step.

        Returns:
        --------
        T_oil_new : float
            New oil temperature [K]
        """
        dT_oil_dt = self.compute_oil_temp_derivative(T_oil_current, Q_in_oil, T_ambient)
        T_oil_new = T_oil_current + dT_oil_dt * dt
        return T_oil_new