import React from 'react'
import './IndexToggles.css'

const IndexToggles = ({ visibility, onToggle }) => {
  const indices = [
    { key: 'commercials', label: 'Commercials Index', color: '#8884d8' },
    { key: 'largeSpeculators', label: 'Large Speculators Index', color: '#00ff88' },
    { key: 'smallSpeculators', label: 'Small Speculators Index', color: '#ffc658' }
  ]

  return (
    <div className="index-toggles">
      <h3>Toggle Index Overlays</h3>
      <div className="toggle-buttons">
        {indices.map(index => (
          <button
            key={index.key}
            className={`toggle-button ${visibility[index.key] ? 'active' : ''}`}
            onClick={() => onToggle(index.key)}
            style={{
              borderColor: index.color,
              backgroundColor: visibility[index.key] ? `rgba(${index.key === 'commercials' ? '136, 132, 216' : index.key === 'largeSpeculators' ? '0, 255, 136' : '255, 198, 88'}, 0.2)` : 'transparent',
              color: visibility[index.key] ? index.color : index.color
            }}
          >
            {index.label}
          </button>
        ))}
      </div>
    </div>
  )
}

export default IndexToggles

