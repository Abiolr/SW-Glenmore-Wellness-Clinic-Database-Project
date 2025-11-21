import React, { useEffect, useState } from 'react'

export default function MonthlyStatements() {
  const now = new Date()
  const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`

  const [monthValue, setMonthValue] = useState<string>(defaultMonth)
  const [loading, setLoading] = useState<boolean>(false)
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [year, month] = monthValue.split('-')
      const res = await fetch(`${import.meta.env.VITE_API_URL}/statements/monthly?year=${Number(year)}&month=${Number(month)}`)
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const json = await res.json()
      setData(json)
    } catch (err: any) {
      setError(err.message || String(err))
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  function toggle(pid: string | number) {
    setExpanded((s) => ({ ...s, [String(pid)]: !s[String(pid)] }))
  }

  function downloadCSV(section: 'paid' | 'unpaid') {
    if (!data) return
    const rows: string[] = []
    rows.push('patient_id,patient_name,total_invoiced,payments_received,balance')
    const patients = data.summary?.[section]?.patients || []
    for (const p of patients) {
      rows.push(`${p.patient_id},"${(p.patient_name||'').replace(/"/g,'""')}",${p.total_invoiced},${p.payments_received},${p.balance}`)
    }
    const csv = rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `statements_${data.month}_${section}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Patient Monthly Statements</h2>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
        <input type="month" value={monthValue} onChange={(e) => setMonthValue(e.target.value)} />
        <button onClick={load} disabled={loading}>
          {loading ? 'Loading...' : 'Load'}
        </button>
        <span style={{ marginLeft: 12 }}>{data ? `Showing: ${data.month}` : ''}</span>
      </div>

      {error && <div style={{ color: 'red' }}>{error}</div>}

      {!data && !error && <div>No data. Click Load to fetch statements.</div>}

      {data && (
        <div>
          <section style={{ marginBottom: 24 }}>
            <h3>Paid (invoices issued this month and fully paid by month-end)</h3>
            <div style={{ marginBottom: 8 }}>
              <strong>Totals:</strong>
              <span style={{ marginLeft: 8 }}>Invoiced: {data.summary.paid.totals.total_invoiced.toFixed(2)}</span>
              <span style={{ marginLeft: 8 }}>Payments: {data.summary.paid.totals.payments_received.toFixed(2)}</span>
              <span style={{ marginLeft: 8 }}>Balance: {data.summary.paid.totals.balance.toFixed(2)}</span>
              <button style={{ marginLeft: 12 }} onClick={() => downloadCSV('paid')}>Download CSV</button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc' }}>Patient</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Invoiced</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Payments</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Balance</th>
                  <th style={{ textAlign: 'center', borderBottom: '1px solid #ccc' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {data.summary.paid.patients.map((p: any) => (
                  <React.Fragment key={p.patient_id}>
                    <tr>
                      <td style={{ padding: '6px 4px' }}>{p.patient_name || p.patient_id}</td>
                      <td style={{ textAlign: 'right' }}>{(p.total_invoiced || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'right' }}>{(p.payments_received || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'right' }}>{(p.balance || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'center' }}>
                        <button onClick={() => toggle(p.patient_id)}>{expanded[String(p.patient_id)] ? 'Hide' : 'Show'}</button>
                      </td>
                    </tr>
                    {expanded[String(p.patient_id)] && (
                      <tr>
                        <td colSpan={5} style={{ background: '#fafafa', padding: 8 }}>
                          <strong>Invoices</strong>
                          <table style={{ width: '100%', marginTop: 8 }}>
                            <thead>
                              <tr>
                                <th style={{ textAlign: 'left' }}>Invoice ID</th>
                                <th style={{ textAlign: 'left' }}>Date</th>
                                <th style={{ textAlign: 'right' }}>Patient Portion</th>
                                <th style={{ textAlign: 'right' }}>Paid</th>
                                <th style={{ textAlign: 'right' }}>Balance</th>
                              </tr>
                            </thead>
                            <tbody>
                              {p.invoices.map((inv: any) => (
                                <tr key={inv.invoice_id}>
                                  <td>{inv.invoice_id}</td>
                                  <td>{inv.invoice_date}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.patient_portion || 0).toFixed(2)}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.total_paid || 0).toFixed(2)}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.balance_due || 0).toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </section>

          <section>
            <h3>Unpaid (invoices issued this month not fully paid by month-end)</h3>
            <div style={{ marginBottom: 8 }}>
              <strong>Totals:</strong>
              <span style={{ marginLeft: 8 }}>Invoiced: {data.summary.unpaid.totals.total_invoiced.toFixed(2)}</span>
              <span style={{ marginLeft: 8 }}>Payments: {data.summary.unpaid.totals.payments_received.toFixed(2)}</span>
              <span style={{ marginLeft: 8 }}>Balance Due: {data.summary.unpaid.totals.balance.toFixed(2)}</span>
              <button style={{ marginLeft: 12 }} onClick={() => downloadCSV('unpaid')}>Download CSV</button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc' }}>Patient</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Invoiced</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Payments</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ccc' }}>Balance</th>
                  <th style={{ textAlign: 'center', borderBottom: '1px solid #ccc' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {data.summary.unpaid.patients.map((p: any) => (
                  <React.Fragment key={p.patient_id}>
                    <tr>
                      <td style={{ padding: '6px 4px' }}>{p.patient_name || p.patient_id}</td>
                      <td style={{ textAlign: 'right' }}>{(p.total_invoiced || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'right' }}>{(p.payments_received || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'right' }}>{(p.balance || 0).toFixed(2)}</td>
                      <td style={{ textAlign: 'center' }}>
                        <button onClick={() => toggle(p.patient_id)}>{expanded[String(p.patient_id)] ? 'Hide' : 'Show'}</button>
                      </td>
                    </tr>
                    {expanded[String(p.patient_id)] && (
                      <tr>
                        <td colSpan={5} style={{ background: '#fff7f7', padding: 8 }}>
                          <strong>Invoices</strong>
                          <table style={{ width: '100%', marginTop: 8 }}>
                            <thead>
                              <tr>
                                <th style={{ textAlign: 'left' }}>Invoice ID</th>
                                <th style={{ textAlign: 'left' }}>Date</th>
                                <th style={{ textAlign: 'right' }}>Patient Portion</th>
                                <th style={{ textAlign: 'right' }}>Paid</th>
                                <th style={{ textAlign: 'right' }}>Balance</th>
                              </tr>
                            </thead>
                            <tbody>
                              {p.invoices.map((inv: any) => (
                                <tr key={inv.invoice_id}>
                                  <td>{inv.invoice_id}</td>
                                  <td>{inv.invoice_date}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.patient_portion || 0).toFixed(2)}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.total_paid || 0).toFixed(2)}</td>
                                  <td style={{ textAlign: 'right' }}>{(inv.balance_due || 0).toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </div>
  )
}
