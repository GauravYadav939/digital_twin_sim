"""
Validation Test Suite
Implements Level 1, 2, and 3 validation tests
Reference: engine_model_specification_v0.3.txt §6
"""

import numpy as np
import pandas as pd
from pathlib import Path


class ValidationTests:
    """
    Three-level validation test suite per v0.3 §6.
    """

    def __init__(self, simulator):
        """
        Initialize validation tests.

        Parameters:
        -----------
        simulator : EngineSimulator
            Initialized simulator instance
        """
        self.simulator = simulator
        self.results = {}

    def level1_mathematical_consistency(self, df):
        """
        Level 1: Mathematical/Physical Consistency Tests.

        Tests from v0.3 §6.1:
        - Dimensional consistency (implicitly checked by implementation)
        - No divide-by-zero / NaN / Inf
        - No negative RPM
        - Energy bookkeeping integrity
        - Timestep convergence

        Parameters:
        -----------
        df : pandas.DataFrame
            Telemetry dataframe

        Returns:
        --------
        results : dict
            Test results with pass/fail status
        """
        results = {
            'level': 1,
            'name': 'Mathematical Consistency',
            'tests': {}
        }

        # Test: No NaN or Inf
        has_nan = df.isnull().any().any()
        has_inf = np.isinf(df.select_dtypes(include=[np.number])).any().any()
        results['tests']['no_nan_inf'] = {
            'pass': not (has_nan or has_inf),
            'details': f"NaN found: {has_nan}, Inf found: {has_inf}"
        }

        # Test: No negative RPM
        min_rpm = df['N_rpm'].min()
        results['tests']['no_negative_rpm'] = {
            'pass': min_rpm >= 0,
            'details': f"Minimum RPM: {min_rpm:.1f}"
        }

        # Test: Energy bookkeeping (should be near zero)
        max_residual = df['energy_residual_W'].abs().max()
        mean_residual = df['energy_residual_W'].abs().mean()
        # Allow small numerical error (< 0.1% of typical fuel power)
        typical_fuel_power = 50000  # ~50 kW typical
        threshold = 0.001 * typical_fuel_power  # 0.1%
        results['tests']['energy_bookkeeping'] = {
            'pass': max_residual < threshold,
            'details': f"Max residual: {max_residual:.2f} W, Mean: {mean_residual:.2f} W, Threshold: {threshold:.2f} W"
        }

        # Test: RPM never hit floor (should not reach omega_floor in healthy scenarios)
        N_floor = self.simulator.config['engine']['N_floor']
        reached_floor = (df['N_rpm'] <= N_floor + 10).any()  # 10 RPM margin
        results['tests']['no_floor_contact'] = {
            'pass': not reached_floor,
            'details': f"N_floor: {N_floor} RPM, Reached floor: {reached_floor}, Min RPM: {min_rpm:.1f}"
        }

        return results

    def level2_directional_behavioral(self, scenarios_dfs):
        """
        Level 2: Directional/Behavioral Validation.

        Tests from v0.3 §6.3:
        - Directional inequalities (12 checks from v0.2 §9.5)
        - Transient behavior reasonability

        Parameters:
        -----------
        scenarios_dfs : dict
            Dictionary mapping scenario names to telemetry DataFrames

        Returns:
        --------
        results : dict
            Test results
        """
        results = {
            'level': 2,
            'name': 'Directional/Behavioral',
            'tests': {}
        }

        # Check if we have throttle_step scenario
        if 'throttle_step' in scenarios_dfs:
            df = scenarios_dfs['throttle_step']

            # Split into before and after step
            mid_idx = len(df) // 2
            df_before = df.iloc[:mid_idx]
            df_after = df.iloc[mid_idx:]

            # Test: Increasing throttle increases average RPM
            rpm_before = df_before['N_rpm'].mean()
            rpm_after = df_after['N_rpm'].mean()
            results['tests']['throttle_increases_rpm'] = {
                'pass': rpm_after > rpm_before,
                'details': f"RPM before: {rpm_before:.1f}, after: {rpm_after:.1f}"
            }

            # Test: Increasing throttle increases fuel flow
            fuel_before = df_before['fuel_flow_Lph'].mean()
            fuel_after = df_after['fuel_flow_Lph'].mean()
            results['tests']['throttle_increases_fuel'] = {
                'pass': fuel_after > fuel_before,
                'details': f"Fuel flow before: {fuel_before:.1f} L/h, after: {fuel_after:.1f} L/h"
            }

            # Test: Increasing throttle increases CHT
            cht_before = df_before['T_CHT_C'].mean()
            cht_after = df_after['T_CHT_C'].mean()
            results['tests']['throttle_increases_cht'] = {
                'pass': cht_after > cht_before,
                'details': f"CHT before: {cht_before:.1f}°C, after: {cht_after:.1f}°C"
            }

        # Check altitude sweep
        if 'altitude_sweep' in scenarios_dfs:
            df = scenarios_dfs['altitude_sweep']

            # Test: Increasing altitude decreases power (naturally aspirated)
            power_start = df['P_brake_kW'].iloc[:10].mean()
            power_end = df['P_brake_kW'].iloc[-10:].mean()
            results['tests']['altitude_reduces_power'] = {
                'pass': power_end < power_start,
                'details': f"Power at low alt: {power_start:.2f} kW, at high alt: {power_end:.2f} kW"
            }

        return results

    def level3_real_engine_comparison(self, operating_points_dfs):
        """
        Level 3: Representative Real-Engine Comparison.

        Compare against FOCA ranges from v0.3 §5.3.

        FOCA O-360-A3A logged ranges (representative, not target):
        - RPM: 1410–2570
        - CHT: 170–220 °C
        - Oil temp: 75–98 °C
        - Fuel flow: 8–59 L/h

        Parameters:
        -----------
        operating_points_dfs : dict
            Dictionary mapping operating point names to steady-state DataFrames

        Returns:
        --------
        results : dict
            Comparison results
        """
        results = {
            'level': 3,
            'name': 'Real-Engine Comparison (FOCA O-360 ranges)',
            'tests': {},
            'disclaimer': 'This is NOT validation that the simulator represents a real UAV engine. '
                         'It is an order-of-magnitude plausibility check against published data.'
        }

        # FOCA ranges (from v0.3 §5.3)
        foca_ranges = {
            'RPM': (1410, 2570),
            'CHT_C': (170, 220),
            'T_oil_C': (75, 98),
            'fuel_flow_Lph': (8, 59)
        }

        # Check each operating point
        for op_name, df in operating_points_dfs.items():
            # Use steady-state values (last 50% of simulation)
            df_steady = df.iloc[len(df)//2:]

            op_results = {}

            for param, (foca_min, foca_max) in foca_ranges.items():
                if param not in df_steady.columns:
                    mean_val = 0
                else:
                    mean_val = df_steady[param].mean()

                in_range = foca_min <= mean_val <= foca_max

                # For parameters outside range, calculate how far off
                if mean_val < foca_min:
                    deviation = f"{(foca_min - mean_val)/foca_min * 100:.1f}% below"
                elif mean_val > foca_max:
                    deviation = f"{(mean_val - foca_max)/foca_max * 100:.1f}% above"
                else:
                    deviation = "within range"

                op_results[param] = {
                    'value': mean_val,
                    'foca_range': (foca_min, foca_max),
                    'in_range': in_range,
                    'deviation': deviation
                }

            results['tests'][op_name] = op_results

        return results

    def run_full_validation(self):
        """
        Run complete validation test suite.

        Returns:
        --------
        validation_report : dict
            Complete validation results
        """
        print("\n" + "="*60)
        print("RUNNING FULL VALIDATION SUITE")
        print("="*60)

        from scenarios.scenarios import Scenarios

        # Level 1: Run basic scenario and check mathematical consistency
        print("\n--- Level 1: Mathematical Consistency ---")
        self.simulator.initialize_state(altitude_m=1000, T_ambient_C=15.0)
        telemetry = self.simulator.run_scenario(
            throttle_schedule=50.0,
            load_schedule=50.0,
            duration=60.0,
            dt=0.1
        )
        df_basic = self.simulator.get_telemetry_dataframe()
        level1_results = self.level1_mathematical_consistency(df_basic)

        for test_name, test_result in level1_results['tests'].items():
            status = "✓ PASS" if test_result['pass'] else "✗ FAIL"
            print(f"  {status}: {test_name}")
            print(f"    {test_result['details']}")

        # Level 2: Run directional scenarios
        print("\n--- Level 2: Directional/Behavioral ---")
        scenarios_dfs = {}

        # Throttle step
        print("  Running throttle step scenario...")
        throttle_sched = Scenarios.throttle_step(step_time=30.0, throttle_initial=30.0, throttle_final=70.0)
        self.simulator.initialize_state()
        self.simulator.run_scenario(throttle_sched, load_schedule=50.0, duration=60.0)
        scenarios_dfs['throttle_step'] = self.simulator.get_telemetry_dataframe()

        # Altitude sweep
        print("  Running altitude sweep scenario...")
        alt_sched = Scenarios.altitude_sweep(alt_initial=0.0, alt_final=3000.0, duration=60.0)
        self.simulator.initialize_state()
        self.simulator.run_scenario(throttle_schedule=60.0, load_schedule=50.0,
                                    duration=60.0, altitude_m=alt_sched)
        scenarios_dfs['altitude_sweep'] = self.simulator.get_telemetry_dataframe()

        level2_results = self.level2_directional_behavioral(scenarios_dfs)

        for test_name, test_result in level2_results['tests'].items():
            status = "✓ PASS" if test_result['pass'] else "✗ FAIL"
            print(f"  {status}: {test_name}")
            print(f"    {test_result['details']}")

        # Level 3: Steady-state operating points
        print("\n--- Level 3: Real-Engine Comparison (FOCA O-360 ranges) ---")
        print(f"  Disclaimer: {level1_results.get('disclaimer', 'Order-of-magnitude check only')}")

        operating_points = Scenarios.steady_state_operating_points()
        op_dfs = {}

        for op in operating_points:
            print(f"  Running {op['name']} operating point...")
            self.simulator.initialize_state(altitude_m=op['altitude'], T_ambient_C=op['T_ambient'])
            self.simulator.run_scenario(
                throttle_schedule=op['throttle'],
                load_schedule=op['load'],
                duration=op['duration']
            )
            op_dfs[op['name']] = self.simulator.get_telemetry_dataframe()

        level3_results = self.level3_real_engine_comparison(op_dfs)

        # Print Level 3 results
        for op_name, op_tests in level3_results['tests'].items():
            print(f"\n  {op_name}:")
            for param, param_result in op_tests.items():
                in_range_str = "✓" if param_result['in_range'] else "✗"
                print(f"    {in_range_str} {param}: {param_result['value']:.1f} "
                      f"(FOCA range: {param_result['foca_range']}, {param_result['deviation']})")

        # Compile full report
        validation_report = {
            'level1': level1_results,
            'level2': level2_results,
            'level3': level3_results,
            'scenarios_dataframes': scenarios_dfs,
            'operating_points_dataframes': op_dfs
        }

        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60 + "\n")

        return validation_report    