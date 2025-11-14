import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { format } from 'date-fns'

const IndexChart = ({ data, indexVisibility }) => {
  // Check if any index is visible
  const hasVisibleIndices = Object.values(indexVisibility).some(v => v)
  
  if (!hasVisibleIndices) {
    return null
  }

  // Filter data to start from Sept 1, 2022
  const startDate = new Date('2022-09-01')
  const filteredData = data.filter(item => {
    const itemDate = item.time instanceof Date ? item.time : new Date(item.time)
    return itemDate >= startDate
  })

  // Format data for chart
  const chartData = filteredData.map(item => ({
    date: item.time,
    dateLabel: format(new Date(item.time), 'MMM dd, yyyy'),
    commercials: item['Commercials Index'],
    largeSpeculators: item['Large Speculators Index'],
    smallSpeculators: item['Small Speculators Index']
  }))

  const formatDate = (tickItem) => {
    try {
      return format(new Date(tickItem), 'MMM yyyy')
    } catch {
      return tickItem
    }
  }

  return (
    <div className="index-chart-container">
      <h2>Speculator Indices</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            interval="preserveStartEnd"
          />
          <YAxis domain={[0, 100]} />
          <Tooltip
            labelFormatter={(value) => {
              try {
                return format(new Date(value), 'MMM dd, yyyy')
              } catch {
                return value
              }
            }}
            formatter={(value) => {
              return [value?.toFixed(1) || 'N/A', '']
            }}
          />
          <Legend />
          
          {/* Index lines (toggleable) */}
          {indexVisibility.commercials && (
            <Line
              type="monotone"
              dataKey="commercials"
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
              name="Commercials Index"
            />
          )}
          
          {indexVisibility.largeSpeculators && (
            <Line
              type="monotone"
              dataKey="largeSpeculators"
              stroke="#82ca9d"
              strokeWidth={2}
              dot={false}
              name="Large Speculators Index"
            />
          )}
          
          {indexVisibility.smallSpeculators && (
            <Line
              type="monotone"
              dataKey="smallSpeculators"
              stroke="#ffc658"
              strokeWidth={2}
              dot={false}
              name="Small Speculators Index"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default IndexChart

