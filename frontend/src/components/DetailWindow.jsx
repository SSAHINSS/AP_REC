import { useState, useRef, useEffect } from 'react'
import { useSort } from './useSort'
import { trendsDetail, cardholderDetail } from '../api'

const MONEY = v =>
  v === 0 || v == null ? '—'
  : v < 0 ? `(${Math.abs(v).toLocaleString(undefined, { maximumFractionDigits: 2 })})`
  : v.toLocaleString(undefined, { maximumFractionDigits: 2 })

const DETAIL_COLS = [
  { key: 'date',       label: 'DATE',        type: 'str', get: r => r.date },
  { key: 'location',   label: 'LOCATION',    type: 'str', get: r => r.location },
  { key: 'pay',        label: 'TYPE',        type: 'str', get: r => (r.is_cc ? 'CC' : 'AP') },
  { key: 'account',    label: 'ACCOUNT',     type: 'str', get: r => r.account },
  { key: 'cardholder', label: 'CARDHOLDER',  type: 'str', get: r => r.cardholder },
  { key: 'memo',       label: 'MEMO',        type: 'str', get: r => r.memo },
  { key: 'doc',        label: 'DOC #',       type: 'str', get: r => r.doc },
  { key: 'amount',     label: 'AMOUNT',      type: 'num', get: r => r.amount },
]

function SliceTable({ slice }) {
  const { sorted, clickSort, arrow } = useSort(slice.rows || [], DETAIL_COLS)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, padding: '6px 4px', flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700 }}>
          {slice.comparison_label || 'This period'}
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
          {slice.scope} · {slice.row_count} txns
          {slice.cc_count > 0 && ` · ${slice.cc_count} CC`}
        </span>
        <span style={{ flex: 1 }} />
        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--ox)' }}>
          ${MONEY(slice.total)}
        </span>
      </div>
      <div style={{ overflow: 'auto', flex: 1 }}>
        <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 10 }}>
          <thead><tr>
            {DETAIL_COLS.map(c => (
              <th key={c.key} onClick={() => clickSort(c.key)}
                  style={{ padding: '4px 6px', textAlign: c.type === 'num' ? 'right' : 'left',
                           fontSize: 9, color: 'var(--muted)', cursor: 'pointer', userSelect: 'none',
                           position: 'sticky', top: 0, background: 'var(--surface)',
                           borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' }}>
                {c.label}{arrow(c.key)}
              </th>
            ))}
          </tr></thead>
          <tbody>
            {sorted.map((t, i) => (
              <tr key={i} style={{ background: i % 2 ? 'transparent' : 'var(--stripe)' }}>
                <td style={dtd()} title={t.date}>{t.date}</td>
                <td style={dtd()} title={t.location}>{t.location}</td>
                <td style={dtd()}>
                  <span style={{ fontSize: 9, padding: '0 4px', borderRadius: 2,
                                 color: t.is_cc ? 'var(--ox)' : 'var(--muted)',
                                 border: `1px solid ${t.is_cc ? 'var(--ox-b)' : 'var(--border)'}` }}>
                    {t.is_cc ? '💳 CC' : 'AP'}
                  </span>
                </td>
                <td style={dtd({ whiteSpace: 'normal', maxWidth: 240, wordBreak: 'break-word' })} title={t.account}>{t.account}</td>
                <td style={dtd({ whiteSpace: 'normal', maxWidth: 130, wordBreak: 'break-word' })} title={t.cardholder}>{t.cardholder}</td>
                <td style={dtd({ whiteSpace: 'normal', maxWidth: 300, wordBreak: 'break-word' })} title={t.memo}>{t.memo}</td>
                <td style={dtd({ whiteSpace: 'normal', maxWidth: 120, wordBreak: 'break-word' })} title={t.doc}>{t.doc}</td>
                <td style={dtd({ textAlign: 'right', color: t.amount < 0 ? 'var(--err)' : undefined })}>{MONEY(t.amount)}</td>
              </tr>
            ))}
            <tr style={{ borderTop: '1px solid var(--border)' }}>
              <td colSpan={7} style={dtd({ fontWeight: 700 })}>TOTAL — {slice.row_count} txns</td>
              <td style={dtd({ textAlign: 'right', fontWeight: 700 })}>{MONEY(slice.total)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

const COMPARE_OPTS = [
  { id: 'prior_period',   label: 'Prior period' },
  { id: 'same_last_year', label: 'Same month last year' },
  { id: 'two_prior',      label: 'Two periods prior' },
]

export default function DetailWindow({ req, onClose }) {
  // req: { label, view, entity, month, period }
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [comparisons, setComparisons] = useState([])
  const [minimized, setMinimized] = useState(false)
  const [maximized, setMaximized] = useState(false)

  const [pos, setPos]   = useState({ x: Math.max(24, window.innerWidth / 2 - 590), y: 90 })
  const [size, setSize] = useState({ w: 1180, h: 680 })
  const drag = useRef(null)

  async function fetchDetail(cmps = comparisons) {
    setLoading(true); setError('')
    try {
      let d
      if (req.kind === 'cardholder') {
        const cd = await cardholderDetail({
          holder: req.holder, entities: req.entities || [],
          start: req.start, end: req.end,
        })
        // shape into the slice format SliceTable expects
        d = { label: req.holder, is_window: true, scope: req.title || req.holder,
              rows: cd.rows.map(r => ({ ...r, is_cc: true, cardholder: req.holder })),
              row_count: cd.row_count, total: cd.total, cc_count: cd.row_count,
              truncated: cd.truncated, comparisons: [] }
      } else {
        d = await trendsDetail({
          label: req.label, view: req.view, entity: req.entity,
          month: req.month, period: req.period, comparisons: cmps.join(','),
        })
      }
      setData(d)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { fetchDetail() }, [req])  // eslint-disable-line

  function toggleCompare(id) {
    const next = comparisons.includes(id)
      ? comparisons.filter(c => c !== id)
      : (comparisons.length >= 3 ? comparisons : [...comparisons, id])
    setComparisons(next)
    fetchDetail(next)
  }

  // Dragging by the title bar
  function onDragStart(e) {
    if (maximized) return
    drag.current = { sx: e.clientX, sy: e.clientY, ox: pos.x, oy: pos.y }
    window.addEventListener('mousemove', onDragMove)
    window.addEventListener('mouseup', onDragEnd)
  }
  function onDragMove(e) {
    if (!drag.current) return
    setPos({ x: drag.current.ox + (e.clientX - drag.current.sx),
             y: Math.max(0, drag.current.oy + (e.clientY - drag.current.sy)) })
  }
  function onDragEnd() {
    drag.current = null
    window.removeEventListener('mousemove', onDragMove)
    window.removeEventListener('mouseup', onDragEnd)
  }

  const canCompare = req.kind !== 'cardholder' && req.month && !data?.is_window
  const frame = maximized
    ? { left: 12, top: 12, width: 'calc(100vw - 24px)', height: 'calc(100vh - 24px)' }
    : { left: pos.x, top: pos.y, width: size.w, height: minimized ? 'auto' : size.h }

  const slices = data ? [data, ...(data.comparisons || [])] : []

  return (
    <div style={{ position: 'fixed', zIndex: 400, ...frame,
                  background: 'var(--surface)', border: '1px solid var(--ox-b)',
                  borderRadius: 6, boxShadow: '0 12px 40px rgba(0,0,0,0.4)',
                  display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* Title bar */}
      <div onMouseDown={onDragStart}
           style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px',
                    background: 'color-mix(in srgb, var(--ox) 12%, var(--surface))',
                    borderBottom: '1px solid var(--border)',
                    cursor: maximized ? 'default' : 'move', userSelect: 'none' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700 }}>
          {req.kind === 'cardholder' ? '💳 ' + req.holder : req.label}
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)' }}>
          {req.kind === 'cardholder'
            ? (req.title || '')
            : `${req.entity || 'all entities'}${req.month ? ` · ${req.month}` : ' · full window'}`}
        </span>
        <span style={{ flex: 1 }} />
        <button onClick={() => setMinimized(m => !m)} title="Minimize" style={winBtn}>{minimized ? '▢' : '—'}</button>
        <button onClick={() => { setMaximized(m => !m); setMinimized(false) }} title="Maximize" style={winBtn}>⛶</button>
        <button onClick={onClose} title="Close" style={{ ...winBtn, color: 'var(--err)' }}>✕</button>
      </div>

      {!minimized && (
        <>
          {/* Compare controls */}
          {canCompare && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px',
                          borderBottom: '1px solid var(--border)', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                             textTransform: 'uppercase', letterSpacing: '0.08em' }}>Compare to</span>
              {COMPARE_OPTS.map(o => {
                const on = comparisons.includes(o.id)
                const disabled = !on && comparisons.length >= 3
                return (
                  <button key={o.id} onClick={() => toggleCompare(o.id)} disabled={disabled}
                    style={{ fontFamily: 'var(--mono)', fontSize: 10, padding: '3px 9px', borderRadius: 2,
                             cursor: disabled ? 'not-allowed' : 'pointer',
                             color: on ? 'var(--ox)' : 'var(--muted)',
                             background: on ? 'rgba(255,112,48,0.1)' : 'transparent',
                             border: `1px solid ${on ? 'var(--ox-b)' : 'var(--border)'}`,
                             opacity: disabled ? 0.4 : 1 }}>
                    {on ? '✓ ' : ''}{o.label}
                  </button>
                )
              })}
            </div>
          )}

          {/* Body: side-by-side slices */}
          <div style={{ flex: 1, overflow: 'auto', padding: 10, display: 'flex', gap: 12 }}>
            {loading && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', padding: 10 }}>loading transactions…</div>}
            {error && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--err)', padding: 10 }}>{error}</div>}
            {!loading && !error && slices.map((s, i) => (
              <div key={i} style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column',
                                    borderLeft: i > 0 ? '1px solid var(--border)' : 'none',
                                    paddingLeft: i > 0 ? 12 : 0 }}>
                <SliceTable slice={s} />
              </div>
            ))}
          </div>

          {/* Resize handle */}
          {!maximized && (
            <div onMouseDown={e => {
                   e.preventDefault()
                   const sx = e.clientX, sy = e.clientY, ow = size.w, oh = size.h
                   const mm = ev => setSize({ w: Math.max(420, ow + (ev.clientX - sx)),
                                              h: Math.max(240, oh + (ev.clientY - sy)) })
                   const mu = () => { window.removeEventListener('mousemove', mm); window.removeEventListener('mouseup', mu) }
                   window.addEventListener('mousemove', mm); window.addEventListener('mouseup', mu)
                 }}
                 style={{ position: 'absolute', right: 0, bottom: 0, width: 16, height: 16,
                          cursor: 'nwse-resize',
                          background: 'linear-gradient(135deg, transparent 50%, var(--ox-b) 50%)' }} />
          )}
        </>
      )}
    </div>
  )
}

const winBtn = {
  fontFamily: 'var(--mono)', fontSize: 12, lineHeight: 1, cursor: 'pointer',
  background: 'transparent', border: '1px solid var(--border)', borderRadius: 2,
  color: 'var(--text)', width: 22, height: 20, padding: 0,
}
const dtd = extra => ({ padding: '3px 6px', textAlign: 'left', whiteSpace: 'nowrap', ...extra })
