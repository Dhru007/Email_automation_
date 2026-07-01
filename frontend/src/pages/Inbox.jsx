import React, { useEffect, useState } from 'react'
import client from '../api/client'
import { Link } from 'react-router-dom'
import SentimentBadge from '../components/SentimentBadge'

const CATEGORIES = ['legal', 'product_issue', 'delivery_issue', 'return_refund', 'billing', 'general_enquiry', 'feedback_praise', 'spam']
const SENTIMENTS = ['angry', 'frustrated', 'sad', 'neutral', 'happy']
const STATUSES = ['open', 'replied', 'escalated', 'auto_replied']

export default function Inbox() {
  const [threads, setThreads] = useState([])
  const [filters, setFilters] = useState({ category: '', sentiment: '', status: '' })

  useEffect(() => {
    const params = {}
    Object.entries(filters).forEach(([k, v]) => { if (v) params[k] = v })
    client.get('/api/emails/threads', { params }).then((r) => setThreads(r.data)).catch(() => {})
  }, [filters])

  return (
    <div>
      <div className="page-title">Inbox</div>
      <div className="page-sub">Filter by category, sentiment, or status.</div>

      <div className="filters">
        <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
          <option value="">All categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
        </select>
        <select value={filters.sentiment} onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}>
          <option value="">All sentiment</option>
          {SENTIMENTS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
      </div>

      <div className="thread-list">
        {threads.map((t) => (
          <Link key={t.id} to={`/inbox/${t.id}`} className="thread-row">
            <div className="thread-main">
              <div className="thread-subject">{t.subject || '(no subject)'}</div>
              <div className="thread-from">{t.sender_email} {t.is_vip && '· VIP'}</div>
            </div>
            <div className="thread-meta">
              {t.category && <span className="badge badge-status">{t.category.replace('_', ' ')}</span>}
              <SentimentBadge sentiment={t.sentiment} />
              <span className="badge badge-status">{t.status}</span>
            </div>
          </Link>
        ))}
        {threads.length === 0 && <div className="card">No emails match these filters.</div>}
      </div>
    </div>
  )
}
