"""
Simulator Service
Wraps v0.3 EngineSimulator for API access

This service manages the lifecycle of the v0.3 simulator instance.
It provides methods for initialization, stepping, and state management.

IMPORTANT: This does NOT modify v0.3 simulator physics.
It only provides a clean interface for the API layer.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading
import time

# Import v0.3 simulator (FROZEN BASELINE)
simulator_path = Path(__file__).parent.parent.parent / 'simulator'
sys.path.insert(0, str(simulator_path))

from simulation.simulator import EngineSimulator


class SimulatorService:
    """
    Service layer wrapping v0.3 EngineSimulator

    Manages:
    - Simulator initialization
    - Simulation execution
    - State management
    - Telemetry access
    """

    def __init__(self):
        """Initialize service"""
        self.simulator: Optional[EngineSimulator] = None
        self.initialized = False
        self.running = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.current_inputs = {
            'throttle_pct': 0.0,
            'load_pct': 0.0,
            'altitude_m': 0.0,
            'T_ambient_C': 15.0
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current simulator status"""
        return {
            'running': self.running,
            'initialized': self.initialized,
            'current_time': self.simulator.time if self.simulator else 0.0,
            'message': 'Simulator ready' if self.initialized else 'Not initialized'
        }

    def initialize(self, altitude_m: float = 0.0, T_ambient_C: float = 15.0) -> Dict[str, Any]:
        """
        Initialize simulator at idle

        Parameters:
        -----------
        altitude_m : float
            Initial altitude [m]
        T_ambient_C : float
            Ambient temperature [°C]

        Returns:
        --------
        dict : Initial engine state
        """
        try:
            # Create new simulator instance
            self.simulator = EngineSimulator()

            # Initialize at idle
            initial_state = self.simulator.initialize_state(
                altitude_m=altitude_m,
                T_ambient_C=T_ambient_C
            )

            self.initialized = True
            self.current_inputs['altitude_m'] = altitude_m
            self.current_inputs['T_ambient_C'] = T_ambient_C

            return {
                'N_rpm': initial_state['N_rpm'],
                'altitude_m': altitude_m,
                'T_ambient_C': T_ambient_C,
                'message': 'Simulator initialized at idle'
            }
        except Exception as e:
            raise Exception(f"Initialization failed: {str(e)}")

    def start_simulation(
        self,
        throttle_pct: float,
        load_pct: float,
        altitude_m: Optional[float] = None,
        T_ambient_C: Optional[float] = None,
        duration: float = 60.0,
        dt: float = 0.1
    ) -> Dict[str, Any]:
        """
        Start simulation run

        Note: This doesn't use background threading for simplicity.
        Frontend will call step() repeatedly via API.
        """
        if not self.initialized:
            raise Exception("Simulator not initialized. Call /api/simulator/init first.")

        if self.running:
            raise Exception("Simulation already running. Stop it first.")

        self.running = True
        self.current_inputs['throttle_pct'] = throttle_pct
        self.current_inputs['load_pct'] = load_pct
        if altitude_m is not None:
            self.current_inputs['altitude_m'] = altitude_m
        if T_ambient_C is not None:
            self.current_inputs['T_ambient_C'] = T_ambient_C

        return {
            'message': 'Simulation started. Call /api/simulator/step to advance.',
            'inputs': self.current_inputs
        }

    def step(
        self,
        throttle_pct: float,
        load_pct: float,
        altitude_m: Optional[float] = None,
        T_ambient_C: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute single simulation step

        Advances simulator by one timestep (dt) with given inputs.
        Returns telemetry for this step.
        """
        if not self.initialized:
            raise Exception("Simulator not initialized")

        # Update inputs
        self.current_inputs['throttle_pct'] = throttle_pct
        self.current_inputs['load_pct'] = load_pct
        if altitude_m is not None:
            self.current_inputs['altitude_m'] = altitude_m
        if T_ambient_C is not None:
            self.current_inputs['T_ambient_C'] = T_ambient_C

        # Execute step
        telemetry = self.simulator.step(
            throttle_pct=throttle_pct,
            load_pct=load_pct,
            altitude_m=altitude_m,
            T_ambient_C=T_ambient_C
        )

        return telemetry

    def get_current_telemetry(self) -> Optional[Dict[str, Any]]:
        """
        Get current telemetry data

        Returns the most recent telemetry from simulator.
        """
        if not self.initialized or not self.simulator:
            return None

        if len(self.simulator.telemetry_history) == 0:
            return None

        # Return most recent telemetry
        return self.simulator.telemetry_history[-1]

    def get_telemetry_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get telemetry history

        Parameters:
        -----------
        limit : int
            Maximum number of recent data points to return

        Returns:
        --------
        list : Recent telemetry history
        """
        if not self.initialized or not self.simulator:
            return []

        history = self.simulator.telemetry_history

        # Return last 'limit' items
        return history[-limit:] if len(history) > limit else history

    def stop(self) -> Dict[str, Any]:
        """
        Stop simulation

        Halts simulation but preserves current state.
        """
        self.running = False

        return {
            'message': 'Simulation stopped',
            'current_time': self.simulator.time if self.simulator else 0.0
        }

    def reset(self) -> Dict[str, Any]:
        """
        Reset simulator

        Clears all state and telemetry history.
        Requires re-initialization.
        """
        self.simulator = None
        self.initialized = False
        self.running = False
        self.current_inputs = {
            'throttle_pct': 0.0,
            'load_pct': 0.0,
            'altitude_m': 0.0,
            'T_ambient_C': 15.0
        }

        return {
            'message': 'Simulator reset. Call /api/simulator/init to reinitialize.'
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get simulator configuration

        Returns the current engine_config.yaml parameters.
        """
        if not self.initialized or not self.simulator:
            raise Exception("Simulator not initialized")

        return self.simulator.config