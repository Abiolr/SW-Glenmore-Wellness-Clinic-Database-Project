import React, { useEffect, useState } from 'react'
import { get } from '../../api/client'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

interface Props {
  invoiceId: number
}

export default function PhysicianStatement({ invoiceId }: Props) {
  const [invoice, setInvoice] = useState<any>(null)
  const [patient, setPatient] = useState<any>(null)
  const [visit, setVisit] = useState<any>(null)
  const [staff, setStaff] = useState<any>(null)
  const [lineItems, setLineItems] = useState<any[]>([])
  const [payments, setPayments] = useState<any[]>([])
  const [procedures, setProcedures] = useState<any[]>([])
  const [diagnoses, setDiagnoses] = useState<any[]>([])
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Reset state before loading a new invoice to avoid showing stale data
    setLoading(true)
    setError(null)
    setInvoice(null)
    setPatient(null)
    setVisit(null)
    setStaff(null)
    setLineItems([])
    setPayments([])
    setProcedures([])
    setDiagnoses([])

    const load = async () => {
      try {
        // Get invoice directly
        const inv = await get<any>(`/invoices/${invoiceId}`).catch(() => null)
        console.log('Invoice data:', inv)
        
        if (!inv) {
          setError('Invoice not found')
          setLoading(false)
          return
        }

        setInvoice(inv)
        
        // Get patient info
        const patientId = inv.patient_id || inv.Patient_Id
        console.log('Patient ID:', patientId)
        if (patientId) {
          const pat = await get<any>(`/patients/${patientId}`).catch(() => null)
          console.log('Patient data:', pat)
          console.log('Gov Card No:', pat?.gov_card_no)
          console.log('Insurance No:', pat?.insurance_no)
          setPatient(pat)
        }

        // Get visit info
        const visitId = inv.visit_id || inv.Visit_Id
        console.log('Visit ID:', visitId)
        if (visitId) {
          const vis = await get<any>(`/visits/${visitId}`).catch(() => null)
          console.log('Visit data:', vis)
          setVisit(vis)
          
          // Get staff info from visit
          const staffId = vis?.staff_id || vis?.Staff_Id
          console.log('Staff ID:', staffId)
          if (staffId) {
            const st = await get<any>(`/staff/${staffId}`).catch(() => null)
            console.log('Staff data:', st)
            setStaff(st)
          }

          // Get procedures for visit
          const procs = await get<any[]>(`/visits/${visitId}/procedures`).catch(() => [])
          setProcedures(procs || [])

          // Get diagnoses for visit
          const diags = await get<any[]>(`/visits/${visitId}/diagnoses`).catch(() => [])
          setDiagnoses(diags || [])
        }

        // Get invoice lines
        const lines = await get<any[]>(`/invoices/${invoiceId}/lines`).catch(() => [])
        console.log('Invoice lines:', lines)
        setLineItems(lines || [])

        // Get payments for invoice
        const pays = await get<any[]>(`/invoices/${invoiceId}/payments`).catch(() => [])
        console.log('Invoice payments:', pays)
        setPayments(pays || [])

      } catch (err) {
        console.error('Fetch error:', err)
        setError('Failed to load physician statement')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [invoiceId])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />
  if (!invoice) return <p>No invoice data found.</p>

  const getField = (obj: any, ...keys: string[]) => {
    if (!obj) return null
    for (const key of keys) {
      if (obj[key] !== undefined && obj[key] !== null) return obj[key]
    }
    return null
  }

  const formatDate = (date: any) => {
    if (!date) return 'N/A'
    try {
      return new Date(date).toLocaleDateString()
    } catch {
      return String(date)
    }
  }

  const formatCurrency = (amount: any) => {
    const num = Number(amount) || 0
    return `$${num.toFixed(2)}`
  }

  // Calculate totals
  const lineTotal = lineItems.reduce((sum, item) => {
    const qty = Number(getField(item, 'qty', 'Qty', 'quantity')) || 0
    const price = Number(getField(item, 'unit_price', 'Unit_Price', 'price')) || 0
    return sum + (qty * price)
  }, 0)

  // If no line items, use invoice total_amount as fallback
  const invoiceTotal = Number(getField(invoice, 'total_amount', 'Total_Amount', 'patient_portion', 'Patient_Portion')) || 0
  const calculatedTotal = lineTotal > 0 ? lineTotal : invoiceTotal

  const totalPaid = payments.reduce((sum, payment) => {
    const amount = Number(getField(payment, 'amount', 'Amount')) || 0
    return sum + amount
  }, 0)

  const balance = calculatedTotal - totalPaid

  return (
    <div className="physician-statement" style={{
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      border: '2px solid #000',
      padding: '2rem',
      backgroundColor: '#fff'
    }}>
      {/* Clinic Header */}
      <div style={{ textAlign: 'center', marginBottom: '1.5rem', borderBottom: '2px solid #000', paddingBottom: '1rem' }}>
        <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.5rem' }}>SW Glenmore Wellness Clinic</h2>
        <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}>Calgary, Alberta, Canada</p>
        <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}>Phone: (403) 555-0100 | Fax: (403) 555-0101</p>
      </div>

      <h3 style={{ textAlign: 'center', margin: '1rem 0' }}>INSURANCE RECEIPT / PHYSICIAN STATEMENT</h3>

      {/* Patient Information */}
      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.75rem' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Patient Information</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.9rem' }}>
          <div><strong>Name:</strong> {getField(patient, 'first_name', 'First_Name') || ''} {getField(patient, 'last_name', 'Last_Name') || ''}</div>
          <div><strong>Patient ID:</strong> {getField(patient, 'patient_id', 'Patient_Id') || 'N/A'}</div>
          <div><strong>Date of Birth:</strong> {formatDate(getField(patient, 'date_of_birth', 'Date_Of_Birth'))}</div>
          <div><strong>Invoice Date:</strong> {formatDate(getField(invoice, 'invoice_date', 'Invoice_Date'))}</div>
          <div><strong>Health Card #:</strong> {getField(patient, 'gov_card_no', 'Gov_Card_No', 'GovCardNo') || 'N/A'}</div>
          <div><strong>Insurance #:</strong> {getField(patient, 'insurance_no', 'Insurance_No', 'InsuranceNo') || 'N/A'}</div>
          <div><strong>Phone:</strong> {getField(patient, 'phone', 'Phone') || 'N/A'}</div>
        </div>
      </div>

      {/* Diagnoses */}
      {diagnoses.length > 0 && (
        <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.75rem' }}>
          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Diagnoses</h4>
          <ul style={{ margin: '0', paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
            {diagnoses.map((diag, idx) => (
              <li key={idx}>
                <strong>Code:</strong> {getField(diag, 'code', 'Code') || 'N/A'} - {getField(diag, 'description', 'Description') || getField(diag, 'diagnosis_name', 'Diagnosis_Name') || 'N/A'}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Procedures */}
      {procedures.length > 0 && (
        <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.75rem' }}>
          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Procedures Performed</h4>
          <ul style={{ margin: '0', paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
            {procedures.map((proc, idx) => (
              <li key={idx}>
                <strong>Code:</strong> {getField(proc, 'code', 'Code') || 'N/A'} - {getField(proc, 'description', 'Description') || getField(proc, 'procedure_name', 'Procedure_Name') || 'N/A'}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Fee Details - Line Items */}
      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.75rem' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Fee Details</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #000' }}>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>Description</th>
              <th style={{ textAlign: 'center', padding: '0.5rem' }}>Qty</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Unit Price</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Total</th>
            </tr>
          </thead>
          <tbody>
            {lineItems.length === 0 && invoiceTotal > 0 ? (
              // Fallback: Show invoice total as a single line item if no line items exist
              <tr>
                <td style={{ padding: '0.5rem' }}>Medical Services (Invoice Total)</td>
                <td style={{ textAlign: 'center', padding: '0.5rem' }}>1</td>
                <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(invoiceTotal)}</td>
                <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(invoiceTotal)}</td>
              </tr>
            ) : (
              lineItems.map((item, idx) => {
                const qty = Number(getField(item, 'qty', 'Qty', 'quantity')) || 0
                const price = Number(getField(item, 'unit_price', 'Unit_Price', 'price')) || 0
                const total = qty * price
                return (
                  <tr key={idx}>
                    <td style={{ padding: '0.5rem' }}>{getField(item, 'description', 'Description') || 'Service'}</td>
                    <td style={{ textAlign: 'center', padding: '0.5rem' }}>{qty}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(price)}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(total)}</td>
                  </tr>
                )
              })
            )}
            <tr style={{ borderTop: '1px solid #000', fontWeight: 'bold' }}>
              <td colSpan={3} style={{ textAlign: 'right', padding: '0.5rem' }}>Subtotal:</td>
              <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(calculatedTotal)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Payments */}
      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.75rem' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>Payment Record</h4>
        {payments.length === 0 ? (
          <p style={{ margin: '0.5rem 0', fontSize: '0.9rem', fontStyle: 'italic' }}>No payments recorded</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #000' }}>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>Date</th>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>Method</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '0.5rem' }}>{formatDate(getField(payment, 'payment_date', 'Payment_Date'))}</td>
                  <td style={{ padding: '0.5rem' }}>{getField(payment, 'method', 'payment_method', 'Payment_Method') || 'N/A'}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(getField(payment, 'amount', 'Amount'))}</td>
                </tr>
              ))}
              <tr style={{ borderTop: '1px solid #000', fontWeight: 'bold' }}>
                <td colSpan={2} style={{ textAlign: 'right', padding: '0.5rem' }}>Total Paid:</td>
                <td style={{ textAlign: 'right', padding: '0.5rem' }}>{formatCurrency(totalPaid)}</td>
              </tr>
            </tbody>
          </table>
        )}
      </div>

      {/* Balance Summary */}
      <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f5f5f5', border: '1px solid #999' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.5rem', fontSize: '1rem' }}>
          <div style={{ fontWeight: 'bold' }}>Total Charges:</div>
          <div style={{ textAlign: 'right' }}>{formatCurrency(calculatedTotal)}</div>
          <div style={{ fontWeight: 'bold' }}>Total Payments:</div>
          <div style={{ textAlign: 'right' }}>-{formatCurrency(totalPaid)}</div>
          <div style={{ fontWeight: 'bold', fontSize: '1.1rem', borderTop: '2px solid #000', paddingTop: '0.5rem' }}>Balance Due:</div>
          <div style={{ textAlign: 'right', fontSize: '1.1rem', fontWeight: 'bold', borderTop: '2px solid #000', paddingTop: '0.5rem' }}>
            {formatCurrency(balance)}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{ marginTop: '2rem', fontSize: '0.85rem', color: '#666', textAlign: 'center' }}>
        <p style={{ margin: '0.5rem 0' }}>Invoice #{getField(invoice, 'invoice_id', 'Invoice_Id')} | Status: {getField(invoice, 'status', 'Status')}</p>
        <p style={{ margin: '0.5rem 0' }}>For insurance claims, please submit this statement with your claim form.</p>
        <button 
          onClick={() => window.print()} 
          style={{
            marginTop: '1rem',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#4285f4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Print Receipt
        </button>
      </div>
    </div>
  )
}
