import React, { useEffect, useState } from 'react'
import { getActiveVisits } from '../../api/views'
import { get } from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import { Link } from 'react-router-dom'

export default function LogsIndex() {
  const [visits, setVisits] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const v = await getActiveVisits()
        if (Array.isArray(v) && v.length > 0) {
          setVisits(v || [])
          return
        }

        // Fallback: if no active visits view data, fetch recent visits directly
        const recent = await get<any[]>('/visits?limit=20')
        setVisits(recent || [])
      } catch (e) {
        setError('Failed to load active or recent visits')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Active Visits</h2>
      {visits.length === 0 ? (
        <p>No active visits found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Visit ID</th>
              <th>Patient</th>
              <th>Staff</th>
              <th>Start Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {visits.map((v) => (
              <tr key={v.visit_id}>
                <td>{v.visit_id}</td>
                <td>{v.patient_name} ({v.patient_id})</td>
                <td>{v.staff_name} ({v.staff_id})</td>
                <td>{v.start_time}</td>
                <td>
                  <Link to={`/logs/delivery/${v.visit_id}`}>Delivery</Link>{' '}
                  <Link to={`/logs/laboratory/${v.visit_id}`}>Lab</Link>{' '}
                  <Link to={`/logs/recovery/${v.visit_id}`}>Recovery</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
