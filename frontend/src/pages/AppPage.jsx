import { useState } from 'react'
import { reconcile, downloadFile, logout } from '../api'
import DropZone from '../components/DropZone'
import AnimatedLogo from '../components/AnimatedLogo'

export default function AppPage({ onLogout }) {
  const [glFiles, setGlFiles] = useState([])
  const [stmtFiles, setStmtFiles] = useState([])
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState([])
  const [jobId, setJobId] = useState(null)
  const [error, setError] = useState('')

  async function handleRun() {
    if (!glFiles[0] || !stmtFiles.length) return
    setRunning(true)
    setLogs([])
    setJobId(null)
    setError('')
    try {
      const result = await reconcile(glFiles[0], stmtFiles, msg => {
        setLogs(prev => [...prev, msg])
      })
      setJobId(result.job_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const ready = glFiles.length > 0 && stmtFiles.length > 0 && !running

  return (
    <div style={{
      minHeight: '100vh',
      maxWidth: 680,
      margin: '0 auto',
      padding: '48px 24px 80px',
      display: 'flex',
      flexDirection: 'column',
      gap: 32,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <AnimatedLogo width={160} />
          <div>
            <h1 style={{ fontSize: 20 }}>AP Reconciliation</h1>
            <p style={{ color: 'var(--muted)', fontSize: 12, fontFamily: 'var(--mono)' }}>
              vendor statement processor
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="badge">Authenticated</span>
          <button className="btn btn-icon" onClick={() => { logout(); onLogout() }}>
            Sign out
          </button>
        </div>
      </div>

      {/* GL Upload */}
      <div className="card">
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>
            01 — GL Export
          </div>
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>
            Upload your general ledger CSV export
          </p>
        </div>
        <DropZone
          label="Drop GL CSV here"
          accept={['csv']}
          files={glFiles}
          onChange={setGlFiles}
        />
      </div>

      {/* Statements Upload */}
      <div className="card">
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>
            02 — Vendor Statements
          </div>
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>
            Upload one or more vendor statement PDFs or Excel files
          </p>
        </div>
        <DropZone
          label="Drop vendor statements here"
          accept={['pdf', 'xlsx']}
          multiple
          files={stmtFiles}
          onChange={setStmtFiles}
        />
      </div>

      {/* Run */}
      <button
        className="btn btn-primary"
        onClick={handleRun}
        disabled={!ready}
        style={{ fontSize: 15, padding: '16px 24px' }}
      >
        {running ? 'Processing…' : 'Run Reconciliation →'}
      </button>

      {/* Progress / Logs */}
      {(running || logs.length > 0) && (
        <div className="card" style={{ gap: 12, display: 'flex', flexDirection: 'column' }}>
          {running && (
            <div className="progress-bar">
              <div className="progress-bar-fill" style={{ width: '60%', animation: 'pulse 1.5s ease-in-out infinite' }} />
            </div>
          )}
          <div className="log">
            {logs.map((l, i) => {
              const cls = l.includes('✓') || l.includes('matched') ? 'log-ok'
                        : l.includes('skip') || l.includes('SKIP') ? 'log-skip'
                        : l.includes('error') || l.includes('Error') ? 'log-err'
                        : ''
              return <div key={i} className={cls}>{l}</div>
            })}
            {running && <div style={{ opacity: 0.5 }}>▋</div>}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(248,113,113,0.08)',
          border: '1px solid rgba(248,113,113,0.3)',
          borderRadius: 4,
          padding: '16px 20px',
          color: '#F87171',
          fontFamily: 'var(--mono)',
          fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {/* Download */}
      {jobId && (
        <div style={{
          background: 'rgba(255,112,48,0.06)',
          border: '1px solid var(--ox-b)',
          borderRadius: 4,
          padding: '20px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          flexWrap: 'wrap',
        }}>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Reconciliation complete</div>
            <div style={{ color: 'var(--muted)', fontSize: 13 }}>
              {stmtFiles.length} statement{stmtFiles.length !== 1 ? 's' : ''} processed
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => downloadFile(jobId)}
            style={{ width: 'auto', padding: '10px 28px' }}
          >
            Download XLSX ↓
          </button>
        </div>
      )}
    </div>
  )
}
