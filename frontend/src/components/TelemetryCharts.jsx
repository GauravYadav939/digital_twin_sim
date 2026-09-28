/**
 * Telemetry Charts Component
 * Real-time line charts for engine parameters
 */

import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function TelemetryCharts({ telemetry, history }) {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(19, 24, 37, 0.9)',
        titleColor: '#fff',
        bodyColor: '#e5e7eb',
        borderColor: '#3b82f6',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: '#1e2638'
        },
        ticks: {
          color: '#9ca3af',
          maxTicksLimit: 10
        }
      },
      y: {
        display: true,
        grid: {
          color: '#1e2638'
        },
        ticks: {
          color: '#9ca3af'
        }
      }
    }
  }

  // Prepare data from history
  const times = history.map(d => d.time?.toFixed(1) || 0)

  const charts = [
    {
      title: 'Engine Speed',
      data: history.map(d => d.N_rpm || 0),
      color: '#3b82f6',
      unit: 'RPM'
    },
    {
      title: 'Cylinder Head Temperature',
      data: history.map(d => d.T_CHT_C || 0),
      color: '#ef4444',
      unit: '°C'
    },
    {
      title: 'Exhaust Gas Temperature',
      data: history.map(d => d.T_EGT_C || 0),
      color: '#f59e0b',
      unit: '°C'
    },
    {
      title: 'Oil Temperature',
      data: history.map(d => d.T_oil_C || 0),
      color: '#10b981',
      unit: '°C'
    },
    {
      title: 'Oil Pressure',
      data: history.map(d => d.P_oil_psi || 0),
      color: '#8b5cf6',
      unit: 'PSI'
    },
    {
      title: 'Fuel Flow',
      data: history.map(d => d.fuel_flow_Lph || 0),
      color: '#06b6d4',
      unit: 'L/h'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-lg p-6">
        <h3 className="text-lg font-bold text-white mb-6">
          Real-Time Telemetry
        </h3>

        {history.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            <p>No telemetry data yet. Start simulation to see charts.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {charts.map((chart) => (
              <div key={chart.title} className="bg-engine-bg rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-300 mb-3">
                  {chart.title}
                </h4>
                <div style={{ height: '200px' }}>
                  <Line
                    data={{
                      labels: times,
                      datasets: [
                        {
                          data: chart.data,
                          borderColor: chart.color,
                          backgroundColor: chart.color + '20',
                          borderWidth: 2,
                          tension: 0.4,
                          pointRadius: 0
                        }
                      ]
                    }}
                    options={chartOptions}
                  />
                </div>
                <div className="mt-2 text-right text-xs text-gray-500">
                  Current: <span style={{color: chart.color}} className="font-medium">
                    {chart.data[chart.data.length - 1]?.toFixed(1) || '0.0'} {chart.unit}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Energy Split */}
      {telemetry && (
        <div className="glass-panel rounded-lg p-6">
          <h3 className="text-lg font-bold text-white mb-6">
            Energy Distribution
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <EnergyBar
              label="Brake Work"
              value={telemetry.energy_split_brake_pct || 0}
              color="#10b981"
            />
            <EnergyBar
              label="Exhaust"
              value={telemetry.energy_split_exhaust_pct || 0}
              color="#f59e0b"
            />
            <EnergyBar
              label="CHT Heat"
              value={telemetry.energy_split_CHT_pct || 0}
              color="#ef4444"
            />
            <EnergyBar
              label="Oil Heat"
              value={telemetry.energy_split_oil_pct || 0}
              color="#8b5cf6"
            />
          </div>
        </div>
      )}
    </div>
  )
}

function EnergyBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-300">{label}</span>
        <span className="text-sm font-bold text-white">{value.toFixed(1)}%</span>
      </div>
      <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-300"
          style={{
            width: `${value}%`,
            backgroundColor: color
          }}
        />
      </div>
    </div>
  )
}