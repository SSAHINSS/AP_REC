import { useState, useEffect } from 'react'
import { isLoggedIn, logout } from './api'
import LoginPage from './pages/LoginPage'
import AppPage from './pages/AppPage'
import FileNamerPage from './pages/FileNamerPage'
import Sidebar from './components/Sidebar'
import AnimatedLogo from './components/AnimatedLogo'
import FileNamerLogo from './components/FileNamerLogo'
import './index.css'

// Shared sticky header — identical layout on every page
function SharedHeader({ page, onLogout }) {
  const [scrollY,     setScrollY]     = useState(0)
  const [leftHovered, setLeftHovered] = useState(false)
  const [centHovered, setCentHovered] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // AP-REC scroll animation — only active on aprec page
  const p            = page === 'aprec' ? Math.min(scrollY / 120, 1) : 0
  const leftOpacity  = Math.max(0, 1 - p * 2.5)
  const leftBlur     = p * 8
  const centOpacity  = Math.max(0, (p - 0.3) / 0.7)
  const centBlur     = (1 - p) * 8
  const scrollTop    = () => window.scrollTo({ top: 0, behavior: 'smooth' })

  return (
    <div style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'var(--bg)',
      borderBottom: `1px solid rgba(255,255,255,${Math.max(p * 0.08, page === 'filenamer' ? 0.05 : 0)})`,
      padding: '12px 24px',
      height: 84,
      display: 'flex',
      alignItems: 'center',
    }}>

      {/* Logo area — same bounding box always */}
      <div style={{ flex: 1, position: 'relative', height: 60, display: 'flex', alignItems: 'center' }}>

        {/* AP-REC: left logo (fades out on scroll) */}
        {page === 'aprec' && (
          <div
            onClick={scrollTop}
            onMouseEnter={() => setLeftHovered(true)}
            onMouseLeave={() => setLeftHovered(false)}
            style={{
              display: 'flex', alignItems: 'center', gap: 16,
              opacity: leftOpacity, filter: `blur(${leftBlur}px)`,
              transform: `scale(${leftHovered ? 1.03 : 1})`,
              pointerEvents: p < 0.5 ? 'auto' : 'none',
              cursor: 'pointer',
              transition: 'transform 0.18s cubic-bezier(0.34,1.56,0.64,1)',
              userSelect: 'none',
            }}
          >
            <AnimatedLogo width={320} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>AP Reconciliation</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 400, color: 'var(--muted)', margin: 0 }}>vendor statement processor</p>
            </div>
          </div>
        )}

        {/* AP-REC: center logo (fades in on scroll) */}
        {page === 'aprec' && (
          <div
            onClick={scrollTop}
            onMouseEnter={() => setCentHovered(true)}
            onMouseLeave={() => setCentHovered(false)}
            style={{
              position: 'absolute', left: '50%',
              transform: `translateX(-50%) scale(${centHovered ? 1.09 : 1})`,
              opacity: centOpacity, filter: `blur(${centBlur}px)`,
              pointerEvents: p > 0.5 ? 'auto' : 'none',
              cursor: 'pointer',
              transition: 'transform 0.2s cubic-bezier(0.34,1.56,0.64,1)',
              zIndex: 10, userSelect: 'none',
            }}
          >
            <AnimatedLogo width={120} quick={true} />
          </div>
        )}

        {/* FILE-NMR: static left logo + subtitle */}
        {page === 'filenamer' && (
          <div
            onClick={scrollTop}
            onMouseEnter={() => setLeftHovered(true)}
            onMouseLeave={() => setLeftHovered(false)}
            style={{
              display: 'flex', alignItems: 'center', gap: 16,
              transform: `scale(${leftHovered ? 1.03 : 1})`,
              cursor: 'pointer',
              transition: 'transform 0.18s cubic-bezier(0.34,1.56,0.64,1)',
              userSelect: 'none',
            }}
          >
            <FileNamerLogo width={460} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>File Namer</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 400, color: 'var(--muted)', margin: 0 }}>vendor file renaming</p>
            </div>
          </div>
        )}
      </div>

      {/* Auth controls — NEVER MOVE, always right side */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        flexShrink: 0,
        opacity: Math.max(0.25, 1 - p * 0.85),
      }}>
        <span className="badge">Authenticated</span>
        <button
          className="btn btn-icon"
          onClick={() => { logout(); onLogout() }}
          style={{ padding: '2px 10px', fontSize: 10 }}
        >
          Sign out
        </button>
      </div>

    </div>
  )
}

export default function App() {
  const [authed,  setAuthed]  = useState(isLoggedIn)
  const [page,    setPage]    = useState(() => localStorage.getItem('ap_page') || 'aprec')
  const [visible, setVisible] = useState(true)

  function switchPage(newPage) {
    if (newPage === page) return
    setVisible(false)
    setTimeout(() => { setPage(newPage); localStorage.setItem('ap_page', newPage); setVisible(true) }, 220)
  }

  if (!authed) return <LoginPage onLogin={() => setAuthed(true)} />

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar page={page} setPage={switchPage} />
      <div style={{ marginLeft: 64, flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>

        <SharedHeader page={page} onLogout={() => setAuthed(false)} />

        {/* Page content with fade transition */}
        <div style={{
          flex: 1,
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(6px)',
          transition: 'opacity 0.22s ease, transform 0.22s ease',
        }}>
          {page === 'aprec'
            ? <AppPage />
            : <FileNamerPage />
          }
        </div>

      </div>
    </div>
  )
}
