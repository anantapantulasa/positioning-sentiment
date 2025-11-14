import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'
import GoldChart from './GoldChart'
import IndexChart from './IndexChart'
import SignalDisplay from './SignalDisplay'
import DateSelector from './DateSelector'
import IndexToggles from './IndexToggles'
import StrategyDashboard from './StrategyDashboard'
import Navigation from './Navigation'

const API_BASE_URL = 'http://localhost:8000'

const CommodityDashboard = ({ commodityKey, commodityName }) => {
  const [commodityData, setCommodityData] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [tradingSignal, setTradingSignal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [signalLoading, setSignalLoading] = useState(false)
  const [indexVisibility, setIndexVisibility] = useState({
    commercials: false,
    largeSpeculators: false,
    smallSpeculators: false
  })
  const [binarySignals, setBinarySignals] = useState({
    long: null,
    short: null
  })

  useEffect(() => {
    if (commodityKey) {
      fetchCommodityData(commodityKey)
    }
  }, [commodityKey])

  useEffect(() => {
    if (selectedDate && commodityKey) {
      fetchTradingSignal(commodityKey, selectedDate)
    }
  }, [selectedDate, commodityKey])

  const fetchCommodityData = async (commodity) => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/${commodity}/data`)
      const data = response.data
        .map(item => ({
          ...item,
          time: item.time ? new Date(item.time) : null
        }))
        .filter(item => item.time !== null)
        .sort((a, b) => a.time - b.time)
      
      setCommodityData(data)
      
      // Set initial selected date to the most recent date
      if (data.length > 0) {
        const lastDate = data[data.length - 1].time
        setSelectedDate(format(lastDate, 'yyyy-MM-dd'))
      }
    } catch (error) {
      console.error(`Error fetching ${commodity} data:`, error)
      alert(`Error loading ${commodity} data. Make sure the backend is running.`)
    } finally {
      setLoading(false)
    }
  }

  const fetchTradingSignal = async (commodity, date) => {
    if (!date) {
      console.warn('No date provided for signal fetch')
      return
    }
    try {
      setSignalLoading(true)
      console.log(`🔍 Fetching trading signal for ${commodity} on date: ${date}`)
      const response = await axios.get(`${API_BASE_URL}/api/${commodity}/signal/${date}`)
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
        <div className="loading">Loading {commodityName} data...</div>
      </div>
    )
  }

  const dateRange = commodityData.length > 0 ? {
    min: commodityData[0].time,
    max: commodityData[commodityData.length - 1].time
  } : null

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>{commodityName} Trading Signal Dashboard</h1>
        <p>Analyze {commodityName.toLowerCase()} prices with sentiment-based trading signals</p>
      </header>

      <Navigation />

      <div className="main-content">
        <div className="chart-section">
          <div className="controls-panel">
            <IndexToggles
              visibility={indexVisibility}
              onToggle={handleIndexToggle}
            />
          </div>
          
          <GoldChart
            data={commodityData}
            commodityName={commodityName}
          />
          
          <IndexChart
            data={commodityData}
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
            data={commodityData}
            selectedDate={selectedDate}
            onBinarySignalsChange={setBinarySignals}
          />
          <SignalDisplay
            signal={tradingSignal}
            loading={signalLoading}
            selectedDate={selectedDate}
            binarySignals={binarySignals}
          />
        </div>
      </div>
    </div>
  )
}

export default CommodityDashboard

