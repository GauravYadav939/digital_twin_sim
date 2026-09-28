"""
Sensor Model Module
Converts true engine states to telemetry with noise/bias
Reference: engine_model_specification_v0.3.txt §4.12
"""

import numpy as np


class SensorModel:
    """
    Sensor model that adds measurement noise to true engine states.
    Converts TRUE ENGINE STATE → TELEMETRY with realistic sensor characteristics.
    """

    def __init__(self, config):
        """
        Initialize sensor model.

        Parameters from config:
        - noise_rpm: RPM noise std dev [RPM]
        - noise_cht: CHT noise std dev [°C]
        - noise_egt: EGT noise std dev [°C]
        - noise_oil_temp: Oil temp noise std dev [°C]
        - noise_oil_pressure: Oil pressure noise std dev [Pa]
        - noise_fuel_flow: Fuel flow noise std dev [kg/s]
        - noise_vibration: Vibration relative noise std dev [fraction]
        """
        sensor_config = config['sensor']
        self.noise_rpm = sensor_config['noise_rpm']
        self.noise_cht = sensor_config['noise_cht']
        self.noise_egt = sensor_config['noise_egt']
        self.noise_oil_temp = sensor_config['noise_oil_temp']
        self.noise_oil_pressure = sensor_config['noise_oil_pressure']
        self.noise_fuel_flow = sensor_config['noise_fuel_flow']
        self.noise_vibration = sensor_config['noise_vibration']

    def add_gaussian_noise(self, true_value, noise_std):
        """
        Add Gaussian measurement noise.

        Parameters:
        -----------
        true_value : float
            True state value
        noise_std : float
            Noise standard deviation

        Returns:
        --------
        measured_value : float
            Measured value with noise
        """
        noise = np.random.normal(0, noise_std)
        measured_value = true_value + noise
        return measured_value

    def measure(self, true_states):
        """
        Convert true engine states to sensor measurements.

        Parameters:
        -----------
        true_states : dict
            Dictionary of true engine states with keys:
            - N_rpm: Engine speed [RPM]
            - T_CHT: CHT [K]
            - T_EGT: EGT [K]
            - T_oil: Oil temperature [K]
            - P_oil: Oil pressure [Pa]
            - m_dot_fuel: Fuel flow [kg/s]
            - vibration: Vibration proxy
            - ... (other states for telemetry)

        Returns:
        --------
        measurements : dict
            Dictionary of sensor measurements (with noise)

        Sensor Model Philosophy (from §9 of specification):
        ---------------------------------------------------
        Distinguish TRUE ENGINE STATE from SENSOR MEASUREMENT.
        Noise represents:
        - Sensor resolution limits
        - Electrical noise
        - Quantization
        - Environmental effects
        NOT: fundamental model uncertainty (that's in the physics)
        """
        measurements = {}

        # RPM
        measurements['N_rpm'] = self.add_gaussian_noise(
            true_states['N_rpm'], self.noise_rpm)

        # CHT (convert K to °C for output)
        T_CHT_C = true_states['T_CHT'] - 273.15
        measurements['T_CHT_C'] = self.add_gaussian_noise(T_CHT_C, self.noise_cht)

        # EGT (convert K to °C for output)
        T_EGT_C = true_states['T_EGT'] - 273.15
        measurements['T_EGT_C'] = self.add_gaussian_noise(T_EGT_C, self.noise_egt)

        # Oil temperature (convert K to °C)
        T_oil_C = true_states['T_oil'] - 273.15
        measurements['T_oil_C'] = self.add_gaussian_noise(T_oil_C, self.noise_oil_temp)

        # Oil pressure (convert Pa to psi for output)
        P_oil_psi = true_states['P_oil'] / 6894.76
        measurements['P_oil_psi'] = self.add_gaussian_noise(
            P_oil_psi, self.noise_oil_pressure / 6894.76)

        # Fuel flow (keep in kg/s, or convert to L/h for practical output)
        # AVGAS density ≈ 0.72 kg/L
        fuel_flow_Lph = true_states['m_dot_fuel'] * 3600 / 0.72
        measurements['fuel_flow_Lph'] = self.add_gaussian_noise(
            fuel_flow_Lph, self.noise_fuel_flow * 3600 / 0.72)

        # Vibration (relative noise)
        measurements['vibration'] = true_states['vibration'] * (
            1.0 + np.random.normal(0, self.noise_vibration))

        # Pass through other states without noise (for telemetry/analysis)
        measurements['torque_Nm'] = true_states.get('T_ind', 0)
        measurements['P_brake_kW'] = true_states.get('P_brake', 0) / 1000.0
        measurements['throttle_pct'] = true_states.get('throttle_pct', 0)
        measurements['load_pct'] = true_states.get('load_pct', 0)
        measurements['altitude_m'] = true_states.get('altitude_m', 0)

        return measurements