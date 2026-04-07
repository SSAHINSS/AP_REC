import { useState, useEffect, useRef } from 'react'
import { reconcile, downloadFile } from '../api'
import DropZone from '../components/DropZone'

const WORD = 'PROCESSING...'
const CENTER = (WORD.length - 1) / 2

function SlinkyText() {
  const tRef = useRef(0); const lastRef = useRef(null)
  const [, forceUpdate] = useState(0); const rafRef = useRef(null)
  useEffect(() => {
    function frame(now) {
      if (lastRef.current !== null) { tRef.current += (now - lastRef.current) / 1000 * 2.2; forceUpdate(n => n+1) }
      lastRef.current = now; rafRef.current = requestAnimationFrame(frame)
    }
    rafRef.current = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(rafRef.current)
  }, [])
  const t = tRef.current
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 0 }}>
      {WORD.split('').map((char, i) => {
        const phase = i * 0.38; const offset = i - CENTER
        const y = Math.sin(t - phase) * 13
        const spreadWave = Math.sin(t * 0.55); const x = spreadWave * offset * 28
        const bright = (Math.sin(t * 0.55) + 1) / 2; const alpha = 0.55 + bright * 0.45
        return (
          <span key={i} style={{
            display: 'inline-block',
            transform: `translateY(${y.toFixed(2)}px) translateX(${x.toFixed(2)}px)`,
            color: `rgba(255,${Math.round(112+bright*30)},48,${alpha})`,
            fontFamily: 'var(--mono)', fontSize: Math.round(18+bright*10),
            letterSpacing: '0.04em', fontWeight: 900, willChange: 'transform',
          }}>{char}</span>
        )
      })}
    </span>
  )
}

export default function AppPage() {
  const [glFiles,   setGlFiles]   = useState([])
  const [stmtFiles, setStmtFiles] = useState([])
  const [running,   setRunning]   = useState(false)
  const [logs,      setLogs]      = useState([])
  const [jobId,     setJobId]     = useState(null)
  const [error,     setError]     = useState('')

  const stmtRef     = useRef(null)
  const runRef      = useRef(null)
  const downloadRef = useRef(null)

  useEffect(() => {
    if (glFiles.length > 0 && stmtRef.current)
      setTimeout(() => stmtRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 120)
  }, [glFiles.length > 0])

  useEffect(() => {
    if (stmtFiles.length > 0 && runRef.current)
      setTimeout(() => runRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' }), 120)
  }, [stmtFiles.length > 0])

  useEffect(() => {
    if (jobId && downloadRef.current)
      setTimeout(() => downloadRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' }), 200)
  }, [jobId])

  async function handleRun() {
    if (!glFiles[0] || !stmtFiles.length) return
    setRunning(true); setLogs([]); setJobId(null); setError('')
    try {
      const result = await reconcile(glFiles[0], stmtFiles, msg => setLogs(prev => [...prev, msg]))
      setJobId(result.job_id)
    } catch(e) { setError(e.message) }
    finally { setRunning(false) }
  }

  const ready = glFiles.length > 0 && stmtFiles.length > 0 && !running

  return (
    <div style={{ maxWidth: 680, margin: '0 auto', padding: '32px 24px 80px', display: 'flex', flexDirection: 'column', gap: 32 }}>

      <div className="card">
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>01 — GL Export</div>
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>Upload your general ledger CSV export</p>
        </div>
        <DropZone label="Drop GL CSV here" accept={['csv']} files={glFiles} onChange={setGlFiles} />
      </div>

      <div className="card" ref={stmtRef}>
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 4 }}>02 — Vendor Statements</div>
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>Upload one or more vendor statement PDFs or Excel files</p>
        </div>
        <DropZone label="Drop vendor statements here" accept={['pdf','xlsx']} multiple files={stmtFiles} onChange={setStmtFiles} />
      </div>

      <button ref={runRef} className="btn btn-primary" onClick={handleRun} disabled={!ready}
        style={{ fontSize: 15, padding: running ? '28px 24px' : '16px 24px', position: 'relative', overflow: 'visible',
          borderColor: running ? 'transparent' : undefined, background: running ? 'transparent' : undefined }}>
        {running ? <SlinkyText /> : 'Run Reconciliation'}
      </button>

      {!running && logs.length > 0 && (
        <div className="card">
          <div className="log">
            {logs.map((l, i) => {
              const cls = l.includes('✓') || l.includes('matched') ? 'log-ok'
                        : l.includes('skip') || l.includes('SKIP')  ? 'log-skip'
                        : l.includes('error') || l.includes('Error') ? 'log-err' : ''
              return <div key={i} className={cls}>{l}</div>
            })}
          </div>
        </div>
      )}

      {error && (
        <div style={{ background:'rgba(248,113,113,0.08)', border:'1px solid rgba(248,113,113,0.3)',
          borderRadius:4, padding:'16px 20px', color:'#F87171', fontFamily:'var(--mono)', fontSize:13 }}>
          {error}
        </div>
      )}

      {jobId && (
        <div ref={downloadRef} style={{ background:'rgba(255,112,48,0.06)', border:'1px solid var(--ox-b)',
          borderRadius:4, padding:'20px 24px', display:'flex', alignItems:'center',
          justifyContent:'space-between', gap:16, flexWrap:'wrap' }}>
          <div>
            <div style={{ fontWeight:600, marginBottom:4 }}>Reconciliation complete</div>
            <div style={{ color:'var(--muted)', fontSize:13 }}>{stmtFiles.length} statement{stmtFiles.length!==1?'s':''} processed</div>
          </div>
          <button className="btn btn-primary" onClick={() => downloadFile(jobId)} style={{ width:'auto', padding:'10px 28px' }}>
            Download XLSX ↓
          </button>
        </div>
      )}

    </div>
  )
}
