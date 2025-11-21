import React from 'react'

interface Props {
  invoiceId: number
  date: string
  total: number
  status: string
}

export default function InvoiceCard({ invoiceId, date, total, status }: Props) {
  return (
    <div className="invoice-card" style={{
      border: '1px solid #ccc',
      borderRadius: '8px',
      padding: '1rem',
      marginBottom: '1rem',
      backgroundColor: '#f9f9f9'
    }}>
      <h4>Invoice #{invoiceId}</h4>
      <p><strong>Date:</strong> {date}</p>
      <p><strong>Total:</strong> ${total.toFixed(2)}</p>
      <p><strong>Status:</strong> {status}</p>
    </div>
  )
}
