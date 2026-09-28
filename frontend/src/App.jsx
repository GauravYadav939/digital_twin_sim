import { useState, useEffect } from 'react'
import SimulatorDashboard from './components/SimulatorDashboard'
import './styles/App.css'

function App() {
  return (
    <div className="min-h-screen bg-engine-bg">
      {/* Header */}
      <header className="bg-engine-panel border-b border-engine-border px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              UAV Piston Engine Simulator
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              SIH 2026 | Digital Twin for Engine Health Monitoring
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">Phase 1</div>
              <div className="text-sm font-medium text-engine-accent">
                v0.3 Baseline
              </div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        <SimulatorDashboard />
      </main>

      {/* Footer */}
      <footer className="bg-engine-panel border-t border-engine-border px-6 py-4 mt-8">
        <div className="max-w-7xl mx-auto text-center text-gray-400 text-sm">
          <p>
            Virtual Engine Simulation | Phase 1: Healthy Engine Only
          </p>
          <p className="mt-1 text-xs">
            User Inputs → Virtual Engine Physics → Simulated Telemetry
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App