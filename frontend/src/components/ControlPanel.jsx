/**
 * Control Panel Component
 * Input sliders for throttle, load, altitude, temperature
 */

export default function ControlPanel({ inputs, onInputChange, disabled }) {
  const controls = [
    {
      name: 'throttle_pct',
      label: 'Throttle',
      value: inputs.throttle_pct,
      min: 0,
      max: 100,
      step: 1,
      unit: '%',
      color: 'text-green-400'
    },
    {
      name: 'load_pct',
      label: 'Engine Load',
      value: inputs.load_pct,
      min: 0,
      max: 100,
      step: 1,
      unit: '%',
      color: 'text-orange-400'
    },
    {
      name: 'altitude_m',
      label: 'Altitude',
      value: inputs.altitude_m,
      min: 0,
      max: 5000,
      step: 100,
      unit: 'm',
      color: 'text-blue-400'
    },
    {
      name: 'T_ambient_C',
      label: 'Ambient Temperature',
      value: inputs.T_ambient_C,
      min: -20,
      max: 50,
      step: 1,
      unit: '°C',
      color: 'text-red-400'
    }
  ]

  return (
    <div className="glass-panel rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-6">
        Operating Conditions
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {controls.map((control) => (
          <div key={control.name} className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-300">
                {control.label}
              </label>
              <span className={`text-lg font-bold ${control.color}`}>
                {control.value}{control.unit}
              </span>
            </div>

            <input
              type="range"
              min={control.min}
              max={control.max}
              step={control.step}
              value={control.value}
              onChange={(e) => onInputChange(control.name, parseFloat(e.target.value))}
              disabled={disabled}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: disabled
                  ? '#374151'
                  : `linear-gradient(to right, ${getSliderColor(control.name)} 0%, ${getSliderColor(control.name)} ${((control.value - control.min) / (control.max - control.min)) * 100}%, #374151 ${((control.value - control.min) / (control.max - control.min)) * 100}%, #374151 100%)`
              }}
            />

            <div className="flex justify-between text-xs text-gray-500">
              <span>{control.min}{control.unit}</span>
              <span>{control.max}{control.unit}</span>
            </div>
          </div>
        ))}
      </div>

      {disabled && (
        <div className="mt-4 text-center text-sm text-yellow-500">
          ⚠️ Controls locked during simulation. Stop to adjust.
        </div>
      )}
    </div>
  )
}

function getSliderColor(name) {
  const colors = {
    throttle_pct: '#10b981',
    load_pct: '#f59e0b',
    altitude_m: '#3b82f6',
    T_ambient_C: '#ef4444'
  }
  return colors[name] || '#6b7280'
}