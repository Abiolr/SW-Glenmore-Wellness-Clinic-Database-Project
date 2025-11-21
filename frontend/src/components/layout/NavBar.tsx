import React from 'react'
import { Link } from 'react-router-dom'


export default function NavBar() {
  return (
    <nav className="app-navbar" style={{
      background: '#f0f0f0',
      padding: '0.75rem 1rem',
      borderBottom: '1px solid #ccc'
    }}>
      <ul style={{
        display: 'flex',
        gap: '1.5rem',
        listStyle: 'none',
        margin: 0,
        padding: 0
      }}>
        {/* Billing */}
        <li><Link to="/billing/insurance">Insurance</Link></li>
        <li><Link to="/billing/monthly">Monthly</Link></li>
        <li><Link to="/billing/prescriptions">Prescriptions</Link></li>

        {/* Logs */}
        <li><Link to="/logs/delivery">Delivery Log</Link></li>
        <li><Link to="/logs/laboratory">Lab Log</Link></li>
        <li><Link to="/logs/recovery">Recovery Log</Link></li>
      </ul>
    </nav>
  )
}
