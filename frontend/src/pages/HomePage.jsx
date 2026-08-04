import { useState, useEffect } from 'react'
import { glStatus, uploadGl, healthCheck } from '../api'
import DropZone from '../components/DropZone'

function monthLabel(m) {
  if (!m) return ''
  const [y, mo] = m.split('-')
  return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
}

const MODULES = [
  { id: 'aprec',     name: 'AP Rec',     desc: 'Reconcile vendor statements against the GL', needsGl: false },
  { id: 'filenamer', name: 'File Namer', desc: 'Rename invoice PDFs from their content',      needsGl: false },
  { id: 'trends',    name: 'Expense Trends', desc: 'Vendor & credit-card expense analysis with flags', needsGl: true },
  { id: 'payroll',   name: 'Payroll',    desc: 'Month-end accrual calculator + payroll trends', needsGl: true },
]

export default function HomePage({ go }) {
  const [files, setFiles]     = useState([])
  const [stored, setStored]   = useState(null)   // {filename, uploaded_at, rows?, first_month?, last_month?, entities?}
  const [busy, setBusy]       = useState(false)
  const [error, setError]     = useState('')
  const [ephemeralDb, setEphemeralDb] = useState(false)
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    glStatus().then(s => {
      if (s.has_gl) setStored({ filename: s.filename, uploaded_at: s.uploaded_at })
      else setShowUpload(true)
    }).catch(() => setShowUpload(true))
    healthCheck().then(hc => {
      if ((hc.db || '').startsWith('sqlite')) setEphemeralDb(true)
    }).catch(() => {})
  }, [])

  async function doUpload() {
    if (!files[0]) return
    setBusy(true); setError('')
    try {
      const res = await uploadGl(files[0])
      setStored(res)
      setFiles([])
      setShowUpload(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1100, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>

      {ephemeralDb && (
        <div className="card" style={{ border: '1px solid var(--warn)',
                                       fontFamily: 'var(--mono)', fontSize: 12, lineHeight: 1.7 }}>
          <b style={{ color: 'var(--warn)' }}>⚠ TEMPORARY DATABASE — your data will NOT survive the next deploy.</b><br/>
          Accounts and uploaded GLs are being stored on the server's temporary disk.
          Fix (one time, ~1 min): Railway → AP_REC project → <b>+ New</b> → <b>Database</b> →
          <b> Add PostgreSQL</b>, then on the backend service → <b>Variables</b> →
          <b> + New Variable</b> → <b>Add Reference</b> → Postgres → <b>DATABASE_URL</b>.
          This banner disappears once it's connected.
        </div>
      )}

      {/* Module launcher — the main event */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 16 }}>
        {MODULES.map(m => {
          const locked = m.needsGl && !stored
          return (
            <button key={m.id} onClick={() => go(m.id)}
              className="card"
              style={{ textAlign: 'left', cursor: 'pointer', border: '1px solid var(--border)',
                       display: 'flex', flexDirection: 'column', gap: 8,
                       opacity: locked ? 0.55 : 1 }}>
              <span style={{ fontFamily: 'var(--mono)', fontWeight: 700, fontSize: 15, color: 'var(--ox)' }}>
                {m.name}
              </span>
              <span style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.5 }}>{m.desc}</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: locked ? 'var(--warn)' : 'var(--muted)',
                             marginTop: 'auto' }}>
                {locked ? 'upload a GL first' : 'open →'}
              </span>
            </button>
          )
        })}
      </div>

      {/* GL data status — compact bar; dropzone tucked behind "Replace GL" */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px 18px',
                      fontFamily: 'var(--mono)', fontSize: 12 }}>
          <span style={{ fontSize: 11, color: 'var(--ox)', letterSpacing: '0.1em',
                         textTransform: 'uppercase' }}>General Ledger</span>
          {stored ? (
            <>
              <span><b>{stored.filename}</b></span>
              {stored.uploaded_at && (
                <span style={{ color: 'var(--muted)' }}>
                  last updated {new Date(stored.uploaded_at).toLocaleString()}
                </span>
              )}
              {stored.rows != null && <span style={{ color: 'var(--muted)' }}>{stored.rows.toLocaleString()} rows</span>}
              {stored.first_month && <span style={{ color: 'var(--muted)' }}>{monthLabel(stored.first_month)} – {monthLabel(stored.last_month)}</span>}
              {stored.entities != null && <span style={{ color: 'var(--muted)' }}>{stored.entities} entities</span>}
            </>
          ) : (
            <span style={{ color: 'var(--warn)' }}>
              No GL on file — upload your Sage Intacct GL Detail export (CSV) to unlock Expense Trends and Payroll.
            </span>
          )}
          <span style={{ flex: 1 }} />
          <button className="btn btn-icon" onClick={() => setShowUpload(s => !s)}
                  style={{ padding: '3px 12px', fontSize: 10 }}>
            {showUpload ? 'Cancel' : stored ? 'Replace GL' : 'Upload GL'}
          </button>
        </div>

        {showUpload && (
          <div style={{ marginTop: 14 }}>
            <DropZone label={stored ? 'Drop a NEW GL CSV to replace the saved one' : 'Drop GL CSV here'}
                      accept={['csv']} files={files} onChange={setFiles} />
            <button className="btn btn-primary" disabled={!files.length || busy}
                    onClick={doUpload} style={{ marginTop: 12 }}>
              {busy ? 'Uploading…' : stored ? 'Replace GL →' : 'Upload GL →'}
            </button>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', marginTop: 8 }}>
              Note: attaching a GL inside AP Rec / Expense Trends / Payroll also updates the saved copy —
              "last updated" reflects the newest from any source.
            </div>
            {error && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 12, marginTop: 10 }}>{error}</div>}
          </div>
        )}
      </div>
    </div>
  )
}
