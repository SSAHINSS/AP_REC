import { useState, useEffect } from 'react'
import { isLoggedIn, logout, isAdmin, listUsers, createUser, deleteUser } from './api'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import AppPage from './pages/AppPage'
import FileNamerPage from './pages/FileNamerPage'
import TrendsPage from './pages/TrendsPage'
import PayrollPage from './pages/PayrollPage'
import Sidebar from './components/Sidebar'
import AnimatedLogo from './components/AnimatedLogo'
import FileNamerLogo from './components/FileNamerLogo'
import TrendsLogo from './components/TrendsLogo'
import HomeLogo from './components/HomeLogo'
import PayrollLogo from './components/PayrollLogo'
import './index.css'

// Shared sticky header — identical layout on every page
function SharedHeader({ page, onLogout, theme, onToggleTheme, onOpenUsers }) {
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
      borderBottom: page === 'filenamer' ? 'none' : `1px solid color-mix(in srgb, var(--text) ${Math.round(p * 8)}%, transparent)`,
      padding: '12px 24px',
      height: 84,
      display: 'flex',
      alignItems: 'center',
    }}>

      {/* Logo area — same bounding box always */}
      <div style={{ flex: 1, position: 'relative', height: 60, display: 'flex', alignItems: 'center' }}>

        {/* HOME: static left logo + subtitle */}
        {page === 'home' && (
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
            <HomeLogo width={244} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>AP Rec Site</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 400, color: 'var(--muted)', margin: 0 }}>upload once · analyze everywhere</p>
            </div>
          </div>
        )}

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

        {/* TRENDS: static text title + subtitle */}
        {page === 'trends' && (
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
            <TrendsLogo width={804} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>Expense Trends</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 400, color: 'var(--muted)', margin: 0 }}>vendors · credit cards · flags</p>
            </div>
          </div>
        )}

        {/* PAYROLL: static left logo + subtitle */}
        {page === 'payroll' && (
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
            <PayrollLogo width={422} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>Payroll</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 400, color: 'var(--muted)', margin: 0 }}>accruals · trends</p>
            </div>
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
        <button
          className="btn btn-icon"
          title="Toggle light / dark theme"
          onClick={onToggleTheme}
          style={{ padding: '2px 10px', fontSize: 10 }}
        >
          {theme === 'light' ? 'Dark' : 'Light'}
        </button>
        {isAdmin() && (
          <button
            className="btn btn-icon"
            onClick={onOpenUsers}
            style={{ padding: '2px 10px', fontSize: 10 }}
          >
            Users
          </button>
        )}
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

function UsersModal({ onClose }) {
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [makeAdmin, setMakeAdmin] = useState(false)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const refresh = () => listUsers().then(setUsers).catch(e => setErr(e.message))
  useEffect(() => { refresh() }, [])

  async function add() {
    setErr(''); setBusy(true)
    try {
      await createUser(email.trim(), password, makeAdmin)
      setEmail(''); setPassword(''); setMakeAdmin(false)
      refresh()
    } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }
  async function remove(id) {
    setErr('')
    try { await deleteUser(id); refresh() } catch (e) { setErr(e.message) }
  }

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, zIndex: 300,
      background: 'rgba(0,0,0,0.55)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div onClick={e => e.stopPropagation()} className="card"
           style={{ width: '100%', maxWidth: 460, background: 'var(--surface)',
                    border: '1px solid var(--border)', borderRadius: 6, padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 14 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ox)',
                         letterSpacing: '0.1em', textTransform: 'uppercase' }}>Users</span>
          <span style={{ flex: 1 }} />
          <button className="btn btn-icon" onClick={onClose} style={{ padding: '2px 10px', fontSize: 10 }}>Close</button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 16 }}>
          {users.map(u => (
            <div key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 8,
                                     fontFamily: 'var(--mono)', fontSize: 12 }}>
              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{u.email}</span>
              {u.is_admin && <span style={{ fontSize: 9, color: 'var(--ox)' }}>ADMIN</span>}
              <button className="btn btn-icon" onClick={() => remove(u.id)}
                      style={{ padding: '1px 8px', fontSize: 10 }}>remove</button>
            </div>
          ))}
        </div>

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14,
                      display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div className="input-wrap"><input type="email" placeholder="new user email"
               value={email} onChange={e => setEmail(e.target.value)} /></div>
          <div className="input-wrap"><input type="text" placeholder="temporary password (6+ chars)"
               value={password} onChange={e => setPassword(e.target.value)} /></div>
          <label style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)',
                          display: 'flex', gap: 6, alignItems: 'center', cursor: 'pointer' }}>
            <input type="checkbox" checked={makeAdmin} onChange={e => setMakeAdmin(e.target.checked)} />
            admin (can manage users)
          </label>
          <button className="btn btn-primary" disabled={busy || !email || password.length < 6}
                  onClick={add}>Add user</button>
          {err && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 11 }}>{err}</div>}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [authed,  setAuthed]  = useState(isLoggedIn)
  const [page,    setPage]    = useState(() => localStorage.getItem('ap_page') || 'home')
  const [visible, setVisible] = useState(true)
  const [theme,   setTheme]   = useState(() => localStorage.getItem('ap_theme') || 'dark')
  const [usersOpen, setUsersOpen] = useState(false)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('ap_theme', theme)
  }, [theme])

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

        <SharedHeader page={page} onLogout={() => setAuthed(false)}
                      theme={theme}
                      onToggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
                      onOpenUsers={() => setUsersOpen(true)} />
        {usersOpen && <UsersModal onClose={() => setUsersOpen(false)} />}

        {/* Page content with fade transition */}
        <div style={{
          flex: 1,
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(6px)',
          transition: 'opacity 0.22s ease, transform 0.22s ease',
        }}>
          {page === 'home'
            ? <HomePage go={switchPage} />
            : page === 'aprec'
              ? <AppPage />
              : page === 'filenamer'
                ? <FileNamerPage />
                : page === 'payroll'
                  ? <PayrollPage />
                  : <TrendsPage />
          }
        </div>

      </div>
    </div>
  )
}
