import { useState } from 'react'
import { logout, analyzeTrends } from '../api'
import DropZone from '../components/DropZone'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 0 })

const FLAG_COLORS = {
  'Possibly Missing': { fg: '#F87171', bg: 'rgba(248,113,113,0.10)', bd: 'rgba(248,113,113,0.35)' },
  'Possibly High':    { fg: '#FCD34D', bg: 'rgba(252,211,77,0.10)',  bd: 'rgba(252,211,77,0.35)'  },
  'Possibly Low':     { fg: '#FCA5A5', bg: 'rgba(252,165,165,0.08)', bd: 'rgba(252,165,165,0.30)' },
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

export default function TrendsPage({ onLogout }) {
  const [glFiles, setGlFiles]   = useState([])
  const [running, setRunning]   = useState(false)
  const [error,   setError]     = useState('')
  const [data,    setData]      = useState(null)
  const [entity,  setEntity]    = useState('')      // '' = whole org
  const [view,    setView]      = useState('vendor')
  const [openGroups, setOpenGroups] = useState({})  // group name -> bool
  const [showFlagsOnly, setShowFlagsOnly] = useState(false)

  async function run(nextEntity = entity, nextView = view) {
    if (!glFiles[0]) return
    setRunning(true); setError('')
    try {
      const res = await analyzeTrends(glFiles[0], nextEntity, nextView)
      setData(res)
      setOpenGroups({})
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  function pick(nextEntity) {
    setEntity(nextEntity)
    run(nextEntity, view)
  }
  function pickView(v) {
    setView(v)
    run(entity, v)
  }

  const months = data?.months || []
  const shortMonths = months.map(m => {
    const [y, mo] = m.split('-')
    return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
  })

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1280, margin: '0 auto', padding: '48px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 20 }}>Expense Trends</h1>
          <p style={{ color: 'var(--muted)', fontSize: 12, fontFamily: 'var(--mono)' }}>
            vendor × month analysis · validate accuracy · catch missing bills
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="badge">Authenticated</span>
          <button className="btn btn-icon" onClick={() => { logout(); onLogout() }}>Sign out</button>
        </div>
      </div>

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
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }}>View</span>
              <button onClick={() => pickView('vendor')}  style={pill(view === 'vendor')}>By Vendor</button>
              <button onClick={() => pickView('account')} style={pill(view === 'account')}>By GL Account</button>
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
            <div className="card">
              <div style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ox)',
                            letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12 }}>
                Review Queue — {data.flags.length} flags, worst first
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 320, overflowY: 'auto' }}>
                {data.flags.map((f, i) => (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '130px 160px 1fr 110px 110px 90px',
                                        gap: 8, alignItems: 'center', padding: '5px 8px',
                                        background: i % 2 ? 'transparent' : 'rgba(255,255,255,0.02)',
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
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: '#FCD34D' }}>
                      {g.rows.filter(r => r.flag).length} flagged
                    </span>}
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)' }}>
                    ${MONEY(g.total)}
                  </span>
                </button>

                {open && (
                  <div style={{ overflowX: 'auto', borderTop: '1px solid var(--border)' }}>
                    <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
                      <thead>
                        <tr>
                          <th style={th({ textAlign: 'left', minWidth: 220, position: 'sticky', left: 0, background: 'var(--surface)' })}>
                            {view === 'vendor' ? 'VENDOR' : 'ACCOUNT'}
                          </th>
                          {shortMonths.map((m, i) => (
                            <th key={m} style={th({ color: i === shortMonths.length - 1 ? 'var(--ox)' : 'var(--muted)' })}>{m}</th>
                          ))}
                          <th style={th({})}>TOTAL</th>
                          <th style={th({ textAlign: 'left' })}>FLAG</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((r, ri) => (
                          <tr key={r.label} style={{ background: ri % 2 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                            <td style={td({ textAlign: 'left', position: 'sticky', left: 0,
                                            background: ri % 2 ? 'var(--bg)' : 'var(--surface)',
                                            maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })}>
                              {r.label}
                            </td>
                            {r.values.map((v, i) => (
                              <td key={i} style={td({
                                color: v === 0 ? 'var(--border)' : v < 0 ? '#F87171' : undefined,
                                fontWeight: i === r.values.length - 1 ? 600 : 400,
                              })}>{MONEY(v)}</td>
                            ))}
                            <td style={td({ fontWeight: 600 })}>{MONEY(r.total)}</td>
                            <td style={td({ textAlign: 'left' })}>{r.flag ? <FlagChip flag={r.flag} /> : ''}</td>
                          </tr>
                        ))}
                        <tr style={{ borderTop: '1px solid var(--border)' }}>
                          <td style={td({ textAlign: 'left', fontWeight: 700, position: 'sticky', left: 0, background: 'var(--surface)' })}>TOTAL</td>
                          {g.totals.map((v, i) => (
                            <td key={i} style={td({ fontWeight: 700 })}>{MONEY(v)}</td>
                          ))}
                          <td style={td({ fontWeight: 700 })}>{MONEY(g.total)}</td>
                          <td style={td({})}></td>
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
  padding: '5px 10px', textAlign: 'right', whiteSpace: 'nowrap', ...extra,
})
