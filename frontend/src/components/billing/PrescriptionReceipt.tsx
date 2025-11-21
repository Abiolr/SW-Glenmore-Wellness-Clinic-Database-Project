import React from 'react'

interface Props {
  prescription: any
  patient: any
  drug: any
  visit: any
  dispensedBy: any
  insuranceInfo?: any
}

export default function PrescriptionReceipt({ 
  prescription, 
  patient, 
  drug, 
  visit, 
  dispensedBy,
  insuranceInfo 
}: Props) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'N/A'
    try {
      return new Date(dateStr).toLocaleDateString()
    } catch {
      return dateStr
    }
  }

  const formatCurrency = (amount: number | null | undefined) => {
    if (amount == null) return '$0.00'
    return `$${Number(amount).toFixed(2)}`
  }

  // Helper to get field value with different casing variations
  const getField = (obj: any, ...keys: string[]) => {
    if (!obj) return null
    for (const key of keys) {
      if (obj[key] !== undefined && obj[key] !== null) return obj[key]
    }
    return null
  }

  // Extract all fields with case tolerance
  const prescriptionId = getField(prescription, 'prescription_id', 'Prescription_Id')
  const dispensedAt = getField(prescription, 'dispensed_at', 'Dispensed_At')
  const dosage = getField(prescription, 'dosage', 'Dosage', 'Dosage_Instruction')
  const duration = getField(prescription, 'duration', 'Duration')
  const instructions = getField(prescription, 'instructions', 'Instructions', 'Dosage_Instruction')
  const price = getField(prescription, 'price', 'Price')
  
  const patientFirstName = getField(patient, 'first_name', 'First_Name')
  const patientLastName = getField(patient, 'last_name', 'Last_Name')
  const patientInsuranceNo = getField(patient, 'insurance_no', 'Insurance_No')
  
  const drugBrandName = getField(drug, 'brand_name', 'Brand_Name')
  const drugGenericName = getField(drug, 'generic_name', 'Generic_Name')
  const drugStrengthForm = getField(drug, 'strength_form', 'Strength_Form')
  
  const dispensedByFirstName = getField(dispensedBy, 'first_name', 'First_Name')
  const dispensedByLastName = getField(dispensedBy, 'last_name', 'Last_Name')

  // Calculate pricing breakdown
  const totalPrice = price || 0
  const insuranceCoverage = insuranceInfo?.coverage_percentage || 0
  const insuranceAmount = (totalPrice * insuranceCoverage) / 100
  const patientResponsibility = totalPrice - insuranceAmount

  return (
    <div className="prescription-receipt" style={{
      border: '2px solid #333',
      padding: '1.5rem',
      maxWidth: '600px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#fff'
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1rem', fontSize: '1.2rem' }}>
        PRESCRIPTION RECEIPT
      </h2>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Receipt Date:</strong> {formatDate(dispensedAt || new Date().toISOString())}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Rx Number:</strong> {prescriptionId}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Patient:</strong> {patientFirstName} {patientLastName}
        </p>
      </div>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Drug Information</h3>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Medication:</strong> {drugBrandName || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Generic:</strong> {drugGenericName || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Strength/Form:</strong> {drugStrengthForm || 'N/A'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Dosage:</strong> {dosage || 'As prescribed'}
        </p>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Duration:</strong> {duration || 'As prescribed'}
        </p>
      </div>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Usage Instructions</h3>
        <p style={{ margin: '0.25rem 0', fontStyle: 'italic' }}>
          {instructions || 'Take as directed by your physician.'}
        </p>
        <p style={{ margin: '0.5rem 0', fontSize: '0.85rem', color: '#666' }}>
          <strong>Note:</strong> Complete the full course of medication unless otherwise directed.
        </p>
      </div>

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Pricing & Payment</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <tbody>
            <tr>
              <td style={{ padding: '0.25rem 0' }}>Prescription Total:</td>
              <td style={{ textAlign: 'right', padding: '0.25rem 0' }}>{formatCurrency(totalPrice)}</td>
            </tr>
            {insuranceCoverage > 0 && (
              <>
                <tr>
                  <td style={{ padding: '0.25rem 0' }}>
                    Insurance Coverage ({insuranceCoverage}%):
                  </td>
                  <td style={{ textAlign: 'right', padding: '0.25rem 0' }}>
                    -{formatCurrency(insuranceAmount)}
                  </td>
                </tr>
                <tr style={{ borderTop: '1px solid #ccc', fontWeight: 'bold' }}>
                  <td style={{ padding: '0.5rem 0' }}>Patient Responsibility:</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem 0' }}>
                    {formatCurrency(patientResponsibility)}
                  </td>
                </tr>
              </>
            )}
          </tbody>
        </table>
      </div>

      {insuranceInfo && (
        <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Insurance Information</h3>
          <p style={{ margin: '0.25rem 0' }}>
            <strong>Provider:</strong> {insuranceInfo?.provider || patientInsuranceNo || 'N/A'}
          </p>
          <p style={{ margin: '0.25rem 0' }}>
            <strong>Policy Number:</strong> {insuranceInfo?.policy_number || patientInsuranceNo || 'N/A'}
          </p>
        </div>
      )}

      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Dispensed By</h3>
        <p style={{ margin: '0.25rem 0' }}>
          <strong>Pharmacist:</strong> {dispensedByFirstName && dispensedByLastName ? `${dispensedByFirstName} ${dispensedByLastName}` : 'N/A'}
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
        <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.75rem', color: '#666' }}>
          For questions, please contact your healthcare provider.
        </p>
      </div>

      <div style={{ 
        marginTop: '1rem', 
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#666'
      }}>
        <button 
          onClick={() => window.print()} 
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#4285f4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Print Receipt
        </button>
      </div>
    </div>
  )
}
