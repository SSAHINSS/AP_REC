import { useState, useEffect } from 'react'
import { reconcile, downloadFile, logout } from '../api'
import DropZone from '../components/DropZone'
import AnimatedLogo from '../components/AnimatedLogo'
import PixelProgressBar from '../components/PixelProgressBar'

export default function AppPage({ onLogout }) {
  const [glFiles, setGlFiles]       = useState([])
  const [stmtFiles, setStmtFiles]   = useState([])
  const [running, setRunning]       = useState(false)
  const [logs, setLogs]             = useState([])
  const [jobId, setJobId]           = useState(null)
  const [error, setError]           = useState('')
  const [scrollY, setScrollY]       = useState(0)

  // Track scroll for sticky header animation
  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // p: 0 = top of page, 1 = logo fully centered (after 160px scroll)
  const p = Math.min(scrollY / 160, 1)

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
      padding: '0 24px 80px',
      display: 'flex',
      flexDirection: 'column',
      gap: 0,
    }}>

      {/* ── Sticky Header ── */}
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'var(--bg)',
        borderBottom: `1px solid rgba(255,255,255,${p * 0.08})`,
        padding: '14px 0',
        marginBottom: 32,
      }}>
        <div style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          height: 56,
        }}>

          {/* Logo group — slides left→center as p goes 0→1 */}
          <div style={{
            position: 'absolute',
            left: `${p * 50}%`,
            transform: `translateX(${p * -50}%)`,
            display: 'flex',
            alignItems: 'center',
            gap: 14,
          }}>
            <AnimatedLogo width={Math.round(160 - p * 60)} />

            {/* Title fades out as logo centers */}
            <div style={{
              opacity: Math.max(0, 1 - p * 2.2),
              pointerEvents: 'none',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
            }}>
              <h1 style={{ fontSize: 20 }}>AP Reconciliation</h1>
              <p style={{ color: 'var(--muted)', fontSize: 12, fontFamily: 'var(--mono)' }}>
                vendor statement processor
              </p>
            </div>
          </div>

          {/* Auth controls — always right */}
          <div style={{
            marginLeft: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            opacity: Math.max(0.3, 1 - p * 0.4),
          }}>
            <span className="badge">Authenticated</span>
            <button className="btn btn-icon" onClick={() => { logout(); onLogout() }}>
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* ── Content ── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

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

        {/* Run button */}
        <button
          className="btn btn-primary"
          onClick={handleRun}
          disabled={!ready}
          style={{ fontSize: 15, padding: '16px 24px' }}
        >
          {running ? 'Processing…' : 'Run Reconciliation →'}
        </button>

        {/* ── Progress / Logs ── */}
        {running && (
          <PixelProgressBar running={running} />
        )}

        {!running && logs.length > 0 && (
          <div className="card" style={{ gap: 0, display: 'flex', flexDirection: 'column' }}>
            <div className="log">
              {logs.map((l, i) => {
                const cls = l.includes('✓') || l.includes('matched') ? 'log-ok'
                          : l.includes('skip') || l.includes('SKIP')  ? 'log-skip'
                          : l.includes('error') || l.includes('Error') ? 'log-err'
                          : ''
                return <div key={i} className={cls}>{l}</div>
              })}
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
    </div>
  )
}
