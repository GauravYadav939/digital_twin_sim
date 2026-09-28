"""
Standard Test Scenarios
Reference: engine_model_specification_v0.3.txt §6 (Validation)
"""

import numpy as np


class Scenarios:
    """
    Standard test scenarios for validation.
    Based on v0.3 §6.3 directional/behavioral validation requirements.
    """

    @staticmethod
    def throttle_step(step_time=10.0, throttle_initial=30.0, throttle_final=70.0):
        """
        Throttle step response scenario.

        Tests directional behavior:
        - Increasing throttle should increase air/fuel flow, power, RPM, temperatures

        Parameters:
        -----------
        step_time : float
            Time of step change [s]
        throttle_initial : float
            Initial throttle [%]
        throttle_final : float
            Final throttle [%]

        Returns:
        --------
        throttle_schedule : callable
            Function throttle(t) returning throttle %
        """
        def throttle(t):
            return throttle_initial if t < step_time else throttle_final
        return throttle

    @staticmethod
    def altitude_sweep(alt_initial=0.0, alt_final=3000.0, duration=60.0):
        """
        Altitude sweep scenario.

        Tests directional behavior:
        - Increasing altitude should reduce air density and available power
          (for naturally aspirated engine)

        Parameters:
        -----------
        alt_initial : float
            Initial altitude [m]
        alt_final : float
            Final altitude [m]
        duration : float
            Sweep duration [s]

        Returns:
        --------
        altitude_schedule : callable
            Function altitude(t) returning altitude [m]
        """
        def altitude(t):
            return alt_initial + (alt_final - alt_initial) * min(t / duration, 1.0)
        return altitude

    @staticmethod
    def ambient_temp_sweep(T_initial=15.0, T_final=35.0, duration=60.0):
        """
        Ambient temperature sweep scenario.

        Tests directional behavior:
        - Increasing ambient temperature should affect air density and cooling

        Parameters:
        -----------
        T_initial : float
            Initial temperature [°C]
        T_final : float
            Final temperature [°C]
        duration : float
            Sweep duration [s]

        Returns:
        --------
        temp_schedule : callable
            Function temp(t) returning temperature [°C]
        """
        def temp(t):
            return T_initial + (T_final - T_initial) * min(t / duration, 1.0)
        return temp

    @staticmethod
    def load_sweep(load_initial=20.0, load_final=80.0, duration=60.0):
        """
        Load sweep scenario.

        Tests directional behavior:
        - Increasing load should increase required torque and affect RPM

        Parameters:
        -----------
        load_initial : float
            Initial load [%]
        load_final : float
            Final load [%]
        duration : float
            Sweep duration [s]

        Returns:
        --------
        load_schedule : callable
            Function load(t) returning load %
        """
        def load(t):
            return load_initial + (load_final - load_initial) * min(t / duration, 1.0)
        return load

    @staticmethod
    def sustained_high_power(throttle=85.0, load=70.0):
        """
        Sustained high power scenario.

        Tests thermal behavior:
        - Should see thermal states rise until cooling equilibrium

        Parameters:
        -----------
        throttle : float
            Sustained throttle [%]
        load : float
            Sustained load [%]

        Returns:
        --------
        throttle, load : float, float
            Constant schedules
        """
        return throttle, load

    @staticmethod
    def power_reduction_recovery(step_time=30.0, throttle_high=80.0,
                                 throttle_low=40.0):
        """
        Power reduction and recovery scenario.

        Tests transient behavior:
        - Thermal states should decay during low power
        - RPM should adjust

        Parameters:
        -----------
        step_time : float
            Time of power reduction [s]
        throttle_high : float
            High throttle [%]
        throttle_low : float
            Low throttle [%]

        Returns:
        --------
        throttle_schedule : callable
            Function throttle(t)
        """
        def throttle(t):
            if t < step_time:
                return throttle_high
            elif t < step_time + 30.0:
                return throttle_low
            else:
                return throttle_high
        return throttle

    @staticmethod
    def steady_state_operating_points():
        """
        Return standard steady-state operating points for Level 3 validation.

        Based on FOCA power modes (v0.3 §5.2):
        - Idle/Taxi: ~10-15%
        - Cruise: 65%
        - Higher-power cruise (Climb-out): 85%
        - Takeoff: 100%

        Returns:
        --------
        operating_points : list of dict
            Each dict has keys: name, throttle, load, altitude, T_ambient, duration
        """
        return [
            {
                'name': 'Idle/Taxi',
                'throttle': 15.0,
                'load': 10.0,
                'altitude': 0.0,
                'T_ambient': 15.0,
                'duration': 60.0
            },
            {
                'name': 'Cruise_65pct',
                'throttle': 65.0,
                'load': 50.0,
                'altitude': 2000.0,
                'T_ambient': 15.0,
                'duration': 60.0
            },
            {
                'name': 'Climb_85pct',
                'throttle': 85.0,
                'load': 70.0,
                'altitude': 1000.0,
                'T_ambient': 15.0,
                'duration': 60.0
            },
            {
                'name': 'Takeoff_100pct',
                'throttle': 100.0,
                'load': 85.0,
                'altitude': 0.0,
                'T_ambient': 25.0,
                'duration': 60.0
            }
        ]