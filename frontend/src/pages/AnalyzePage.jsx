import { useState } from 'react'
import { analyzeFlags } from '../api'
import DropZone from '../components/DropZone'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `($${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`

const TYPE_COLORS = {
  'Vanished Vendor': { fg: '#F87171', bg: 'rgba(248,113,113,0.10)', bd: 'rgba(248,113,113,0.35)' },
  'Spike':           { fg: '#FCD34D', bg: 'rgba(252,211,77,0.10)',  bd: 'rgba(252,211,77,0.35)'  },
  'Trailing Off':    { fg: '#FCA5A5', bg: 'rgba(252,165,165,0.10)', bd: 'rgba(252,165,165,0.32)' },
  'Dip':             { fg: '#FCA5A5', bg: 'rgba(252,165,165,0.08)', bd: 'rgba(252,165,165,0.28)' },
  'Duplicate':       { fg: '#93C5FD', bg: 'rgba(147,197,253,0.10)', bd: 'rgba(147,197,253,0.35)' },
}

function TypeChip({ type }) {
  const c = TYPE_COLORS[type] || {}
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: 10, whiteSpace: 'nowrap',
      color: c.fg, background: c.bg, border: `1px solid ${c.bd}`,
      borderRadius: 2, padding: '2px 6px',
    }}>{type}</span>
  )
}

// Tiny inline sparkline for the 12-month series; last point emphasized.
function Spark({ series }) {
  if (!series || !series.length) return <span style={{ color: 'var(--border)' }}>—</span>
  const w = 132, h = 26, pad = 2
  const vals = series.map(v => v || 0)
  const min = Math.min(...vals, 0), max = Math.max(...vals, 0)
  const span = max - min || 1
  const x = i => pad + (i * (w - 2 * pad)) / (vals.length - 1 || 1)
  const y = v => h - pad - ((v - min) / span) * (h - 2 * pad)
  const pts = vals.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ')
  const lastX = x(vals.length - 1), lastY = y(vals[vals.length - 1])
  return (
    <svg width={w} height={h} style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke="var(--muted)" strokeWidth="1" />
      <circle cx={lastX} cy={lastY} r="2.4" fill="var(--ox)" />
    </svg>
  )
}

export default function AnalyzePage() {
  const [glFiles, setGlFiles]   = useState([])
  const [running, setRunning]   = useState(false)
  const [error,   setError]     = useState('')
  const [data,    setData]      = useState(null)
  const [entity,  setEntity]    = useState('')      // '' = whole org
  const [period,  setPeriod]    = useState('')      // '' = latest month
  const [typeFilter, setTypeFilter] = useState('all')
  const [openRow, setOpenRow]   = useState(null)

  async function run(nextEntity = entity, nextPeriod = period) {
    if (!glFiles[0]) return
    setRunning(true); setError('')
    try {
      const res = await analyzeFlags(glFiles[0], nextEntity, nextPeriod)
      setData(res); setOpenRow(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }
  const pick       = e => { setEntity(e); run(e, period) }
  const pickPeriod = p => { setPeriod(p); run(entity, p) }

  const monthLabel = m => {
    if (!m) return ''
    const [y, mo] = m.split('-')
    return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
  }

  const flags = data?.flags || []
  const shown = typeFilter === 'all' ? flags : flags.filter(f => f.type === typeFilter)
  const types = data ? Object.keys(data.counts || {}) : []

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Upload */}
      <div className="card">
        <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)',
                      letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12 }}>
          Sage Intacct GL Detail (CSV)
        </div>
        <DropZone label="Drop GL CSV here" accept={['csv']} files={glFiles} onChange={setGlFiles} />
        <button className="btn btn-primary" disabled={!glFiles.length || running}
                onClick={() => run()} style={{ marginTop: 12 }}>
          {running ? 'Analyzing…' : 'Analyze →'}
        </button>
        {error && <div style={{ color: '#F87171', fontFamily: 'var(--mono)', fontSize: 12, marginTop: 10 }}>{error}</div>}
      </div>

      {data && !data.error && (
        <>
          {/* Entity + period + type filter */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>Entity</span>
              <button onClick={() => pick('')} style={pill(entity === '')}>ALL (ORG)</button>
              {data.entities.map(e => (
                <button key={e} onClick={() => pick(e)} style={pill(entity === e)}>{e}</button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>
                Analysis Month
              </span>
              <select value={data.period || ''} onChange={e => pickPeriod(e.target.value)}
                style={{ fontFamily: 'var(--mono)', fontSize: 11, padding: '4px 8px',
                         background: 'var(--surface)', color: 'var(--text)',
                         border: '1px solid var(--border)', borderRadius: 2 }}>
                {(data.available_months || []).slice().reverse().map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
              <span style={{ flex: 1 }} />
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
                {data.total_flags} flags · window {monthLabel(data.months?.[0])}–{monthLabel(data.months?.[data.months.length-1])}
              </span>
            </div>
            {/* Type filter */}
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>Type</span>
              <button onClick={() => setTypeFilter('all')} style={pill(typeFilter === 'all')}>
                All ({data.total_flags})
              </button>
              {types.map(t => (
                <button key={t} onClick={() => setTypeFilter(t)} style={pill(typeFilter === t)}>
                  {t} ({data.counts[t]})
                </button>
              ))}
            </div>
          </div>

          {/* Flag list */}
          {shown.length === 0 ? (
            <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)' }}>
              No flags for this selection.
            </div>
          ) : (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
                  <thead>
                    <tr>
                      <th style={th({ textAlign: 'left', width: 120 })}>TYPE</th>
                      <th style={th({ textAlign: 'left', width: 54 })}>ENTITY</th>
                      <th style={th({ textAlign: 'left', minWidth: 220 })}>VENDOR</th>
                      <th style={th({ textAlign: 'left', minWidth: 150 })}>GROUP</th>
                      <th style={th({})}>CURRENT</th>
                      <th style={th({})}>AVG</th>
                      <th style={th({})}>MONTHS</th>
                      <th style={th({ textAlign: 'left', width: 140 })}>TREND</th>
                      <th style={th({})}>SEVERITY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {shown.map((f, i) => {
                      const isOpen = openRow === i
                      return (
                        <>
                          <tr key={i}
                              onClick={() => setOpenRow(isOpen ? null : i)}
                              style={{ cursor: 'pointer',
                                       background: isOpen ? 'rgba(255,112,48,0.06)'
                                                  : i % 2 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                            <td style={td({ textAlign: 'left' })}><TypeChip type={f.type} /></td>
                            <td style={td({ textAlign: 'left', color: 'var(--muted)' })}>{f.entity}</td>
                            <td style={td({ textAlign: 'left', maxWidth: 260, overflow: 'hidden',
                                            textOverflow: 'ellipsis', whiteSpace: 'nowrap' })}>{f.vendor}</td>
                            <td style={td({ textAlign: 'left', color: 'var(--muted)' })}>{f.group}</td>
                            <td style={td({ fontWeight: 600 })}>{MONEY(f.current)}</td>
                            <td style={td({ color: 'var(--muted)' })}>{f.history_mean == null ? '—' : MONEY(f.history_mean)}</td>
                            <td style={td({ color: 'var(--muted)' })}>
                              {f.months_present == null ? '—' : `${f.months_present}/${f.months_history}`}
                            </td>
                            <td style={td({ textAlign: 'left' })}><Spark series={f.series} /></td>
                            <td style={td({ fontWeight: 600, color: 'var(--ox)' })}>
                              {f.severity.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                            </td>
                          </tr>
                          {isOpen && (
                            <tr>
                              <td colSpan={9} style={{ padding: '12px 16px', background: 'rgba(255,112,48,0.04)',
                                                       borderBottom: '1px solid var(--border)' }}>
                                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text)', marginBottom: 8 }}>
                                  {f.explain}
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 18, fontFamily: 'var(--mono)',
                                              fontSize: 11, color: 'var(--muted)' }}>
                                  {f.history_mean != null && <span>history avg: <b style={{ color: 'var(--text)' }}>{MONEY(f.history_mean)}</b></span>}
                                  {f.history_sd != null && <span>σ: <b style={{ color: 'var(--text)' }}>{MONEY(f.history_sd)}</b></span>}
                                  {f.months_present != null && <span>present: <b style={{ color: 'var(--text)' }}>{f.months_present}/{f.months_history} mo</b></span>}
                                  <span>current: <b style={{ color: 'var(--text)' }}>{MONEY(f.current)}</b></span>
                                  {f.last_doc && <span>last doc #: <b style={{ color: 'var(--text)' }}>{f.last_doc}</b></span>}
                                  {f.dates && <span>dates: <b style={{ color: 'var(--text)' }}>{f.dates.join(', ')}</b></span>}
                                </div>
                                {f.series && (
                                  <div style={{ display: 'flex', gap: 10, marginTop: 10, flexWrap: 'wrap' }}>
                                    {data.months.map((m, mi) => (
                                      <div key={m} style={{ textAlign: 'center', minWidth: 58 }}>
                                        <div style={{ fontSize: 9, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>{monthLabel(m)}</div>
                                        <div style={{ fontSize: 11, fontFamily: 'var(--mono)',
                                                      fontWeight: mi === data.months.length - 1 ? 700 : 400,
                                                      color: mi === data.months.length - 1 ? 'var(--ox)'
                                                           : (f.series[mi] === 0 ? 'var(--border)' : 'var(--text)') }}>
                                          {MONEY(f.series[mi])}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </td>
                            </tr>
                          )}
                        </>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {data?.error && <div style={{ color: '#F87171', fontFamily: 'var(--mono)', fontSize: 12 }}>{data.error}</div>}
    </div>
  )
}

const pill = active => ({
  fontFamily: 'var(--mono)', fontSize: 11, cursor: 'pointer',
  padding: '4px 10px', borderRadius: 2,
  color: active ? 'var(--ox)' : 'var(--muted)',
  background: active ? 'rgba(255,112,48,0.1)' : 'transparent',
  border: active ? '1px solid var(--ox-b)' : '1px solid var(--border)',
})

const th = extra => ({
  padding: '8px 10px', textAlign: 'right', fontWeight: 600, fontSize: 10,
  letterSpacing: '0.06em', color: 'var(--muted)',
  borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap', ...extra,
})

const td = extra => ({
  padding: '6px 10px', textAlign: 'right', whiteSpace: 'nowrap',
  borderBottom: '1px solid rgba(255,255,255,0.03)', ...extra,
})
