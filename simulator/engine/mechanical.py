"""
Mechanical Dynamics Module
Implements crankshaft dynamics with omega_floor guards
Reference: engine_model_specification_v0.3.txt §4.6
"""

import numpy as np


class MechanicalModel:
    """
    Mechanical dynamics model for crankshaft rotation.
    Includes numerical guards for omega -> 0 as per v0.3 §4.6a/b.
    """

    def __init__(self, config):
        """
        Initialize mechanical model.

        Parameters from config:
        - J: Crankshaft rotational inertia [kg·m²]
        - T_friction0: Friction torque constant [N·m]
        - c_friction: Friction linear coefficient [N·m·s/rad]
        - N_floor: Numerical floor RPM [RPM] (§4.6a)
        - omega_idle_rpm: Idle speed [RPM] (for initialization)
        """
        engine_config = config['engine']
        self.J = engine_config['J']
        self.T_friction0 = engine_config['T_friction0']
        self.c_friction = engine_config['c_friction']
        self.N_floor = engine_config['N_floor']
        self.omega_idle_rpm = engine_config['omega_idle_rpm']

        # Convert floor RPM to rad/s
        self.omega_floor = 2.0 * np.pi * self.N_floor / 60.0

    def compute_friction_torque(self, omega):
        """
        Compute friction torque.

        Parameters:
        -----------
        omega : float
            Crankshaft angular velocity [rad/s]

        Returns:
        --------
        T_friction : float
            Friction torque [N·m]

        Equation (ASSUMED functional form):
        -----------------------------------
        T_friction(ω) = T_friction0 + c_friction·ω

        This represents Coulomb friction plus viscous friction.
        """
        T_friction = self.T_friction0 + self.c_friction * omega
        return T_friction

    def compute_indicated_torque(self, P_ind_real, omega):
        """
        Compute indicated torque from indicated power.

        Parameters:
        -----------
        P_ind_real : float
            Real indicated power [W]
        omega : float
            Crankshaft angular velocity [rad/s]

        Returns:
        --------
        T_ind : float
            Indicated torque [N·m]

        Equation (REF - standard mechanics, §4.6a with guard):
        -------------------------------------------------------
        T_ind = P_ind,real / ω_div
        where ω_div = max(ω, ω_floor)

        The floor guard prevents division by zero and is purely numerical.
        The true analytic limit as ω→0 is finite (cranking torque).
        """
        omega_div = max(omega, self.omega_floor)
        T_ind = P_ind_real / omega_div
        return T_ind

    def compute_brake_power(self, P_ind_real, omega):
        """
        Compute brake power (power at crankshaft output).

        Parameters:
        -----------
        P_ind_real : float
            Real indicated power [W]
        omega : float
            Crankshaft angular velocity [rad/s]

        Returns:
        --------
        dict with keys:
            - P_brake: Brake power [W]
            - P_friction: Friction power loss [W]
            - T_friction: Friction torque [N·m]

        Equations:
        ----------
        T_friction = T_friction0 + c_friction·ω
        P_friction = T_friction · ω
        P_brake = P_ind,real - P_friction
        """
        T_friction = self.compute_friction_torque(omega)
        P_friction = T_friction * omega
        P_brake = P_ind_real - P_friction

        return {
            'P_brake': P_brake,
            'P_friction': P_friction,
            'T_friction': T_friction
        }

    def compute_angular_acceleration(self, T_ind, T_load, T_friction):
        """
        Compute angular acceleration from torque balance.

        Parameters:
        -----------
        T_ind : float
            Indicated torque [N·m]
        T_load : float
            Load torque (from propeller) [N·m]
        T_friction : float
            Friction torque [N·m]

        Returns:
        --------
        alpha : float
            Angular acceleration [rad/s²]

        Equation (REF - rigid body dynamics):
        -------------------------------------
        J·dω/dt = T_ind - T_load - T_friction
        α = dω/dt = (T_ind - T_load - T_friction) / J
        """
        alpha = (T_ind - T_load - T_friction) / self.J
        return alpha

    def integrate_omega(self, omega_current, alpha, dt):
        """
        Integrate angular velocity with floor clamp (§4.6b).

        Parameters:
        -----------
        omega_current : float
            Current angular velocity [rad/s]
        alpha : float
            Angular acceleration [rad/s²]
        dt : float
            Time step [s]

        Returns:
        --------
        omega_new : float
            New angular velocity [rad/s], clamped to omega_floor

        Equation (Euler integration with numerical clamp):
        --------------------------------------------------
        ω_candidate = ω_current + α·dt
        ω_new = max(ω_candidate, ω_floor)

        The clamp prevents negative omega (non-physical).
        This is NOT a stall/flameout model - just numerical state handling.
        """
        omega_candidate = omega_current + alpha * dt
        omega_new = max(omega_candidate, self.omega_floor)
        return omega_new

    def rpm_from_omega(self, omega):
        """Convert angular velocity to RPM."""
        return omega * 60.0 / (2.0 * np.pi)

    def omega_from_rpm(self, rpm):
        """Convert RPM to angular velocity."""
        return rpm * 2.0 * np.pi / 60.0

    def get_idle_omega(self):
        """Get idle angular velocity [rad/s]."""
        return self.omega_from_rpm(self.omega_idle_rpm)