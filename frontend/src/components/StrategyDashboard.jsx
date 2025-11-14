import React, { useState, useMemo } from 'react'
import { format, parseISO } from 'date-fns'
import './StrategyDashboard.css'

const StrategyDashboard = ({ data, selectedDate }) => {
  const [strategy, setStrategy] = useState('long') // 'long' or 'short'
  const [indexEnabled, setIndexEnabled] = useState({
    commercials: true,
    largeSpeculators: true,
    smallSpeculators: true
  })
  
  // Thresholds for long strategy
  const [longThresholds, setLongThresholds] = useState({
    commercials: 95,      // Commercials > threshold
    largeSpeculators: 5,  // Large Specs < threshold
    smallSpeculators: 5   // Small Specs < threshold
  })
  
  // Thresholds for short strategy
  const [shortThresholds, setShortThresholds] = useState({
    commercials: 5,        // Commercials < threshold
    largeSpeculators: 95,  // Large Specs > threshold
    smallSpeculators: 95   // Small Specs > threshold
  })

  // Find data for selected date
  const selectedDateData = useMemo(() => {
    if (!selectedDate || !data || data.length === 0) return null
    
    const targetDate = typeof selectedDate === 'string' 
      ? parseISO(selectedDate) 
      : new Date(selectedDate)
    
    // Find closest date match
    const targetTime = targetDate.getTime()
    let closest = null
    let minDiff = Infinity
    
    for (const item of data) {
      const itemTime = item.time instanceof Date 
        ? item.time.getTime() 
        : new Date(item.time).getTime()
      const diff = Math.abs(itemTime - targetTime)
      
      if (diff < minDiff) {
        minDiff = diff
        closest = item
      }
    }
    
    return closest
  }, [data, selectedDate])

  // Get index values
  const indexValues = useMemo(() => {
    if (!selectedDateData) {
      return {
        commercials: null,
        largeSpeculators: null,
        smallSpeculators: null
      }
    }

    return {
      commercials: selectedDateData['Commercials Index'] ?? null,
      largeSpeculators: selectedDateData['Large Speculators Index'] ?? null,
      smallSpeculators: selectedDateData['Small Speculators Index'] ?? null
    }
  }, [selectedDateData])

  // Calculate binary signal
  const binarySignal = useMemo(() => {
    if (!selectedDateData) return null

    const commercials = indexValues.commercials
    const largeSpecs = indexValues.largeSpeculators
    const smallSpecs = indexValues.smallSpeculators

    // Check if any values are null
    if (commercials === null || largeSpecs === null || smallSpecs === null) {
      return null
    }

    if (strategy === 'long') {
      // Long: Commercials > threshold AND Large Specs < threshold AND Small Specs < threshold
      const commercialsCheck = !indexEnabled.commercials || commercials > longThresholds.commercials
      const largeSpecsCheck = !indexEnabled.largeSpeculators || largeSpecs < longThresholds.largeSpeculators
      const smallSpecsCheck = !indexEnabled.smallSpeculators || smallSpecs < longThresholds.smallSpeculators
      
      return commercialsCheck && largeSpecsCheck && smallSpecsCheck
    } else {
      // Short: Commercials < threshold AND Large Specs > threshold AND Small Specs > threshold
      const commercialsCheck = !indexEnabled.commercials || commercials < shortThresholds.commercials
      const largeSpecsCheck = !indexEnabled.largeSpeculators || largeSpecs > shortThresholds.largeSpeculators
      const smallSpecsCheck = !indexEnabled.smallSpeculators || smallSpecs > shortThresholds.smallSpeculators
      
      return commercialsCheck && largeSpecsCheck && smallSpecsCheck
    }
  }, [strategy, indexValues, indexEnabled, longThresholds, shortThresholds, selectedDateData])

  const handleIndexToggle = (index) => {
    setIndexEnabled(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const handleThresholdChange = (strategyType, index, value) => {
    const numValue = parseFloat(value) || 0
    if (strategyType === 'long') {
      setLongThresholds(prev => ({
        ...prev,
        [index]: numValue
      }))
    } else {
      setShortThresholds(prev => ({
        ...prev,
        [index]: numValue
      }))
    }
  }

  const getCurrentThresholds = () => {
    return strategy === 'long' ? longThresholds : shortThresholds
  }

  const getThresholdOperator = (index, strategyType) => {
    if (strategyType === 'long') {
      return index === 'commercials' ? '>' : '<'
    } else {
      return index === 'commercials' ? '<' : '>'
    }
  }

  const checkRequirement = (index, value, threshold, operator) => {
    if (value === null) return null
    if (operator === '>') {
      return value > threshold
    } else {
      return value < threshold
    }
  }

  if (!selectedDate) {
    return (
      <div className="strategy-dashboard">
        <h2>Strategy Dashboard</h2>
        <p className="no-date-message">Please select a date to view strategy signals</p>
      </div>
    )
  }

  return (
    <div className="strategy-dashboard">
      <h2>Strategy Dashboard</h2>
      
      <div className="strategy-selector">
        <label>Strategy:</label>
        <div className="strategy-buttons">
          <button
            className={strategy === 'long' ? 'active' : ''}
            onClick={() => setStrategy('long')}
          >
            Long
          </button>
          <button
            className={strategy === 'short' ? 'active' : ''}
            onClick={() => setStrategy('short')}
          >
            Short
          </button>
        </div>
      </div>

      <div className="selected-date-info">
        <p className="date-label">
          Selected Date: <strong>{format(parseISO(selectedDate), 'MMM dd, yyyy')}</strong>
        </p>
      </div>

      <div className="index-values">
        <h3>Index Values (0-100)</h3>
        <div className="index-list">
          <div className="index-item">
            <div className="index-header">
              <span className="index-name">Commercials</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={indexEnabled.commercials}
                  onChange={() => handleIndexToggle('commercials')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="index-value">
              {indexValues.commercials !== null 
                ? indexValues.commercials.toFixed(1) 
                : 'N/A'}
            </div>
            {indexEnabled.commercials && (
              <div className="threshold-control">
                <label>
                  Threshold:
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={getCurrentThresholds().commercials}
                    onChange={(e) => handleThresholdChange(strategy, 'commercials', e.target.value)}
                    className="threshold-input"
                  />
                </label>
                <div className="index-requirement">
                  Required: {getThresholdOperator('commercials', strategy)} {getCurrentThresholds().commercials}
                  {indexValues.commercials !== null && (
                    <span className={checkRequirement('commercials', indexValues.commercials, getCurrentThresholds().commercials, getThresholdOperator('commercials', strategy)) ? 'met' : 'not-met'}>
                      {checkRequirement('commercials', indexValues.commercials, getCurrentThresholds().commercials, getThresholdOperator('commercials', strategy)) ? ' ✓' : ' ✗'}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="index-item">
            <div className="index-header">
              <span className="index-name">Large Speculators</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={indexEnabled.largeSpeculators}
                  onChange={() => handleIndexToggle('largeSpeculators')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="index-value">
              {indexValues.largeSpeculators !== null 
                ? indexValues.largeSpeculators.toFixed(1) 
                : 'N/A'}
            </div>
            {indexEnabled.largeSpeculators && (
              <div className="threshold-control">
                <label>
                  Threshold:
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={getCurrentThresholds().largeSpeculators}
                    onChange={(e) => handleThresholdChange(strategy, 'largeSpeculators', e.target.value)}
                    className="threshold-input"
                  />
                </label>
                <div className="index-requirement">
                  Required: {getThresholdOperator('largeSpeculators', strategy)} {getCurrentThresholds().largeSpeculators}
                  {indexValues.largeSpeculators !== null && (
                    <span className={checkRequirement('largeSpeculators', indexValues.largeSpeculators, getCurrentThresholds().largeSpeculators, getThresholdOperator('largeSpeculators', strategy)) ? 'met' : 'not-met'}>
                      {checkRequirement('largeSpeculators', indexValues.largeSpeculators, getCurrentThresholds().largeSpeculators, getThresholdOperator('largeSpeculators', strategy)) ? ' ✓' : ' ✗'}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="index-item">
            <div className="index-header">
              <span className="index-name">Small Speculators</span>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={indexEnabled.smallSpeculators}
                  onChange={() => handleIndexToggle('smallSpeculators')}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="index-value">
              {indexValues.smallSpeculators !== null 
                ? indexValues.smallSpeculators.toFixed(1) 
                : 'N/A'}
            </div>
            {indexEnabled.smallSpeculators && (
              <div className="threshold-control">
                <label>
                  Threshold:
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={getCurrentThresholds().smallSpeculators}
                    onChange={(e) => handleThresholdChange(strategy, 'smallSpeculators', e.target.value)}
                    className="threshold-input"
                  />
                </label>
                <div className="index-requirement">
                  Required: {getThresholdOperator('smallSpeculators', strategy)} {getCurrentThresholds().smallSpeculators}
                  {indexValues.smallSpeculators !== null && (
                    <span className={checkRequirement('smallSpeculators', indexValues.smallSpeculators, getCurrentThresholds().smallSpeculators, getThresholdOperator('smallSpeculators', strategy)) ? 'met' : 'not-met'}>
                      {checkRequirement('smallSpeculators', indexValues.smallSpeculators, getCurrentThresholds().smallSpeculators, getThresholdOperator('smallSpeculators', strategy)) ? ' ✓' : ' ✗'}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="binary-signal">
        <h3>Binary Signal</h3>
        {binarySignal === null ? (
          <div className="signal-result unavailable">
            <span>Unable to calculate (missing index data)</span>
          </div>
        ) : (
          <div className={`signal-result ${binarySignal ? 'active' : 'inactive'}`}>
            <span className="signal-icon">{binarySignal ? '✓' : '✗'}</span>
            <span className="signal-text">
              {binarySignal ? 'Signal Active' : 'Signal Inactive'}
            </span>
          </div>
        )}
        <div className="signal-explanation">
          {strategy === 'long' ? (
            <p>
              Long signal is active when: Commercials &gt; {longThresholds.commercials} AND Large Speculators &lt; {longThresholds.largeSpeculators} AND Small Speculators &lt; {longThresholds.smallSpeculators}
              <br />
              (Disabled indices are ignored in the calculation)
            </p>
          ) : (
            <p>
              Short signal is active when: Commercials &lt; {shortThresholds.commercials} AND Large Speculators &gt; {shortThresholds.largeSpeculators} AND Small Speculators &gt; {shortThresholds.smallSpeculators}
              <br />
              (Disabled indices are ignored in the calculation)
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default StrategyDashboard

