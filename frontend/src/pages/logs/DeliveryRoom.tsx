import React from 'react'
import { useParams } from 'react-router-dom'
import DeliveryRoomLog from '../../components/logs/DeliveryRoomLog'

export default function DeliveryRoom() {
  const { visitId } = useParams<{ visitId: string }>()
  return (
    <div>
      <DeliveryRoomLog visitId={visitId ? Number(visitId) : undefined} />
    </div>
  )
}
