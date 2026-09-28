"""
Visualization Module
Plotting functions for simulator results
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class Plotter:
    """
    Visualization tools for engine simulator results.
    """

    def __init__(self, output_dir='data/generated'):
        """
        Initialize plotter.

        Parameters:
        -----------
        output_dir : str or Path
            Directory for saving plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_standard_telemetry(self, df, scenario_name='simulation'):
        """
        Create standard telemetry plots.

        Parameters:
        -----------
        df : pandas.DataFrame
            Telemetry dataframe
        scenario_name : str
            Name for output files
        """
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        fig.suptitle(f'UAV Engine Simulator - {scenario_name}', fontsize=14, fontweight='bold')

        # RPM
        axes[0, 0].plot(df['time'], df['N_rpm'], 'b-', linewidth=2)
        axes[0, 0].set_ylabel('RPM')
        axes[0, 0].set_title('Engine Speed')
        axes[0, 0].grid(True, alpha=0.3)

        # CHT
        axes[0, 1].plot(df['time'], df['T_CHT_C'], 'r-', linewidth=2)
        axes[0, 1].set_ylabel('CHT [°C]')
        axes[0, 1].set_title('Cylinder Head Temperature')
        axes[0, 1].grid(True, alpha=0.3)

        # EGT
        axes[0, 2].plot(df['time'], df['T_EGT_C'], 'orange', linewidth=2)
        axes[0, 2].set_ylabel('EGT [°C]')
        axes[0, 2].set_title('Exhaust Gas Temperature')
        axes[0, 2].grid(True, alpha=0.3)

        # Oil Temperature
        axes[1, 0].plot(df['time'], df['T_oil_C'], 'green', linewidth=2)
        axes[1, 0].set_ylabel('Oil Temp [°C]')
        axes[1, 0].set_title('Oil Temperature')
        axes[1, 0].grid(True, alpha=0.3)

        # Oil Pressure
        axes[1, 1].plot(df['time'], df['P_oil_psi'], 'darkgreen', linewidth=2)
        axes[1, 1].set_ylabel('Oil Press [psi]')
        axes[1, 1].set_title('Oil Pressure')
        axes[1, 1].grid(True, alpha=0.3)

        # Fuel Flow
        axes[1, 2].plot(df['time'], df['fuel_flow_Lph'], 'purple', linewidth=2)
        axes[1, 2].set_ylabel('Fuel Flow [L/h]')
        axes[1, 2].set_title('Fuel Flow')
        axes[1, 2].grid(True, alpha=0.3)

        # Brake Power
        axes[2, 0].plot(df['time'], df['P_brake_kW'], 'darkblue', linewidth=2)
        axes[2, 0].set_ylabel('Power [kW]')
        axes[2, 0].set_xlabel('Time [s]')
        axes[2, 0].set_title('Brake Power')
        axes[2, 0].grid(True, alpha=0.3)

        # Vibration
        axes[2, 1].plot(df['time'], df['vibration'], 'brown', linewidth=2)
        axes[2, 1].set_ylabel('Vibration')
        axes[2, 1].set_xlabel('Time [s]')
        axes[2, 1].set_title('Vibration Proxy')
        axes[2, 1].grid(True, alpha=0.3)

        # Throttle & Load
        axes[2, 2].plot(df['time'], df['throttle_pct'], 'b-', label='Throttle', linewidth=2)
        axes[2, 2].plot(df['time'], df['load_pct'], 'r--', label='Load', linewidth=2)
        axes[2, 2].set_ylabel('Input [%]')
        axes[2, 2].set_xlabel('Time [s]')
        axes[2, 2].set_title('Inputs')
        axes[2, 2].legend()
        axes[2, 2].grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / f'{scenario_name}_telemetry.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {output_path}")
        plt.close()

    def plot_energy_split(self, df, scenario_name='simulation'):
        """
        Plot energy balance split.

        Parameters:
        -----------
        df : pandas.DataFrame
            Telemetry dataframe
        scenario_name : str
            Name for output files
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(df['time'], df['energy_split_brake_pct'], label='Brake', linewidth=2)
        ax.plot(df['time'], df['energy_split_exhaust_pct'], label='Exhaust', linewidth=2)
        ax.plot(df['time'], df['energy_split_CHT_pct'], label='CHT', linewidth=2)
        ax.plot(df['time'], df['energy_split_oil_pct'], label='Oil', linewidth=2)

        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Energy Split [%]')
        ax.set_title(f'Energy Balance - {scenario_name}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)

        plt.tight_layout()

        output_path = self.output_dir / f'{scenario_name}_energy_split.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {output_path}")
        plt.close()

    def plot_validation_comparison(self, scenarios_results):
        """
        Plot comparison across multiple scenarios for validation.

        Parameters:
        -----------
        scenarios_results : dict
            Dict mapping scenario names to telemetry DataFrames
        """
        num_scenarios = len(scenarios_results)
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Validation Scenarios Comparison', fontsize=14, fontweight='bold')

        for scenario_name, df in scenarios_results.items():
            # RPM
            axes[0, 0].plot(df['time'], df['N_rpm'], label=scenario_name, linewidth=2)
            # CHT
            axes[0, 1].plot(df['time'], df['T_CHT_C'], label=scenario_name, linewidth=2)
            # Oil Temp
            axes[1, 0].plot(df['time'], df['T_oil_C'], label=scenario_name, linewidth=2)
            # Brake Power
            axes[1, 1].plot(df['time'], df['P_brake_kW'], label=scenario_name, linewidth=2)

        axes[0, 0].set_ylabel('RPM')
        axes[0, 0].set_title('Engine Speed')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].set_ylabel('CHT [°C]')
        axes[0, 1].set_title('Cylinder Head Temperature')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        axes[1, 0].set_ylabel('Oil Temp [°C]')
        axes[1, 0].set_xlabel('Time [s]')
        axes[1, 0].set_title('Oil Temperature')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].set_ylabel('Power [kW]')
        axes[1, 1].set_xlabel('Time [s]')
        axes[1, 1].set_title('Brake Power')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / 'validation_comparison.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved: {output_path}")
        plt.close()