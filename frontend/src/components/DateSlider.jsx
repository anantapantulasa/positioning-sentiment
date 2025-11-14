import React from 'react'
import { format, differenceInDays } from 'date-fns'
import './DateSlider.css'

const DateSlider = ({ minDate, maxDate, selectedDate, onDateChange }) => {
  if (!minDate || !maxDate) return null

  const min = new Date(minDate)
  const max = new Date(maxDate)
  const selected = selectedDate ? new Date(selectedDate) : max
  
  const totalDays = differenceInDays(max, min)
  const selectedDays = differenceInDays(selected, min)
  const percentage = (selectedDays / totalDays) * 100

  const handleSliderChange = (e) => {
    const daysFromMin = parseInt(e.target.value)
    const newDate = new Date(min)
    newDate.setDate(newDate.getDate() + daysFromMin)
    onDateChange(format(newDate, 'yyyy-MM-dd'))
  }

  return (
    <div className="date-slider-container">
      <div className="date-slider-header">
        <h3>Select Date</h3>
        <div className="selected-date-display">
          {format(selected, 'MMM dd, yyyy')}
        </div>
      </div>
      
      <div className="slider-wrapper">
        <input
          type="range"
          min={0}
          max={totalDays}
          value={selectedDays}
          onChange={handleSliderChange}
          className="date-slider"
        />
        
        <div className="slider-labels">
          <span>{format(min, 'MMM yyyy')}</span>
          <span>{format(max, 'MMM yyyy')}</span>
        </div>
      </div>
    </div>
  )
}

export default DateSlider

