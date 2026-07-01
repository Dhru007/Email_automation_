import React from 'react'

const EMOJI = { angry: '😡', frustrated: '😤', sad: '😢', neutral: '😐', happy: '😊' }

export default function SentimentBadge({ sentiment }) {
  if (!sentiment) return null
  return (
    <span className={`badge badge-${sentiment}`}>
      {EMOJI[sentiment] || ''} {sentiment}
    </span>
  )
}
