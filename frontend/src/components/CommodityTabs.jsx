import React from 'react'
import './CommodityTabs.css'

const CommodityTabs = ({ commodities, selectedCommodity, onCommodityChange }) => {
  if (!commodities || commodities.length === 0) {
    return null
  }

  return (
    <div className="commodity-tabs">
      {commodities.map(commodity => (
        <button
          key={commodity.key}
          className={`commodity-tab ${selectedCommodity === commodity.key ? 'active' : ''}`}
          onClick={() => onCommodityChange(commodity.key)}
        >
          {commodity.name}
        </button>
      ))}
    </div>
  )
}

export default CommodityTabs

