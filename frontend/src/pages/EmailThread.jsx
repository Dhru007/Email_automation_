import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import client from '../api/client'
import SentimentBadge from '../components/SentimentBadge'

export default function EmailThread() {
  const { threadId } = useParams()
  const [thread, setThread] = useState(null)
  const [drafts, setDrafts] = useState({})

  function load() {
    client.get(`/api/emails/threads/${threadId}`).then((r) => setThread(r.data))
  }

  useEffect(() => { load() }, [threadId])

  async function approveSend(messageId) {
    await client.post('/api/emails/approve-send', {
      message_id: messageId,
      edited_body: drafts[messageId],
    })
    load()
  }

  if (!thread) return <div className="page-title">Loading…</div>

  return (
    <div>
      <div className="page-title">{thread.subject || '(no subject)'}</div>
      <div className="page-sub">
        {thread.sender_email} {thread.is_vip && '· VIP'} · {thread.contact_count} contact(s)
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {thread.category && <span className="badge badge-status">{thread.category.replace('_', ' ')}</span>}
        <SentimentBadge sentiment={thread.sentiment} />
        <span className="badge badge-status">{thread.status}</span>
        {thread.ai_confidence != null && (
          <span className="badge badge-status">confidence {(thread.ai_confidence * 100).toFixed(0)}%</span>
        )}
      </div>

      {thread.messages.map((m) => (
        <div key={m.id} className={`message-bubble ${m.direction}`}>
          <div className="message-meta">
            {m.direction === 'inbound' ? 'Customer' : 'AI Draft'} · {new Date(m.created_at).toLocaleString()}
          </div>
          {m.direction === 'inbound' ? (
            <div>{m.body}</div>
          ) : (
            <div className="draft-box">
              <textarea
                defaultValue={m.ai_draft || ''}
                onChange={(e) => setDrafts({ ...drafts, [m.id]: e.target.value })}
              />
              {!m.is_approved ? (
                <div style={{ marginTop: 8 }}>
                  <button className="btn-primary" onClick={() => approveSend(m.id)}>Approve & Send</button>
                </div>
              ) : (
                <span className="badge badge-happy" style={{ marginTop: 8 }}>Sent</span>
              )}
              {m.kb_chunks_used?.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  <div className="message-meta">KB chunks used</div>
                  {m.kb_chunks_used.map((c, i) => (
                    <div key={i} className="kb-chunk">{(c.text || '').slice(0, 140)}…</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
