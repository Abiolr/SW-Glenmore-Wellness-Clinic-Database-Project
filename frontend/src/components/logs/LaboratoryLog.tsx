import React, { useEffect, useState } from 'react'
import { getActiveVisits } from '../../api/views'
import { getLabTestsByVisit, createLabTest as apiCreateLabTest, updateLabTest, deleteLabTest } from '../../api/functions'
import { get } from '../../api/client'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { getLocalDateString, formatMST, getMSTNow } from '../../utils/timeUtils'
import './LaboratoryLog.css'

type LabTest = any
type Visit = any

export default function LaboratoryLog({ visitId }: { visitId?: number }) {
  const [loading, setLoading] = useState(false)
  const [visits, setVisits] = useState<Visit[]>([])
  const [staff, setStaff] = useState<any[]>([])
  const [labTests, setLabTests] = useState<LabTest[]>([])
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingTest, setEditingTest] = useState<LabTest | null>(null)
  const [form, setForm] = useState({ visit_id: '', test_name: '', ordered_by: '', notes: '' })

  useEffect(() => {
    // Always load staff so user can create tests, but defer lab test data until a date is chosen
    loadStaff()
    loadVisitsForDropdown()
    if (visitId) {
      // If a specific visit context is provided, still load its tests immediately
      loadData()
    }
  }, [visitId])

  const loadVisitsForDropdown = async () => {
    try {
      let v = await get<any[]>('/visits?limit=50').catch(() => [])
      
      // Enrich visits with patient names
      const enrichedVisits = await Promise.all(
        v.map(async (visit) => {
          const patientId = visit.patient_id || visit.Patient_Id
          if (patientId) {
            try {
              const patient = await get<any>(`/patients/${patientId}`)
              const first = patient.first_name || patient.First_Name || ''
              const last = patient.last_name || patient.Last_Name || ''
              const name = `${first} ${last}`.trim()
              return { 
                ...visit, 
                patient_name: name || `Patient ${patientId}`,
                display_name: `Visit ${visit.visit_id || visit._id} - ${name || `Patient ${patientId}`}`
              }
            } catch {
              return { 
                ...visit, 
                patient_name: `Patient ${patientId}`,
                display_name: `Visit ${visit.visit_id || visit._id} - Patient ${patientId}`
              }
            }
          }
          return { 
            ...visit, 
            patient_name: 'Unknown',
            display_name: `Visit ${visit.visit_id || visit._id} - Unknown Patient`
          }
        })
      )
      
      setVisits(enrichedVisits)
    } catch (e) {
      console.error('Failed to load visits for dropdown', e)
    }
  }

  const loadStaff = async () => {
    try {
      const staffList = await get<any[]>('/staff?limit=100').catch(() => [])
      const validStaff = staffList.filter(s => {
        const firstName = s.first_name || s.First_Name || ''
        const lastName = s.last_name || s.Last_Name || ''
        const name = `${firstName} ${lastName}`.trim()
        return name && 
               name !== 'test' && 
               !name.toLowerCase().includes('deactivate') &&
               !name.toLowerCase().includes('updated name') &&
               (s.staff_id || s.Staff_Id || s._id)
      })
      setStaff(validStaff)
    } catch (e) {
      console.error('Failed to load staff', e)
    }
  }

  const enrichLabTestsWithPatients = async (tests: any[]) => {
    const enriched = await Promise.all(
      tests.map(async (test) => {
        const visitId = test.visit_id || test.Visit_Id
        if (visitId) {
          try {
            // Get visit details which should include patient info
            const visit = await get<any>(`/visits/${visitId}`)
            const patientId = visit.patient_id || visit.Patient_Id
            
            if (patientId) {
              try {
                const patient = await get<any>(`/patients/${patientId}`)
                const first = patient.first_name || patient.First_Name || ''
                const last = patient.last_name || patient.Last_Name || ''
                const name = `${first} ${last}`.trim()
                return { 
                  ...test, 
                  patient_name: name || `Patient ${patientId}`,
                  patient_id: patientId
                }
              } catch {
                return { ...test, patient_name: `Patient ${patientId}`, patient_id: patientId }
              }
            }
          } catch (err) {
            console.error('Failed to get visit for lab test', err)
          }
        }
        return { ...test, patient_name: 'Unknown' }
      })
    )
    return enriched
  }

  const loadData = async () => {
    // If no visit and no date selected yet, do not auto-load records
    if (!visitId && !selectedDate) {
      setLabTests([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      if (!visitId && selectedDate) {
        try {
          const results = await get(`/lab-tests/date/${selectedDate}`)
          const enriched = await enrichLabTestsWithPatients(results)
          setLabTests(enriched)
          return
        } catch (err) {
          console.warn('Date endpoint failed, falling back to per-visit fetch', err)
        }
      }

      if (visitId) {
        const tests = await getLabTestsByVisit(visitId)
        const enriched = await enrichLabTestsWithPatients(tests)
        setLabTests(enriched)
        return
      }

      // Load visits for the dropdown (only when loading all tests)
      let v = await getActiveVisits().catch(() => [])
      if (!v || v.length === 0) {
        v = await get<any[]>('/visits?limit=20')
      }
      
      // Enrich visits with patient names
      const enrichedVisits = await Promise.all(
        v.map(async (visit) => {
          const patientId = visit.patient_id || visit.Patient_Id
          if (patientId) {
            try {
              const patient = await get<any>(`/patients/${patientId}`)
              const first = patient.first_name || patient.First_Name || ''
              const last = patient.last_name || patient.Last_Name || ''
              const name = `${first} ${last}`.trim()
              return { 
                ...visit, 
                patient_name: name || `Patient ${patientId}`,
                display_name: `Visit ${visit.visit_id || visit._id} - ${name || `Patient ${patientId}`}`
              }
            } catch {
              return { 
                ...visit, 
                patient_name: `Patient ${patientId}`,
                display_name: `Visit ${visit.visit_id || visit._id} - Patient ${patientId}`
              }
            }
          }
          return { 
            ...visit, 
            patient_name: 'Unknown',
            display_name: `Visit ${visit.visit_id || visit._id} - Unknown Patient`
          }
        })
      )
      
      setVisits(enrichedVisits)

      // Load all lab tests across visits (date not specified)
      const testsPromises = enrichedVisits.map((vis: any) => 
        getLabTestsByVisit(vis.visit_id || vis._id || vis.id).catch(() => [])
      )
      const testsArrays = await Promise.all(testsPromises)
      const combined: LabTest[] = []
      testsArrays.forEach((tests, idx) => {
        if (Array.isArray(tests) && tests.length > 0) {
          const withPatient = tests.map((t: any) => ({
            ...t,
            patient_name: enrichedVisits[idx].patient_name,
            patient_id: enrichedVisits[idx].patient_id || enrichedVisits[idx].Patient_Id
          }))
          combined.push(...withPatient)
        }
      })
      combined.sort((a, b) => {
        const dateA = a.ordered_at || a.Ordered_At || 0
        const dateB = b.ordered_at || b.Ordered_At || 0
        return new Date(dateB).getTime() - new Date(dateA).getTime()
      })
      setLabTests(combined)
    } catch (err) {
      console.error('Failed loading lab log', err)
      setError('Failed to load laboratory log')
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setEditingTest(null)
    setForm({ 
      visit_id: visits[0]?.visit_id || visits[0]?._id || '', 
      test_name: '', 
      ordered_by: '',
      notes: ''
    })
    setShowModal(true)
  }

  const openEditModal = (test: LabTest) => {
    setEditingTest(test)
    setForm({
      visit_id: test.visit_id || test.Visit_Id || '',
      test_name: test.test_name || test.Test_Name || '',
      ordered_by: test.ordered_by || test.Ordered_By || '',
      notes: test.notes || test.Notes || ''
    })
    setShowModal(true)
  }

  const loadToday = async () => {
    const today = getLocalDateString()
    setSelectedDate(today)
    setLoading(true)
    setError(null)
    try {
      const results = await get(`/lab-tests/date/${today}`)
      const enriched = await enrichLabTestsWithPatients(results)
      setLabTests(enriched)
    } catch (err) {
      console.error('Failed to load today\'s tests', err)
      setError('Failed to load today\'s lab tests')
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    if (!form.visit_id || !form.test_name) {
      alert('Please select a visit and enter a test name')
      return
    }
    if (!form.ordered_by) {
      alert('Please select who ordered the test')
      return
    }
    
    try {
      if (editingTest) {
        // Update existing test - preserve ordered_at from original
        const testId = editingTest.labtest_id || editingTest.LabTest_Id
        const updateData: any = {
          visit_id: Number(form.visit_id),
          test_name: form.test_name,
          ordered_by: Number(form.ordered_by),
          notes: form.notes
        }
        
        // Preserve ordered_at if it exists
        if (editingTest.ordered_at || editingTest.Ordered_At) {
          updateData.ordered_at = editingTest.ordered_at || editingTest.Ordered_At
        }
        
        await updateLabTest(testId, updateData)
        alert('Lab test updated successfully!')
      } else {
        // Create new test
        await apiCreateLabTest({ 
          visit_id: Number(form.visit_id), 
          test_name: form.test_name, 
          ordered_by: Number(form.ordered_by),
          notes: form.notes
        })
        alert('Lab test created successfully!')
      }
      
      setShowModal(false)
      await loadData()
    } catch (err) {
      console.error(err)
      alert(`Failed to ${editingTest ? 'update' : 'create'} lab test`)
    }
  }

  const handleDelete = async (test: LabTest) => {
    const testId = test.labtest_id || test.LabTest_Id
    const testName = test.test_name || test.Test_Name
    
    if (!confirm(`Are you sure you want to delete lab test "${testName}" (ID: ${testId})?`)) {
      return
    }
    
    try {
      await deleteLabTest(testId)
      alert('Lab test deleted successfully!')
      await loadData()
    } catch (err) {
      console.error(err)
      alert('Failed to delete lab test')
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="log-page">
      <div className="toolbar">
        <div className="toolbar-left">
          <h3 style={{ margin: 0 }}>Laboratory Log</h3>
        </div>
        {!visitId && (
          <div className="toolbar-right">
            <input 
              type="date" 
              className="date" 
              value={selectedDate} 
              onChange={(e) => setSelectedDate(e.target.value)} 
            />
            <button className="btn" disabled={!selectedDate} onClick={loadData}>Load</button>
            <button className="btn" onClick={loadToday}>Today</button>
            <button className="btn btn-primary" onClick={openCreateModal}>Add Lab Test</button>
          </div>
        )}
      </div>

      {labTests.length === 0 ? (
        <p className="muted" style={{ marginTop: 12 }}>
          {visitId
            ? 'No lab tests found for this visit.'
            : selectedDate
              ? 'No lab tests found for selected date.'
              : 'Select a date to view lab tests.'}
        </p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Test ID</th>
              <th>Patient</th>
              <th>Test</th>
              <th>Ordered</th>
              <th>Notes</th>
              <th>Ordered By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {labTests.map((t, i) => {
              const testId = t.labtest_id || t.LabTest_Id || t._id || t.id
              const orderedBy = t.ordered_by || t.Ordered_By
              const staffMember = staff.find(s => 
                (s.staff_id || s.Staff_Id) === orderedBy
              )
              const staffName = staffMember 
                ? `${staffMember.first_name || staffMember.First_Name || ''} ${staffMember.last_name || staffMember.Last_Name || ''}`.trim()
                : orderedBy || '—'
              
              return (
                <tr key={testId || i}>
                  <td>{testId || 'N/A'}</td>
                  <td>{t.patient_name || 'Unknown'}</td>
                  <td>{t.test_name || t.Test_Name || 'N/A'}</td>
                  <td>{formatMST(t.ordered_at || t.Ordered_At)}</td>
                  <td>{t.notes || t.Notes || '—'}</td>
                  <td>{staffName}</td>
                  <td>
                    <button className="btn" onClick={() => openEditModal(t)} style={{ marginRight: 4 }}>Edit</button>
                    <button 
                      className="btn" 
                      onClick={() => handleDelete(t)}
                      style={{ background: '#dc3545', color: 'white', borderColor: '#dc3545' }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>{editingTest ? 'Edit Lab Test' : 'Add Lab Test'}</h3>
            
            <div className="form-group">
              <label>Visit:</label>
              <select 
                className="select"
                value={form.visit_id} 
                onChange={(e) => setForm({ ...form, visit_id: e.target.value })}
                disabled={!!editingTest}
                style={{ width: '100%' }}
              >
                <option value="">Select visit</option>
                {visits.map((v) => (
                  <option key={v.visit_id || v._id} value={v.visit_id || v._id}>
                    {v.display_name || v.patient_name || `Visit ${v.visit_id || v._id}`}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Test name:</label>
              <input 
                className="input"
                value={form.test_name} 
                onChange={(e) => setForm({ ...form, test_name: e.target.value })} 
                placeholder="e.g., Blood Test, X-Ray, Urinalysis"
                style={{ width: '100%' }}
              />
            </div>
            
            <div className="form-group">
              <label>Ordered by:</label>
              <select 
                className="select"
                value={form.ordered_by} 
                onChange={(e) => setForm({ ...form, ordered_by: e.target.value })}
                style={{ width: '100%' }}
              >
                <option value="">Select practitioner</option>
                {staff.map((s) => {
                  const staffId = s.staff_id || s.Staff_Id || s._id
                  const firstName = s.first_name || s.First_Name || ''
                  const lastName = s.last_name || s.Last_Name || ''
                  const specialty = s.specialty || s.Specialty || ''
                  const name = `${firstName} ${lastName}`.trim()
                  return (
                    <option key={staffId} value={staffId}>
                      {name} {specialty ? `(${specialty})` : ''} - ID: {staffId}
                    </option>
                  )
                })}
              </select>
            </div>
            
            <div className="form-group">
              <label>Notes/Results:</label>
              <textarea 
                className="input"
                value={form.notes} 
                onChange={(e) => setForm({ ...form, notes: e.target.value })} 
                placeholder="Enter test results or notes"
                rows={3}
                style={{ width: '100%', fontFamily: 'inherit' }}
              />
            </div>
            
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={submit}>
                {editingTest ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
