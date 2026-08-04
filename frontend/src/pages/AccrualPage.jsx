import { useState, useEffect, useRef } from 'react'
import { analyzeTrends, accrualDraftGet, accrualDraftPut, accrualAccounts,
         accrualRowinfo, accrualExport } from '../api'
import GlPicker from '../components/GlPicker'
import DetailWindow from '../components/DetailWindow'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 0 })

function monthLabel(m) {
  if (!m) return ''
  const [y, mo] = m.split('-')
  return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
}
const rowKey = (g, l) => `${g}::${l}`

export default function AccrualPage() {
  const [entity, setEntity]   = useState('')
  const [period, setPeriod]   = useState('')
  const [data, setData]       = useState(null)
  const [accounts, setAccounts] = useState([])
  const [creditAcct, setCreditAcct] = useState('')
  const [rows, setRows]       = useState({})     // key -> {on, amount, acct, loc, vendor_valid}
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [noGl, setNoGl]       = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportErrors, setExportErrors] = useState([])
  const [win, setWin]         = useState(null)
  const saveTimer = useRef(null)

  useEffect(() => {
    accrualAccounts().then(setAccounts).catch(e => {
      if ((e.message || '').includes('No GL')) setNoGl(true)
    })
  }, [])

  async function loadEntity(e, p) {
    setLoading(true); setError(''); setExportErrors([])
    try {
      const t = await analyzeTrends(e, 'vendor', p || '')
      setData(t)
      const per = p || t.period
      if (!p) setPeriod(t.period)
      const draft = await accrualDraftGet(e, per)
      setRows(draft.rows || {})
      if (draft.credit_acct) setCreditAcct(draft.credit_acct)
    } catch (err) {
      if ((err.message || '').includes('No GL')) setNoGl(true)
      else setError(err.message)
    } finally { setLoading(false) }
  }

  const pickEntity = e => { setEntity(e); loadEntity(e, period) }
  const pickPeriod = p => { setPeriod(p); if (entity) loadEntity(entity, p) }

  // Debounced autosave — the accountant's review survives sessions
  function scheduleSave(nextRows, nextCredit) {
    clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      if (!entity || !period) return
      accrualDraftPut({ entity, period, rows: nextRows, credit_acct: nextCredit }).catch(() => {})
    }, 700)
  }

  async function toggleRow(g, label, payType) {
    if (payType === 'cc') return
    const k = rowKey(g, label)
    const cur = rows[k]
    let next
    if (cur?.on) {
      next = { ...rows, [k]: { ...cur, on: false } }
    } else if (cur) {
      next = { ...rows, [k]: { ...cur, on: true } }
    } else {
      // first check: fetch Sage-validated defaults for account/location/vendor
      next = { ...rows, [k]: { on: true, amount: '', acct: '', loc: '', loading: true } }
      setRows(next); scheduleSave(next, creditAcct)
      try {
        const info = await accrualRowinfo({ entity, group: g, label, period })
        next = { ...next, [k]: { on: true, amount: '', acct: info.acct_no,
                                 loc: info.location_id, vendor_valid: info.vendor_valid } }
      } catch {
        next = { ...next, [k]: { on: true, amount: '', acct: '', loc: '' } }
      }
    }
    setRows(next); scheduleSave(next, creditAcct)
  }
  function setField(k, field, value) {
    const next = { ...rows, [k]: { ...rows[k], [field]: value } }
    setRows(next); scheduleSave(next, creditAcct)
  }
  function setCredit(v) {
    setCreditAcct(v); scheduleSave(rows, v)
  }

  const activeLines = Object.entries(rows)
    .filter(([, r]) => r.on && parseFloat(r.amount) > 0)
    .map(([k, r]) => {
      const [group, label] = k.split('::')
      return { label, group, amount: parseFloat(r.amount),
               acct_no: r.acct, location_id: r.loc }
    })
  const accrualTotal = activeLines.reduce((s, l) => s + l.amount, 0)

  async function doExport() {
    setExporting(true); setExportErrors([]); setError('')
    try {
      await accrualExport({ entity, period, credit_acct: creditAcct, lines: activeLines })
    } catch (e) {
      if (Array.isArray(e.validationErrors)) setExportErrors(e.validationErrors)
      else setError(e.message)
    } finally { setExporting(false) }
  }

  const openDetail = (label, group, monthIdx) => setWin({
    label, view: 'vendor', entity, group,
    month: data.months[monthIdx], period: data?.period || '',
    _k: `${label}:${monthIdx}:${Date.now()}`,
  })

  const months = data?.months || []
  const showMonths = months.length ? [months.length - 4, months.length - 3, months.length - 2] : []

  return (
    <div style={{ minHeight: '100vh', maxWidth: 1760, margin: '0 auto', padding: '24px 24px 120px',
                  display: 'flex', flexDirection: 'column', gap: 18 }}>

      <GlPicker module="trends" moduleLabel="Accrual Builder"
                onChanged={() => entity && loadEntity(entity, period)} />

      <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
        <b style={{ color: 'var(--warn)' }}>EXPERIMENTAL</b> — review AP spend, check the vendors to
        accrue, enter amounts, and export a Sage-ready JE import CSV. Uses the same GL as Expense
        Trends. Credit-card lines can't be accrued (already paid). Your work autosaves per
        entity + month.
      </div>

      {noGl && (
        <div className="card" style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>
          No GL on file yet — use the GL Source bar above to upload one.
        </div>
      )}

      {/* Step 1: entity + month */}
      {!noGl && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
            <span style={lbl}>1 · Entity</span>
            {(data?.entities || ['LIB','OE','SH','MAD','PRED','WRI','JTS','ODS','OCMGT','CHCO','RRT','CSC','MACD']).map(e => (
              <button key={e} onClick={() => pickEntity(e)} style={pill(entity === e)}>{e}</button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={lbl}>Close Month</span>
            <select value={period} onChange={e => pickPeriod(e.target.value)} style={sel} disabled={!data}>
              {(data?.available_months || []).slice().reverse().map(m => <option key={m} value={m}>{m}</option>)}
            </select>
            <span style={{ ...lbl, marginLeft: 18 }}>2 · Accrue to (credit)</span>
            <select value={creditAcct || ''} onChange={e => setCredit(e.target.value)} style={sel}>
              <option value="">— select account —</option>
              {accounts.map(a => (
                <option key={a.account} value={a.account}>{a.account} {a.title}</option>
              ))}
            </select>
            {loading && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>loading…</span>}
            {error && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)' }}>{error}</span>}
          </div>
        </div>
      )}

      {/* Step 3: review table */}
      {data && !data.error && entity && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
            3 · Check vendors to accrue — amounts blank by design; click any month number for its
            transactions. Account &amp; location prefill from the GL (editable, Sage-validated on export).
          </div>
          <div style={{ overflowX: 'auto', borderTop: '1px solid var(--border)' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
              <thead><tr>
                <th style={th({ textAlign: 'left', minWidth: 200 })}>VENDOR</th>
                <th style={th({ textAlign: 'left', width: 56 })}>TYPE</th>
                {showMonths.map(i => <th key={i} style={th({})}>{monthLabel(months[i])}</th>)}
                <th style={th({ color: 'var(--ox)' })}>{monthLabel(data.period)}</th>
                <th style={th({})}>TOTAL</th>
                <th style={th({ textAlign: 'left', minWidth: 330 })}>ACCRUE</th>
              </tr></thead>
              <tbody>
                {data.groups.map(g => (
                  <>
                  <tr key={g.name}>
                    <td colSpan={7 + showMonths.length - 2}
                        style={{ padding: '7px 10px', background: 'var(--bg2, rgba(0,0,0,0.18))',
                                 fontWeight: 700, fontSize: 10, letterSpacing: '0.08em',
                                 color: 'var(--ox)', textTransform: 'uppercase' }}>
                      {g.name}
                    </td>
                  </tr>
                  {g.rows.map((r, ri) => {
                    const k = rowKey(g.name, r.label)
                    const st = rows[k]
                    const isCC = r.pay_type === 'cc'
                    const aIdx = months.length - 2
                    return (
                      <tr key={k} style={{ background: st?.on
                          ? 'color-mix(in srgb, var(--ox) 7%, transparent)'
                          : ri % 2 ? 'transparent' : 'var(--stripe)' }}>
                        <td style={td({ textAlign: 'left' })}>{r.label}</td>
                        <td style={td({ textAlign: 'left' })}>
                          <span style={{ fontSize: 9, padding: '0 4px', borderRadius: 2,
                                         color: isCC ? 'var(--ox)' : r.pay_type === 'mixed' ? 'var(--warn)' : 'var(--muted)',
                                         border: '1px solid var(--border)' }}>
                            {isCC ? 'CC' : r.pay_type === 'mixed' ? 'MIX' : 'AP'}
                          </span>
                        </td>
                        {showMonths.map(i => (
                          <td key={i} onClick={() => r.values[i] !== 0 && openDetail(r.label, g.name, i)}
                              style={td({ color: r.values[i] === 0 ? 'var(--dim)' : undefined,
                                          cursor: r.values[i] !== 0 ? 'pointer' : 'default',
                                          textDecoration: r.values[i] !== 0 ? 'underline dotted' : 'none',
                                          textUnderlineOffset: 3 })}>{MONEY(r.values[i])}</td>
                        ))}
                        <td onClick={() => r.values[aIdx] !== 0 && openDetail(r.label, g.name, aIdx)}
                            style={td({ fontWeight: 600,
                                        cursor: r.values[aIdx] !== 0 ? 'pointer' : 'default',
                                        textDecoration: r.values[aIdx] !== 0 ? 'underline dotted' : 'none',
                                        textUnderlineOffset: 3 })}>{MONEY(r.values[aIdx])}</td>
                        <td style={td({})}>{MONEY(r.total)}</td>
                        <td style={td({ textAlign: 'left' })}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                            <input type="checkbox" checked={!!st?.on} disabled={isCC}
                                   title={isCC ? 'Credit-card spend is already paid — nothing to accrue' : 'Accrue this vendor'}
                                   onChange={() => toggleRow(g.name, r.label, r.pay_type)}
                                   style={{ cursor: isCC ? 'not-allowed' : 'pointer' }} />
                            {st?.on && (
                              <>
                                <input type="number" placeholder="amount" value={st.amount}
                                       onChange={e => setField(k, 'amount', e.target.value)}
                                       style={inp(100)} />
                                <input type="text" placeholder="acct" value={st.acct || ''}
                                       onChange={e => setField(k, 'acct', e.target.value)}
                                       title="GL account (prefilled from history)" style={inp(64)} />
                                <input type="text" placeholder="location" value={st.loc || ''}
                                       onChange={e => setField(k, 'loc', e.target.value)}
                                       title="Location ID (prefilled from history)" style={inp(96)} />
                                {st.vendor_valid === false && (
                                  <span title="Not an active Sage vendor — export will flag this"
                                        style={{ color: 'var(--warn)', fontSize: 11 }}>⚠</span>
                                )}
                              </>
                            )}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Step 4: sticky export bar */}
      {entity && data && (
        <div style={{ position: 'fixed', left: 64, right: 0, bottom: 0, zIndex: 50,
                      background: 'var(--surface)', borderTop: '1px solid var(--ox-b)',
                      padding: '10px 24px', display: 'flex', alignItems: 'center', gap: 18,
                      fontFamily: 'var(--mono)', fontSize: 12, flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 700 }}>4 · Export</span>
          <span>{activeLines.length} accrual line{activeLines.length === 1 ? '' : 's'}</span>
          <span>credit → {creditAcct || '—'}</span>
          <span style={{ flex: 1 }} />
          <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--ox)' }}>${MONEY(accrualTotal)}</span>
          <button className="btn btn-primary" disabled={exporting || !activeLines.length || !creditAcct}
                  onClick={doExport}>
            {exporting ? 'Building…' : `Export JE CSV — ${entity} ${period}`}
          </button>
        </div>
      )}
      {exportErrors.length > 0 && (
        <div className="card" style={{ border: '1px solid var(--err)', fontFamily: 'var(--mono)', fontSize: 11 }}>
          <b style={{ color: 'var(--err)' }}>Export blocked — fix these Sage validation problems:</b>
          {exportErrors.map((e, i) => <div key={i} style={{ marginTop: 4 }}>• {e}</div>)}
        </div>
      )}

      {win && <DetailWindow key={win._k} req={win} onClose={() => setWin(null)} />}
    </div>
  )
}

const lbl = { fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
              textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: 6 }
const sel = { fontFamily: 'var(--mono)', fontSize: 11, padding: '4px 8px',
              background: 'var(--surface)', color: 'var(--text)',
              border: '1px solid var(--border)', borderRadius: 2, maxWidth: 320 }
const pill = active => ({
  fontFamily: 'var(--mono)', fontSize: 11, cursor: 'pointer', padding: '4px 10px', borderRadius: 2,
  color: active ? 'var(--ox)' : 'var(--muted)',
  background: active ? 'rgba(255,112,48,0.1)' : 'transparent',
  border: active ? '1px solid var(--ox-b)' : '1px solid var(--border)',
})
const th = extra => ({ padding: '8px 8px', textAlign: 'right', fontWeight: 600, fontSize: 10,
  letterSpacing: '0.06em', color: 'var(--muted)', borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap', userSelect: 'none',
  position: 'sticky', top: 0, zIndex: 3, background: 'var(--surface)',
  boxShadow: '0 1px 0 var(--border)', ...extra })
const td = extra => ({ padding: '5px 8px', textAlign: 'right', whiteSpace: 'nowrap', ...extra })
const inp = w => ({ fontFamily: 'var(--mono)', fontSize: 11, width: w, padding: '3px 6px',
  background: 'var(--bg)', color: 'var(--text)',
  border: '1px solid var(--border)', borderRadius: 2 })
