import { useState, useEffect, useRef } from 'react'
import { reconcile, downloadFile, logout } from '../api'
import DropZone from '../components/DropZone'
import AnimatedLogo from '../components/AnimatedLogo'

const WORD = 'PROCESSING'
const CENTER = (WORD.length - 1) / 2

function SlinkyText() {
  const [t, setT] = useState(0)
  const rafRef = useRef(null)
  const lastRef = useRef(null)

  useEffect(() => {
    function frame(now) {
      if (lastRef.current !== null) {
        const dt = (now - lastRef.current) / 1000
        setT(prev => prev + dt * 2.2)
      }
      lastRef.current = now
      rafRef.current = requestAnimationFrame(frame)
    }
    rafRef.current = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(rafRef.current)
  }, [])

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 0 }}>
      {WORD.split('').map((char, i) => {
        const phase  = i * 0.38
        const offset = i - CENTER

        // Vertical slinky wave
        const y = Math.sin(t - phase) * 9

        // Accordion spread: oscillates open/closed
        const spreadWave = Math.sin(t * 0.55)
        const x = spreadWave * offset * 4.5

        // Color pulse: brighter at peak of spread
        const bright = (Math.sin(t * 0.55) + 1) / 2
        const alpha  = 0.55 + bright * 0.45

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `translateY(${y.toFixed(2)}px) translateX(${x.toFixed(2)}px)`,
              color: `rgba(255, ${Math.round(112 + bright * 30)}, 48, ${alpha})`,
              fontFamily: 'var(--mono)',
              fontSize: 13,
              letterSpacing: '0.12em',
              fontWeight: 500,
              willChange: 'transform',
            }}
          >
            {char}
          </span>
        )
      })}
      <span style={{
        display: 'inline-block',
        marginLeft: 6,
        animation: 'blink 0.85s step-end infinite',
        color: 'var(--ox)',
        fontSize: 14,
        lineHeight: 1,
      }}>█</span>
    </span>
  )
}

export default function AppPage({ onLogout }) {
  const [glFiles, setGlFiles]     = useState([])
  const [stmtFiles, setStmtFiles] = useState([])
  const [running, setRunning]     = useState(false)
  const [logs, setLogs]           = useState([])
  const [jobId, setJobId]         = useState(null)
  const [error, setError]         = useState('')
  const [scrollY, setScrollY]     = useState(0)

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const p = Math.min(scrollY / 120, 1)
  const leftOpacity   = Math.max(0, 1 - p * 2.5)
  const leftBlur      = p * 8
  const centerOpacity = Math.max(0, (p - 0.3) / 0.7)
  const centerBlur    = (1 - p) * 8

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
        padding: '12px 0',
        marginBottom: 32,
      }}>
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', height: 60 }}>

          {/* Left logo — disintegrates on scroll */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            opacity: leftOpacity,
            filter: `blur(${leftBlur}px)`,
            transform: `scale(${1 - p * 0.04})`,
            pointerEvents: p > 0.5 ? 'none' : 'auto',
          }}>
            <AnimatedLogo width={150} />
            <div>
              <h1 style={{ fontSize: 19 }}>AP Reconciliation</h1>
              <p style={{ color: 'var(--muted)', fontSize: 12, fontFamily: 'var(--mono)' }}>
                vendor statement processor
              </p>
            </div>
          </div>

          {/* Center logo — reassembles at center */}
          <div style={{
            position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)',
            opacity: centerOpacity,
            filter: `blur(${centerBlur}px)`,
            pointerEvents: p < 0.5 ? 'none' : 'auto',
          }}>
            <AnimatedLogo width={110} />
          </div>

          {/* Auth controls */}
          <div style={{
            marginLeft: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            opacity: Math.max(0.25, 1 - p * 0.85),
            transform: `scale(${1 - p * 0.08})`,
            transformOrigin: 'right center',
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
            <p style={{ color: 'var(--muted)', fontSize: 13 }}>Upload your general ledger CSV export</p>
          </div>
          <DropZone label="Drop GL CSV here" accept={['csv']} files={glFiles} onChange={setGlFiles} />
        </div>

        {/* Statements Upload */}
        <div className="card">
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>
              02 — Vendor Statements
            </div>
            <p style={{ color: 'var(--muted)', fontSize: 13 }}>Upload one or more vendor statement PDFs or Excel files</p>
          </div>
          <DropZone label="Drop vendor statements here" accept={['pdf', 'xlsx']} multiple files={stmtFiles} onChange={setStmtFiles} />
        </div>

        {/* ── Run / Processing button ── */}
        <button
          className="btn btn-primary"
          onClick={handleRun}
          disabled={!ready}
          style={{
            fontSize: 15,
            padding: '16px 24px',
            position: 'relative',
            overflow: 'hidden',
            borderColor: running ? 'var(--ox)' : undefined,
            boxShadow: running ? '0 0 20px rgba(255,112,48,0.12), inset 0 0 20px rgba(255,112,48,0.04)' : undefined,
          }}
        >
          {running && (
            <span style={{
              position: 'absolute',
              inset: 0,
              background: 'linear-gradient(90deg, transparent 0%, rgba(255,112,48,0.10) 50%, transparent 100%)',
              animation: 'btnScan 2s linear infinite',
              pointerEvents: 'none',
            }} />
          )}
          {running ? <SlinkyText /> : 'Run Reconciliation →'}
        </button>

        {/* Logs */}
        {!running && logs.length > 0 && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
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
