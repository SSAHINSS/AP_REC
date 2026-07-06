import { useState, useEffect } from 'react'
import { payrollAccrual, payrollTrends } from '../api'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 0 })

const SCHED_LABEL = {
  cohort1: 'Biweekly — Cohort 1',
  cohort2: 'Biweekly — Cohort 2',
  weekly:  'Weekly',
  unknown: 'Unknown',
}

function monthLabel(m) {
  if (!m) return ''
  const [y, mo] = m.split('-')
  return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
}
function lastDay(period) {           // "2026-06" -> "2026-06-30"
  const [y, m] = period.split('-').map(Number)
  const d = new Date(y, m, 0).getDate()
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

export default function PayrollPage() {
  const [entity,   setEntity]   = useState('')
  const [period,   setPeriod]   = useState('')       // "YYYY-MM"
  const [months,   setMonths]   = useState([])       // available months
  const [trendData, setTrendData] = useState(null)
  const [accData,  setAccData]  = useState(null)
  const [overrides, setOverrides] = useState({})     // entity -> schedule
  const [running,  setRunning]  = useState(false)
  const [error,    setError]    = useState('')
  const [noGl,     setNoGl]     = useState(false)

  async function loadAll(nextEntity = entity, nextPeriod = period, nextOverrides = overrides) {
    setRunning(true); setError(''); setNoGl(false)
    try {
      const t = await payrollTrends(nextEntity, nextPeriod)
      setTrendData(t)
      setMonths(t.available_months || [])
      const p = nextPeriod || t.period
      if (!nextPeriod) setPeriod(t.period)
      const a = await payrollAccrual(lastDay(p), nextEntity, nextOverrides)
      setAccData(a)
    } catch (e) {
      if ((e.message || '').includes('No GL')) setNoGl(true)
      else setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  useEffect(() => { loadAll() }, [])

  const pick       = e => { setEntity(e); loadAll(e, period, overrides) }
  const pickPeriod = p => { setPeriod(p); loadAll(entity, p, overrides) }
  const setSched   = (ent, s) => {
    const next = { ...overrides, [ent]: s }
    setOverrides(next)
    loadAll(entity, period, next)
  }

  if (noGl) return (
    <div style={{ maxWidth: 1760, margin: '0 auto', padding: '24px' }}>
      <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>
        No GL on file yet. Upload your Sage Intacct GL on the <b>Trends</b> page first —
        Payroll uses the same saved GL.
      </div>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Selectors */}
      {trendData && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
            <span style={lbl}>Entity</span>
            <button onClick={() => pick('')} style={pill(entity === '')}>ALL (ORG)</button>
            {trendData.entities.map(e => (
              <button key={e} onClick={() => pick(e)} style={pill(entity === e)}>{e}</button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={lbl}>Close Month</span>
            <select value={period} onChange={e => pickPeriod(e.target.value)} style={sel}>
              {months.slice().reverse().map(m => <option key={m} value={m}>{m}</option>)}
            </select>
            {running && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>calculating…</span>}
            {error && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: '#F87171' }}>{error}</span>}
          </div>
        </div>
      )}

      {/* ── ACCRUAL CALCULATOR ── */}
      {accData && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ ...lbl, marginRight: 0 }}>Month-End Accrual — {accData.month_end}</span>
            <span style={{ flex: 1 }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
              reverses {accData.reversal_date}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700, color: 'var(--ox)' }}>
              ${MONEY(accData.grand_total)}
            </span>
          </div>

          {accData.rows.map(r => (
            <div key={r.entity} style={{ borderTop: '1px solid var(--border)', padding: '12px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                <span style={{ fontFamily: 'var(--mono)', fontWeight: 700, fontSize: 13 }}>{r.entity}</span>
                <select value={overrides[r.entity] || r.schedule}
                        onChange={e => setSched(r.entity, e.target.value)} style={sel}
                        title={r.schedule_basis}>
                  {['cohort1','cohort2','weekly','unknown'].map(s =>
                    <option key={s} value={s}>{SCHED_LABEL[s]}</option>)}
                </select>
                {r.days != null && (
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
                    expensed through {r.expensed_through} → <b style={{ color: 'var(--text)' }}>{r.days} days to accrue</b>
                  </span>
                )}
                {r.note && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: '#FCD34D' }}>{r.note}</span>}
                <span style={{ flex: 1 }} />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700 }}>${MONEY(r.total)}</span>
              </div>
              {r.categories.length > 0 && (
                <table style={{ borderCollapse: 'collapse', marginTop: 8, fontFamily: 'var(--mono)', fontSize: 11 }}>
                  <thead><tr>
                    <th style={th({ textAlign: 'left', minWidth: 150 })}>CATEGORY</th>
                    <th style={th({})}>DAILY RATE</th>
                    <th style={th({})}>DAYS</th>
                    <th style={th({})}>ACCRUAL</th>
                    <th style={th({ textAlign: 'left' })}>RATE BASIS</th>
                  </tr></thead>
                  <tbody>
                    {r.categories.map(c => (
                      <tr key={c.category}>
                        <td style={td({ textAlign: 'left' })}>{c.category}</td>
                        <td style={td({})}>${MONEY(c.daily_rate)}/day</td>
                        <td style={td({})}>{c.days}</td>
                        <td style={td({ fontWeight: 700 })}>${MONEY(c.accrual)}</td>
                        <td style={td({ textAlign: 'left', color: 'var(--muted)' })}>
                          {c.rate_source} · ${MONEY(c.rate_basis_total)} over {c.rate_days_covered}d
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── PAYROLL TRENDS ── */}
      {trendData && !trendData.error && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px' }}>
            <span style={lbl}>Payroll Trends — trailing 12 months</span>
          </div>
          <div style={{ overflowX: 'auto', borderTop: '1px solid var(--border)' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
              <thead><tr>
                <th style={th({ textAlign: 'left', minWidth: 140, position: 'sticky', left: 0, background: 'var(--surface)', zIndex: 2 })}>CATEGORY</th>
                {trendData.months.map((m, i) => (
                  <th key={m} style={th({ color: i === trendData.months.length - 1 ? 'var(--ox)' : 'var(--muted)' })}>{monthLabel(m)}</th>
                ))}
                <th style={th({})}>YTD AVG/MO</th>
                <th style={th({})}>LY YTD AVG</th>
                <th style={th({})}>Δ%</th>
              </tr></thead>
              <tbody>
                {trendData.rows.map((r, ri) => (
                  <tr key={r.category} style={{ background: ri % 2 ? 'transparent' : 'rgba(127,127,127,0.04)' }}>
                    <td style={td({ textAlign: 'left', position: 'sticky', left: 0, zIndex: 1,
                                    background: ri % 2 ? 'var(--bg)' : 'var(--surface)' })}>{r.category}</td>
                    {r.values.map((v, i) => (
                      <td key={i} style={td({ color: v === 0 ? 'var(--border)' : undefined,
                                              fontWeight: i === r.values.length - 1 ? 600 : 400 })}>{MONEY(v)}</td>
                    ))}
                    <td style={td({ fontWeight: 600 })}>{MONEY(r.ytd_avg)}</td>
                    <td style={td({ color: 'var(--muted)' })}>{r.ly_ytd_avg ? MONEY(r.ly_ytd_avg) : '—'}</td>
                    <td style={td({ color: r.delta_pct == null ? 'var(--muted)' : r.delta_pct > 0 ? '#FCD34D' : '#86EFAC' })}>
                      {r.delta_pct == null ? '—' : `${r.delta_pct > 0 ? '+' : ''}${r.delta_pct}%`}
                    </td>
                  </tr>
                ))}
                <tr style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={td({ textAlign: 'left', fontWeight: 700, position: 'sticky', left: 0, zIndex: 1, background: 'var(--surface)' })}>TOTAL</td>
                  {trendData.totals.map((v, i) => <td key={i} style={td({ fontWeight: 700 })}>{MONEY(v)}</td>)}
                  <td style={td({})}></td><td style={td({})}></td><td style={td({})}></td>
                </tr>
              </tbody>
            </table>
          </div>
          {trendData.ly_ytd_months === 0 && (
            <div style={{ padding: '10px 16px', fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
              LY YTD needs a GL export covering last year — current file starts {monthLabel(trendData.available_months[0])}.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

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
  borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap', ...extra,
})
const td = extra => ({
  padding: '5px 8px', textAlign: 'right', whiteSpace: 'nowrap', ...extra,
})
