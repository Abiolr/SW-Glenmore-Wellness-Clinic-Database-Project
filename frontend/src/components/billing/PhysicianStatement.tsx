import React, { useEffect, useState } from 'react'
import { getInvoiceCalculatedTotal, getInvoiceAggregation } from '../../api/functions'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

interface Props {
  invoiceId: number
}

export default function PhysicianStatement({ invoiceId }: Props) {
  const [data, setData] = useState<{
    invoice_id: number
    invoice_date: string
    status: string
    calculated_total: number
    line_items_count: number
  } | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

useEffect(() => {
  const load = async () => {
    try {
      // prefer server aggregation
      const agg = await getInvoiceAggregation(invoiceId).catch(() => null)
      if (agg && agg.invoice_id) {
        setData({
          invoice_id: agg.invoice_id,
          invoice_date: agg.invoice_date,
          status: agg.status,
          calculated_total: agg.total_amount ?? 0,
          line_items_count: agg.line_count ?? (agg.items ? agg.items.length : 0)
        })
        return
      }

      // fallback to client-side calculation
      const res = await getInvoiceCalculatedTotal(invoiceId)
      setData(res)
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
  if (!data) return <p>No data found.</p>

  return (
    <div className="physician-statement">
      <h3>Physician Statement</h3>
      <p><strong>Invoice ID:</strong> {data.invoice_id}</p>
      <p><strong>Date:</strong> {data.invoice_date}</p>
      <p><strong>Status:</strong> {data.status}</p>
      <p><strong>Total:</strong> ${data.calculated_total.toFixed(2)}</p>
      <p><strong>Line Items:</strong> {data.line_items_count}</p>
    </div>
  )
}
