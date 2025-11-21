import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Billing Pages
import InsuranceForms from './pages/billing/InsuranceForms'
import MonthlyStatements from './pages/billing/MonthlyStatements'
import Prescriptions from './pages/billing/Prescriptions'

// Logs Pages
import DeliveryRoom from './pages/logs/DeliveryRoom'
import Laboratory from './pages/logs/Laboratory'
import RecoveryRoom from './pages/logs/RecoveryRoom'
import LogsIndex from './pages/logs/LogsIndex'

// Optional: shared layout or navigation wrapper
import Layout from './components/layout/Layout'

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Billing Routes */}
          <Route path="/billing/insurance" element={<InsuranceForms />} />
          <Route path="/billing/monthly" element={<MonthlyStatements />} />
          <Route path="/billing/prescriptions" element={<Prescriptions />} />

          {/* Logs Routes */}
          <Route path="/logs" element={<LogsIndex />} />
          <Route path="/logs/delivery" element={<DeliveryRoom />} />
          <Route path="/logs/delivery/:visitId" element={<DeliveryRoom />} />
          <Route path="/logs/laboratory" element={<Laboratory />} />
          <Route path="/logs/laboratory/:visitId" element={<Laboratory />} />
          <Route path="/logs/recovery" element={<RecoveryRoom />} />
          <Route path="/logs/recovery/:stayId" element={<RecoveryRoom />} />
        </Routes>
      </Layout>
    </Router>
  )
}
