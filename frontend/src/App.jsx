import { useState, useEffect } from 'react'
import SimulatorDashboard from './components/SimulatorDashboard'
import { ExternalLink, AlertCircle } from 'lucide-react'
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

      {/* About Section */}
      <div className="max-w-7xl mx-auto px-6 pt-6">
        <div className="glass-panel rounded-lg p-6 mb-6">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
            <AlertCircle size={20} className="text-blue-400" />
            <span>About This Simulator</span>
          </h2>
          <p className="text-gray-300 leading-relaxed mb-4">
            This is a <span className="text-blue-400 font-semibold">piston engine simulator</span> replicating a UAV's piston engine.
            This engine simulator is made keeping the following as benchmarks:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <a
              href="https://www.faa.gov/regulationspolicies/handbooksmanuals/aviation/faa-h-8083-32b-aviation-maintenance-technician"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start space-x-2 p-3 bg-engine-bg rounded border border-engine-border hover:border-blue-500 transition-colors"
            >
              <ExternalLink size={16} className="text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-white">FAA Handbook</div>
                <div className="text-xs text-gray-400 mt-1">Aviation Maintenance Technician</div>
              </div>
            </a>

            <a
              href="https://dl.icdst.org/pdfs/files3/99e7aaa5c9b3ad06088da291045abca2.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start space-x-2 p-3 bg-engine-bg rounded border border-engine-border hover:border-blue-500 transition-colors"
            >
              <ExternalLink size={16} className="text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-white">Internal Combustion Engine</div>
                <div className="text-xs text-gray-400 mt-1">Fundamentals & Theory</div>
              </div>
            </a>

            <a
              href="https://www.grc.nasa.gov/WWW/k-12/BGP/otto.html"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start space-x-2 p-3 bg-engine-bg rounded border border-engine-border hover:border-blue-500 transition-colors"
            >
              <ExternalLink size={16} className="text-blue-400 mt-1 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-white">NASA Otto Cycle</div>
                <div className="text-xs text-gray-400 mt-1">Thermodynamics & Propulsion</div>
              </div>
            </a>
          </div>

          <p className="text-sm text-gray-400 italic">
            ✓ This engine simulator satisfies all basic thermodynamic laws
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 pb-6">
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