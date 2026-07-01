import React, { useEffect, useState } from 'react'
import client from '../api/client'
import { Link } from 'react-router-dom'
import SentimentBadge from '../components/SentimentBadge'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [recent, setRecent] = useState([])

  useEffect(() => {
    client.get('/api/analytics/summary').then((r) => setSummary(r.data)).catch(() => {})
    client.get('/api/emails/threads').then((r) => setRecent(r.data.slice(0, 6))).catch(() => {})
  }, [])

  return (
    <div>
      <div className="page-title">Overview</div>
      <div className="page-sub">Everything at a glance — volume, escalations, and recent activity.</div>

      <div className="grid-stats">
        <div className="card">
          <div className="stat-label">Total emails</div>
          <div className="stat-value">{summary?.total_emails ?? '–'}</div>
        </div>
        <div className="card">
          <div className="stat-label">Auto-replied</div>
          <div className="stat-value">{summary?.auto_replied ?? '–'}</div>
        </div>
        <div className="card">
          <div className="stat-label">Escalated</div>
          <div className="stat-value">{summary?.escalated ?? '–'}</div>
        </div>
      </div>

      <div className="page-title" style={{ fontSize: '1.1rem' }}>Recent threads</div>
      <div className="thread-list" style={{ marginTop: 12 }}>
        {recent.map((t) => (
          <Link key={t.id} to={`/inbox/${t.id}`} className="thread-row">
            <div className="thread-main">
              <div className="thread-subject">{t.subject || '(no subject)'}</div>
              <div className="thread-from">{t.sender_email}</div>
            </div>
            <div className="thread-meta">
              <SentimentBadge sentiment={t.sentiment} />
              <span className="badge badge-status">{t.status}</span>
            </div>
          </Link>
        ))}
        {recent.length === 0 && <div className="card">No emails yet. Connect a Gmail inbox in Settings.</div>}
      </div>
    </div>
  )
}
