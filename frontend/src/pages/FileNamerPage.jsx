import { useState, useRef } from 'react'
import FileNamerLogo from '../components/FileNamerLogo'
import DropZone from '../components/DropZone'
import { logout } from '../api'

const BASE = import.meta.env.VITE_API_URL || '/api'
function getToken() { return localStorage.getItem('ap_token') }

async function proposeRenames(files) {
  const form = new FormData()
  for (const f of files) form.append('files', f)
  const res = await fetch(`${BASE}/rename/propose`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Failed to propose renames')
  }
  return res.json()
}

async function downloadZip(jobId, renameMap) {
  const res = await fetch(`${BASE}/rename/download/${jobId}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rename_map: renameMap }),
  })
  if (!res.ok) throw new Error('Download failed')
  const blob = await res.blob()
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = 'renamed_files.zip'
  a.click()
  URL.revokeObjectURL(url)
}

export default function FileNamerPage({ onLogout }) {
  const [files,     setFiles]     = useState([])
  const [running,   setRunning]   = useState(false)
  const [proposals, setProposals] = useState([])  // [{original, entity, vendor, date, proposed, note, multi}]
  const [edits,     setEdits]     = useState({})   // { index: { entity, vendor, date } }
  const [jobId,     setJobId]     = useState(null)
  const [error,     setError]     = useState('')
  const [logs,      setLogs]      = useState([])
  const resultsRef = useRef(null)

  function updateEdit(i, field, value) {
    setEdits(prev => ({ ...prev, [i]: { ...prev[i], [field]: value } }))
  }

  function getRow(i) {
    const p = proposals[i]
    const e = edits[i] || {}
    return {
      entity: e.entity ?? p.entity,
      vendor: e.vendor ?? p.vendor,
      date:   e.date   ?? p.date,
    }
  }

  function buildProposed(i) {
    const ext = proposals[i].proposed.match(/\.\w+$/)?.[0] || ''
    const { entity, vendor, date } = getRow(i)
    return `${entity}_${vendor}_${date}${ext}`.replace(/\s+/g,'_')
  }

  async function handlePropose() {
    if (!files.length) return
    setRunning(true); setError(''); setProposals([]); setEdits({}); setJobId(null); setLogs([])
    try {
      const data = await proposeRenames(files)
      setProposals(data.proposals)
      setJobId(data.job_id)
      setLogs(data.logs || [])
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150)
    } catch(e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  async function handleDownload() {
    if (!jobId) return
    const renameMap = {}
    proposals.forEach((p, i) => { renameMap[p.original] = buildProposed(i) })
    try {
      await downloadZip(jobId, renameMap)
    } catch(e) {
      setError(e.message)
    }
  }

  return (
    <div style={{ minHeight: '100vh', maxWidth: 680, margin: '0 auto', padding: '32px 24px 80px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 36 }}>
        <FileNamerLogo width={260} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="badge">Authenticated</span>
          <button className="btn btn-icon" onClick={() => { logout(); onLogout() }}
            style={{ padding: '2px 10px', fontSize: 10 }}>
            Sign out
          </button>
        </div>
      </div>

      {/* Upload */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>
            01 — Upload Files
          </div>
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>
            Drop vendor statement PDFs or Excel files to rename
          </p>
        </div>
        <DropZone label="Drop files here" accept={['pdf','xlsx']} multiple files={files} onChange={setFiles} />
      </div>

      {/* Analyse button */}
      <button
        className="btn btn-primary"
        onClick={handlePropose}
        disabled={!files.length || running}
        style={{ fontSize: 15, padding: '16px 24px', marginBottom: 24 }}
      >
        {running ? 'Analysing…' : 'Analyse Files'}
      </button>

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.3)',
          borderRadius: 4, padding: '16px 20px', color: '#F87171',
          fontFamily: 'var(--mono)', fontSize: 13, marginBottom: 24,
        }}>
          {error}
        </div>
      )}

      {/* Results */}
      {proposals.length > 0 && (
        <div ref={resultsRef} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>
            02 — Review & Edit Names
          </div>

          {proposals.map((p, i) => {
            const row = getRow(i)
            const finalName = buildProposed(i)
            return (
              <div key={i} className="card" style={{
                borderColor: p.multi ? 'rgba(252,211,77,0.3)' : 'var(--border)',
                padding: '16px 20px',
              }}>
                {/* Original filename + multi badge */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
                    {p.original}
                  </span>
                  {p.multi && (
                    <span style={{
                      fontFamily: 'var(--mono)', fontSize: 9, color: '#FCD34D',
                      background: 'rgba(252,211,77,0.1)', border: '1px solid rgba(252,211,77,0.3)',
                      borderRadius: 2, padding: '1px 6px', letterSpacing: '0.1em', textTransform: 'uppercase',
                    }}>
                      Multi-entity split
                    </span>
                  )}
                  {p.note && (
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--muted)' }}>
                      {p.note}
                    </span>
                  )}
                </div>

                {/* Editable fields */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 8, marginBottom: 12 }}>
                  <div>
                    <div style={{ fontSize: 9, fontFamily: 'var(--mono)', color: 'var(--muted)', marginBottom: 4, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Entity</div>
                    <input
                      value={row.entity}
                      onChange={e => updateEdit(i, 'entity', e.target.value)}
                      style={{
                        width: '100%', background: 'var(--bg)', border: '1px solid var(--border)',
                        borderRadius: 2, color: 'var(--text)', fontFamily: 'var(--mono)',
                        fontSize: 12, padding: '6px 10px',
                      }}
                    />
                  </div>
                  <div>
                    <div style={{ fontSize: 9, fontFamily: 'var(--mono)', color: 'var(--muted)', marginBottom: 4, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Vendor</div>
                    <input
                      value={row.vendor}
                      onChange={e => updateEdit(i, 'vendor', e.target.value)}
                      style={{
                        width: '100%', background: 'var(--bg)', border: '1px solid var(--border)',
                        borderRadius: 2, color: 'var(--text)', fontFamily: 'var(--mono)',
                        fontSize: 12, padding: '6px 10px',
                      }}
                    />
                  </div>
                  <div>
                    <div style={{ fontSize: 9, fontFamily: 'var(--mono)', color: 'var(--muted)', marginBottom: 4, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Date</div>
                    <input
                      value={row.date}
                      onChange={e => updateEdit(i, 'date', e.target.value)}
                      style={{
                        width: 80, background: 'var(--bg)', border: '1px solid var(--border)',
                        borderRadius: 2, color: 'var(--text)', fontFamily: 'var(--mono)',
                        fontSize: 12, padding: '6px 10px',
                      }}
                    />
                  </div>
                </div>

                {/* Preview */}
                <div style={{
                  fontFamily: 'var(--mono)', fontSize: 12,
                  color: 'var(--ox)', background: 'rgba(255,112,48,0.06)',
                  border: '1px solid var(--ox-b)', borderRadius: 2,
                  padding: '6px 10px',
                }}>
                  → {finalName}
                </div>
              </div>
            )
          })}

          {/* Download zip */}
          <button
            className="btn btn-primary"
            onClick={handleDownload}
            style={{ fontSize: 15, padding: '16px 24px', marginTop: 8 }}
          >
            Download Renamed Files (ZIP)
          </button>

        </div>
      )}
    </div>
  )
}
