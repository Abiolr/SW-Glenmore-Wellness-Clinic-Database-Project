import React, { useEffect, useState } from 'react'
import { getActiveVisits } from '../../api/views'
import { getLabTestsByVisit, createLabTest as apiCreateLabTest } from '../../api/functions'
import { get } from '../../api/client'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

type LabTest = any
type Visit = any

export default function LaboratoryLog({ visitId }: { visitId?: number }) {
  const [loading, setLoading] = useState(true)
  const [visits, setVisits] = useState<Visit[]>([])
  const [labTests, setLabTests] = useState<LabTest[]>([])
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ visit_id: '', test_name: '', ordered_by: '' })

  useEffect(() => {
    loadData()
    // if a specific visitId is provided, load that visit's tests
  }, [visitId])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      // If a date is selected and not viewing a single visit, load by date
      if (!visitId && selectedDate) {
        try {
          const results = await get(`/lab-tests/date/${selectedDate}`)
          setLabTests(results)
          return
        } catch (err) {
          // If the date endpoint is not available (404) or fails, fall back
          // to fetching lab tests per recent visits and filter by date.
          console.warn('Date endpoint failed, falling back to per-visit fetch', err)
          let v = await getActiveVisits()
          if (!v || v.length === 0) {
            v = await get<any[]>('/visits?limit=200')
          }

          const promises = v.map((vis: any) => getLabTestsByVisit(vis.visit_id || vis._id || vis.id).catch(() => []))
          const results = await Promise.all(promises)
          const combined: any[] = []
          results.forEach((arr, idx) => {
            if (Array.isArray(arr) && arr.length > 0) {
              const withVisit = arr.map((t: any) => ({ ...t, visit: v[idx] }))
              combined.push(...withVisit)
            }
          })

          // filter by selectedDate using ISO prefix or Date parsing
          const filtered = combined.filter((t: any) => {
            const dt = t.result_at || t.Result_At || t.ordered_time || t.ordered_at
            if (!dt) return false
            try {
              const iso = (typeof dt === 'string') ? dt : new Date(dt).toISOString()
              return iso.startsWith(selectedDate)
            } catch (e) {
              return false
            }
          })

          // sort and set
          filtered.sort((a, b) => new Date(b.result_at || b.ordered_time || 0).getTime() - new Date(a.result_at || a.ordered_time || 0).getTime())
          setLabTests(filtered)
          return
        }
      }

      if (visitId) {
        const tests = await getLabTestsByVisit(visitId)
        setLabTests(tests)
        return
      }

      let v = await getActiveVisits()
      if (!v || v.length === 0) {
        v = await get<any[]>('/visits?limit=20')
      }
      setVisits(v)

      const testsPromises = v.map((vis: any) => getLabTestsByVisit(vis.visit_id || vis._id || vis.id))
      const testsArrays = await Promise.allSettled(testsPromises)
      const combined: LabTest[] = []
      testsArrays.forEach((r, idx) => {
        if (r.status === 'fulfilled' && Array.isArray(r.value)) {
          const withVisit = r.value.map((t: any) => ({ ...t, visit: v[idx] }))
          combined.push(...withVisit)
        }
      })
      combined.sort((a, b) => new Date(b.ordered_time || b.result_at || 0).getTime() - new Date(a.ordered_time || a.result_at || 0).getTime())
      setLabTests(combined)
    } catch (err) {
      console.error('Failed loading lab log', err)
      setError('Failed to load laboratory log')
    } finally {
      setLoading(false)
    }
  }

  const openModal = () => {
    setForm({ visit_id: visits[0]?.visit_id || visits[0]?._id || '', test_name: '', ordered_by: '' })
    setShowModal(true)
  }

  const loadToday = async () => {
    setLoading(true)
    setError(null)
    try {
      const today = new Date().toISOString().slice(0, 10)
      setSelectedDate(today)
      try {
        const results = await get(`/lab-tests/date/${today}`)
        setLabTests(results)
        return
      } catch (err) {
        // fallback to per-visit fetch (same as loadData's fallback)
        console.warn('Date endpoint failed for today, falling back to per-visit fetch', err)
        let v = await getActiveVisits()
        if (!v || v.length === 0) {
          v = await get<any[]>('/visits?limit=200')
        }

        const promises = v.map((vis: any) => getLabTestsByVisit(vis.visit_id || vis._id || vis.id).catch(() => []))
        const results = await Promise.all(promises)
        const combined: any[] = []
        results.forEach((arr, idx) => {
          if (Array.isArray(arr) && arr.length > 0) {
            const withVisit = arr.map((t: any) => ({ ...t, visit: v[idx] }))
            combined.push(...withVisit)
          }
        })

        const filtered = combined.filter((t: any) => {
          const dt = t.result_at || t.Result_At || t.ordered_time || t.ordered_at
          if (!dt) return false
          try {
            const iso = (typeof dt === 'string') ? dt : new Date(dt).toISOString()
            return iso.startsWith(today)
          } catch (e) {
            return false
          }
        })

        filtered.sort((a, b) => new Date(b.result_at || b.ordered_time || 0).getTime() - new Date(a.result_at || a.ordered_time || 0).getTime())
        setLabTests(filtered)
        return
      }
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    if (!form.visit_id || !form.test_name) {
      alert('Please select a visit and enter a test name')
      return
    }
    try {
      await apiCreateLabTest({ visit_id: Number(form.visit_id), test_name: form.test_name, ordered_by: form.ordered_by })
      setShowModal(false)
      await loadData()
      alert('Lab test created')
    } catch (err) {
      console.error(err)
      alert('Failed to create lab test')
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Laboratory Log</h3>
        {!visitId && (
          <div>
            <button onClick={openModal}>Add Lab Test</button>
            <button onClick={loadData} style={{ marginLeft: 8 }}>Refresh</button>
          </div>
        )}
      </div>

      <div style={{ marginTop: 12 }}>
        {!visitId && (
          <div>
            <label>Load lab results for date: </label>
            <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
            <button onClick={loadData} style={{ marginLeft: 8 }}>Load</button>
            <button onClick={loadToday} style={{ marginLeft: 8 }}>Today</button>
          </div>
        )}
      </div>

      {labTests.length === 0 ? (
        <p style={{ marginTop: 12 }}>{visitId ? 'No lab tests found for this visit.' : 'No lab tests found for recent visits.'}</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Test ID</th>
            <th style={{ textAlign: 'left' }}>Patient</th>
            <th style={{ textAlign: 'left' }}>Test</th>
            <th style={{ textAlign: 'left' }}>Ordered</th>
            <th style={{ textAlign: 'left' }}>Result</th>
            <th style={{ textAlign: 'left' }}>Practitioner</th>
          </tr>
        </thead>
        <tbody>
          {labTests.map((t, i) => (
            <tr key={t.labtest_id || t._id || t.id || i}>
              <td>{t.labtest_id || t._id || t.id || 'N/A'}</td>
              <td>{t.visit?.patient_name || t.visit?.patient?.name || 'Unknown'}</td>
              <td>{t.test_name}</td>
              <td>{(t.ordered_time || t.result_at) ? new Date(t.ordered_time || t.result_at).toLocaleString() : '—'}</td>
              <td>{t.notes || t.result || 'Pending'}</td>
              <td>{t.ordered_by || t.performed_by || '—'}</td>
            </tr>
          ))}
        </tbody>
        </table>
      )}

      {showModal && (
        <div style={{ position: 'fixed', left: 0, right: 0, top: 0, bottom: 0, background: 'rgba(0,0,0,0.3)' }}>
          <div style={{ background: 'white', padding: 16, width: 480, margin: '60px auto', borderRadius: 6 }}>
            <h4>Add Lab Test</h4>
            <div style={{ marginBottom: 8 }}>
              <label>Visit:</label>
              <select value={form.visit_id} onChange={(e) => setForm({ ...form, visit_id: e.target.value })}>
                <option value="">Select visit</option>
                {visits.map((v) => (
                  <option key={v.visit_id || v._id} value={v.visit_id || v._id}>
                    {v.patient_name || v.patient?.name || `Visit ${v.visit_id || v._id}`}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ marginBottom: 8 }}>
              <label>Test name:</label>
              <input value={form.test_name} onChange={(e) => setForm({ ...form, test_name: e.target.value })} />
            </div>
            <div style={{ marginBottom: 8 }}>
              <label>Ordered by:</label>
              <input value={form.ordered_by} onChange={(e) => setForm({ ...form, ordered_by: e.target.value })} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowModal(false)}>Cancel</button>
              <button onClick={submit} style={{ marginLeft: 8 }}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
