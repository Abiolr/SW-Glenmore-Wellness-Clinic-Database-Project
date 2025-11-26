import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { get } from '../../api/client'

export default function MonthlyActivityReport() {
  const [loading, setLoading] = useState(true)
  const [reportData, setReportData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedMonth, setSelectedMonth] = useState('')
  const [selectedYear, setSelectedYear] = useState('')

  useEffect(() => {
    // Set current month/year on load
    const now = new Date()
    setSelectedMonth(String(now.getMonth() + 1).padStart(2, '0'))
    setSelectedYear(String(now.getFullYear()))
  }, [])

  useEffect(() => {
    if (selectedMonth && selectedYear) {
      loadReport()
    }
  }, [selectedMonth, selectedYear])

  const loadReport = async () => {
    if (!selectedMonth || !selectedYear) return
    
    setLoading(true)
    setError(null)
    try {
      const data = await get<any>(`/reports/monthly-activity?month=${parseInt(selectedMonth)}&year=${parseInt(selectedYear)}`)
      setReportData(data)
    } catch (e) {
      console.error('Failed to load monthly activity report', e)
      setError('Failed to load monthly activity report')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    loadReport()
  }

  const handleThisMonth = () => {
    const now = new Date()
    setSelectedMonth(String(now.getMonth() + 1).padStart(2, '0'))
    setSelectedYear(String(now.getFullYear()))
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Monthly Activity Report</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={handleRefresh}>Refresh</button>
        </div>
      </div>

      {/* Month/Year Selector */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '12px', alignItems: 'center', background: '#f5f5f5', padding: '12px', borderRadius: 6 }}>
        <label style={{ fontWeight: 'bold' }}>Select Period:</label>
        <select 
          value={selectedMonth} 
          onChange={(e) => setSelectedMonth(e.target.value)}
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}
        >
          <option value="01">January</option>
          <option value="02">February</option>
          <option value="03">March</option>
          <option value="04">April</option>
          <option value="05">May</option>
          <option value="06">June</option>
          <option value="07">July</option>
          <option value="08">August</option>
          <option value="09">September</option>
          <option value="10">October</option>
          <option value="11">November</option>
          <option value="12">December</option>
        </select>
        <input 
          type="number" 
          value={selectedYear} 
          onChange={(e) => setSelectedYear(e.target.value)}
          placeholder="Year"
          min="2000"
          max="2100"
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc', width: '100px' }}
        />
        <button onClick={handleThisMonth} style={{ marginLeft: 8 }}>This Month</button>
      </div>

      {!reportData ? (
        <p style={{ marginTop: 12 }}>No activity data found for the selected period.</p>
      ) : (
        <div>
          {/* Summary Section */}
          {reportData.summary && (
            <div style={{ marginBottom: '2rem', background: '#f9f9f9', padding: '1rem', borderRadius: 6 }}>
              <h3 style={{ marginTop: 0 }}>Summary</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {Object.entries(reportData.summary).map(([key, value]) => (
                  <div key={key} style={{ background: 'white', padding: '0.75rem', borderRadius: 4, border: '1px solid #e0e0e0' }}>
                    <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>
                      {typeof value === 'number' ? value.toLocaleString() : value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Activities Table */}
          {reportData.activities && reportData.activities.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Detailed Activities</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem', border: '1px solid #ddd' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Activity ID</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Patient</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Staff</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.activities.map((activity: any, i: number) => (
                      <tr key={activity.activity_id || activity._id || i} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{activity.activity_id || activity._id || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{activity.patient_name || activity.patient_id || 'Unknown'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{activity.activity_type || activity.type || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{activity.staff_name || activity.staff_id || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                          {activity.activity_date ? new Date(activity.activity_date).toLocaleDateString() : '—'}
                        </td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{activity.notes || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Visits Section */}
          {reportData.visits && reportData.visits.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Visits</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem', border: '1px solid #ddd' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Visit ID</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Patient</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Visit Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Status</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Practitioner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.visits.map((visit: any, i: number) => (
                      <tr key={visit.visit_id || visit._id || i} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{visit.visit_id || visit._id || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{visit.patient_name || visit.patient_id || 'Unknown'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                          {visit.visit_date ? new Date(visit.visit_date).toLocaleDateString() : '—'}
                        </td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                          <span style={{ 
                            padding: '0.25rem 0.5rem', 
                            borderRadius: 4, 
                            fontSize: '0.85rem',
                            background: visit.status === 'completed' ? '#d4edda' : '#fff3cd',
                            color: visit.status === 'completed' ? '#155724' : '#856404'
                          }}>
                            {visit.status || 'active'}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{visit.practitioner_name || visit.practitioner_id || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Procedures Section */}
          {reportData.procedures && reportData.procedures.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Procedures</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem', border: '1px solid #ddd' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Procedure ID</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Name</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Patient</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right', border: '1px solid #ddd' }}>Fee</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.procedures.map((proc: any, i: number) => (
                      <tr key={proc.procedure_id || i} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{proc.procedure_id || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{proc.procedure_name || proc.name || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{proc.patient_name || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                          {proc.date ? new Date(proc.date).toLocaleDateString() : '—'}
                        </td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'right' }}>
                          {proc.fee ? `$${Number(proc.fee).toFixed(2)}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Diagnoses Section */}
          {reportData.diagnoses && reportData.diagnoses.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Diagnoses</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '0.5rem', border: '1px solid #ddd' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Diagnosis Code</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Description</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Patient</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Date</th>
                      <th style={{ padding: '0.75rem', textAlign: 'center', border: '1px solid #ddd' }}>Primary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportData.diagnoses.map((diag: any, i: number) => (
                      <tr key={diag.diagnosis_id || i} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{diag.code || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{diag.description || diag.name || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{diag.patient_name || '—'}</td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                          {diag.date ? new Date(diag.date).toLocaleDateString() : '—'}
                        </td>
                        <td style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'center' }}>
                          {diag.is_primary ? '✓' : ''}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Appointments Section */}
          {reportData.appointments && reportData.appointments.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Appointments</h3>
              <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                {reportData.appointments.length} appointment(s) scheduled this month
              </p>
            </div>
          )}

          {/* Prescriptions Section */}
          {reportData.prescriptions && reportData.prescriptions.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Prescriptions</h3>
              <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                {reportData.prescriptions.length} prescription(s) dispensed this month
              </p>
            </div>
          )}

          {/* Lab Tests Section */}
          {reportData.lab_tests && reportData.lab_tests.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Lab Tests</h3>
              <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                {reportData.lab_tests.length} lab test(s) ordered this month
              </p>
            </div>
          )}

          {/* Deliveries Section */}
          {reportData.deliveries && reportData.deliveries.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h3>Deliveries</h3>
              <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                {reportData.deliveries.length} delivery(ies) recorded this month
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}