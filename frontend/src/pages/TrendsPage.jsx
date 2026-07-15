import { useState, useEffect } from 'react'
import { analyzeTrends, exportTrends } from '../api'
import DetailWindow from '../components/DetailWindow'
import CardholderView from './CardholderView'

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
    <span title={`${flag.group ? flag.group + ' | ' : ''}avg $${(flag.history_mean ?? 0).toLocaleString()} | σ $${(flag.history_sd ?? 0).toLocaleString()} | ${flag.months_present}/${flag.months_history} months | current $${(flag.current ?? 0).toLocaleString()}${flag.last_doc ? ` | last doc ${flag.last_doc}` : ''}`}
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

const ALL = '__ALL__'

export default function TrendsPage() {
  const [stored,  setStored]    = useState(null)
  const [noGl,    setNoGl]      = useState(false)
  const [running, setRunning]   = useState(false)
  const [error,   setError]     = useState('')
  const [data,    setData]      = useState(null)
  const [entity,  setEntity]    = useState('')      // '' = whole org
  const [view,    setView]      = useState('vendor')
  const [period,  setPeriod]    = useState('')      // '' = smart default (backend)
  const [group,   setGroup]     = useState(ALL)     // GL group dropdown
  const [queueOpen, setQueueOpen] = useState(true)
  const [showFlagsOnly, setShowFlagsOnly] = useState(false)
  const [sort,    setSort]      = useState({ key: null, dir: 'desc' })  // key: 'label' | 'total' | month index
  const [win,     setWin]       = useState(null)   // floating detail window request
  const [mode,    setMode]      = useState('trends')  // 'trends' | 'cards'
  const [exporting, setExporting] = useState(false)

  function openDetail(label, monthOrTotal) {
    setWin({
      label, view, entity,
      month: monthOrTotal === 'total' ? '' : months[monthOrTotal],
      period: data?.period || '',
      _k: `${label}:${monthOrTotal}:${Date.now()}`,
    })
  }

  async function doExport() {
    setExporting(true)
    try { await exportTrends(entity, view, data?.period || '') }
    catch (e) { setError(e.message) }
    finally { setExporting(false) }
  }

  async function run(nextEntity = entity, nextView = view, nextPeriod = period) {
    setRunning(true); setError(''); setNoGl(false)
    try {
      const res = await analyzeTrends(null, nextEntity, nextView, nextPeriod)
      setData(res)
      setSort({ key: null, dir: 'desc' })
      setWin(null)
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

  function pick(nextEntity)  { setEntity(nextEntity); run(nextEntity, view, period) }
  function pickView(v)       { setView(v);            run(entity, v, period) }
  function pickPeriod(p)     { setPeriod(p);          run(entity, view, p) }

  const months = data?.months || []
  const analysisIdx = data ? months.indexOf(data.period) : -1
  const shortMonths = months.map(m => {
    const [y, mo] = m.split('-')
    return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
  })

  // ── Build the single table's rows for the selected group (or ALL merged) ──
  function buildRows() {
    if (!data) return []
    if (group !== ALL) {
      const g = data.groups.find(g => g.name === group)
      return g ? g.rows.map(r => ({ ...r })) : []
    }
    // ALL: merge every group's rows by label (a vendor can span groups)
    const flagsByLabel = {}
    for (const f of data.flags) {
      if (!flagsByLabel[f.label] || f.severity > flagsByLabel[f.label].severity)
        flagsByLabel[f.label] = f
    }
    const merged = new Map()
    for (const g of data.groups) {
      for (const r of g.rows) {
        const m = merged.get(r.label)
        if (m) {
          m.values = m.values.map((v, i) => Math.round((v + r.values[i]) * 100) / 100)
          m.total = Math.round((m.total + r.total) * 100) / 100
          m.cc_total = Math.round((m.cc_total + (r.cc_total || 0)) * 100) / 100
          m.ap_total = Math.round((m.ap_total + (r.ap_total || 0)) * 100) / 100
          m.pay_type = m.cc_total && m.ap_total ? 'mixed' : m.cc_total ? 'cc' : 'ap'
        } else {
          merged.set(r.label, { label: r.label, values: [...r.values], total: r.total,
                                cc_total: r.cc_total || 0, ap_total: r.ap_total || 0, pay_type: r.pay_type })
        }
      }
    }
    const rows = [...merged.values()]
    for (const r of rows) {
      const f = flagsByLabel[r.label]
      if (f) r.flag = f
    }
    return rows
  }

  function sortedRows() {
    let rows = buildRows()
    if (showFlagsOnly) rows = rows.filter(r => r.flag)
    if (sort.key === null) {
      rows.sort((a, b) => Math.abs(b.total) - Math.abs(a.total))
    } else if (sort.key === 'label') {
      rows.sort((a, b) => sort.dir === 'asc'
        ? a.label.localeCompare(b.label)
        : b.label.localeCompare(a.label))
    } else {
      const val = r => sort.key === 'total' ? r.total
        : sort.key === 'pay' ? (r.cc_total || 0)
        : (r.values[sort.key] || 0)
      rows.sort((a, b) => sort.dir === 'asc' ? val(a) - val(b) : val(b) - val(a))
    }
    return rows
  }

  // Click a header: first click sorts desc (high→low), second flips asc.
  function clickSort(key) {
    setSort(s => s.key === key
      ? { key, dir: s.dir === 'desc' ? 'asc' : 'desc' }
      : { key, dir: key === 'label' ? 'asc' : 'desc' })
  }
  const arrow = key => sort.key === key ? (sort.dir === 'desc' ? ' ▼' : ' ▲') : ''

  const rows = data ? sortedRows() : []
  const colTotals = months.map((_, i) =>
    Math.round(rows.reduce((s, r) => s + (r.values[i] || 0), 0) * 100) / 100)
  const grandTotal = Math.round(rows.reduce((s, r) => s + r.total, 0) * 100) / 100
  const flaggedCount = rows.filter(r => r.flag).length

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>
      <style>{CROSSHAIR_CSS}</style>

      <div style={{ display: 'flex', gap: 6 }}>
        <button onClick={() => setMode('trends')} style={modePill(mode === 'trends')}>Expense Trends</button>
        <button onClick={() => setMode('cards')} style={modePill(mode === 'cards')}>Credit Card Expenses</button>
      </div>

      {mode === 'cards' && <CardholderView openDetail={setWin} />}

      {mode === 'trends' && noGl && !data && (
        <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>
          No GL on file yet. Upload it on the <b style={{ color: 'var(--ox)' }}>Home</b> page —
          every module reads the same saved GL.
        </div>
      )}
      {mode === 'trends' && error && <div className="card" style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 12 }}>{error}</div>}
      {mode === 'trends' && running && !data && (
        <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)' }}>Analyzing…</div>
      )}

      {mode === 'trends' && data && !data.error && (
        <>
          {/* Entity + view + month + group selectors */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
              <span style={lbl}>Entity</span>
              <button onClick={() => pick('')} style={pill(entity === '')}>ALL (ORG)</button>
              {data.entities.map(e => (
                <button key={e} onClick={() => pick(e)} style={pill(entity === e)}>{e}</button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={lbl}>View</span>
              <button onClick={() => pickView('vendor')}  style={pill(view === 'vendor')}>By Vendor</button>
              <button onClick={() => pickView('account')} style={pill(view === 'account')}>By GL Account</button>

              <span style={{ ...lbl, margin: '0 6px 0 18px' }}>Analysis Month</span>
              <select value={data.period || ''} onChange={e => pickPeriod(e.target.value)} style={sel}>
                {(data.available_months || []).slice().reverse().map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>

              <span style={{ ...lbl, margin: '0 6px 0 18px' }}>GL Group</span>
              <select value={group} onChange={e => setGroup(e.target.value)} style={sel}>
                <option value={ALL}>ALL GROUPS</option>
                {data.groups.map(g => (
                  <option key={g.name} value={g.name}>{g.name}</option>
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

          {/* Review Queue — worst first, across all groups */}
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

          {/* THE table — one table, group-filtered, click-sortable headers */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>
                {group === ALL ? 'All Groups' : group}
              </span>
              <span style={{ flex: 1 }} />
              <button className="btn btn-icon" onClick={doExport} disabled={exporting}
                      style={{ padding: '3px 12px', fontSize: 10 }}>
                {exporting ? 'Building…' : 'Export Report (xlsx)'}
              </button>
              {flaggedCount > 0 &&
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--warn)' }}>
                  {flaggedCount} flagged
                </span>}
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--muted)' }}>
                ${MONEY(grandTotal)}
              </span>
            </div>
            <div className="trend-wrap" style={{ overflowX: 'auto', overflowY: 'hidden', borderTop: '1px solid var(--border)' }}>
              <table className="trend-table" style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
                <thead>
                  <tr>
                    <th onClick={() => clickSort('label')}
                        style={th({ textAlign: 'left', minWidth: 220, position: 'sticky', left: 0, top: 0, zIndex: 4,
                                    background: 'var(--surface)', cursor: 'pointer' })}>
                      {view === 'vendor' ? 'VENDOR' : 'ACCOUNT'}{arrow('label')}
                    </th>
                    <th onClick={() => clickSort('pay')}
                        style={th({ textAlign: 'left', cursor: 'pointer', width: 64, minWidth: 64 })}>
                      TYPE{arrow('pay')}
                    </th>
                    {shortMonths.map((m, i) => (
                      <th key={m} onClick={() => clickSort(i)}
                          style={th({ cursor: 'pointer',
                                      color: i === analysisIdx ? 'var(--ox)' : 'var(--muted)',
                                      fontWeight: i === analysisIdx ? 700 : 600 })}>
                        {m}{arrow(i)}
                      </th>
                    ))}
                    <th onClick={() => clickSort('total')}
                        style={th({ position: 'sticky', right: 130, top: 0, zIndex: 4, background: 'var(--surface)', cursor: 'pointer' })}>
                      TOTAL{arrow('total')}
                    </th>
                    <th style={th({ textAlign: 'left', position: 'sticky', right: 0, top: 0, zIndex: 4, background: 'var(--surface)', width: 130, minWidth: 130 })}>FLAG</th>
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
                      <td style={td({ textAlign: 'left', width: 64, minWidth: 64 })}>
                        {r.pay_type === 'cc' && <span style={payChip('var(--ox)', 'var(--ox-b)')}>💳 CC</span>}
                        {r.pay_type === 'ap' && <span style={payChip('var(--muted)', 'var(--border)')}>AP</span>}
                        {r.pay_type === 'mixed' && (
                          <span title={`CC $${Math.round(r.cc_total).toLocaleString()} · AP $${Math.round(r.ap_total).toLocaleString()}`}
                                style={payChip('var(--warn)', 'color-mix(in srgb, var(--warn) 40%, transparent)')}>◐ MIX</span>
                        )}
                      </td>
                      {r.values.map((v, i) => (
                        <td key={i}
                            onClick={() => v !== 0 && openDetail(r.label, i)}
                            style={td({
                          color: v === 0 ? 'var(--dim)' : v < 0 ? 'var(--err)' : undefined,
                          fontWeight: i === analysisIdx ? 600 : 400,
                          cursor: v !== 0 ? 'pointer' : 'default',
                          textDecoration: v !== 0 ? 'underline dotted' : 'none',
                          textUnderlineOffset: 3,
                        })}>{MONEY(v)}</td>
                      ))}
                      <td onClick={() => r.total !== 0 && openDetail(r.label, 'total')}
                          style={td({ fontWeight: 600, position: 'sticky', right: 130, zIndex: 1,
                                      background: rowBg,
                                      cursor: r.total !== 0 ? 'pointer' : 'default',
                                      textDecoration: r.total !== 0 ? 'underline dotted' : 'none',
                                      textUnderlineOffset: 3 })}>{MONEY(r.total)}</td>
                      <td style={td({ textAlign: 'left', position: 'sticky', right: 0, zIndex: 1, background: rowBg, width: 130, minWidth: 130 })}>{r.flag ? <FlagChip flag={r.flag} /> : ''}</td>
                    </tr>
                    )
                  })}
                  <tr style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={td({ textAlign: 'left', fontWeight: 700, position: 'sticky', left: 0, zIndex: 1, background: 'var(--surface)' })}>TOTAL</td>
                    <td style={td({ width: 64, minWidth: 64 })}></td>
                    {colTotals.map((v, i) => (
                      <td key={i} style={td({ fontWeight: 700 })}>{MONEY(v)}</td>
                    ))}
                    <td style={td({ fontWeight: 700, position: 'sticky', right: 130, zIndex: 1, background: 'var(--surface)' })}>{MONEY(grandTotal)}</td>
                    <td style={td({ position: 'sticky', right: 0, zIndex: 1, background: 'var(--surface)', width: 130, minWidth: 130 })}></td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Drill-down: the transactions behind the clicked number */}
          </div>
        </>
      )}

      {data?.error && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 12 }}>{data.error}</div>}

      {win && <DetailWindow key={win._k} req={win} onClose={() => setWin(null)} />}
    </div>
  )
}

const modePill = active => ({
  fontFamily: 'var(--mono)', fontSize: 12, cursor: 'pointer', padding: '6px 14px', borderRadius: 3,
  color: active ? 'var(--ox)' : 'var(--muted)', fontWeight: active ? 700 : 400,
  background: active ? 'rgba(255,112,48,0.1)' : 'transparent',
  border: active ? '1px solid var(--ox-b)' : '1px solid var(--border)',
})
const payChip = (fg, bd) => ({
  fontFamily: 'var(--mono)', fontSize: 9, whiteSpace: 'nowrap',
  color: fg, border: `1px solid ${bd}`, borderRadius: 2, padding: '1px 5px',
})
const lbl = { fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
              textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }
const sel = { fontFamily: 'var(--mono)', fontSize: 11, padding: '4px 8px',
              background: 'var(--surface)', color: 'var(--text)',
              border: '1px solid var(--border)', borderRadius: 2 }
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
  borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap',
  userSelect: 'none',
  position: 'sticky', top: 0, zIndex: 3, background: 'var(--surface)',
  boxShadow: '0 1px 0 var(--border), 0 3px 6px rgba(0,0,0,0.10)',
  ...extra,
})
const td = extra => ({
  padding: '5px 8px', textAlign: 'right', whiteSpace: 'nowrap', ...extra,
})
