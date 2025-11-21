import React from 'react'
import { useParams } from 'react-router-dom'
import RecoveryRoomLog from '../../components/logs/RecoveryRoomLog'

export default function RecoveryRoom() {
  const { stayId } = useParams<{ stayId: string }>()
  return (
    <div>
      <RecoveryRoomLog stayId={stayId ? Number(stayId) : undefined} />
    </div>
  )
}
