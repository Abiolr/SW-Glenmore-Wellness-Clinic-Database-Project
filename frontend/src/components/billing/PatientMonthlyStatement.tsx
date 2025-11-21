import React, { useEffect, useState } from 'react'
import { calculateInvoiceTotal } from '../../api/functions'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

interface Props {
  invoiceId: number
}

export default function PatientMonthlyStatement({ invoiceId }: Props) {
  const [total, setTotal] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    calculateInvoiceTotal(invoiceId)
      .then(res => setTotal(res.total))
      .catch(() => setError('Failed to load monthly statement'))
      .finally(() => setLoading(false))
  }, [invoiceId])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />
  if (total === null) return <p>No data found.</p>

  return (
    <div className="monthly-statement">
      <h3>Patient Monthly Statement</h3>
      <p><strong>Invoice ID:</strong> {invoiceId}</p>
      <p><strong>Total Charges:</strong> ${total.toFixed(2)}</p>
    </div>
  )
}
