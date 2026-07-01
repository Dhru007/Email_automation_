import React, { useEffect, useState } from 'react'
import client from '../api/client'

export default function KnowledgeBase() {
  const [articles, setArticles] = useState([])
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [file, setFile] = useState(null)
  const [previewQuery, setPreviewQuery] = useState('')
  const [previewResults, setPreviewResults] = useState([])

  function load() {
    client.get('/api/kb/articles').then((r) => setArticles(r.data))
  }
  useEffect(load, [])

  async function addManual(e) {
    e.preventDefault()
    await client.post('/api/kb/articles/manual', {
      title, raw_text: text, category_tags: tags.split(',').map((t) => t.trim()).filter(Boolean),
    })
    setTitle(''); setText(''); setTags('')
    load()
  }

  async function uploadFile(e) {
    e.preventDefault()
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    form.append('category_tags', tags)
    await client.post('/api/kb/articles/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    setFile(null)
    load()
  }

  async function removeArticle(id) {
    await client.delete(`/api/kb/articles/${id}`)
    load()
  }

  async function runPreview() {
    const res = await client.post('/api/kb/preview', { query: previewQuery, top_k: 5 })
    setPreviewResults(res.data)
  }

  return (
    <div>
      <div className="page-title">Knowledge Base</div>
      <div className="page-sub">Upload FAQs, policies, and product docs. Articles are chunked and embedded for RAG retrieval.</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <form className="card" onSubmit={addManual}>
          <div className="field"><label>Title</label><input value={title} onChange={(e) => setTitle(e.target.value)} required /></div>
          <div className="field"><label>Content</label><textarea rows={5} value={text} onChange={(e) => setText(e.target.value)} required /></div>
          <div className="field"><label>Tags (comma separated)</label><input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="protein, returns" /></div>
          <button className="btn-primary" type="submit">Add article</button>
        </form>

        <form className="card" onSubmit={uploadFile}>
          <div className="field"><label>Upload PDF / DOCX / TXT</label>
            <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0])} />
          </div>
          <div className="field"><label>Tags (comma separated)</label><input value={tags} onChange={(e) => setTags(e.target.value)} /></div>
          <button className="btn-primary" type="submit">Upload</button>
        </form>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="page-sub" style={{ marginBottom: 8 }}>Preview retrieval — see which chunks would be used for a sample email</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input style={{ flex: 1 }} value={previewQuery} onChange={(e) => setPreviewQuery(e.target.value)} placeholder="e.g. my protein has lumps" />
          <button className="btn-ghost" onClick={runPreview}>Preview</button>
        </div>
        {previewResults.map((r, i) => (
          <div key={i} className="kb-chunk">[{r.metadata?.title}] {r.text.slice(0, 160)}…</div>
        ))}
      </div>

      <div className="thread-list">
        {articles.map((a) => (
          <div key={a.id} className="thread-row" style={{ cursor: 'default' }}>
            <div className="thread-main">
              <div className="thread-subject">{a.title}</div>
              <div className="thread-from">{a.source_type} · {a.chunk_count} chunks · {a.category_tags.join(', ')}</div>
            </div>
            <button className="btn-ghost" onClick={() => removeArticle(a.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  )
}
