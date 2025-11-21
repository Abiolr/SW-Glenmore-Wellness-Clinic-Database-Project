import React, { useEffect, useState } from 'react'
import { getInsurers, createInsurer } from '../../api/functions'
import { getInvoiceSummary, InvoicePaymentSummary } from '../../api/views'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import PhysicianStatement from '../../components/billing/PhysicianStatement'

export default function InsuranceForms() {
  const [insurers, setInsurers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [name, setName] = useState('')

  // For insurance receipt/statement
  const [invoices, setInvoices] = useState<InvoicePaymentSummary[]>([])
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | null>(null)
  const [invoiceLoading, setInvoiceLoading] = useState(true)
  const [invoiceError, setInvoiceError] = useState<string | null>(null)

  useEffect(() => {
    getInsurers()
      .then(setInsurers)
      .catch(() => setError('Failed to load insurers'))
      .finally(() => setLoading(false))
  }, [])

  // Load invoices for selection
  useEffect(() => {
    setInvoiceLoading(true)
    getInvoiceSummary()
      .then(setInvoices)
      .catch(() => setInvoiceError('Failed to load invoices'))
      .finally(() => setInvoiceLoading(false))
  }, [])

  const handleCreate = async () => {
    try {
      const newIns = await createInsurer({ name })
      setInsurers((s) => [newIns, ...s])
      setName('')
    } catch (e) {
      alert('Failed to create insurer')
    }
  }

  // Only show loading/error for invoices, not insurers
  if (invoiceLoading) return <LoadingSpinner />
  if (invoiceError) return <ErrorMessage message={invoiceError} />

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Insurance Receipt / Physician Statement</h2>
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="invoice-select"><strong>Select Invoice:</strong> </label>
        {invoices.length === 0 ? (
          <span style={{ marginLeft: 8 }}>No invoices available.</span>
        ) : (
          <select
            id="invoice-select"
            value={selectedInvoiceId ?? ''}
            onChange={e => setSelectedInvoiceId(Number(e.target.value) || null)}
          >
            <option value="">-- Select Invoice --</option>
            {invoices.map(inv => (
              <option key={inv.invoice_id} value={inv.invoice_id}>
                #{inv.invoice_id} | {inv.patient_name} | {inv.invoice_date} | ${inv.total_amount.toFixed(2)}
              </option>
            ))}
          </select>
        )}
      </div>
      {selectedInvoiceId && (
        <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem', background: '#fafaff' }}>
          <PhysicianStatement invoiceId={selectedInvoiceId} />
        </div>
      )}
    </div>
  )
}
