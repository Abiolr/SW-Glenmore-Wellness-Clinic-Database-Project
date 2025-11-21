import React from 'react'

interface Props {
  prescription: any
  patient: any
  drug: any
  dispensedBy: any
}

export default function PrescriptionLabel({ prescription, patient, drug, dispensedBy }: Props) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'N/A'
    try {
      return new Date(dateStr).toLocaleDateString()
    } catch {
      return dateStr
    }
  }

  // Helper to get field value with different casing variations
  const getField = (obj: any, ...keys: string[]) => {
    if (!obj) return null
    for (const key of keys) {
      if (obj[key] !== undefined && obj[key] !== null) return obj[key]
    }
    return null
  }

  const prescriptionId = getField(prescription, 'prescription_id', 'Prescription_Id')
  const dispensedAt = getField(prescription, 'dispensed_at', 'Dispensed_At')
  const nameOnLabel = getField(prescription, 'name_on_label', 'Name_On_Label')
  const patientFirstName = getField(patient, 'first_name', 'First_Name')
  const patientLastName = getField(patient, 'last_name', 'Last_Name')
  const patientDob = getField(patient, 'date_of_birth', 'Date_Of_Birth')
  const patientId = getField(patient, 'patient_id', 'Patient_Id')
  const drugBrandName = getField(drug, 'brand_name', 'Brand_Name')
  const drugGenericName = getField(drug, 'generic_name', 'Generic_Name')
  const drugStrengthForm = getField(drug, 'strength_form', 'Strength_Form')
  const dispensedByFirstName = getField(dispensedBy, 'first_name', 'First_Name')
  const dispensedByLastName = getField(dispensedBy, 'last_name', 'Last_Name')

  return (
    <div className="prescription-label" style={{
      border: '2px solid #333',
      padding: '1.5rem',
      maxWidth: '500px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#fff'
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1rem', fontSize: '1.2rem' }}>
        PRESCRIPTION LABEL
      </h2>
      
      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Patient Information</h3>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Name:</strong> {patientFirstName} {patientLastName}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>DOB:</strong> {formatDate(patientDob)}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Patient ID:</strong> {patientId}
        </p>
      </div>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Medication</h3>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Drug:</strong> {drugBrandName || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Generic Name:</strong> {drugGenericName || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Strength/Form:</strong> {drugStrengthForm || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Name on Label:</strong> {nameOnLabel || `${patientFirstName} ${patientLastName}`}
        </p>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Prescription Details</h3>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Rx Number:</strong> {prescriptionId}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Dispensed Date:</strong> {formatDate(dispensedAt)}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Dispensed By:</strong> {dispensedByFirstName && dispensedByLastName ? `${dispensedByFirstName} ${dispensedByLastName}` : 'N/A'}
        </p>
      </div>

      <div style={{ 
        marginTop: '1rem', 
        padding: '0.5rem', 
        backgroundColor: '#f0f0f0',
        fontSize: '0.85rem'
      }}>
        <p style={{ margin: 0, fontWeight: 'bold' }}>SW Glenmore Wellness Clinic</p>
        <p style={{ margin: 0 }}>Calgary, Alberta</p>
      </div>
    </div>
  )
}
