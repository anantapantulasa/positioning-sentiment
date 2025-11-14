import React from 'react'
import './IndexToggles.css'

const IndexToggles = ({ visibility, onToggle }) => {
  const indices = [
    { key: 'commercials', label: 'Commercials Index', color: '#8884d8' },
    { key: 'largeSpeculators', label: 'Large Speculators Index', color: '#82ca9d' },
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
              backgroundColor: visibility[index.key] ? index.color : 'transparent',
              color: visibility[index.key] ? 'white' : index.color
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

