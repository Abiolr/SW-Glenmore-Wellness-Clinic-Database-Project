import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { getActiveVisits } from '../../api/views'
import { createRecoveryStay, getRecoveryObservationsByStay, createRecoveryObservation, getRecoveryStay, updateRecoveryStay } from '../../api/functions'
import { get } from '../../api/client'

export default function RecoveryRoomLog({ stayId }: { stayId?: number }) {
  const [loading, setLoading] = useState(true)
  const [visits, setVisits] = useState<any[]>([])
  const [currentStay, setCurrentStay] = useState<any | null>(null)
  const [currentPatient, setCurrentPatient] = useState<any | null>(null)
  const [observations, setObservations] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [showCreateStay, setShowCreateStay] = useState(false)
  const [formStay, setFormStay] = useState({ visit_id: '', practitioner_id: '' })
  const [newObs, setNewObs] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (stayId) {
      loadStay(stayId)
    }
  }, [stayId])

  const loadData = async () => {
    setLoading(true)
    try {
      let v = await getActiveVisits()
      if (!v || v.length === 0) {
        v = await get<any[]>('/visits?limit=20')
      }
      setVisits(v)
      if (currentStay && currentStay.id) {
        await loadStay(currentStay.id)
      }
    } catch (e) {
      console.error('Recovery load failed', e)
      setError('Failed to load recovery data')
    } finally {
      setLoading(false)
    }
  }

  const loadStay = async (id: number) => {
    setLoading(true)
    try {
      const s = await getRecoveryStay(id)
      setCurrentStay(s)
      const obs = await getRecoveryObservationsByStay(id)
      setObservations(obs || [])
      // load patient details
      try {
        const p = await get(`/patients/${s.patient_id}`)
        setCurrentPatient(p)
      } catch (err) {
        setCurrentPatient(null)
      }
      // load discharged_by staff details if present
      if (s.discharged_by) {
        try {
          const staff = await get(`/staff/${s.discharged_by}`)
          setCurrentStay((prev: any) => ({ ...prev, discharged_by_name: staff.first_name && staff.last_name ? `${staff.first_name} ${staff.last_name}` : staff.staff_id }))
        } catch (err) {
          // ignore
        }
      }
    } catch (e) {
      console.error('Failed to load stay or observations', e)
      setError('Failed to load stay observations')
    } finally {
      setLoading(false)
    }
  }

  const openCreateStay = () => {
    // Only default to the first visit if no visit has already been selected
    setFormStay((prev) => ({
      visit_id: prev.visit_id || visits[0]?.visit_id || visits[0]?._id || '',
      practitioner_id: prev.practitioner_id || ''
    }))
    setShowCreateStay(true)
  }

  const submitCreateStay = async () => {
    if (!formStay.visit_id) return alert('Select a visit')
    try {
      // find patient_id for the selected visit
      const visit = visits.find((v: any) => (v.visit_id || v._id) === Number(formStay.visit_id))
      const patient_id = visit?.patient_id || visit?.patient?.patient_id || visit?.patient?._id
      if (!patient_id) return alert('Selected visit does not have a patient')

      const payload: any = {
        patient_id: Number(patient_id),
        admit_time: new Date().toISOString(),
      }
      // optional notes
      if ((formStay as any).notes) payload.notes = (formStay as any).notes

      const res = await createRecoveryStay(payload)
      const stayId = res.stay_id || res._id || res.id
      if (stayId) await loadStay(Number(stayId))
      setShowCreateStay(false)
      alert('Recovery stay created')
    } catch (e) {
      console.error(e)
      alert('Failed to create stay')
    }
  }

  const addObservation = async () => {
    if (!currentStay || !currentStay.stay_id) return alert('Select or create a stay first')
    if (!newObs) return alert('Enter observation text')
    try {
      await createRecoveryObservation({ stay_id: currentStay.stay_id, text_on: new Date().toISOString(), notes: newObs })
      const obs = await getRecoveryObservationsByStay(currentStay.stay_id)
      setObservations(obs || [])
      setNewObs('')
      alert('Observation added')
    } catch (e) {
      console.error(e)
      alert('Failed to add observation')
    }
  }

  const dischargeStay = async () => {
    if (!currentStay || !currentStay.stay_id) return alert('No stay selected')
    const practitioner = prompt('Enter practitioner (staff) ID for sign-off')
    if (!practitioner) return
    try {
      const updated = await updateRecoveryStay(currentStay.stay_id, { discharge_time: new Date().toISOString(), discharged_by: Number(practitioner) })
      await loadStay(updated.stay_id || currentStay.stay_id)
      alert('Stay discharged')
    } catch (err) {
      console.error(err)
      alert('Failed to discharge stay')
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Recovery Room</h3>
        <div>
          <button onClick={openCreateStay}>Create Stay</button>
          <button onClick={loadData} style={{ marginLeft: 8 }}>Refresh</button>
        </div>
      </div>

      <div style={{ marginTop: 12 }}>
        <label>Select visit to create a stay:</label>
        <select value={formStay.visit_id} onChange={(e) => setFormStay({ ...formStay, visit_id: e.target.value })}>
          <option value="">-- Select a visit --</option>
          {visits.map((v) => (
            <option key={(v as any).visit_id || (v as any)._id} value={(v as any).visit_id || (v as any)._id}>
              {(v as any).patient_name || (v as any).patient?.name || `Visit ${(v as any).visit_id || (v as any)._id}`}
            </option>
          ))}
        </select>

        <div style={{ marginTop: 8 }}>
          <label>Or load existing stay by ID:</label>
          <input type="number" placeholder="Stay ID" onBlur={(e) => { const v = Number(e.target.value); if (v) loadStay(v); }} />
        </div>
      </div>

      {currentStay && (
        <div style={{ marginTop: 12 }}>
          <p><strong>Stay ID:</strong> {currentStay.stay_id}</p>
          <p><strong>Patient:</strong> {currentPatient ? `${currentPatient.first_name} ${currentPatient.last_name} (ID ${currentPatient.patient_id})` : currentStay.patient_id}</p>
          <p><strong>Admission:</strong> {currentStay.admit_time}</p>
          <p><strong>Discharge:</strong> {currentStay.discharge_time || '—'}</p>
          {currentStay.discharged_by_name ? (
            <p><strong>Discharged By:</strong> {currentStay.discharged_by_name}</p>
          ) : currentStay.discharged_by ? (
            <p><strong>Discharged By (ID):</strong> {currentStay.discharged_by}</p>
          ) : null}
          { !currentStay.discharge_time && (
            <div style={{ marginTop: 8 }}>
              <button onClick={dischargeStay}>Practitioner Sign-off (Discharge)</button>
            </div>
          )}

          <h4>Observations</h4>
          {observations.length === 0 ? <p>No observations yet.</p> : (
            <ul>
              {observations.map((o) => (
                <li key={o.text_on || o._id}>{o.text_on}: {o.notes}</li>
              ))}
            </ul>
          )}

          <div style={{ marginTop: 12 }}>
            <textarea value={newObs} onChange={(e) => setNewObs(e.target.value)} placeholder="Write observation..." rows={3} style={{ width: '100%' }} />
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
              <button onClick={addObservation}>Add Observation</button>
            </div>
          </div>
        </div>
      )}

      {showCreateStay && (
        <div style={{ position: 'fixed', left: 0, right: 0, top: 0, bottom: 0, background: 'rgba(0,0,0,0.3)' }}>
          <div style={{ background: 'white', padding: 16, width: 480, margin: '60px auto', borderRadius: 6 }}>
            <h4>Create Recovery Stay</h4>
            <div style={{ marginBottom: 8 }}>
              <label>Visit:</label>
              {/* If a visit is already selected in the main form, show it read-only inside the modal. */}
              {formStay.visit_id ? (
                <div style={{ padding: 8, background: '#f6f6f6', borderRadius: 4 }}>
                  {(() => {
                    const v = visits.find((x: any) => (x.visit_id || x._id) === Number(formStay.visit_id));
                    return v ? ((v.patient_name || v.patient?.name) ? `${v.patient_name || v.patient?.name} (Visit ${v.visit_id || v._id})` : `Visit ${v.visit_id || v._id}`) : `Visit ${formStay.visit_id}`;
                  })()}
                </div>
              ) : (
                <select value={formStay.visit_id} onChange={(e) => setFormStay({ ...formStay, visit_id: e.target.value })}>
                  <option value="">Select visit</option>
                  {visits.map((v) => (
                    <option key={(v as any).visit_id || (v as any)._id} value={(v as any).visit_id || (v as any)._id}>
                      {(v as any).patient_name || (v as any).patient?.name || `Visit ${(v as any).visit_id || (v as any)._id}`}
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div style={{ marginBottom: 8 }}>
              <label>Practitioner ID:</label>
              <input value={formStay.practitioner_id} onChange={(e) => setFormStay({ ...formStay, practitioner_id: e.target.value })} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowCreateStay(false)}>Cancel</button>
              <button onClick={submitCreateStay} style={{ marginLeft: 8 }}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
