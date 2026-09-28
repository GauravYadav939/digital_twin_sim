"""
UAV Engine Simulator Backend API
FastAPI server wrapping v0.3 Python simulator

This API layer provides HTTP endpoints for the React frontend
to communicate with the existing v0.3 engine simulator.

DO NOT modify v0.3 simulator physics here.
This is purely an interface layer.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add simulator path
simulator_path = Path(__file__).parent.parent / 'simulator'
sys.path.insert(0, str(simulator_path))

from services.simulator_service import SimulatorService

# Initialize FastAPI app
app = FastAPI(
    title="UAV Engine Simulator API",
    description="Backend API for Engine Simulator Frontend",
    version="1.0.0"
)

# CORS Configuration - Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev
        "https://*.vercel.app",   # Vercel deployments
        "*"  # For demo - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulator service instance
simulator_service = SimulatorService()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class InitRequest(BaseModel):
    altitude_m: float = 0.0
    T_ambient_C: float = 15.0


class SimulationConfig(BaseModel):
    throttle_pct: float
    load_pct: float
    altitude_m: Optional[float] = None
    T_ambient_C: Optional[float] = None
    duration: float = 60.0
    dt: float = 0.1


class StepRequest(BaseModel):
    throttle_pct: float
    load_pct: float
    altitude_m: Optional[float] = None
    T_ambient_C: Optional[float] = None


class SimulatorStatus(BaseModel):
    running: bool
    initialized: bool
    current_time: float
    message: str


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "UAV Engine Simulator API",
        "version": "1.0.0",
        "simulator": "v0.3 (frozen baseline)"
    }


@app.get("/api/status")
async def get_status() -> SimulatorStatus:
    """
    Get current simulator status
    """
    status = simulator_service.get_status()
    return SimulatorStatus(**status)


@app.post("/api/simulator/init")
async def initialize_simulator(request: InitRequest):
    """
    Initialize simulator at idle conditions

    This sets up the engine at idle with specified environmental conditions.
    Per v0.3: Engine starts already running at idle (no starter motor).
    """
    try:
        result = simulator_service.initialize(
            altitude_m=request.altitude_m,
            T_ambient_C=request.T_ambient_C
        )
        return {
            "status": "initialized",
            "initial_state": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulator/start")
async def start_simulation(config: SimulationConfig):
    """
    Start simulation with given configuration

    This begins the time-stepping simulation loop.
    Frontend will poll /api/simulator/telemetry for updates.
    """
    try:
        result = simulator_service.start_simulation(
            throttle_pct=config.throttle_pct,
            load_pct=config.load_pct,
            altitude_m=config.altitude_m,
            T_ambient_C=config.T_ambient_C,
            duration=config.duration,
            dt=config.dt
        )
        return {
            "status": "started",
            "config": config.dict(),
            "message": result["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulator/step")
async def step_simulation(request: StepRequest):
    """
    Execute single simulation step

    Advances simulator by one timestep with given inputs.
    Returns telemetry for this step.
    """
    try:
        telemetry = simulator_service.step(
            throttle_pct=request.throttle_pct,
            load_pct=request.load_pct,
            altitude_m=request.altitude_m,
            T_ambient_C=request.T_ambient_C
        )
        return {
            "status": "success",
            "telemetry": telemetry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulator/telemetry")
async def get_telemetry():
    """
    Get current telemetry data

    Returns the latest engine state/sensor measurements.
    Frontend polls this endpoint for real-time updates.
    """
    try:
        telemetry = simulator_service.get_current_telemetry()
        if telemetry is None:
            return {
                "status": "no_data",
                "message": "Simulator not initialized or no data available"
            }
        return {
            "status": "success",
            "telemetry": telemetry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulator/history")
async def get_telemetry_history(limit: int = 100):
    """
    Get telemetry history

    Returns historical telemetry data for plotting trends.
    Limit parameter controls how many recent data points to return.
    """
    try:
        history = simulator_service.get_telemetry_history(limit=limit)
        return {
            "status": "success",
            "count": len(history),
            "data": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulator/stop")
async def stop_simulation():
    """
    Stop running simulation

    Halts the simulation loop but preserves current state.
    """
    try:
        result = simulator_service.stop()
        return {
            "status": "stopped",
            "message": result["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulator/reset")
async def reset_simulation():
    """
    Reset simulator to initial state

    Clears all state and telemetry history.
    Requires re-initialization before running again.
    """
    try:
        result = simulator_service.reset()
        return {
            "status": "reset",
            "message": result["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulator/config")
async def get_configuration():
    """
    Get current simulator configuration

    Returns the engine parameters from engine_config.yaml
    """
    try:
        config = simulator_service.get_config()
        return {
            "status": "success",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("="*60)
    print("UAV Engine Simulator Backend API")
    print("="*60)
    print("Starting server on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("="*60)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload during development
        log_level="info"
    )