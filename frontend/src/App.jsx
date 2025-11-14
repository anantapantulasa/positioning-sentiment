import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format, parseISO, subDays } from 'date-fns'
import GoldChart from './components/GoldChart'
import IndexChart from './components/IndexChart'
import SignalDisplay from './components/SignalDisplay'
import DateSelector from './components/DateSelector'
import IndexToggles from './components/IndexToggles'
import StrategyDashboard from './components/StrategyDashboard'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [goldData, setGoldData] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [tradingSignal, setTradingSignal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [signalLoading, setSignalLoading] = useState(false)
  const [indexVisibility, setIndexVisibility] = useState({
    commercials: false,
    largeSpeculators: false,
    smallSpeculators: false
  })

  useEffect(() => {
    fetchGoldData()
  }, [])

  useEffect(() => {
    if (selectedDate) {
      fetchTradingSignal(selectedDate)
    }
  }, [selectedDate])

  const fetchGoldData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/gold/data`)
      const data = response.data
        .map(item => ({
          ...item,
          time: item.time ? new Date(item.time) : null
        }))
        .filter(item => item.time !== null)
        .sort((a, b) => a.time - b.time)
      
      setGoldData(data)
      
      // Set initial selected date to the most recent date
      if (data.length > 0) {
        const lastDate = data[data.length - 1].time
        setSelectedDate(format(lastDate, 'yyyy-MM-dd'))
      }
    } catch (error) {
      console.error('Error fetching gold data:', error)
      alert('Error loading gold data. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const fetchTradingSignal = async (date) => {
    if (!date) {
      console.warn('No date provided for signal fetch')
      return
    }
    try {
      setSignalLoading(true)
      console.log(`🔍 Fetching trading signal for date: ${date}`)
      const response = await axios.get(`${API_BASE_URL}/api/gold/signal/${date}`)
      console.log('✅ Signal response:', response.data)
      setTradingSignal(response.data)
    } catch (error) {
      console.error('❌ Error fetching trading signal:', error)
      if (error.response) {
        console.error('Response status:', error.response.status)
        console.error('Response data:', error.response.data)
      }
      setTradingSignal(null)
    } finally {
      setSignalLoading(false)
    }
  }

  const handleDateChange = (date) => {
    console.log('📅 Date changed to:', date)
    setSelectedDate(date)
  }

  const handleIndexToggle = (index) => {
    setIndexVisibility(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading gold data...</div>
      </div>
    )
  }

  const dateRange = goldData.length > 0 ? {
    min: goldData[0].time,
    max: goldData[goldData.length - 1].time
  } : null

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Gold Trading Signal Dashboard</h1>
        <p>Analyze gold prices with sentiment-based trading signals</p>
      </header>

      <div className="main-content">
        <div className="chart-section">
          <div className="controls-panel">
            <IndexToggles
              visibility={indexVisibility}
              onToggle={handleIndexToggle}
            />
          </div>
          
          <GoldChart
            data={goldData}
          />
          
          <IndexChart
            data={goldData}
            indexVisibility={indexVisibility}
          />

          {dateRange && (
            <DateSelector
              minDate={dateRange.min}
              maxDate={dateRange.max}
              selectedDate={selectedDate}
              onDateChange={handleDateChange}
            />
          )}
        </div>

        <div className="signal-section">
          <StrategyDashboard
            data={goldData}
            selectedDate={selectedDate}
          />
          <SignalDisplay
            signal={tradingSignal}
            loading={signalLoading}
            selectedDate={selectedDate}
          />
        </div>
      </div>
    </div>
  )
}

export default App

