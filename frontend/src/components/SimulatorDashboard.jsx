/**
 * Simulator Dashboard Component
 * Main interface for engine simulator
 */

import { useState, useEffect } from 'react'
import { simulatorAPI } from '../services/api'
import ControlPanel from './ControlPanel'
import EngineGauges from './EngineGauges'
import TelemetryCharts from './TelemetryCharts'
import { Play, Square, RotateCcw, AlertCircle } from 'lucide-react'

export default function SimulatorDashboard() {
  const [isRunning, setIsRunning] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const [telemetry, setTelemetry] = useState(null)
  const [telemetryHistory, setTelemetryHistory] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  // Control inputs
  const [inputs, setInputs] = useState({
    throttle_pct: 30,
    load_pct: 50,
    altitude_m: 1000,
    T_ambient_C: 20
  })

  // Initialize simulator on mount
  useEffect(() => {
    handleInitialize()
  }, [])

  // Simulation loop - poll telemetry when running
  useEffect(() => {
    if (!isRunning) return

    const interval = setInterval(async () => {
      try {
        // Step the simulation
        const response = await simulatorAPI.step(inputs)

        if (response.status === 'success') {
          const newTelemetry = response.telemetry
          setTelemetry(newTelemetry)

          // Add to history (keep last 200 points)
          setTelemetryHistory(prev => {
            const updated = [...prev, newTelemetry]
            return updated.slice(-200)
          })
        }
      } catch (err) {
        console.error('Step error:', err)
        setError('Simulation step failed: ' + err.message)
        setIsRunning(false)
      }
    }, 500) // Update every 500ms

    return () => clearInterval(interval)
  }, [isRunning, inputs])

  const handleInitialize = async () => {
    setLoading(true)
    setError(null)
    try {
      await simulatorAPI.initialize(inputs.altitude_m, inputs.T_ambient_C)
      setIsInitialized(true)
      setError(null)
    } catch (err) {
      setError('Initialization failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    if (!isInitialized) {
      await handleInitialize()
    }

    setLoading(true)
    setError(null)
    try {
      await simulatorAPI.start({
        throttle_pct: inputs.throttle_pct,
        load_pct: inputs.load_pct,
        altitude_m: inputs.altitude_m,
        T_ambient_C: inputs.T_ambient_C,
        duration: 300,
        dt: 0.1
      })
      setIsRunning(true)
    } catch (err) {
      setError('Start failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      await simulatorAPI.stop()
      setIsRunning(false)
    } catch (err) {
      setError('Stop failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    setLoading(true)
    setError(null)
    try {
      await simulatorAPI.reset()
      setIsInitialized(false)
      setIsRunning(false)
      setTelemetry(null)
      setTelemetryHistory([])

      // Reinitialize
      await handleInitialize()
    } catch (err) {
      setError('Reset failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (name, value) => {
    setInputs(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="text-red-500 mt-0.5 flex-shrink-0" size={20} />
          <div className="flex-1">
            <h3 className="font-semibold text-red-400">Error</h3>
            <p className="text-sm text-red-300 mt-1">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Control Bar */}
      <div className="glass-panel rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">
              Engine Simulator Controls
            </h2>
            <p className="text-gray-400 text-sm">
              Virtual Engine Status: {' '}
              <span className={isRunning ? 'status-normal' : 'text-gray-500'}>
                {isRunning ? 'RUNNING' : 'STOPPED'}
              </span>
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleStart}
              disabled={isRunning || loading}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              <Play size={20} />
              <span>START</span>
            </button>

            <button
              onClick={handleStop}
              disabled={!isRunning || loading}
              className="flex items-center space-x-2 px-6 py-3 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              <Square size={20} />
              <span>STOP</span>
            </button>

            <button
              onClick={handleReset}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              <RotateCcw size={20} />
              <span>RESET</span>
            </button>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <ControlPanel
        inputs={inputs}
        onInputChange={handleInputChange}
        disabled={isRunning}
      />

      {/* Engine Gauges */}
      <EngineGauges telemetry={telemetry} />

      {/* Telemetry Charts */}
      <TelemetryCharts
        telemetry={telemetry}
        history={telemetryHistory}
      />
    </div>
  )
}