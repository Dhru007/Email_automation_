import React, { useEffect, useState } from 'react'
import client from '../api/client'

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ email: '', password: '', name: '', role: 'agent' })

  function load() {
    client.get('/api/auth/users').then((r) => setUsers(r.data))
  }
  useEffect(load, [])

  async function addUser(e) {
    e.preventDefault()
    await client.post('/api/auth/users', form)
    setForm({ email: '', password: '', name: '', role: 'agent' })
    load()
  }

  async function removeUser(id) {
    await client.delete(`/api/auth/users/${id}`)
    load()
  }

  return (
    <div>
      <div className="page-title">Admin · Team</div>
      <div className="page-sub">Manage who has access to the inbox.</div>

      <div className="card" style={{ marginBottom: 20 }}>
        {users.map((u) => (
          <div key={u.id} className="thread-row" style={{ cursor: 'default', marginBottom: 8 }}>
            <div>{u.name || u.email} <span className="badge badge-status">{u.role}</span></div>
            <button className="btn-ghost" onClick={() => removeUser(u.id)}>Remove</button>
          </div>
        ))}
      </div>

      <form className="card" onSubmit={addUser} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input placeholder="Email" type="email" value={form.email} required
               onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Temp password" type="password" value={form.password} required
               onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="agent">Agent</option>
          <option value="admin">Admin</option>
        </select>
        <button className="btn-primary" type="submit">Add team member</button>
      </form>
    </div>
  )
}
