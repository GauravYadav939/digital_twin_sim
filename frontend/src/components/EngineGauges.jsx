/**
 * Engine Gauges Component
 * Circular gauges for key engine parameters
 */

import { Gauge } from 'lucide-react'

export default function EngineGauges({ telemetry }) {
  const gauges = [
    {
      label: 'RPM',
      value: telemetry?.N_rpm || 0,
      unit: '',
      min: 0,
      max: 3000,
      warning: 2500,
      danger: 2800,
      color: '#3b82f6'
    },
    {
      label: 'CHT',
      value: telemetry?.T_CHT_C || 0,
      unit: '°C',
      min: 0,
      max: 300,
      warning: 240,
      danger: 260,
      color: '#ef4444'
    },
    {
      label: 'EGT',
      value: telemetry?.T_EGT_C || 0,
      unit: '°C',
      min: 0,
      max: 1000,
      warning: 850,
      danger: 900,
      color: '#f59e0b'
    },
    {
      label: 'Oil Temp',
      value: telemetry?.T_oil_C || 0,
      unit: '°C',
      min: 0,
      max: 150,
      warning: 115,
      danger: 130,
      color: '#10b981'
    },
    {
      label: 'Oil Pressure',
      value: telemetry?.P_oil_psi || 0,
      unit: 'PSI',
      min: 0,
      max: 100,
      warning: 30,
      danger: 20,
      reversed: true,
      color: '#8b5cf6'
    },
    {
      label: 'Fuel Flow',
      value: telemetry?.fuel_flow_Lph || 0,
      unit: 'L/h',
      min: 0,
      max: 300,
      warning: 250,
      danger: 280,
      color: '#06b6d4'
    }
  ]

  return (
    <div className="glass-panel rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-6 flex items-center space-x-2">
        <Gauge size={20} />
        <span>Engine Parameters</span>
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {gauges.map((gauge) => (
          <CircularGauge key={gauge.label} {...gauge} />
        ))}
      </div>

      {telemetry && (
        <div className="mt-6 pt-6 border-t border-engine-border grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Brake Power</div>
            <div className="text-xl font-bold text-white mt-1">
              {telemetry.P_brake_kW?.toFixed(1) || '0.0'} kW
            </div>
          </div>
          <div>
            <div className="text-gray-400">Torque</div>
            <div className="text-xl font-bold text-white mt-1">
              {telemetry.torque_Nm?.toFixed(1) || '0.0'} Nm
            </div>
          </div>
          <div>
            <div className="text-gray-400">Vibration</div>
            <div className="text-xl font-bold text-white mt-1">
              {telemetry.vibration?.toFixed(2) || '0.00'}
            </div>
          </div>
          <div>
            <div className="text-gray-400">Time</div>
            <div className="text-xl font-bold text-white mt-1">
              {telemetry.time?.toFixed(1) || '0.0'}s
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function CircularGauge({ label, value, unit, min, max, warning, danger, reversed, color }) {
  const percentage = ((value - min) / (max - min)) * 100
  const clampedPercentage = Math.max(0, Math.min(100, percentage))

  // Determine status color
  let statusColor = color
  if (reversed) {
    if (value < danger) statusColor = '#ef4444'
    else if (value < warning) statusColor = '#f59e0b'
  } else {
    if (value > danger) statusColor = '#ef4444'
    else if (value > warning) statusColor = '#f59e0b'
  }

  const circumference = 2 * Math.PI * 45
  const offset = circumference - (clampedPercentage / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90">
          {/* Background circle */}
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="#1e2638"
            strokeWidth="8"
            fill="none"
          />
          {/* Value circle */}
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke={statusColor}
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-300"
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-2xl font-bold text-white">
            {value.toFixed(0)}
          </div>
          <div className="text-xs text-gray-400">{unit}</div>
        </div>
      </div>

      <div className="mt-2 text-center">
        <div className="text-sm font-medium text-white">{label}</div>
        <div className="text-xs text-gray-500 mt-1">
          {min} - {max}{unit}
        </div>
      </div>
    </div>
  )
}