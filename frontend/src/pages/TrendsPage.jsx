import { useState, useEffect } from 'react'
import { analyzeTrends } from '../api'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 0 })

const FLAG_COLORS = {
  'Possibly Missing': { fg: 'var(--err)',  bg: 'color-mix(in srgb, var(--err) 10%, transparent)',  bd: 'color-mix(in srgb, var(--err) 35%, transparent)'  },
  'Possibly High':    { fg: 'var(--warn)', bg: 'color-mix(in srgb, var(--warn) 10%, transparent)', bd: 'color-mix(in srgb, var(--warn) 35%, transparent)' },
  'Possibly Low':     { fg: 'var(--err)',  bg: 'color-mix(in srgb, var(--err) 7%, transparent)',   bd: 'color-mix(in srgb, var(--err) 28%, transparent)'  },
}

function FlagChip({ flag }) {
  const c = FLAG_COLORS[flag.flag] || {}
  return (
    <span title={`avg $${flag.history_mean.toLocaleString()} | σ $${flag.history_sd.toLocaleString()} | ${flag.months_present}/${flag.months_history} months | current $${flag.current.toLocaleString()}${flag.last_doc ? ` | last doc ${flag.last_doc}` : ''}`}
      style={{
        fontFamily: 'var(--mono)', fontSize: 10, whiteSpace: 'nowrap',
        color: c.fg, background: c.bg, border: `1px solid ${c.bd}`,
        borderRadius: 2, padding: '2px 6px',
      }}>
      {flag.flag}
    </span>
  )
}

const CROSSHAIR_CSS = `
  .trend-wrap { position: relative; }
  .trend-table td, .trend-table th { position: relative; }
  /* Column beam: tall overlay from the hovered cell, clipped by the scroll container */
  .trend-table td:hover::after,
  .trend-table th:hover::after {
    content: ""; position: absolute; left: 0; top: -6000px;
    width: 100%; height: 12000px;
    background: rgba(255,112,48,0.07);
    pointer-events: none; z-index: 3;
  }
  /* Row beam */
  .trend-table tbody tr:hover td {
    background-color: color-mix(in srgb, var(--surface), #FF7030 10%) !important;
  }
  .trend-table tbody tr:hover td:first-child {
    box-shadow: inset 2px 0 0 var(--ox);
  }
`

export default function TrendsPage() {
  const [stored,  setStored]    = useState(null)   // {filename, uploaded_at} if a GL is saved
  const [noGl,    setNoGl]      = useState(false)  // backend says nothing is uploaded yet
  const [running, setRunning]   = useState(false)
  const [error,   setError]     = useState('')
  const [data,    setData]      = useState(null)
  const [entity,  setEntity]    = useState('')      // '' = whole org
  const [view,    setView]      = useState('vendor')
  const [period,  setPeriod]    = useState('')      // '' = latest month in data
  const [openGroups, setOpenGroups] = useState({})  // group name -> bool
  const [queueOpen, setQueueOpen] = useState(true)
  const [showFlagsOnly, setShowFlagsOnly] = useState(false)

  async function run(nextEntity = entity, nextView = view, nextPeriod = period) {
    setRunning(true); setError(''); setNoGl(false)
    try {
      const res = await analyzeTrends(null, nextEntity, nextView, nextPeriod)
      setData(res)
      setOpenGroups({})
      if (res.gl_filename) setStored({ filename: res.gl_filename, uploaded_at: res.gl_uploaded_at })
    } catch (e) {
      if ((e.message || '').includes('No GL')) setNoGl(true)
      else setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  // On page load, analyze the saved GL immediately (backend 422s if none).
  useEffect(() => { run() }, [])

  function pick(nextEntity) {
    setEntity(nextEntity)
    run(nextEntity, view, period)
  }
  function pickView(v) {
    setView(v)
    run(entity, v, period)
  }
  function pickPeriod(p) {
    setPeriod(p)
    run(entity, view, p)
  }

  const months = data?.months || []
  const shortMonths = months.map(m => {
    const [y, mo] = m.split('-')
    return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
  })

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>
      <style>{CROSSHAIR_CSS}</style>

      {noGl && !data && (
        <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>
          No GL on file yet. Upload it on the <b style={{ color: 'var(--ox)' }}>Home</b> page —
          every module reads the same saved GL.
        </div>
      )}
      {error && <div className="card" style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 12 }}>{error}</div>}

      {data && !data.error && (
        <>
          {/* Entity + view selectors */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>Entity</span>
              <button onClick={() => pick('')}
                style={pill(entity === '')}>ALL (ORG)</button>
              {data.entities.map(e => (
                <button key={e} onClick={() => pick(e)} style={pill(entity === e)}>{e}</button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>View</span>
              <button onClick={() => pickView('vendor')}  style={pill(view === 'vendor')}>By Vendor</button>
              <button onClick={() => pickView('account')} style={pill(view === 'account')}>By GL Account</button>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', margin: '0 6px 0 18px' }}>
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
              <label style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)',
                              display: 'flex', gap: 6, alignItems: 'center', cursor: 'pointer' }}>
                <input type="checkbox" checked={showFlagsOnly}
                       onChange={e => setShowFlagsOnly(e.target.checked)} />
                flagged rows only
              </label>
            </div>
          </div>

          {/* Flags summary — the automated "Summary" tab, worst first */}
          {data.flags.length > 0 && (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <button onClick={() => setQueueOpen(q => !q)}
                style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12,
                         background: 'transparent', border: 'none', cursor: 'pointer',
                         padding: '14px 16px', color: 'var(--text)' }}>
                <span style={{ fontFamily: 'var(--mono)', color: 'var(--ox)', fontSize: 12 }}>{queueOpen ? '▾' : '▸'}</span>
                <span style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)',
                               letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  Review Queue — {data.flags.length} flags, worst first
                </span>
              </button>
              {queueOpen && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 320,
                            overflowY: 'auto', padding: '0 16px 14px' }}>
                {data.flags.map((f, i) => (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '130px 160px 1fr 110px 110px 90px',
                                        gap: 8, alignItems: 'center', padding: '5px 8px',
                                        background: i % 2 ? 'transparent' : 'var(--stripe)',
                                        fontFamily: 'var(--mono)', fontSize: 11 }}>
                    <FlagChip flag={f} />
                    <span style={{ color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.group}</span>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.label}</span>
                    <span style={{ textAlign: 'right' }}>cur ${MONEY(f.current)}</span>
                    <span style={{ textAlign: 'right', color: 'var(--muted)' }}>avg ${MONEY(f.history_mean)}</span>
                    <span style={{ textAlign: 'right', color: 'var(--muted)' }}>{f.months_present}/{f.months_history} mo</span>
                  </div>
                ))}
              </div>
              )}
            </div>
          )}

          {/* Group matrices — P&L order */}
          {data.groups.map(g => {
            const open = openGroups[g.name] ?? false
            const rows = showFlagsOnly ? g.rows.filter(r => r.flag) : g.rows
            if (showFlagsOnly && !rows.length) return null
            return (
              <div key={g.name} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <button onClick={() => setOpenGroups(o => ({ ...o, [g.name]: !open }))}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12,
                           background: 'transparent', border: 'none', cursor: 'pointer',
                           padding: '14px 16px', color: 'var(--text)' }}>
                  <span style={{ fontFamily: 'var(--mono)', color: 'var(--ox)', fontSize: 12 }}>{open ? '▾' : '▸'}</span>
                  <span style={{ fontWeight: 600, fontSize: 14 }}>{g.name}</span>
                  <span style={{ flex: 1 }} />
                  {g.rows.some(r => r.flag) &&
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--warn)' }}>
                      {g.rows.filter(r => r.flag).length} flagged
                    </span>}
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)' }}>
                    ${MONEY(g.total)}
                  </span>
                </button>

                {open && (
                  <div className="trend-wrap" style={{ overflowX: 'auto', overflowY: 'hidden', borderTop: '1px solid var(--border)' }}>
                    <table className="trend-table" style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
                      <thead>
                        <tr>
                          <th style={th({ textAlign: 'left', minWidth: 220, position: 'sticky', left: 0, zIndex: 2, background: 'var(--surface)' })}>
                            {view === 'vendor' ? 'VENDOR' : 'ACCOUNT'}
                          </th>
                          {shortMonths.map((m, i) => (
                            <th key={m} style={th({ color: i === shortMonths.length - 1 ? 'var(--ox)' : 'var(--muted)' })}>{m}</th>
                          ))}
                          <th style={th({ position: 'sticky', right: 130, zIndex: 2, background: 'var(--surface)' })}>TOTAL</th>
                          <th style={th({ textAlign: 'left', position: 'sticky', right: 0, zIndex: 2, background: 'var(--surface)', width: 130, minWidth: 130 })}>FLAG</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((r, ri) => {
                          const rowBg = ri % 2 ? 'var(--bg)' : 'var(--surface)'
                          return (
                          <tr key={r.label} style={{ background: ri % 2 ? 'transparent' : 'var(--stripe)' }}>
                            <td style={td({ textAlign: 'left', position: 'sticky', left: 0, zIndex: 1,
                                            background: rowBg,
                                            maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })}>
                              {r.label}
                            </td>
                            {r.values.map((v, i) => (
                              <td key={i} style={td({
                                color: v === 0 ? 'var(--dim)' : v < 0 ? 'var(--err)' : undefined,
                                fontWeight: i === r.values.length - 1 ? 600 : 400,
                              })}>{MONEY(v)}</td>
                            ))}
                            <td style={td({ fontWeight: 600, position: 'sticky', right: 130, zIndex: 1, background: rowBg })}>{MONEY(r.total)}</td>
                            <td style={td({ textAlign: 'left', position: 'sticky', right: 0, zIndex: 1, background: rowBg, width: 130, minWidth: 130 })}>{r.flag ? <FlagChip flag={r.flag} /> : ''}</td>
                          </tr>
                          )
                        })}
                        <tr style={{ borderTop: '1px solid var(--border)' }}>
                          <td style={td({ textAlign: 'left', fontWeight: 700, position: 'sticky', left: 0, zIndex: 1, background: 'var(--surface)' })}>TOTAL</td>
                          {g.totals.map((v, i) => (
                            <td key={i} style={td({ fontWeight: 700 })}>{MONEY(v)}</td>
                          ))}
                          <td style={td({ fontWeight: 700, position: 'sticky', right: 130, zIndex: 1, background: 'var(--surface)' })}>{MONEY(g.total)}</td>
                          <td style={td({ position: 'sticky', right: 0, zIndex: 1, background: 'var(--surface)', width: 130, minWidth: 130 })}></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )
          })}
        </>
      )}

      {data?.error && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 12 }}>{data.error}</div>}
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
  padding: '8px 8px', textAlign: 'right', fontWeight: 600, fontSize: 10,
  letterSpacing: '0.06em', color: 'var(--muted)',
  borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap', ...extra,
})

const td = extra => ({
  padding: '5px 8px', textAlign: 'right', whiteSpace: 'nowrap', ...extra,
})
