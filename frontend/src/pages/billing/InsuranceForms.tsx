import React, { useEffect, useState } from 'react'
import { get } from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import PhysicianStatement from '../../components/billing/PhysicianStatement'
import './InsurancePrint.css'
import '../../styles/logLayout.css'

export default function InsuranceForms() {
  // For insurance receipt/statement
  const [invoices, setInvoices] = useState<any[]>([])
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | null>(null)
  const [invoiceLoading, setInvoiceLoading] = useState(true)
  const [invoiceError, setInvoiceError] = useState<string | null>(null)

  // Load invoices directly from the invoices collection
  useEffect(() => {
    setInvoiceLoading(true)
    get<any[]>('/invoices')
      .then((data) => {
        console.log('All invoices:', data)
        setInvoices(data || [])
      })
      .catch(() => setInvoiceError('Failed to load invoices'))
      .finally(() => setInvoiceLoading(false))
  }, [])

  // Helper to get field values with case tolerance
  const getField = (obj: any, ...keys: string[]) => {
    if (!obj) return null
    for (const key of keys) {
      if (obj[key] !== undefined && obj[key] !== null) return obj[key]
    }
    return null
  }

  if (invoiceLoading) return <LoadingSpinner />
  if (invoiceError) return <ErrorMessage message={invoiceError} />

  return (
    <div className="log-page">
      <div className="toolbar toolbar-centered" style={{ gap:16 }}>
        <h3 style={{ margin:0 }}>Insurance Receipt / Physician Statement</h3>
        {invoices.length === 0 ? (
          <span className="muted">No invoices</span>
        ) : (
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
            <label htmlFor="invoice-select" style={{ fontWeight:600 }}>Select Invoice</label>
            <select
              className="select"
              id="invoice-select"
              value={selectedInvoiceId ?? ''}
              onChange={e => {
                const raw = e.target.value
                if (!raw) { setSelectedInvoiceId(null); return }
                const parsed = parseInt(raw, 10)
                console.log('Selected invoice ID:', parsed)
                setSelectedInvoiceId(Number.isNaN(parsed) ? null : parsed)
              }}
              style={{ minWidth:280 }}
            >
              <option value="">-- Select Invoice --</option>
              {invoices.map((inv, idx) => {
                const invId = getField(inv, 'invoice_id', 'Invoice_Id')
                const invDate = getField(inv, 'invoice_date', 'Invoice_Date') || 'N/A'
                const patientId = getField(inv, 'patient_id', 'Patient_Id')
                const status = getField(inv, 'status', 'Status') || 'Unknown'
                const totalAmount = getField(inv, 'total_amount', 'Total_Amount') || 0
                return (
                  <option key={`inv-${invId || idx}`} value={invId}>
                    #{invId} Patient {patientId} | {invDate} | ${Number(totalAmount).toFixed(2)} | {status}
                  </option>
                )
              })}
            </select>
          </div>
        )}
      </div>
      {selectedInvoiceId && (
        <div className="card">
          <PhysicianStatement invoiceId={selectedInvoiceId} />
        </div>
      )}
    </div>
  )
}
