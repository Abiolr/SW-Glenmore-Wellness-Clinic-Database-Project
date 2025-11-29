import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
// Added 'del' to imports
import { get, post, del } from '../../api/client'

export default function PractitionerSchedule({ staffId }: { staffId?: number }) {
  const [loading, setLoading] = useState(true)
  const [appointments, setAppointments] = useState<any[]>([])
  const [shifts, setShifts] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [selectedStaff, setSelectedStaff] = useState<number | null>(null)
  const [staffList, setStaffList] = useState<any[]>([])
  const [showModal, setShowModal] = useState(false)
  const [patients, setPatients] = useState<any[]>([])
  const [form, setForm] = useState({
    patient_id: '',
    scheduled_start: '',
    scheduled_end: '',
    appointment_type: '',
    status: 'scheduled',
    notes: ''
  })

  useEffect(() => {
    const today = new Date().toLocaleDateString('en-CA', {
      timeZone: 'America/Edmonton' 
    });
    setSelectedDate(today)
    
    if (staffId) {
      setSelectedStaff(staffId)
    }
    
    loadStaffList()
    loadPatients()
  }, [staffId])

  useEffect(() => {
    if (selectedDate && (selectedStaff || staffId)) {
      loadSchedule()
    }
  }, [selectedDate, selectedStaff])

  const loadStaffList = async () => {
    try {
      const staff = await get<any[]>('/staff?active_only=true')
      setStaffList(staff || [])
      
      if (!staffId && staff && staff.length > 0) {
        setSelectedStaff(staff[0].staff_id || staff[0]._id)
      }
    } catch (e) {
      console.error('Failed to load staff list', e)
    }
  }

  const loadPatients = async () => {
    try {
      const patientData = await get<any[]>('/patients?limit=100')
      setPatients(patientData || [])
    } catch (e) {
      console.error('Failed to load patients', e)
    }
  }

  const loadSchedule = async () => {
    const currentStaffId = staffId || selectedStaff
    if (!selectedDate || !currentStaffId) return
    
    setLoading(true)
    setError(null)
    try {
      const appts = await get<any[]>(`/appointments/staff/${currentStaffId}?date=${selectedDate}`)
      setAppointments(Array.isArray(appts) ? appts : [])

      try {
        const shiftsData = await get<any[]>(`/schedules/daily-master?date=${selectedDate}`)
        const staffShifts = (shiftsData || []).filter(
          (s: any) => s.staff_id === currentStaffId
        )
        setShifts(staffShifts)
      } catch (e) {
        setShifts([])
      }
    } catch (e) {
      console.error('Failed to load practitioner schedule', e)
      setError('Failed to load schedule for the selected date')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    loadSchedule()
  }

  // New function to handle deletion
  const handleDelete = async (appointmentId: number) => {
    if (!window.confirm('Are you sure you want to delete this appointment?')) {
      return
    }

    try {
      await del(`/appointments/${appointmentId}`)
      alert('Appointment deleted successfully')
      loadSchedule()
    } catch (e) {
      console.error('Failed to delete appointment', e)
      alert('Failed to delete appointment')
    }
  }

  const handleToday = () => {
    const today = new Date().toLocaleDateString('en-CA', {
      timeZone: 'America/Edmonton' 
    });
    setSelectedDate(today)
  }

  const openModal = () => {
    const date = selectedDate || new Date().toISOString().slice(0, 10)
    setForm({
      patient_id: '',
      scheduled_start: `${date}T09:00`,
      scheduled_end: `${date}T10:00`,
      appointment_type: 'consultation',
      status: 'scheduled',
      notes: ''
    })
    setShowModal(true)
  }

  const handleSubmit = async () => {
    const currentStaffId = staffId || selectedStaff
    
    if (!form.patient_id || !form.scheduled_start || !form.scheduled_end || !currentStaffId) {
      alert('Please fill in all required fields')
      return
    }

    try {
      const appointmentData = {
        patient_id: Number(form.patient_id),
        staff_id: Number(currentStaffId),
        scheduled_start: form.scheduled_start,
        scheduled_end: form.scheduled_end,
        appointment_type: form.appointment_type,
        status: form.status,
        notes: form.notes || undefined
      }

      await post('/appointments', appointmentData)
      setShowModal(false)
      await loadSchedule()
      alert('Appointment created successfully')
    } catch (err) {
      console.error('Failed to create appointment', err)
      alert('Failed to create appointment')
    }
  }

  const getStaffName = (id: number) => {
    const staff = staffList.find((s) => s.staff_id === id || s._id === id)
    if (!staff) return `Staff ${id}`
    const firstName = staff.first_name || staff.First_Name || ''
    const lastName = staff.last_name || staff.Last_Name || ''
    return `${firstName} ${lastName}`.trim() || `Staff ${id}`
  }

  const getPatientName = (id: number) => {
    const patient = patients.find((p) => p.patient_id === id || p._id === id)
    if (!patient) return `Patient ${id}`
    const firstName = patient.first_name || patient.First_Name || ''
    const lastName = patient.last_name || patient.Last_Name || ''
    return `${firstName} ${lastName}`.trim() || `Patient ${id}`
  }

  const formatTime = (datetime: string) => {
    if (!datetime) return '—'
    return new Date(datetime).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const calculateDuration = (start: string, end: string) => {
    if (!start || !end) return '—'
    const startTime = new Date(start).getTime()
    const endTime = new Date(end).getTime()
    const minutes = (endTime - startTime) / (1000 * 60)
    if (minutes < 60) return `${minutes} min`
    return `${(minutes / 60).toFixed(1)} hrs`
  }

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: { bg: string; text: string } } = {
      scheduled: { bg: '#e3f2fd', text: '#1565c0' },
      completed: { bg: '#e8f5e9', text: '#2e7d32' },
      cancelled: { bg: '#ffebee', text: '#c62828' },
      'no-show': { bg: '#fff3e0', text: '#e65100' },
      'in-progress': { bg: '#fff9c4', text: '#f57f17' }
    }
    return colors[status] || { bg: '#f5f5f5', text: '#666' }
  }

  const currentStaffId = staffId || selectedStaff
  const currentStaffName = currentStaffId ? getStaffName(currentStaffId) : 'Select a practitioner'

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Practitioner Schedule</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          {!staffId && appointments.length > 0 && (
            <button onClick={openModal}>Add Appointment</button>
          )}
          <button onClick={handleRefresh}>Refresh</button>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '12px', alignItems: 'center', background: '#f5f5f5', padding: '12px', borderRadius: 6, flexWrap: 'wrap' }}>
        {!staffId && (
          <>
            <label style={{ fontWeight: 'bold' }}>Practitioner:</label>
            <select 
              value={selectedStaff || ''} 
              onChange={(e) => setSelectedStaff(Number(e.target.value))}
              style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc', minWidth: '200px' }}
            >
              <option value="">Select practitioner</option>
              {staffList.map((staff) => (
                <option key={staff.staff_id || staff._id} value={staff.staff_id || staff._id}>
                  {getStaffName(staff.staff_id || staff._id)}
                </option>
              ))}
            </select>
          </>
        )}
        
        <label style={{ fontWeight: 'bold', marginLeft: staffId ? 0 : '1rem' }}>Schedule Date:</label>
        <input 
          type="date" 
          value={selectedDate} 
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button onClick={handleToday}>Today</button>
      </div>

      {!currentStaffId ? (
        <div style={{ textAlign: 'center', padding: '2rem', background: '#f9f9f9', borderRadius: 6 }}>
          <p style={{ margin: 0, color: '#666' }}>Please select a practitioner to view their schedule</p>
        </div>
      ) : (
        <div>
          <div style={{ background: '#e3f2fd', padding: '1rem', borderRadius: 6, marginBottom: '1.5rem', border: '1px solid #90caf9' }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#1565c0' }}>{currentStaffName}</h3>
            <div style={{ fontSize: '0.9rem', color: '#424242' }}>
              Schedule for: <strong>{new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</strong>
            </div>
          </div>

          {shifts.length > 0 && (
            <div style={{ background: '#f3e5f5', padding: '1rem', borderRadius: 6, marginBottom: '1.5rem', border: '1px solid #ce93d8' }}>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#6a1b9a' }}>Scheduled Shift</h4>
              {shifts.map((shift, idx) => (
                <div key={idx} style={{ fontSize: '0.9rem', color: '#424242' }}>
                  {formatTime(shift.start_time)} - {formatTime(shift.end_time)}
                  {shift.role && <span style={{ marginLeft: '1rem', color: '#666' }}>({shift.role})</span>}
                </div>
              ))}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{ background: 'white', padding: '0.75rem', borderRadius: 6, border: '1px solid #e0e0e0' }}>
              <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>Total Appointments</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333' }}>{appointments.length}</div>
            </div>
            <div style={{ background: 'white', padding: '0.75rem', borderRadius: 6, border: '1px solid #e0e0e0' }}>
              <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>Scheduled</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1565c0' }}>
                {appointments.filter(a => a.status === 'scheduled').length}
              </div>
            </div>
            <div style={{ background: 'white', padding: '0.75rem', borderRadius: 6, border: '1px solid #e0e0e0' }}>
              <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>Completed</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2e7d32' }}>
                {appointments.filter(a => a.status === 'completed').length}
              </div>
            </div>
          </div>

          {appointments.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', background: '#f9f9f9', borderRadius: 6 }}>
              <p style={{ margin: 0, color: '#666' }}>No appointments scheduled for this date</p>
              {!staffId && (
                <button onClick={openModal} style={{ marginTop: '1rem' }}>Add First Appointment</button>
              )}
            </div>
          ) : (
            <div>
              <h3>Appointments</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Time</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Patient</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Duration</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Status</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Notes</th>
                      <th style={{ padding: '0.75rem', textAlign: 'center', border: '1px solid #ddd' }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments
                      .sort((a, b) => new Date(a.scheduled_start).getTime() - new Date(b.scheduled_start).getTime())
                      .map((appt, i) => {
                        const statusColors = getStatusColor(appt.status)
                        const apptId = appt.appointment_id || appt._id
                        return (
                          <tr key={apptId || i} style={{ borderBottom: '1px solid #eee' }}>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              <div style={{ fontWeight: 'bold' }}>{formatTime(appt.scheduled_start)}</div>
                              <div style={{ fontSize: '0.85rem', color: '#666' }}>
                                {formatTime(appt.scheduled_end)}
                              </div>
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              <strong>{getPatientName(appt.patient_id)}</strong>
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {appt.appointment_type || 'General'}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {calculateDuration(appt.scheduled_start, appt.scheduled_end)}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              <span style={{
                                padding: '0.25rem 0.5rem',
                                borderRadius: 4,
                                fontSize: '0.85rem',
                                background: statusColors.bg,
                                color: statusColors.text,
                                fontWeight: 500
                              }}>
                                {appt.status || 'scheduled'}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {appt.notes || '—'}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'center' }}>
                              <button
                                onClick={() => handleDelete(apptId)}
                                style={{
                                  background: '#ffebee',
                                  color: '#c62828',
                                  border: '1px solid #ef9a9a',
                                  borderRadius: '4px',
                                  padding: '4px 8px',
                                  cursor: 'pointer',
                                  fontSize: '0.85rem'
                                }}
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>
              </div>

              <div style={{ marginTop: '2rem' }}>
                <h3>Timeline View</h3>
                <div style={{ background: '#fafafa', padding: '1rem', borderRadius: 6, border: '1px solid #e0e0e0' }}>
                  {appointments
                    .sort((a, b) => new Date(a.scheduled_start).getTime() - new Date(b.scheduled_start).getTime())
                    .map((appt, idx) => (
                      <div 
                        key={idx}
                        style={{ 
                          marginBottom: '0.75rem', 
                          padding: '0.75rem', 
                          background: 'white',
                          borderRadius: 4,
                          border: '1px solid #e0e0e0',
                          borderLeft: `4px solid ${getStatusColor(appt.status).text}`
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <div>
                            <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.25rem' }}>
                              {formatTime(appt.scheduled_start)} - {formatTime(appt.scheduled_end)}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>
                              {getPatientName(appt.patient_id)} • {appt.appointment_type || 'General'}
                            </div>
                            {appt.notes && (
                              <div style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.25rem' }}>
                                {appt.notes}
                              </div>
                            )}
                          </div>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                             <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: 4,
                              fontSize: '0.8rem',
                              background: getStatusColor(appt.status).bg,
                              color: getStatusColor(appt.status).text,
                              fontWeight: 500
                            }}>
                              {appt.status}
                            </span>
                            <button
                              onClick={() => handleDelete(appt.appointment_id || appt._id)}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: '#c62828',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                fontSize: '1rem',
                                padding: '0 4px'
                              }}
                              title="Delete Appointment"
                            >
                              &times;
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {showModal && (
        <div style={{ 
          position: 'fixed', 
          left: 0, 
          right: 0, 
          top: 0, 
          bottom: 0, 
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ 
            background: 'white', 
            padding: '1.5rem', 
            width: '90%',
            maxWidth: '500px', 
            borderRadius: 8,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h3 style={{ marginTop: 0 }}>Schedule Appointment</h3>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                Patient<span style={{ color: 'red' }}>*</span>
              </label>
              <select 
                value={form.patient_id} 
                onChange={(e) => setForm({ ...form, patient_id: e.target.value })}
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              >
                <option value="">Select patient</option>
                {patients.map((patient) => (
                  <option key={patient.patient_id || patient._id} value={patient.patient_id || patient._id}>
                    {getPatientName(patient.patient_id || patient._id)}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                  Start Time<span style={{ color: 'red' }}>*</span>
                </label>
                <input 
                  type="datetime-local"
                  value={form.scheduled_start} 
                  onChange={(e) => setForm({ ...form, scheduled_start: e.target.value })}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                  End Time<span style={{ color: 'red' }}>*</span>
                </label>
                <input 
                  type="datetime-local"
                  value={form.scheduled_end} 
                  onChange={(e) => setForm({ ...form, scheduled_end: e.target.value })}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>Appointment Type</label>
              <select
                value={form.appointment_type} 
                onChange={(e) => setForm({ ...form, appointment_type: e.target.value })}
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              >
                <option value="consultation">Consultation</option>
                <option value="follow-up">Follow-up</option>
                <option value="procedure">Procedure</option>
                <option value="checkup">Check-up</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>Status</label>
              <select
                value={form.status} 
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              >
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>Notes</label>
              <textarea 
                value={form.notes} 
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={3}
                placeholder="Additional notes..."
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc', resize: 'vertical' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button 
                onClick={() => setShowModal(false)}
                style={{ padding: '0.5rem 1rem', borderRadius: 4, border: '1px solid #ccc', background: 'white', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button 
                onClick={handleSubmit}
                style={{ padding: '0.5rem 1rem', borderRadius: 4, border: 'none', background: '#1976d2', color: 'white', cursor: 'pointer' }}
              >
                Schedule
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}