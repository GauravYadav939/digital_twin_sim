"""
Intake/Air Mass Flow Module
Implements volumetric efficiency model and air mass flow calculation
Reference: engine_model_specification_v0.3.txt §4.2
"""

import numpy as np


class IntakeModel:
    """
    Air intake model with volumetric efficiency.
    Computes air mass flow rate as a function of RPM, density, and throttle.
    """

    def __init__(self, config):
        """
        Initialize intake model.

        Parameters from config:
        - n_cyl: Number of cylinders
        - displacement: Total engine displacement [m³]
        - eta_v_max: Maximum volumetric efficiency (ASSUMED)
        - k_v: VE decay coefficient (ASSUMED)
        - N_ref: Reference RPM for VE curve [RPM] (ASSUMED)
        """
        engine_config = config['engine']
        self.n_cyl = engine_config['n_cyl']
        self.V_disp_total = engine_config['displacement']
        self.eta_v_max = engine_config['eta_v_max']
        self.k_v = engine_config['k_v']
        self.N_ref = engine_config['N_ref']

        # Displacement per cylinder
        self.V_cyl = self.V_disp_total / self.n_cyl

    def compute_volumetric_efficiency(self, N_rpm):
        """
        Compute volumetric efficiency as a function of RPM.

        Parameters:
        -----------
        N_rpm : float
            Engine speed [RPM]

        Returns:
        --------
        eta_v : float
            Volumetric efficiency (dimensionless, 0-1)

        Equation (ASSUMED functional form):
        -----------------------------------
        η_v(N) = η_v,max · exp(-k_v · |N - N_ref| / N_ref)

        This represents a peak near N_ref with decay at higher/lower speeds
        due to intake dynamics, valve timing, and flow losses.
        """
        eta_v = self.eta_v_max * np.exp(-self.k_v * np.abs(N_rpm - self.N_ref) / self.N_ref)
        return eta_v

    def compute_air_mass_per_cycle(self, rho_intake, eta_v):
        """
        Compute air mass inducted per engine cycle.

        Parameters:
        -----------
        rho_intake : float
            Intake air density [kg/m³]
        eta_v : float
            Volumetric efficiency (dimensionless)

        Returns:
        --------
        m_air_cycle : float
            Air mass per cycle [kg/cycle]

        Equation (DERIVED):
        ------------------
        m_air,cycle = ρ_intake · V_disp,total · η_v
        """
        m_air_cycle = rho_intake * self.V_disp_total * eta_v
        return m_air_cycle

    def compute_air_mass_flow(self, N_rpm, rho_intake, throttle_pct):
        """
        Compute air mass flow rate.

        Parameters:
        -----------
        N_rpm : float
            Engine speed [RPM]
        rho_intake : float
            Intake air density [kg/m³]
        throttle_pct : float
            Throttle position [%] (0-100)

        Returns:
        --------
        dict with keys:
            - m_dot_air: Air mass flow rate [kg/s]
            - eta_v: Volumetric efficiency used
            - m_air_cycle: Air mass per cycle [kg/cycle]

        Equation (DERIVED from §4.2):
        -----------------------------
        For a 4-stroke engine:
        - Each cylinder fires once every 2 crankshaft revolutions
        - For n_cyl cylinders: n_cyl/2 power strokes per revolution
        - At N RPM: N/60 revolutions per second

        ṁ_air = m_air,cycle · n_cyl · (N/60) / 2
              = m_air,cycle · n_cyl · N / 120

        Throttle effect: Simple linear scaling of effective VE
        (approximation - real throttle dynamics are more complex)
        """
        # Throttle-modified volumetric efficiency
        eta_v_base = self.compute_volumetric_efficiency(N_rpm)
        eta_v_effective = eta_v_base * (throttle_pct / 100.0)

        # Air mass per cycle
        m_air_cycle = self.compute_air_mass_per_cycle(rho_intake, eta_v_effective)

        # Air mass flow rate
        # n_cyl cylinders, N/60 rev/s, 1 intake stroke per 2 revolutions
        m_dot_air = m_air_cycle * self.n_cyl * (N_rpm / 120.0)

        return {
            'm_dot_air': m_dot_air,
            'eta_v': eta_v_effective,
            'm_air_cycle': m_air_cycle
        }