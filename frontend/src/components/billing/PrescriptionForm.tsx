import React, { useEffect, useState } from 'react'
import { getActiveVisits } from '../../api/views'
import { getDrugs, createPrescription, getPrescriptionsByVisit } from '../../api/functions'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

interface Props {
  prescriptionId?: number
  onPrescriptionCreated?: (prescriptionId: number) => void
}

export default function PrescriptionForm({ prescriptionId, onPrescriptionCreated }: Props) {
  const [visits, setVisits] = useState<any[]>([])
  const [drugs, setDrugs] = useState<any[]>([])
  const [selectedVisit, setSelectedVisit] = useState<number | null>(null)
  const [selectedDrug, setSelectedDrug] = useState<string | number | null>(null)
  const [dosage, setDosage] = useState('')
  const [duration, setDuration] = useState('')
  const [price, setPrice] = useState<number | ''>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [prescriptions, setPrescriptions] = useState<any[]>([])

  useEffect(() => {
    const load = async () => {
      try {
        const [v, d] = await Promise.all([getActiveVisits(), getDrugs()])
        setVisits(v || [])
        setDrugs(d || [])
        if (v && v.length > 0) setSelectedVisit(v[0].visit_id)
      } catch (e) {
        setError('Failed to load visits or drugs')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  useEffect(() => {
    if (!selectedVisit) return
    getPrescriptionsByVisit(selectedVisit).then(setPrescriptions).catch(() => setPrescriptions([]))
  }, [selectedVisit])

  const handleCreate = async () => {
    if (!selectedVisit || !selectedDrug) return alert('Select visit and drug')
    try {
      const data = {
        visit_id: selectedVisit,
        drug_name: typeof selectedDrug === 'string' ? selectedDrug : undefined,
        drug_id: typeof selectedDrug === 'number' ? selectedDrug : undefined,
        dosage,
        duration,
        price: Number(price) || 0
      }
      const result = await createPrescription(data)
      const updated = await getPrescriptionsByVisit(selectedVisit)
      setPrescriptions(updated)
      setDosage('')
      setDuration('')
      setPrice('')
      alert('Prescription saved')
      
      // Notify parent component if callback provided
      if (onPrescriptionCreated && result?.prescription_id) {
        onPrescriptionCreated(result.prescription_id)
      }
    } catch (e) {
      alert('Failed to save prescription')
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="prescription-form">
      <h3>Create Prescription</h3>
      <div>
        <label>Visit: </label>
        <select value={selectedVisit ?? ''} onChange={(e) => setSelectedVisit(Number(e.target.value))}>
          {visits.map((v) => (
            <option key={v.visit_id} value={v.visit_id}>{v.visit_id} - {v.patient_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Drug: </label>
        <select value={selectedDrug ?? ''} onChange={(e) => setSelectedDrug(isNaN(Number(e.target.value)) ? e.target.value : Number(e.target.value))}>
          <option value="">--select--</option>
          {drugs.map((d) => (
            <option key={d.drug_id ?? d.id ?? d.name} value={d.drug_id ?? d.id ?? d.name}>{d.brand_name ?? d.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Dosage: </label>
        <input value={dosage} onChange={(e) => setDosage(e.target.value)} />
      </div>

      <div>
        <label>Duration: </label>
        <input value={duration} onChange={(e) => setDuration(e.target.value)} />
      </div>

      <div>
        <label>Price: </label>
        <input value={price as any} onChange={(e) => setPrice(e.target.value === '' ? '' : Number(e.target.value))} />
      </div>

      <button onClick={handleCreate}>Save Prescription</button>

      <h3>Existing Prescriptions</h3>
      {prescriptions.length === 0 ? <p>No prescriptions for this visit.</p> : (
        <table>
          <thead>
            <tr><th>Rx ID</th><th>Drug</th><th>Dosage</th><th>Duration</th><th>Price</th><th>Action</th></tr>
          </thead>
          <tbody>
            {prescriptions.map((p) => (
              <tr key={p.id || p.prescription_id}>
                <td>{p.prescription_id}</td>
                <td>{p.drug_name ?? p.drug}</td>
                <td>{p.dosage}</td>
                <td>{p.duration}</td>
                <td>${p.price?.toFixed(2) || '0.00'}</td>
                <td>
                  <button 
                    onClick={() => onPrescriptionCreated && onPrescriptionCreated(p.prescription_id)}
                    style={{ fontSize: '0.85rem', padding: '0.25rem 0.5rem' }}
                  >
                    View Label/Receipt
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
