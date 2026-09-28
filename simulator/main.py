"""
UAV Piston Engine Simulator - Main Entry Point

Based on engine_model_specification_v0.3.txt
Smart India Hackathon 2026 - Problem Statement 26054

This is Phase 1: Healthy Engine Simulator Only

Usage:
    python main.py
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from simulation.simulator import EngineSimulator
from scenarios.scenarios import Scenarios
from visualization.plots import Plotter
from validation.validation_tests import ValidationTests


def run_demo_scenario():
    """
    Run a simple demonstration scenario.
    """
    print("\n" + "="*60)
    print("UAV PISTON ENGINE SIMULATOR - DEMO")
    print("SIH 2026 Problem Statement 26054")
    print("Phase 1: Healthy Engine Simulator")
    print("="*60 + "\n")

    # Initialize simulator
    print("Initializing simulator...")
    sim = EngineSimulator()

    # Run a throttle step scenario
    print("Running throttle step scenario...")
    print("  Throttle: 30% → 70% at t=20s")
    print("  Load: 50%")
    print("  Duration: 60s")
    print("  Altitude: 1000m")

    throttle_schedule = Scenarios.throttle_step(
        step_time=20.0,
        throttle_initial=30.0,
        throttle_final=70.0
    )

    sim.run_scenario(
        throttle_schedule=throttle_schedule,
        load_schedule=50.0,
        duration=60.0,
        altitude_m=1000.0,
        T_ambient_C=20.0
    )

    # Get results
    df = sim.get_telemetry_dataframe()

    # Save telemetry
    output_file = project_root / 'data' / 'generated' / 'demo_telemetry.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    sim.save_telemetry_csv(output_file)

    # Create plots
    print("\nGenerating plots...")
    plotter = Plotter(output_dir=project_root / 'data' / 'generated')
    plotter.plot_standard_telemetry(df, scenario_name='demo_throttle_step')
    plotter.plot_energy_split(df, scenario_name='demo_throttle_step')

    # Print summary
    print("\n" + "-"*60)
    print("SIMULATION SUMMARY")
    print("-"*60)
    print(f"Final RPM: {df['N_rpm'].iloc[-1]:.1f} RPM")
    print(f"Final CHT: {df['T_CHT_C'].iloc[-1]:.1f} °C")
    print(f"Final EGT: {df['T_EGT_C'].iloc[-1]:.1f} °C")
    print(f"Final Oil Temp: {df['T_oil_C'].iloc[-1]:.1f} °C")
    print(f"Final Oil Pressure: {df['P_oil_psi'].iloc[-1]:.1f} psi")
    print(f"Final Brake Power: {df['P_brake_kW'].iloc[-1]:.2f} kW")
    print(f"Mean Fuel Flow: {df['fuel_flow_Lph'].mean():.1f} L/h")
    print("\nEnergy Split (steady-state average):")
    print(f"  Brake Work: {df['energy_split_brake_pct'].mean():.1f}%")
    print(f"  Exhaust: {df['energy_split_exhaust_pct'].mean():.1f}%")
    print(f"  CHT: {df['energy_split_CHT_pct'].mean():.1f}%")
    print(f"  Oil: {df['energy_split_oil_pct'].mean():.1f}%")
    print("-"*60)

    print(f"\nResults saved to: {output_file.parent}")
    print("\n✓ Demo complete!")


def run_validation():
    """
    Run full validation test suite.
    """
    print("\n" + "="*60)
    print("UAV PISTON ENGINE SIMULATOR - VALIDATION")
    print("="*60)

    # Initialize simulator
    sim = EngineSimulator()

    # Run validation
    validator = ValidationTests(sim)
    report = validator.run_full_validation()

    # Generate comparison plots
    print("\nGenerating validation plots...")
    plotter = Plotter(output_dir=project_root / 'data' / 'generated')
    plotter.plot_validation_comparison(report['scenarios_dataframes'])

    # Save validation dataframes
    print("\nSaving validation data...")
    for scenario_name, df in report['scenarios_dataframes'].items():
        output_file = project_root / 'data' / 'generated' / f'validation_{scenario_name}.csv'
        df.to_csv(output_file, index=False)

    for op_name, df in report['operating_points_dataframes'].items():
        # Sanitize filename
        safe_name = op_name.replace('/', '_').replace(' ', '_')
        output_file = project_root / 'data' / 'generated' / f'operating_point_{safe_name}.csv'
        df.to_csv(output_file, index=False)

    print(f"\nValidation data saved to: {project_root / 'data' / 'generated'}")
    print("\n✓ Validation complete!")


def main():
    """
    Main entry point with command-line interface.
    """
    parser = argparse.ArgumentParser(
        description='UAV Piston Engine Simulator - SIH 2026 PS 26054'
    )
    parser.add_argument(
        '--mode',
        choices=['demo', 'validation', 'both'],
        default='demo',
        help='Run mode: demo (quick demonstration), validation (full test suite), or both'
    )

    args = parser.parse_args()

    try:
        if args.mode in ['demo', 'both']:
            run_demo_scenario()

        if args.mode in ['validation', 'both']:
            run_validation()

        print("\n✓ All tasks completed successfully!\n")

    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()