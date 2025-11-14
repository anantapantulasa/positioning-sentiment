import React from 'react'
import { format, parseISO } from 'date-fns'
import './DateSelector.css'

const DateSelector = ({ minDate, maxDate, selectedDate, onDateChange }) => {
  if (!minDate || !maxDate) return null

  // Format dates as YYYY-MM-DD strings to avoid timezone issues
  const formatDateString = (date) => {
    if (!date) return ''
    // If it's already a string in YYYY-MM-DD format, use it directly
    if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
      return date
    }
    // Otherwise, format the date object
    const d = date instanceof Date ? date : new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const minStr = formatDateString(minDate)
  const maxStr = formatDateString(maxDate)
  const selectedStr = selectedDate || formatDateString(maxDate)

  const handleDateInputChange = (e) => {
    const inputDate = e.target.value // This is already in YYYY-MM-DD format
    console.log('📅 Date input changed to:', inputDate)
    
    if (!inputDate) return

    // Compare as strings to avoid timezone issues
    if (inputDate >= minStr && inputDate <= maxStr) {
      console.log('✅ Date is valid, calling onDateChange with:', inputDate)
      onDateChange(inputDate)
    } else {
      alert(`Please select a date between ${format(parseISO(minStr), 'MMM dd, yyyy')} and ${format(parseISO(maxStr), 'MMM dd, yyyy')}`)
    }
  }

  // Display formatted date for user
  const displayDate = selectedDate ? format(parseISO(selectedDate), 'MMM dd, yyyy') : format(parseISO(selectedStr), 'MMM dd, yyyy')

  return (
    <div className="date-selector-container">
      <div className="date-selector-header">
        <h3>Select Date</h3>
        <div className="date-input-wrapper">
          <label htmlFor="date-input">Date:</label>
          <input
            id="date-input"
            type="date"
            value={selectedStr}
            min={minStr}
            max={maxStr}
            onChange={handleDateInputChange}
            className="date-input"
          />
          <div className="selected-date-display">
            {displayDate}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DateSelector

