import { useState, useEffect } from 'react'
import { ccCardholders } from '../api'
import { useSort } from '../components/useSort'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 0 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 0 })

function monthLabel(m) {
  const [y, mo] = m.split('-')
  return `${['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo]} '${y.slice(2)}`
}

// Multi-select chip picker
function ChipPicker({ label, options, selected, onToggle, onAll, allOn }) {
  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'flex-start', flexWrap: 'wrap' }}>
      <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                     textTransform: 'uppercase', letterSpacing: '0.08em', paddingTop: 5, minWidth: 70 }}>{label}</span>
      <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', flex: 1 }}>
        <button onClick={onAll} style={chip(allOn)}>ALL</button>
        {options.map(o => (
          <button key={o} onClick={() => onToggle(o)} style={chip(!allOn && selected.includes(o))}>{o}</button>
        ))}
      </div>
    </div>
  )
}

export default function CardholderView({ openDetail }) {
  const [data, setData]       = useState(null)
  const [entities, setEntities] = useState([])   // [] = all
  const [holders, setHolders]   = useState([])   // [] = all
  const [start, setStart]     = useState('')
  const [end, setEnd]         = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  async function run(next = {}) {
    setLoading(true); setError('')
    const ents = next.entities ?? entities
    const hlds = next.holders ?? holders
    const s = next.start ?? start
    const e = next.end ?? end
    try {
      const d = await ccCardholders({ entities: ents, holders: hlds, start: s, end: e })
      setData(d)
    } catch (er) { setError(er.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { run() }, [])  // eslint-disable-line

  const months = data?.months || []
  const cols = [
    { key: 'label',   type: 'str', get: r => r.label },
    { key: 'entities',type: 'str', get: r => r.entities.join(',') },
    { key: 'txn',     type: 'num', get: r => r.txn_count },
    ...months.map((m, i) => ({ key: 'm' + i, type: 'num', get: r => r.values[i] })),
    { key: 'total',   type: 'num', get: r => r.total },
  ]
  const { sorted, clickSort, arrow } = useSort(data?.rows || [], cols, { key: 'total', dir: 'desc' })
  const colTotals = data?.totals || []

  const toggleEntity = ent => {
    const next = entities.includes(ent) ? entities.filter(x => x !== ent) : [...entities, ent]
    setEntities(next); run({ entities: next })
  }
  const toggleHolder = h => {
    const next = holders.includes(h) ? holders.filter(x => x !== h) : [...holders, h]
    setHolders(next); run({ holders: next })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Filters */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <ChipPicker label="Entity" options={data?.all_entities || []} selected={entities}
                    allOn={entities.length === 0}
                    onAll={() => { setEntities([]); run({ entities: [] }) }}
                    onToggle={toggleEntity} />
        <ChipPicker label="Cardholder" options={data?.all_cardholders || []} selected={holders}
                    allOn={holders.length === 0}
                    onAll={() => { setHolders([]); run({ holders: [] }) }}
                    onToggle={toggleHolder} />
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                         textTransform: 'uppercase', letterSpacing: '0.08em', minWidth: 70 }}>Period</span>
          <select value={start} onChange={e => { setStart(e.target.value); run({ start: e.target.value }) }} style={sel}>
            <option value="">earliest</option>
            {(data?.months || []).map(m => <option key={m} value={m}>{monthLabel(m)}</option>)}
          </select>
          <span style={{ color: 'var(--muted)' }}>→</span>
          <select value={end} onChange={e => { setEnd(e.target.value); run({ end: e.target.value }) }} style={sel}>
            <option value="">latest</option>
            {(data?.months || []).map(m => <option key={m} value={m}>{monthLabel(m)}</option>)}
          </select>
          {loading && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>loading…</span>}
          {error && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)' }}>{error}</span>}
        </div>
      </div>

      {/* Pivot */}
      {data && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontWeight: 600, fontSize: 14 }}>Credit-Card Spend by Cardholder</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
              {data.rows.length} cardholders · CC only, no AP · click any amount for transactions
            </span>
            <span style={{ flex: 1 }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700, color: 'var(--ox)' }}>
              ${MONEY(data.grand_total)}
            </span>
          </div>
          <div style={{ overflowX: 'auto', borderTop: '1px solid var(--border)' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
              <thead><tr>
                <th onClick={() => clickSort('label')} style={cth({ textAlign: 'left', minWidth: 170, position: 'sticky', left: 0, background: 'var(--surface)', zIndex: 2, cursor: 'pointer' })}>CARDHOLDER{arrow('label')}</th>
                <th onClick={() => clickSort('entities')} style={cth({ textAlign: 'left', cursor: 'pointer' })}>ENTITIES{arrow('entities')}</th>
                <th onClick={() => clickSort('txn')} style={cth({ cursor: 'pointer' })}>TXNS{arrow('txn')}</th>
                {months.map((m, i) => (
                  <th key={m} onClick={() => clickSort('m' + i)} style={cth({ cursor: 'pointer' })}>{monthLabel(m)}{arrow('m' + i)}</th>
                ))}
                <th onClick={() => clickSort('total')} style={cth({ position: 'sticky', right: 0, background: 'var(--surface)', zIndex: 2, cursor: 'pointer' })}>TOTAL{arrow('total')}</th>
              </tr></thead>
              <tbody>
                {sorted.map((r, ri) => (
                  <tr key={r.label} style={{ background: ri % 2 ? 'transparent' : 'var(--stripe)' }}>
                    <td style={ctd({ textAlign: 'left', position: 'sticky', left: 0, zIndex: 1,
                                     background: ri % 2 ? 'var(--bg)' : 'var(--surface)' })}
                        title={r.top_vendor ? `top vendor: ${r.top_vendor}` : ''}>{r.label}</td>
                    <td style={ctd({ textAlign: 'left', color: 'var(--muted)', maxWidth: 160,
                                     overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' })}
                        title={r.entities.join(', ')}>{r.entities.join(', ')}</td>
                    <td style={ctd({ color: 'var(--muted)' })}>{r.txn_count}</td>
                    {r.values.map((v, i) => (
                      <td key={i}
                          onClick={() => v !== 0 && openDetail({
                            kind: 'cardholder', holder: r.label,
                            entities, start: months[i], end: months[i],
                            title: `${r.label} · ${monthLabel(months[i])}` })}
                          style={ctd({ color: v === 0 ? 'var(--dim)' : undefined,
                                       cursor: v !== 0 ? 'pointer' : 'default',
                                       textDecoration: v !== 0 ? 'underline dotted' : 'none',
                                       textUnderlineOffset: 3 })}>{MONEY(v)}</td>
                    ))}
                    <td onClick={() => r.total !== 0 && openDetail({
                          kind: 'cardholder', holder: r.label,
                          entities, start, end,
                          title: `${r.label} · all shown periods` })}
                        style={ctd({ fontWeight: 700, position: 'sticky', right: 0, zIndex: 1,
                                     background: ri % 2 ? 'var(--bg)' : 'var(--surface)',
                                     cursor: r.total !== 0 ? 'pointer' : 'default',
                                     textDecoration: r.total !== 0 ? 'underline dotted' : 'none',
                                     textUnderlineOffset: 3 })}>{MONEY(r.total)}</td>
                  </tr>
                ))}
                <tr style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={ctd({ textAlign: 'left', fontWeight: 700, position: 'sticky', left: 0, zIndex: 1, background: 'var(--surface)' })}>TOTAL</td>
                  <td style={ctd({})}></td><td style={ctd({})}></td>
                  {colTotals.map((v, i) => <td key={i} style={ctd({ fontWeight: 700 })}>{MONEY(v)}</td>)}
                  <td style={ctd({ fontWeight: 700, position: 'sticky', right: 0, zIndex: 1, background: 'var(--surface)' })}>{MONEY(data.grand_total)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

const sel = { fontFamily: 'var(--mono)', fontSize: 11, padding: '4px 8px',
              background: 'var(--surface)', color: 'var(--text)',
              border: '1px solid var(--border)', borderRadius: 2 }
const chip = active => ({
  fontFamily: 'var(--mono)', fontSize: 10, cursor: 'pointer', padding: '3px 8px', borderRadius: 2,
  color: active ? 'var(--ox)' : 'var(--muted)',
  background: active ? 'rgba(255,112,48,0.1)' : 'transparent',
  border: active ? '1px solid var(--ox-b)' : '1px solid var(--border)',
})
const cth = extra => ({ padding: '8px 8px', textAlign: 'right', fontWeight: 600, fontSize: 10,
  letterSpacing: '0.06em', color: 'var(--muted)', borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap', userSelect: 'none', ...extra })
const ctd = extra => ({ padding: '5px 8px', textAlign: 'right', whiteSpace: 'nowrap', ...extra })
