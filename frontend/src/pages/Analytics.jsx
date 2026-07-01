import React, { useEffect, useState } from 'react'
import client from '../api/client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#5EE6C0', '#F4B860', '#FF6B6B', '#8FA1B3', '#7AA2F7', '#C792EA', '#FFB4A2', '#9AA1AC']

export default function Analytics() {
  const [summary, setSummary] = useState(null)
  const [reasons, setReasons] = useState([])

  useEffect(() => {
    client.get('/api/analytics/summary').then((r) => setSummary(r.data))
    client.get('/api/analytics/top-escalation-reasons').then((r) => setReasons(r.data))
  }, [])

  if (!summary) return <div className="page-title">Loading…</div>

  const categoryData = Object.entries(summary.category_breakdown).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="page-title">Analytics</div>
      <div className="page-sub">Volume, category breakdown, and top escalation reasons.</div>

      <div className="grid-stats">
        <div className="card"><div className="stat-label">Total</div><div className="stat-value">{summary.total_emails}</div></div>
        <div className="card"><div className="stat-label">Auto-replied</div><div className="stat-value">{summary.auto_replied}</div></div>
        <div className="card"><div className="stat-label">Escalated</div><div className="stat-value">{summary.escalated}</div></div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card" style={{ height: 320 }}>
          <div className="page-sub">Category breakdown</div>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie data={categoryData} dataKey="value" nameKey="name" outerRadius={90} label>
                {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card" style={{ height: 320 }}>
          <div className="page-sub">Top escalation reasons</div>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={reasons}>
              <XAxis dataKey="reason" stroke="#9AA1AC" fontSize={11} />
              <YAxis stroke="#9AA1AC" fontSize={11} />
              <Tooltip />
              <Bar dataKey="count" fill="#5EE6C0" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
