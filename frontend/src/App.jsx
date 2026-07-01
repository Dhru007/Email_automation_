import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Sidebar from './components/Sidebar'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Inbox from './pages/Inbox'
import EmailThread from './pages/EmailThread'
import KnowledgeBase from './pages/KnowledgeBase'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import AdminUsers from './pages/AdminUsers'

function Shell({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main">{children}</div>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedRoute><Shell><Dashboard /></Shell></ProtectedRoute>} />
      <Route path="/inbox" element={<ProtectedRoute><Shell><Inbox /></Shell></ProtectedRoute>} />
      <Route path="/inbox/:threadId" element={<ProtectedRoute><Shell><EmailThread /></Shell></ProtectedRoute>} />
      <Route path="/knowledge-base" element={<ProtectedRoute><Shell><KnowledgeBase /></Shell></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Shell><Analytics /></Shell></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Shell><Settings /></Shell></ProtectedRoute>} />
      <Route path="/admin/users" element={<ProtectedRoute adminOnly><Shell><AdminUsers /></Shell></ProtectedRoute>} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
