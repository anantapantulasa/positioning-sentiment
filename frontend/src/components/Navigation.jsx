import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Navigation.css'

const Navigation = () => {
  const location = useLocation()

  return (
    <nav className="navigation">
      <Link 
        to="/gold" 
        className={`nav-link ${location.pathname === '/gold' ? 'active' : ''}`}
      >
        Gold
      </Link>
      <Link 
        to="/coffee" 
        className={`nav-link ${location.pathname === '/coffee' ? 'active' : ''}`}
      >
        Coffee
      </Link>
    </nav>
  )
}

export default Navigation

