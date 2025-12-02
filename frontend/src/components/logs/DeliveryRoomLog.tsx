import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { getDeliveryByVisit, createDelivery, updateDelivery, deleteDelivery } from '../../api/functions'
import { getActiveVisits } from '../../api/views'
import { get } from '../../api/client'
import { getLocalDateString, formatMST, getMSTNow } from '../../utils/timeUtils'
import './DeliveryRoomLog.css'

export default function DeliveryRoomLog({ visitId }: { visitId?: number }) {
  const [loading, setLoading] = useState(false)
  const [visits, setVisits] = useState<any[]>([])
  const [staff, setStaff] = useState<any[]>([])
  const [deliveries, setDeliveries] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ visit_id: '', practitioner_id: '', notes: '' })
  const [editingDelivery, setEditingDelivery] = useState<any | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')

  useEffect(() => {
    loadStaff()
    loadVisitsForDropdown()
    if (visitId) {
      // If in a visit context, allow immediate loading
      loadData()
    }
  }, [visitId])

  const loadVisitsForDropdown = async () => {
    try {
      const v = await get<any[]>('/visits?limit=50').catch(() => [])
      const enriched = await enrichVisitsWithPatients(v)
      setVisits(enriched)
    } catch (e) {
      console.error('Failed to load visits for dropdown', e)
    }
  }

  const loadStaff = async () => {
    try {
      const staffList = await get<any[]>('/staff?limit=100').catch(() => [])
      // Filter to only show valid staff with names and filter out test/duplicate entries
      const validStaff = staffList.filter(s => {
        const firstName = s.first_name || s.First_Name || ''
        const lastName = s.last_name || s.Last_Name || ''
        const name = `${firstName} ${lastName}`.trim()
        // Filter out entries without proper names or test entries
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

  const loadData = async () => {
    // Defer auto-loading until a date is chosen unless in visit context
    if (!visitId && !selectedDate) {
      setDeliveries([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      // Load all visits (not just active ones, since getActiveVisits might be empty)
      let v = await get<any[]>('/visits?limit=50').catch(() => [])
      
      // If a date is selected in the UI, load deliveries for that date
      if (selectedDate) {
        const dateDeliveries = await get<any[]>(`/deliveries/date/${selectedDate}`).catch(() => null)
        if (Array.isArray(dateDeliveries)) {
          // Enrich visits with patient names
          const enriched = await enrichVisitsWithPatients(v)
          setVisits(enriched)
          const withVisits = dateDeliveries.map((d: any) => ({ ...d, visit: enriched.find((x: any) => (x.visit_id || x._id) === (d.visit_id || d.visit) ) }))
          setDeliveries(withVisits)
          return
        }
      }

      // prefer a daily deliveries endpoint when available (today) when no explicit date provided
      const todayDeliveries = await get<any[]>('/deliveries/today').catch(() => null)
      if (todayDeliveries && Array.isArray(todayDeliveries) && todayDeliveries.length > 0) {
        // Try to attach visit info to each delivery if possible
        const enriched = await enrichVisitsWithPatients(v)
        setVisits(enriched)
        const withVisits = todayDeliveries.map((d: any) => ({ ...d, visit: enriched.find((x: any) => (x.visit_id || x._id) === (d.visit_id || d.visit) ) }))
        setDeliveries(withVisits)
        if (visitId) {
          const filtered = withVisits.filter((d) => (d.visit as any)?.visit_id === visitId || d.visit_id === visitId)
          setDeliveries(filtered)
        }
        return
      }

      if (visitId) {
        const data = await getDeliveryByVisit(visitId)
        setDeliveries([data])
        const enriched = await enrichVisitsWithPatients(v)
        setVisits(enriched)
        return
      }

      const enriched = await enrichVisitsWithPatients(v)
      setVisits(enriched)

      const promises = enriched.map((vis) => getDeliveryByVisit((vis as any).visit_id || (vis as any)._id || (vis as any).id).catch(() => null))
      const results = await Promise.all(promises)
      const combined = results.filter(Boolean).map((d: any, i: number) => ({ ...d, visit: enriched[i] }))
      setDeliveries(combined as any[])
    } catch (e) {
      console.error('Delivery load failed', e)
      setError('Failed to load delivery records')
    } finally {
      setLoading(false)
    }
  }

  const enrichVisitsWithPatients = async (visits: any[]) => {
    const enriched = await Promise.all(
      visits.map(async (v) => {
        const visitId = v.visit_id || v.Visit_Id || v._id
        const patientId = v.patient_id || v.Patient_Id
        if (patientId) {
          try {
            const patient = await get<any>(`/patients/${patientId}`)
            const first = patient.first_name || patient.First_Name || ''
            const last = patient.last_name || patient.Last_Name || ''
            const name = `${first} ${last}`.trim()
            return { 
              ...v, 
              patient_name: name || `Patient ${patientId}`,
              display_name: `Visit ${visitId} - ${name || `Patient ${patientId}`}`
            }
          } catch {
            return { 
              ...v, 
              patient_name: `Patient ${patientId}`,
              display_name: `Visit ${visitId} - Patient ${patientId}`
            }
          }
        }
        return { 
          ...v, 
          patient_name: 'Unknown',
          display_name: `Visit ${visitId} - Unknown Patient`
        }
      })
    )
    return enriched
  }

  const openModal = () => {
    setEditingDelivery(null)
    setForm({ visit_id: visits[0]?.visit_id || visits[0]?._id || '', practitioner_id: '', notes: '' })
    setShowModal(true)
  }

  const openEditModal = (entry: any) => {
    setEditingDelivery(entry)
    setForm({
      visit_id: String(entry.visit_id || (entry.visit as any)?.visit_id || (entry.visit as any)?._id || ''),
      practitioner_id: String(entry.performed_by || entry.practitioner_id || ''),
      notes: entry.notes || ''
    })
    setShowModal(true)
  }

  const loadByDate = async (dateStr: string) => {
    setSelectedDate(dateStr)
    setLoading(true)
    try {
      const dateDeliveries = await get<any[]>(`/deliveries/date/${dateStr}`)
      const v = await get<any[]>('/visits?limit=50').catch(() => [])
      const enriched = await enrichVisitsWithPatients(v)
      setVisits(enriched)
      const withVisits = (dateDeliveries || []).map((d: any) => ({ ...d, visit: enriched.find((x: any) => (x.visit_id || x._id) === (d.visit_id || d.visit) ) }))
      setDeliveries(withVisits)
    } catch (err) {
      console.error('Failed to load deliveries for date', err)
      setError('Failed to load deliveries for selected date')
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    const targetVisit = visitId || Number(form.visit_id)
    if (!targetVisit) {
      alert('Please select a visit')
      return
    }
    if (!form.practitioner_id) {
      alert('Please select a practitioner')
      return
    }
    try {
      if (editingDelivery) {
        const deliveryId = editingDelivery.delivery_id || editingDelivery.Delivery_Id || editingDelivery._id
        const payload: any = {
          visit_id: Number(targetVisit),
          performed_by: Number(form.practitioner_id),
          notes: form.notes
        }
        // Preserve existing delivery_date if available
        if (editingDelivery.delivery_date || editingDelivery.Start_Time) {
          payload.delivery_date = editingDelivery.delivery_date || editingDelivery.Start_Time
        }
        await updateDelivery(deliveryId, payload)
        alert('Delivery updated successfully!')
      } else {
        // Backend expects 'performed_by' not 'practitioner_id'
        // Do NOT send delivery_date (server will set local time to avoid UTC shift)
        await createDelivery({ 
          visit_id: Number(targetVisit), 
          performed_by: Number(form.practitioner_id),
          notes: form.notes 
        })
        alert('Delivery created successfully!')
      }
      setShowModal(false)
      await loadData()
    } catch (err) {
      console.error(err)
      alert(`Failed to ${editingDelivery ? 'update' : 'create'} delivery`)
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
      <div className="log-page">
        <div className="toolbar">
          <div className="toolbar-left">
            <h3 style={{ margin: 0 }}>Daily Delivery Room Log</h3>
          </div>
        {!visitId && (
            <div className="toolbar-right">
              <input 
                type="date" 
                className="date" 
                value={selectedDate} 
                onChange={(e) => setSelectedDate(e.target.value)} 
              />
              <button className="btn" disabled={!selectedDate} onClick={() => selectedDate && loadByDate(selectedDate)}>Load</button>
              <button className="btn" onClick={() => { const today = getLocalDateString(); loadByDate(today); }}>Today</button>
              <button className="btn btn-primary" onClick={openModal}>Add Delivery</button>
          </div>
        )}
      </div>

      {deliveries.length === 0 ? (
          <p className="muted" style={{ marginTop: 12 }}>
            {visitId
              ? 'No delivery record found for this visit.'
              : selectedDate
                ? 'No delivery records found for selected date.'
                : 'Select a date to view delivery records.'}
          </p>
      ) : (
          <table className="table">
        <thead>
           <tr>
            <th>Delivery ID</th>
            <th>Visit</th>
            <th>Patient</th>
            <th>Practitioner</th>
            <th>Date</th>
            <th>Notes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {deliveries.map((entry, i) => (
              <tr key={entry.delivery_id || entry._id || i}>
                  <td>{entry.delivery_id ?? entry._id ?? 'N/A'}</td>
                  <td>{(entry.visit as any)?.visit_id || entry.visit_id || (entry.visit as any)?._id || '—'}</td>
                  <td>{(entry.visit as any)?.patient_name || (entry.visit as any)?.patient?.name || entry.patient_id || 'Unknown'}</td>
                  <td>{entry.performed_by || entry.practitioner_id || '—'}</td>
                  <td>{formatMST(entry.delivery_date)}</td>
                  <td>{entry.notes || '—'}</td>
                  <td>
                     <button className="btn" onClick={() => openEditModal(entry)} style={{ marginRight: 4 }}>Edit</button>
                      <button 
                        className="btn"
                        onClick={async () => {
                  const deliveryId = entry.delivery_id || entry.Delivery_Id || entry._id
                  const confirmDelete = confirm(`Delete delivery ID ${deliveryId}?`)
                  if (!confirmDelete) return
                  try {
                    await deleteDelivery(deliveryId)
                    alert('Delivery deleted!')
                    await loadData()
                  } catch (e) {
                    console.error(e)
                    alert('Failed to delete delivery')
                  }
                      }} 
                        style={{ background: '#dc3545', color: 'white', borderColor: '#dc3545' }}
                      >
                        Delete
                      </button>
              </td>
            </tr>
          ))}
        </tbody>
        </table>
      )}

      {showModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>{editingDelivery ? 'Edit Delivery' : 'Create Delivery'}</h3>
            {!visitId && (
                <div className="form-group">
                <label>Visit:</label>
                  <select 
                    className="select"
                    value={form.visit_id} 
                    onChange={(e) => setForm({ ...form, visit_id: e.target.value })} 
                    disabled={!!editingDelivery}
                    style={{ width: '100%' }}
                  >
                  <option value="">Select visit</option>
                  {visits.map((v) => (
                    <option key={(v as any).visit_id || (v as any)._id} value={(v as any).visit_id || (v as any)._id}>
                      {(v as any).display_name || (v as any).patient_name || `Visit ${(v as any).visit_id || (v as any)._id}`}
                    </option>
                  ))}
                </select>
              </div>
            )}
              <div className="form-group">
              <label>Practitioner:</label>
                <select 
                  className="select"
                  value={form.practitioner_id} 
                  onChange={(e) => setForm({ ...form, practitioner_id: e.target.value })}
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
              <label>Notes:</label>
                <textarea 
                  className="input"
                  value={form.notes} 
                  onChange={(e) => setForm({ ...form, notes: e.target.value })} 
                  rows={3}
                  style={{ width: '100%', fontFamily: 'inherit' }}
                />
            </div>
              <div className="modal-actions">
                <button className="btn" onClick={() => setShowModal(false)}>Cancel</button>
                <button className="btn btn-primary" onClick={submit}>{editingDelivery ? 'Update' : 'Create'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
