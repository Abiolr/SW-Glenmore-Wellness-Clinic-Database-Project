import React from 'react'
import { useParams } from 'react-router-dom'
import LaboratoryLog from '../../components/logs/LaboratoryLog'

export default function Laboratory() {
  const { visitId } = useParams<{ visitId: string }>()
  return (
    <div>
      <LaboratoryLog visitId={visitId ? Number(visitId) : undefined} />
    </div>
  )
}
