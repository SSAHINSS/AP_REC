// Pixel art icons as inline SVG
function IconAPRec({ active }) {
  const c = active ? '#FF7030' : '#8C7B6A'
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" shapeRendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
      {/* Paper */}
      <rect x="5" y="2" width="14" height="2" fill={c}/>
      <rect x="5" y="4" width="2" height="18" fill={c}/>
      <rect x="17" y="4" width="2" height="18" fill={c}/>
      <rect x="5" y="22" width="14" height="2" fill={c}/>
      {/* Lines on paper */}
      <rect x="8" y="7" width="8" height="2" fill={c} opacity="0.5"/>
      <rect x="8" y="11" width="8" height="2" fill={c} opacity="0.5"/>
      {/* Checkmark */}
      <rect x="8" y="17" width="2" height="2" fill={active ? '#86EFAC' : '#8C7B6A'}/>
      <rect x="10" y="19" width="2" height="2" fill={active ? '#86EFAC' : '#8C7B6A'}/>
      <rect x="12" y="17" width="2" height="2" fill={active ? '#86EFAC' : '#8C7B6A'}/>
      <rect x="14" y="15" width="2" height="2" fill={active ? '#86EFAC' : '#8C7B6A'}/>
    </svg>
  )
}

function IconFileNamer({ active }) {
  const c = active ? '#FF7030' : '#8C7B6A'
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" shapeRendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
      {/* Folder body */}
      <rect x="2" y="8" width="20" height="2" fill={c}/>
      <rect x="2" y="10" width="2" height="14" fill={c}/>
      <rect x="20" y="10" width="2" height="14" fill={c}/>
      <rect x="2" y="24" width="20" height="2" fill={c}/>
      {/* Folder tab */}
      <rect x="2" y="6" width="8" height="2" fill={c}/>
      <rect x="10" y="8" width="2" height="2" fill={c}/>
      {/* Pencil */}
      <rect x="16" y="14" width="2" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
      <rect x="14" y="16" width="2" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
      <rect x="12" y="18" width="2" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
      <rect x="10" y="20" width="2" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
      <rect x="18" y="12" width="2" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
      {/* Pencil tip */}
      <rect x="8" y="22" width="4" height="2" fill={active ? '#FCD34D' : '#8C7B6A'}/>
    </svg>
  )
}

export default function Sidebar({ page, setPage }) {
  const items = [
    { id: 'aprec',     label: 'AP Rec',      Icon: IconAPRec },
    { id: 'filenamer', label: 'File Namer',   Icon: IconFileNamer },
  ]

  return (
    <div style={{
      position: 'fixed',
      left: 0, top: 0, bottom: 0,
      width: 64,
      background: 'var(--surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      paddingTop: 24,
      gap: 8,
      zIndex: 100,
    }}>
      {items.map(({ id, label, Icon }) => {
        const active = page === id
        return (
          <button
            key={id}
            onClick={() => setPage(id)}
            title={label}
            style={{
              background: active ? 'rgba(255,112,48,0.1)' : 'transparent',
              border: active ? '1px solid var(--ox-b)' : '1px solid transparent',
              borderRadius: 4,
              width: 44,
              height: 44,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'background 0.15s, border-color 0.15s',
            }}
            onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(255,112,48,0.06)' }}
            onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
          >
            <Icon active={active} />
          </button>
        )
      })}

      {/* Vertical label at bottom */}
      <div style={{
        position: 'absolute',
        bottom: 16,
        fontSize: 9,
        fontFamily: 'var(--mono)',
        color: 'var(--muted)',
        letterSpacing: '0.1em',
        writingMode: 'vertical-rl',
        textOrientation: 'mixed',
        transform: 'rotate(180deg)',
        opacity: 0.4,
      }}>
        AP·REC
      </div>
    </div>
  )
}
