import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const LINKS = [
  { to: '/', label: '📊  Overview', exact: true },
  { to: '/inbox', label: '📥  Inbox' },
  { to: '/knowledge-base', label: '📚  Knowledge Base' },
  { to: '/analytics', label: '📈  Analytics' },
  { to: '/settings', label: '⚙️  Settings' },
]

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  return (
    <nav className="sidebar">
      <div className="brand">Beast<span>Desk</span></div>
      {LINKS.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.exact}
          className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
        >
          {l.label}
        </NavLink>
      ))}
      {isAdmin && (
        <NavLink to="/admin/users" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
          🛡️  Admin · Team
        </NavLink>
      )}
      <div style={{ marginTop: 'auto', paddingTop: 20 }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', padding: '0 8px 8px' }}>
          {user?.email} {isAdmin && '· admin'}
        </div>
        <button className="btn-ghost" style={{ width: '100%' }} onClick={() => { logout(); navigate('/login') }}>
          Log out
        </button>
      </div>
    </nav>
  )
}
