import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { get, post } from '../../api/client'

export default function DailyMasterSchedule() {
  const [loading, setLoading] = useState(true)
  const [shifts, setShifts] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [showModal, setShowModal] = useState(false)
  const [staffList, setStaffList] = useState<any[]>([])
  const [form, setForm] = useState({
    staff_id: '',
    shift_date: '',
    start_time: '',
    end_time: '',
    role: '',
    notes: ''
  })

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10)
    setSelectedDate(today)
    loadStaffList()
  }, [])

  useEffect(() => {
    if (selectedDate) {
      loadSchedule()
    }
  }, [selectedDate])

  const loadStaffList = async () => {
    try {
      const staff = await get<any[]>('/staff?active_only=true')
      setStaffList(staff || [])
    } catch (e) {
      console.error('Failed to load staff list', e)
    }
  }

  const loadSchedule = async () => {
    if (!selectedDate) return
    
    setLoading(true)
    setError(null)
    try {
      const data = await get<any[]>(`/schedules/daily-master?date=${selectedDate}`)
      setShifts(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error('Failed to load daily master schedule', e)
      setError('Failed to load schedule for the selected date')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    loadSchedule()
  }

  const handleToday = () => {
    const today = new Date().toISOString().slice(0, 10)
    setSelectedDate(today)
  }

  const openModal = () => {
    setForm({
      staff_id: '',
      shift_date: selectedDate,
      start_time: '08:00',
      end_time: '17:00',
      role: '',
      notes: ''
    })
    setShowModal(true)
  }

  const handleSubmit = async () => {
    if (!form.staff_id || !form.shift_date || !form.start_time || !form.end_time) {
      alert('Please fill in all required fields')
      return
    }

    try {
      const shiftData = {
        staff_id: Number(form.staff_id),
        shift_date: form.shift_date,
        start_time: form.start_time,
        end_time: form.end_time,
        role: form.role || undefined,
        notes: form.notes || undefined
      }

      await post('/schedules/shifts', shiftData)
      setShowModal(false)
      await loadSchedule()
      alert('Shift added successfully')
    } catch (err) {
      console.error('Failed to create shift', err)
      alert('Failed to create shift')
    }
  }

  const getStaffName = (staffId: number) => {
    const staff = staffList.find((s) => s.staff_id === staffId || s._id === staffId)
    if (!staff) return `Staff ${staffId}`
    const firstName = staff.first_name || staff.First_Name || ''
    const lastName = staff.last_name || staff.Last_Name || ''
    return `${firstName} ${lastName}`.trim() || `Staff ${staffId}`
  }

  // ==== FIXED: Prevent timezone shift ====
  const formatTime = (time: string) => {
    if (!time) return '—'

    if (time.includes('T')) {
      const safe = time.endsWith('Z') ? time : time + 'Z'
      return new Date(safe).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    return time
  }

  const groupShiftsByTime = () => {
    const grouped: { [key: string]: any[] } = {}
    
    shifts.forEach((shift) => {
      const startTime = formatTime(shift.start_time)
      if (!grouped[startTime]) {
        grouped[startTime] = []
      }
      grouped[startTime].push(shift)
    })

    return Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b))
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  const groupedShifts = groupShiftsByTime()

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Daily Master Schedule</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={openModal}>Add Shift</button>
          <button onClick={handleRefresh}>Refresh</button>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '12px', alignItems: 'center', background: '#f5f5f5', padding: '12px', borderRadius: 6 }}>
        <label style={{ fontWeight: 'bold' }}>Schedule Date:</label>
        <input 
          type="date" 
          value={selectedDate} 
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{ padding: '6px 12px', borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button onClick={handleToday}>Today</button>
      </div>

      {shifts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', background: '#f9f9f9', borderRadius: 6 }}>
          {/* ==== FIXED: DO NOT CALL new Date(selectedDate) ==== */}
          <p style={{ margin: 0, color: '#666' }}>No shifts scheduled for {selectedDate}</p>
        </div>
      ) : (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{ background: '#e3f2fd', padding: '1rem', borderRadius: 6, border: '1px solid #90caf9' }}>
              <div style={{ fontSize: '0.85rem', color: '#1565c0', marginBottom: '0.25rem' }}>Total Shifts</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#0d47a1' }}>{shifts.length}</div>
            </div>
            <div style={{ background: '#f3e5f5', padding: '1rem', borderRadius: 6, border: '1px solid #ce93d8' }}>
              <div style={{ fontSize: '0.85rem', color: '#6a1b9a', marginBottom: '0.25rem' }}>Staff On Duty</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4a148c' }}>
                {new Set(shifts.map(s => s.staff_id)).size}
              </div>
            </div>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
              <thead>
                <tr style={{ background: '#f0f0f0', borderBottom: '2px solid #ddd' }}>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Shift ID</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Staff Member</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Role</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Start Time</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>End Time</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Duration</th>
                  <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Notes</th>
                </tr>
              </thead>
              <tbody>
                {shifts.map((shift, i) => {
                  // ==== FIXED: Prevent timezone shift ====
                  const start = shift.start_time
                    ? new Date((shift.start_time.endsWith('Z') ? shift.start_time : shift.start_time + 'Z'))
                    : null

                  const end = shift.end_time
                    ? new Date((shift.end_time.endsWith('Z') ? shift.end_time : shift.end_time + 'Z'))
                    : null

                  const duration = start && end ? ((end.getTime() - start.getTime()) / (1000 * 60 * 60)).toFixed(1) : '—'
                  
                  return (
                    <tr key={shift.shift_id || shift._id || i} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {shift.shift_id || shift._id || 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        <strong>{getStaffName(shift.staff_id)}</strong>
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {shift.role || shift.position || '—'}
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {formatTime(shift.start_time)}
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {formatTime(shift.end_time)}
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {duration !== '—' ? `${duration} hrs` : '—'}
                      </td>
                      <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                        {shift.notes || '—'}
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
              {groupedShifts.map(([time, timeShifts]) => (
                <div key={time} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #e0e0e0' }}>
                  <div style={{ fontWeight: 'bold', color: '#1976d2', marginBottom: '0.5rem' }}>{time}</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {timeShifts.map((shift, idx) => (
                      <div 
                        key={idx}
                        style={{ 
                          background: '#e3f2fd', 
                          padding: '0.5rem 0.75rem', 
                          borderRadius: 4,
                          border: '1px solid #90caf9',
                          fontSize: '0.9rem'
                        }}
                      >
                        {getStaffName(shift.staff_id)}
                        {shift.role && <span style={{ color: '#666', marginLeft: '0.5rem' }}>({shift.role})</span>}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
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
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ marginTop: 0 }}>Add Staff Shift</h3>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                Staff Member<span style={{ color: 'red' }}>*</span>
              </label>
              <select 
                value={form.staff_id} 
                onChange={(e) => setForm({ ...form, staff_id: e.target.value })}
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              >
                <option value="">Select staff member</option>
                {staffList.map((staff) => (
                  <option key={staff.staff_id || staff._id} value={staff.staff_id || staff._id}>
                    {getStaffName(staff.staff_id || staff._id)}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                Shift Date<span style={{ color: 'red' }}>*</span>
              </label>
              <input 
                type="date"
                value={form.shift_date} 
                onChange={(e) => setForm({ ...form, shift_date: e.target.value })}
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                  Start Time<span style={{ color: 'red' }}>*</span>
                </label>
                <input 
                  type="time"
                  value={form.start_time} 
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                  End Time<span style={{ color: 'red' }}>*</span>
                </label>
                <input 
                  type="time"
                  value={form.end_time} 
                  onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>Role/Position</label>
              <input 
                type="text"
                value={form.role} 
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                placeholder="e.g., Nurse, Doctor, Receptionist"
                style={{ width: '100%', padding: '0.5rem', borderRadius: 4, border: '1px solid #ccc' }}
              />
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
                Add Shift
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
