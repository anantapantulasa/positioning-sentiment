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

const GoldChart = ({ data }) => {
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
    price: item.close
  }))

  const formatDate = (tickItem) => {
    try {
      return format(new Date(tickItem), 'MMM yyyy')
    } catch {
      return tickItem
    }
  }

  return (
    <div className="chart-container">
      <h2>Gold Price Over Time</h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            interval="preserveStartEnd"
          />
          <YAxis yAxisId="price" orientation="left" />
          <Tooltip
            labelFormatter={(value) => {
              try {
                return format(new Date(value), 'MMM dd, yyyy')
              } catch {
                return value
              }
            }}
            formatter={(value) => {
              return [`$${value.toFixed(2)}`, 'Price']
            }}
          />
          <Legend />
          
          {/* Price line */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="price"
            stroke="#FFD700"
            strokeWidth={2}
            dot={false}
            name="Gold Price"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default GoldChart

