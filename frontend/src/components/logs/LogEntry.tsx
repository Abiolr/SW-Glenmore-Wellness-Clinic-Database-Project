import React from 'react'

interface Props {
  label: string
  value: string | number
}

export default function LogEntry({ label, value }: Props) {
  return (
    <tr>
      <td style={{ fontWeight: 'bold' }}>{label}</td>
      <td>{value}</td>
    </tr>
  )
}
