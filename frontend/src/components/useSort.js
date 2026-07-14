import { useState, useMemo } from 'react'

// Universal click-to-sort for any table.
// columns: [{ key, get, type }]  — get(row) returns the sort value; type 'num'|'str'
// First click on a column sorts descending (numbers) / ascending (strings);
// clicking the active column flips direction.
export function useSort(rows, columns, initial = { key: null, dir: 'desc' }) {
  const [sort, setSort] = useState(initial)

  const sorted = useMemo(() => {
    if (!sort.key) return rows
    const col = columns.find(c => c.key === sort.key)
    if (!col) return rows
    const copy = [...rows]
    copy.sort((a, b) => {
      const va = col.get(a), vb = col.get(b)
      let cmp
      if (col.type === 'str') cmp = String(va).localeCompare(String(vb))
      else cmp = (Number(va) || 0) - (Number(vb) || 0)
      return sort.dir === 'asc' ? cmp : -cmp
    })
    return copy
  }, [rows, columns, sort])

  function clickSort(key) {
    const col = columns.find(c => c.key === key)
    const defaultDir = col?.type === 'str' ? 'asc' : 'desc'
    setSort(s => s.key === key
      ? { key, dir: s.dir === 'desc' ? 'asc' : 'desc' }
      : { key, dir: defaultDir })
  }
  const arrow = key => (sort.key === key ? (sort.dir === 'desc' ? ' ▼' : ' ▲') : '')

  return { sorted, sort, clickSort, arrow, setSort }
}
