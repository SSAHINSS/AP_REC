import { useRef, useState } from 'react'

export default function DropZone({ label, accept, multiple = false, files, onChange }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files).filter(f => {
      const ext = f.name.split('.').pop().toLowerCase()
      return accept.includes(ext)
    })
    if (dropped.length) onChange(multiple ? [...files, ...dropped] : [dropped[0]])
  }

  function handleChange(e) {
    const picked = Array.from(e.target.files)
    if (picked.length) onChange(multiple ? [...files, ...picked] : [picked[0]])
    e.target.value = ''
  }

  function remove(idx) {
    onChange(files.filter((_, i) => i !== idx))
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div
        className={`dropzone ${dragging ? 'dragging' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={e => { if (!e.currentTarget.contains(e.relatedTarget)) setDragging(false) }}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept.map(e => `.${e}`).join(',')}
          multiple={multiple}
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        <div style={{ pointerEvents: 'none' }}>
          <div style={{ fontSize: 22, marginBottom: 6, opacity: 0.5 }}>↑</div>
          <div style={{ fontSize: 13, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
            {label}
          </div>
          <div style={{ marginTop: 12 }}>
            <button
              className="btn btn-browse"
              type="button"
              style={{ pointerEvents: 'none' }}
            >
              Browse
            </button>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {files.map((f, i) => (
            <span key={i} className="chip">
              {f.name}
              <button type="button" onClick={e => { e.stopPropagation(); remove(i) }}>✕</button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
