import React, { useEffect, useState } from 'react'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'
import { get, post } from '../../api/client'

interface WeekData {
  [date: string]: {
    shifts: any[]
    appointments: any[]
  }
}

export default function WeeklySchedule() {
  const [loading, setLoading] = useState(true)
  const [weekData, setWeekData] = useState<WeekData>({})
  const [error, setError] = useState<string | null>(null)
  const [selectedWeekStart, setSelectedWeekStart] = useState<string>('')
  const [staffList, setStaffList] = useState<any[]>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({
    staff_id: '',
    shift_date: '',
    start_time: '',
    end_time: '',
    role: '',
    notes: ''
  })

  useEffect(() => {
    // Set to the start of current week (Monday)
    const today = new Date()
    const monday = getMonday(today)
    setSelectedWeekStart(monday.toISOString().slice(0, 10))
    loadStaffList()
  }, [])

  useEffect(() => {
    if (selectedWeekStart) {
      loadWeekSchedule()
    }
  }, [selectedWeekStart])

  const getMonday = (date: Date): Date => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Adjust when day is Sunday
    return new Date(d.setDate(diff))
  }

  const getWeekDates = (startDate: string): string[] => {
    const dates: string[] = []
    const start = new Date(startDate)
    for (let i = 0; i < 7; i++) {
      const date = new Date(start)
      date.setDate(start.getDate() + i)
      dates.push(date.toISOString().slice(0, 10))
    }
    return dates
  }

  const loadStaffList = async () => {
    try {
      const staff = await get<any[]>('/staff?active_only=true')
      setStaffList(staff || [])
    } catch (e) {
      console.error('Failed to load staff list', e)
    }
  }

  const loadWeekSchedule = async () => {
    if (!selectedWeekStart) return
    
    setLoading(true)
    setError(null)
    try {
      const weekDates = getWeekDates(selectedWeekStart)
      const data: WeekData = {}

      // Load schedule for each day of the week
      await Promise.all(
        weekDates.map(async (date) => {
          try {
            // Load shifts for the day
            const shifts = await get<any[]>(`/schedules/daily-master?date=${date}`)
            
            // Load all appointments for the day (we'll need to aggregate from all staff)
            const appointments: any[] = []
            for (const staff of staffList) {
              try {
                const staffAppts = await get<any[]>(
                  `/appointments/staff/${staff.staff_id || staff._id}?date=${date}`
                )
                appointments.push(...(staffAppts || []))
              } catch (e) {
                // Staff might not have appointments, continue
              }
            }

            data[date] = {
              shifts: shifts || [],
              appointments: appointments || []
            }
          } catch (e) {
            console.error(`Failed to load data for ${date}`, e)
            data[date] = { shifts: [], appointments: [] }
          }
        })
      )

      setWeekData(data)
    } catch (e) {
      console.error('Failed to load weekly schedule', e)
      setError('Failed to load weekly schedule')
    } finally {
      setLoading(false)
    }
  }

  const handlePreviousWeek = () => {
    const currentStart = new Date(selectedWeekStart)
    currentStart.setDate(currentStart.getDate() - 7)
    setSelectedWeekStart(currentStart.toISOString().slice(0, 10))
  }

  const handleNextWeek = () => {
    const currentStart = new Date(selectedWeekStart)
    currentStart.setDate(currentStart.getDate() + 7)
    setSelectedWeekStart(currentStart.toISOString().slice(0, 10))
  }

  const handleThisWeek = () => {
    const today = new Date()
    const monday = getMonday(today)
    setSelectedWeekStart(monday.toISOString().slice(0, 10))
  }

  const openModal = (date?: string) => {
    setForm({
      staff_id: '',
      shift_date: date || selectedWeekStart,
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
      await loadWeekSchedule()
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

  const formatTime = (time: string) => {
    if (!time) return '—'
    if (time.includes('T')) {
      return new Date(time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }
    return time
  }

  const getDayName = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', { weekday: 'short' })
  }

  const getDateDisplay = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const isToday = (date: string) => {
    const today = new Date().toLocaleDateString('en-CA', {
      timeZone: 'America/Edmonton' 
    });
    return date === today
  }

  const getTotalShiftsForDay = (date: string) => {
    return weekData[date]?.shifts?.length || 0
  }

  const getTotalAppointmentsForDay = (date: string) => {
    return weekData[date]?.appointments?.length || 0
  }

  const getUniqueStaffForDay = (date: string) => {
    const shifts = weekData[date]?.shifts || []
    return new Set(shifts.map(s => s.staff_id)).size
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  const weekDates = getWeekDates(selectedWeekStart)
  const weekEnd = weekDates[weekDates.length - 1]
  
  // Calculate weekly totals
  const totalShifts = Object.values(weekData).reduce((sum, day) => sum + day.shifts.length, 0)
  const totalAppointments = Object.values(weekData).reduce((sum, day) => sum + day.appointments.length, 0)

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h2>Weekly Schedule</h2>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
            {viewMode === 'grid' ? 'List View' : 'Grid View'}
          </button>
          <button onClick={() => openModal()}>Add Shift</button>
          <button onClick={() => loadWeekSchedule()}>Refresh</button>
        </div>
      </div>

      {/* Week Navigation */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '12px', alignItems: 'center', background: '#f5f5f5', padding: '12px', borderRadius: 6, flexWrap: 'wrap' }}>
        <button onClick={handlePreviousWeek}>← Previous Week</button>
        <div style={{ fontWeight: 'bold', fontSize: '1.1rem', flex: 1, textAlign: 'center' }}>
          {new Date(selectedWeekStart).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          {' - '}
          {new Date(weekEnd).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </div>
        <button onClick={handleThisWeek}>This Week</button>
        <button onClick={handleNextWeek}>Next Week →</button>
      </div>

      {/* Weekly Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#e3f2fd', padding: '1rem', borderRadius: 6, border: '1px solid #90caf9' }}>
          <div style={{ fontSize: '0.85rem', color: '#1565c0', marginBottom: '0.25rem' }}>Total Shifts</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#0d47a1' }}>{totalShifts}</div>
        </div>
        <div style={{ background: '#f3e5f5', padding: '1rem', borderRadius: 6, border: '1px solid #ce93d8' }}>
          <div style={{ fontSize: '0.85rem', color: '#6a1b9a', marginBottom: '0.25rem' }}>Total Appointments</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4a148c' }}>{totalAppointments}</div>
        </div>
        <div style={{ background: '#e8f5e9', padding: '1rem', borderRadius: 6, border: '1px solid #81c784' }}>
          <div style={{ fontSize: '0.85rem', color: '#2e7d32', marginBottom: '0.25rem' }}>Active Staff</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1b5e20' }}>
            {new Set(Object.values(weekData).flatMap(day => day.shifts.map(s => s.staff_id))).size}
          </div>
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div style={{ overflowX: 'auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem', minWidth: '900px' }}>
            {weekDates.map((date) => (
              <div 
                key={date}
                style={{ 
                  border: '1px solid #ddd', 
                  borderRadius: 6,
                  background: isToday(date) ? '#fff9c4' : 'white',
                  overflow: 'hidden'
                }}
              >
                {/* Day Header */}
                <div style={{ 
                  background: isToday(date) ? '#fbc02d' : '#f5f5f5', 
                  padding: '0.75rem',
                  borderBottom: '2px solid #ddd'
                }}>
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{getDayName(date)}</div>
                  <div style={{ fontSize: '0.85rem', color: '#666' }}>{getDateDisplay(date)}</div>
                </div>

                {/* Day Stats */}
                <div style={{ padding: '0.5rem', borderBottom: '1px solid #eee', background: '#fafafa' }}>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    Shifts: <strong>{getTotalShiftsForDay(date)}</strong>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    Appts: <strong>{getTotalAppointmentsForDay(date)}</strong>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    Staff: <strong>{getUniqueStaffForDay(date)}</strong>
                  </div>
                </div>

                {/* Shifts List */}
                <div style={{ padding: '0.5rem', maxHeight: '400px', overflowY: 'auto' }}>
                  {weekData[date]?.shifts?.length === 0 ? (
                    <div style={{ fontSize: '0.8rem', color: '#999', textAlign: 'center', padding: '1rem' }}>
                      No shifts
                    </div>
                  ) : (
                    weekData[date]?.shifts
                      ?.sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''))
                      .map((shift, idx) => (
                        <div 
                          key={idx}
                          style={{ 
                            background: '#e3f2fd',
                            padding: '0.5rem',
                            marginBottom: '0.5rem',
                            borderRadius: 4,
                            border: '1px solid #90caf9',
                            fontSize: '0.8rem'
                          }}
                        >
                          <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                            {getStaffName(shift.staff_id)}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#555' }}>
                            {formatTime(shift.start_time)} - {formatTime(shift.end_time)}
                          </div>
                          {shift.role && (
                            <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.25rem' }}>
                              {shift.role}
                            </div>
                          )}
                        </div>
                      ))
                  )}
                  
                  {/* Add Shift Button */}
                  <button 
                    onClick={() => openModal(date)}
                    style={{ 
                      width: '100%', 
                      padding: '0.5rem', 
                      fontSize: '0.75rem',
                      borderRadius: 4,
                      border: '1px dashed #ccc',
                      background: 'white',
                      cursor: 'pointer',
                      marginTop: '0.5rem'
                    }}
                  >
                    + Add Shift
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div>
          {weekDates.map((date) => (
            <div key={date} style={{ marginBottom: '1.5rem' }}>
              <div style={{ 
                background: isToday(date) ? '#fff9c4' : '#f5f5f5', 
                padding: '0.75rem', 
                borderRadius: 6,
                marginBottom: '0.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <strong style={{ fontSize: '1.1rem' }}>
                    {getDayName(date)}, {getDateDisplay(date)}
                  </strong>
                  {isToday(date) && (
                    <span style={{ 
                      marginLeft: '0.5rem', 
                      padding: '0.25rem 0.5rem', 
                      background: '#fbc02d',
                      borderRadius: 4,
                      fontSize: '0.75rem',
                      fontWeight: 'bold'
                    }}>
                      TODAY
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#666' }}>
                  {getTotalShiftsForDay(date)} shifts • {getTotalAppointmentsForDay(date)} appointments
                </div>
              </div>

              {weekData[date]?.shifts?.length === 0 ? (
                <div style={{ 
                  padding: '2rem', 
                  textAlign: 'center', 
                  background: '#fafafa', 
                  borderRadius: 6,
                  border: '1px dashed #ccc'
                }}>
                  <p style={{ margin: 0, color: '#999' }}>No shifts scheduled</p>
                  <button onClick={() => openModal(date)} style={{ marginTop: '0.5rem' }}>
                    Add First Shift
                  </button>
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #ddd' }}>
                    <thead>
                      <tr style={{ background: '#f0f0f0' }}>
                        <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Staff</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Role</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Start</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>End</th>
                        <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid #ddd' }}>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {weekData[date]?.shifts
                        ?.sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''))
                        .map((shift, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              <strong>{getStaffName(shift.staff_id)}</strong>
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {shift.role || '—'}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {formatTime(shift.start_time)}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {formatTime(shift.end_time)}
                            </td>
                            <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>
                              {shift.notes || '—'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Shift Modal */}
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