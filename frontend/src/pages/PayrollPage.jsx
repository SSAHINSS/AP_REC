import { useState, useEffect } from 'react'
import { payrollAccrual, payrollTrends, payrollDetail } from '../api'
import GlPicker from '../components/GlPicker'

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

// ── Drill-down panel: the GL rows behind a number ──────────────────────────
function DetailRows({ payload }) {
  if (!payload || !payload.rows) return null
  return (
    <table style={{ borderCollapse: 'collapse', fontFamily: 'var(--mono)', fontSize: 10, width: '100%' }}>
      <thead><tr>
        <th style={dth({ textAlign: 'left' })}>DATE</th>
        <th style={dth({ textAlign: 'left' })}>JRNL</th>
        <th style={dth({ textAlign: 'left' })}>ACCOUNT</th>
        <th style={dth({ textAlign: 'left' })}>DESCRIPTION</th>
        <th style={dth({ textAlign: 'left' })}>DOC #</th>
        <th style={dth({})}>AMOUNT</th>
      </tr></thead>
      <tbody>
        {payload.rows.map((r, i) => (
          <tr key={i} style={{ background: i % 2 ? 'transparent' : 'var(--stripe)' }}>
            <td style={dtd({ textAlign: 'left' })}>{r.date}</td>
            <td style={dtd({ textAlign: 'left', color: r.journal === 'PYRJ' ? 'var(--ok)' : 'var(--warn)' })}>{r.journal}</td>
            <td style={dtd({ textAlign: 'left' })}>{r.account} {r.title}</td>
            <td style={dtd({ textAlign: 'left', maxWidth: 340, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })}>{r.desc}</td>
            <td style={dtd({ textAlign: 'left' })}>{r.doc}</td>
            <td style={dtd({ color: r.amount < 0 ? 'var(--err)' : undefined })}>{MONEY(r.amount)}</td>
          </tr>
        ))}
        <tr style={{ borderTop: '1px solid var(--border)' }}>
          <td colSpan={5} style={dtd({ textAlign: 'left', fontWeight: 700 })}>
            TOTAL — {payload.row_count} rows{payload.truncated ? ' (first shown)' : ''}
          </td>
          <td style={dtd({ fontWeight: 700 })}>{MONEY(payload.total)}</td>
        </tr>
      </tbody>
    </table>
  )
}

function RateDetailPanel({ data }) {
  const [showExcluded, setShowExcluded] = useState(false)
  return (
    <div style={{ padding: '10px 12px', background: 'color-mix(in srgb, var(--ox) 4%, transparent)',
                  border: '1px solid var(--border)', borderRadius: 3, margin: '6px 0 10px' }}>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', marginBottom: 8 }}>
        RATE BASIS — {data.source} · trailing {data.window_days} days through {data.month_end}.
        Only PYRJ (payroll journal) postings build the rate; adjusting entries never touch it.
      </div>
      <DetailRows payload={data.included} />
      <button onClick={() => setShowExcluded(s => !s)}
        style={{ marginTop: 8, background: 'transparent', border: 'none', cursor: 'pointer',
                 fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--warn)', padding: 0 }}>
        {showExcluded ? '▾' : '▸'} {data.excluded.row_count} rows EXCLUDED — {data.excluded.reason}
      </button>
      {showExcluded && <div style={{ marginTop: 6 }}><DetailRows payload={data.excluded} /></div>}
    </div>
  )
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
  const [detail,   setDetail]   = useState(null)     // {key, loading, data, error}

  async function loadAll(nextEntity = entity, nextPeriod = period, nextOverrides = overrides) {
    setRunning(true); setError(''); setNoGl(false); setDetail(null)
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

  async function toggleDetail(key, params) {
    if (detail?.key === key) { setDetail(null); return }
    setDetail({ key, loading: true })
    try {
      const data = await payrollDetail(params)
      setDetail({ key, data })
    } catch (e) {
      setDetail({ key, error: e.message })
    }
  }
  const rateKey = (ent, cat) => `rate:${ent}:${cat}`
  const cellKey = (cat, m)   => `cell:${cat}:${m}`

  if (noGl) return (
    <div style={{ maxWidth: 1760, margin: '0 auto', padding: '24px',
                  display: 'flex', flexDirection: 'column', gap: 16 }}>
      <GlPicker module="payroll" moduleLabel="Payroll" onChanged={() => loadAll()} />
      <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>
        No GL on file yet — use the GL Source bar above to upload one.
      </div>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 80px',
                  display: 'flex', flexDirection: 'column', gap: 24 }}>

      <GlPicker module="payroll" moduleLabel="Payroll" onChanged={() => loadAll()} />

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
            {error && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)' }}>{error}</span>}
          </div>
        </div>
      )}

      {/* ── ACCRUAL CALCULATOR ── */}
      {accData && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ ...lbl, marginRight: 0 }}>Month-End Accrual — {accData.month_end}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
              rates from PYRJ pay runs only · click a category for the postings behind it
            </span>
            <span style={{ flex: 1 }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
              reverses {accData.reversal_date}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700, color: 'var(--ox)' }}>
              ${MONEY(accData.grand_total)}
            </span>
          </div>

          {accData.rows.map(r => {
            const ex = r.existing_accruals
            return (
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
                {r.note && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--warn)' }}>{r.note}</span>}
                <span style={{ flex: 1 }} />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700 }}>${MONEY(r.total)}</span>
              </div>

              {/* ⚠ Accrual already posted — warn only, math untouched */}
              {ex?.payroll?.length > 0 && (
                <div style={{ marginTop: 8, padding: '8px 12px', borderRadius: 3,
                              border: '1px solid var(--warn)',
                              background: 'color-mix(in srgb, var(--warn) 7%, transparent)',
                              fontFamily: 'var(--mono)', fontSize: 11 }}>
                  <b style={{ color: 'var(--warn)' }}>
                    ⚠ PAYROLL ACCRUAL ALREADY POSTED for this month — ${MONEY(ex.payroll_total)}
                  </b> — verify before booking the calculated amount.
                  {ex.payroll.map((p, i) => (
                    <div key={i} style={{ color: 'var(--muted)', marginTop: 3 }}>
                      {p.date} · {p.account} {p.account_title} · ${MONEY(p.amount)}
                      {p.desc ? ` · «${p.desc}»` : ' · (no description)'}{p.doc ? ` · doc ${p.doc}` : ''}
                    </div>
                  ))}
                </div>
              )}
              {ex?.other?.length > 0 && (
                <div style={{ marginTop: 6, fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
                  Other accruals this month (informational): {ex.other.map(o => `${o.kind} $${MONEY(o.amount)}`).join(' · ')}
                </div>
              )}

              {r.categories.length > 0 && (
                <table style={{ borderCollapse: 'collapse', marginTop: 8, fontFamily: 'var(--mono)', fontSize: 11, width: '100%' }}>
                  <thead><tr>
                    <th style={th({ textAlign: 'left', minWidth: 150 })}>CATEGORY</th>
                    <th style={th({})}>DAILY RATE</th>
                    <th style={th({})}>DAYS</th>
                    <th style={th({})}>ACCRUAL</th>
                    <th style={th({ textAlign: 'left' })}>RATE BASIS</th>
                  </tr></thead>
                  <tbody>
                    {r.categories.map(c => {
                      const k = rateKey(r.entity, c.category)
                      const open = detail?.key === k
                      return (
                      <>
                      <tr key={c.category} onClick={() => toggleDetail(k, {
                            kind: 'rate', entity: r.entity, category: c.category,
                            month_end: accData.month_end,
                            schedule: overrides[r.entity] || r.schedule })}
                          style={{ cursor: 'pointer',
                                   background: open ? 'color-mix(in srgb, var(--ox) 6%, transparent)' : undefined }}>
                        <td style={td({ textAlign: 'left', color: 'var(--ox)' })}>{open ? '▾' : '▸'} {c.category}</td>
                        <td style={td({})}>${MONEY(c.daily_rate)}/day</td>
                        <td style={td({})}>{c.days}</td>
                        <td style={td({ fontWeight: 700 })}>${MONEY(c.accrual)}</td>
                        <td style={td({ textAlign: 'left', color: 'var(--muted)' })}>
                          {c.rate_source} · ${MONEY(c.rate_basis_total)} over {c.rate_days_covered}d ({c.rate_runs} runs)
                        </td>
                      </tr>
                      {open && (
                        <tr key={c.category + ':detail'}>
                          <td colSpan={5} style={{ padding: 0 }}>
                            {detail.loading && <div style={{ padding: 10, fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>loading postings…</div>}
                            {detail.error && <div style={{ padding: 10, fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)' }}>{detail.error}</div>}
                            {detail.data && <RateDetailPanel data={detail.data} />}
                          </td>
                        </tr>
                      )}
                      </>
                      )
                    })}
                  </tbody>
                </table>
              )}
            </div>
            )
          })}
        </div>
      )}

      {/* ── PAYROLL TRENDS ── */}
      {trendData && !trendData.error && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', display: 'flex', gap: 12, alignItems: 'center' }}>
            <span style={lbl}>Payroll Trends — trailing 12 months</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
              click any amount for its GL lines
            </span>
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
                  <tr key={r.category} style={{ background: ri % 2 ? 'transparent' : 'var(--stripe)' }}>
                    <td style={td({ textAlign: 'left', position: 'sticky', left: 0, zIndex: 1,
                                    background: ri % 2 ? 'var(--bg)' : 'var(--surface)' })}>{r.category}</td>
                    {r.values.map((v, i) => {
                      const k = cellKey(r.category, trendData.months[i])
                      const open = detail?.key === k
                      return (
                      <td key={i}
                          onClick={() => v !== 0 && toggleDetail(k, {
                            kind: 'cell', entity, category: r.category, month: trendData.months[i] })}
                          style={td({ color: v === 0 ? 'var(--dim)' : undefined,
                                      fontWeight: i === r.values.length - 1 ? 600 : 400,
                                      cursor: v !== 0 ? 'pointer' : 'default',
                                      background: open ? 'color-mix(in srgb, var(--ox) 10%, transparent)' : undefined,
                                      textDecoration: v !== 0 ? 'underline dotted' : 'none',
                                      textUnderlineOffset: 3 })}>{MONEY(v)}</td>
                      )
                    })}
                    <td style={td({ fontWeight: 600 })}>{MONEY(r.ytd_avg)}</td>
                    <td style={td({ color: 'var(--muted)' })}>{r.ly_ytd_avg ? MONEY(r.ly_ytd_avg) : '—'}</td>
                    <td style={td({ color: r.delta_pct == null ? 'var(--muted)' : r.delta_pct > 0 ? 'var(--warn)' : 'var(--ok)' })}>
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

          {/* Cell drill-down panel */}
          {detail?.key?.startsWith('cell:') && (
            <div style={{ borderTop: '1px solid var(--border)', padding: '12px 16px' }}>
              {detail.loading && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>loading GL lines…</div>}
              {detail.error && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)' }}>{detail.error}</div>}
              {detail.data && (
                <>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', marginBottom: 8 }}>
                    {detail.data.category} — {monthLabel(detail.data.month)}
                    {detail.data.entity ? ` — ${detail.data.entity}` : ' — all entities'} · every GL line behind this cell
                  </div>
                  <DetailRows payload={detail.data} />
                </>
              )}
            </div>
          )}

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
const dth = extra => ({
  padding: '4px 6px', textAlign: 'right', fontWeight: 600, fontSize: 9,
  letterSpacing: '0.05em', color: 'var(--muted)',
  borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap', ...extra,
})
const dtd = extra => ({
  padding: '3px 6px', textAlign: 'right', whiteSpace: 'nowrap', ...extra,
})
