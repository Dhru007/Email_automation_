import React, { useEffect, useState } from 'react'
import client, { API_BASE_URL } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Settings() {
  const { isAdmin } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [rules, setRules] = useState([])
  const [newRule, setNewRule] = useState({ name: '', category: '', confidence_threshold: 0.7 })

  function load() {
    client.get('/api/gmail/accounts').then((r) => setAccounts(r.data))
    client.get('/api/settings/escalation-rules').then((r) => setRules(r.data))
  }
  useEffect(load, [])

  async function connectGmail() {
    const res = await client.get('/api/gmail/oauth/start')
    window.location.href = res.data.auth_url
  }

  async function removeAccount(id) {
    await client.delete(`/api/gmail/accounts/${id}`)
    load()
  }

  async function addRule(e) {
    e.preventDefault()
    await client.post('/api/settings/escalation-rules', {
      ...newRule,
      category: newRule.category || null,
      confidence_threshold: parseFloat(newRule.confidence_threshold),
    })
    setNewRule({ name: '', category: '', confidence_threshold: 0.7 })
    load()
  }

  async function removeRule(id) {
    await client.delete(`/api/settings/escalation-rules/${id}`)
    load()
  }

  return (
    <div>
      <div className="page-title">Settings</div>
      <div className="page-sub">Connect Gmail accounts and manage escalation rules.</div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="page-sub">Connected Gmail accounts</div>
        {accounts.map((a) => (
          <div key={a.id} className="thread-row" style={{ cursor: 'default', marginBottom: 8 }}>
            <div>{a.email_address}</div>
            {isAdmin && <button className="btn-ghost" onClick={() => removeAccount(a.id)}>Disconnect</button>}
          </div>
        ))}
        {isAdmin && <button className="btn-primary" onClick={connectGmail}>+ Connect Gmail account</button>}
        {!isAdmin && <div className="page-sub">Only admins can connect/disconnect Gmail accounts.</div>}
      </div>

      <div className="card">
        <div className="page-sub">Escalation rules</div>
        {rules.map((r) => (
          <div key={r.id} className="thread-row" style={{ cursor: 'default', marginBottom: 8 }}>
            <div>{r.name} — {r.category || 'any category'} · confidence &lt; {r.confidence_threshold}</div>
            {isAdmin && <button className="btn-ghost" onClick={() => removeRule(r.id)}>Remove</button>}
          </div>
        ))}
        {isAdmin && (
          <form onSubmit={addRule} style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
            <input placeholder="Rule name" value={newRule.name}
                   onChange={(e) => setNewRule({ ...newRule, name: e.target.value })} required />
            <input placeholder="Category (optional)" value={newRule.category}
                   onChange={(e) => setNewRule({ ...newRule, category: e.target.value })} />
            <input type="number" step="0.05" min="0" max="1" value={newRule.confidence_threshold}
                   onChange={(e) => setNewRule({ ...newRule, confidence_threshold: e.target.value })} />
            <button className="btn-primary" type="submit">Add rule</button>
          </form>
        )}
      </div>

      <div className="page-sub" style={{ marginTop: 16 }}>API base: {API_BASE_URL}</div>
    </div>
  )
}
