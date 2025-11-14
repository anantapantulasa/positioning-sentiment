import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import CommodityDashboard from './components/CommodityDashboard'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/gold" replace />} />
      <Route 
        path="/gold" 
        element={<CommodityDashboard commodityKey="gold" commodityName="Gold" />} 
      />
      <Route 
        path="/coffee" 
        element={<CommodityDashboard commodityKey="coffee" commodityName="Coffee" />} 
      />
    </Routes>
  )
}

export default App

