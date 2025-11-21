import React, { useState, useEffect } from 'react'
import PrescriptionLabel from '../../components/billing/PrescriptionLabel'
import PrescriptionReceipt from '../../components/billing/PrescriptionReceipt'
import { getPrescriptionDetails } from '../../api/functions'
import { get } from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ErrorMessage from '../../components/common/ErrorMessage'
import '../../components/billing/PrescriptionPrint.css'

export default function Prescriptions() {
  const [selectedPrescriptionId, setSelectedPrescriptionId] = useState<number | null>(null)
  const [prescriptionData, setPrescriptionData] = useState<any>(null)
  const [prescriptionList, setPrescriptionList] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingList, setLoadingList] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load all prescriptions on mount
  useEffect(() => {
    const loadPrescriptions = async () => {
      try {
        setLoadingList(true)
        const response = await get<any>('/prescriptions/all')
        setPrescriptionList(response || [])
      } catch (e) {
        console.error('Failed to load prescriptions list', e)
        setPrescriptionList([])
      } finally {
        setLoadingList(false)
      }
    }
    loadPrescriptions()
  }, [])

  const handlePrescriptionSelect = async (prescriptionId: number) => {
    if (!prescriptionId) return
    
    setSelectedPrescriptionId(prescriptionId)
    setLoading(true)
    setError(null)
    
    try {
      const data = await getPrescriptionDetails(prescriptionId)
      setPrescriptionData(data)
    } catch (e) {
      setError('Failed to load prescription details')
      setPrescriptionData(null)
    } finally {
      setLoading(false)
    }
  }

  const getField = (obj: any, ...keys: string[]) => {
    if (!obj) return null
    for (const key of keys) {
      if (obj[key] !== undefined && obj[key] !== null) return obj[key]
    }
    return null
  }

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return ''
    try {
      return new Date(dateStr).toLocaleDateString()
    } catch {
      return dateStr
    }
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Prescriptions</h2>
      
      <div style={{ marginBottom: '2rem' }}>
        <h3>Select Prescription</h3>
        {loadingList ? (
          <p>Loading prescriptions...</p>
        ) : (
          <div>
            <label htmlFor="prescription-select" style={{ display: 'block', marginBottom: '0.5rem' }}>
              Choose a prescription:
            </label>
            <select 
              id="prescription-select"
              onChange={(e) => handlePrescriptionSelect(parseInt(e.target.value))}
              value={selectedPrescriptionId || ''}
              style={{ 
                padding: '0.5rem', 
                fontSize: '1rem', 
                width: '100%',
                maxWidth: '600px'
              }}
            >
              <option value="">-- Select a Prescription --</option>
              {prescriptionList.map((rx) => {
                const rxId = getField(rx, 'prescription_id', 'Prescription_Id')
                const patientName = getField(rx, 'patient_name', 'Patient_Name') || 'Unknown Patient'
                const drugName = getField(rx, 'drug_name', 'Drug_Name') || 'Unknown Drug'
                const dispensedAt = getField(rx, 'dispensed_at', 'Dispensed_At')
                const dosage = getField(rx, 'dosage', 'Dosage', 'Dosage_Instruction')
                
                return (
                  <option key={rxId} value={rxId}>
                    Rx #{rxId} - {patientName} - {drugName} {dosage ? `(${dosage})` : ''} - {formatDate(dispensedAt)}
                  </option>
                )
              })}
            </select>
            {prescriptionList.length === 0 && !loadingList && (
              <p style={{ color: '#666', marginTop: '0.5rem' }}>No prescriptions available.</p>
            )}
          </div>
        )}
      </div>

      {selectedPrescriptionId && (
        <div style={{ marginTop: '2rem', borderTop: '2px solid #ccc', paddingTop: '2rem' }}>
          <h3>Prescription Label & Receipt</h3>
          
          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          
          {prescriptionData && !loading && !error && (
            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', marginTop: '1rem' }}>
              <div>
                <h4 style={{ marginBottom: '1rem' }}>Label (Patient Copy)</h4>
                <PrescriptionLabel 
                  prescription={prescriptionData.prescription}
                  patient={prescriptionData.patient}
                  drug={prescriptionData.drug}
                  dispensedBy={prescriptionData.dispensed_by}
                />
              </div>
              
              <div>
                <h4 style={{ marginBottom: '1rem' }}>Receipt (Billing Copy)</h4>
                <PrescriptionReceipt 
                  prescription={prescriptionData.prescription}
                  patient={prescriptionData.patient}
                  drug={prescriptionData.drug}
                  visit={prescriptionData.visit}
                  dispensedBy={prescriptionData.dispensed_by}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
