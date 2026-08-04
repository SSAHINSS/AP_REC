import { useState, useEffect, Fragment } from 'react'
import { isLoggedIn, logout, isAdmin, listUsers, createUser, deleteUser, updateUser, getPerms } from './api'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import AppPage from './pages/AppPage'
import FileNamerPage from './pages/FileNamerPage'
import AccrualPage from './pages/AccrualPage'
import AccrualLogo from './components/AccrualLogo'
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
            </div>
          </div>
        )}

        {/* ACCRUALS: static left logo + subtitle (matches the other modules) */}
        {page === 'accruals' && (
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
            <AccrualLogo width={474} quick={true} />
            <div style={{
              animation: 'taglinePop 0.3s ease forwards',
              animationDelay: '0.32s',
              opacity: 0,
            }}>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--text)', margin: 0 }}>Accrual Builder</p>
              <p style={{ fontSize: 9, fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--warn)', margin: 0 }}>experimental</p>
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

const MODULE_DEFS = [
  { id: 'aprec',     label: 'AP Rec' },
  { id: 'trends',    label: 'Expense Trends' },
  { id: 'payroll',   label: 'Payroll' },
  { id: 'filenamer', label: 'File Namer' },
  { id: 'accruals',  label: 'Accruals' },
]

function UsersModal({ onClose }) {
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [makeAdmin, setMakeAdmin] = useState(false)
  const [newPerms, setNewPerms] = useState(MODULE_DEFS.map(m => m.id))
  const [resetFor, setResetFor] = useState(null)   // user id with reset row open
  const [resetPw, setResetPw] = useState('')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  const refresh = () => listUsers().then(setUsers).catch(e => setErr(e.message))
  useEffect(() => { refresh() }, [])

  async function add() {
    setErr(''); setMsg(''); setBusy(true)
    try {
      await createUser(email.trim(), password, makeAdmin, newPerms)
      setEmail(''); setPassword(''); setMakeAdmin(false); setNewPerms(MODULE_DEFS.map(m => m.id))
      refresh()
    } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }
  async function remove(id) {
    if (!window.confirm('Remove this user? Their saved GL is deleted too.')) return
    setErr(''); setMsg('')
    try { await deleteUser(id); refresh() } catch (e) { setErr(e.message) }
  }
  async function togglePerm(u, mod) {
    setErr(''); setMsg('')
    const cur = u.permissions || []
    const next = cur.includes(mod) ? cur.filter(p => p !== mod) : [...cur, mod]
    try { await updateUser(u.id, { permissions: next }); refresh() }
    catch (e) { setErr(e.message) }
  }
  async function doReset(u) {
    setErr(''); setMsg('')
    try {
      await updateUser(u.id, { password: resetPw })
      setMsg(`Password reset for ${u.email}`)
      setResetFor(null); setResetPw('')
    } catch (e) { setErr(e.message) }
  }

  // Close ONLY via the Close button or Escape — stray clicks (or releasing a
  // text-selection outside the card) must never dismiss the panel mid-edit.
  useEffect(() => {
    const onKey = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 300,
      background: 'rgba(0,0,0,0.55)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div className="card"
           style={{ width: '100%', maxWidth: 860, maxHeight: '86vh', overflow: 'auto',
                    background: 'var(--surface)',
                    border: '1px solid var(--border)', borderRadius: 6, padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 14 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ox)',
                         letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            User Management — {users.length} active
          </span>
          <span style={{ flex: 1 }} />
          <button className="btn btn-icon" onClick={onClose} style={{ padding: '2px 10px', fontSize: 10 }}>Close</button>
        </div>

        <table style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'var(--mono)', fontSize: 11 }}>
          <thead><tr>
            <th style={uth({ textAlign: 'left' })}>USER</th>
            {MODULE_DEFS.map(m => <th key={m.id} style={uth({})}>{m.label.toUpperCase()}</th>)}
            <th style={uth({})}>ROLE</th>
            <th style={uth({})}>ACTIONS</th>
          </tr></thead>
          <tbody>
            {users.map((u, i) => (
              <Fragment key={u.id}>
              <tr style={{ background: i % 2 ? 'transparent' : 'var(--stripe)' }}>
                <td style={utd({ textAlign: 'left' })}>
                  {u.email}
                  {u.created_at && <div style={{ fontSize: 9, color: 'var(--muted)' }}>
                    since {new Date(u.created_at).toLocaleDateString()}</div>}
                </td>
                {MODULE_DEFS.map(m => (
                  <td key={m.id} style={utd({})}>
                    <input type="checkbox"
                           checked={u.is_admin || (u.permissions || []).includes(m.id)}
                           disabled={u.is_admin}
                           title={u.is_admin ? 'Admins always have every module' : `Toggle ${m.label}`}
                           onChange={() => togglePerm(u, m.id)}
                           style={{ cursor: u.is_admin ? 'not-allowed' : 'pointer' }} />
                  </td>
                ))}
                <td style={utd({})}>
                  {u.is_admin
                    ? <span style={{ color: 'var(--ox)', fontSize: 10 }}>ADMIN</span>
                    : <span style={{ color: 'var(--muted)', fontSize: 10 }}>user</span>}
                </td>
                <td style={utd({ whiteSpace: 'nowrap' })}>
                  <button className="btn btn-icon" style={{ padding: '1px 8px', fontSize: 10, marginRight: 6 }}
                          onClick={() => { setResetFor(resetFor === u.id ? null : u.id); setResetPw('') }}>
                    reset pw
                  </button>
                  <button className="btn btn-icon" style={{ padding: '1px 8px', fontSize: 10 }}
                          onClick={() => remove(u.id)}>remove</button>
                </td>
              </tr>
              {resetFor === u.id && (
                <tr>
                  <td colSpan={MODULE_DEFS.length + 3} style={{ padding: '6px 8px' }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <div className="input-wrap" style={{ flex: 1, maxWidth: 320 }}>
                        <input type="text" placeholder={`new password for ${u.email} (6+ chars)`}
                               value={resetPw} onChange={e => setResetPw(e.target.value)} />
                      </div>
                      <button className="btn btn-primary" disabled={resetPw.length < 6}
                              onClick={() => doReset(u)} style={{ padding: '4px 14px', fontSize: 11 }}>
                        Set password
                      </button>
                    </div>
                  </td>
                </tr>
              )}
              </Fragment>
            ))}
          </tbody>
        </table>

        {msg && <div style={{ color: 'var(--ok)', fontFamily: 'var(--mono)', fontSize: 11, marginTop: 10 }}>{msg}</div>}
        {err && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 11, marginTop: 10 }}>{err}</div>}

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14, marginTop: 16,
                      display: 'flex', flexDirection: 'column', gap: 8 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)',
                         textTransform: 'uppercase', letterSpacing: '0.08em' }}>Add user</span>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <div className="input-wrap" style={{ flex: 1, minWidth: 220 }}>
              <input type="email" placeholder="email"
                   value={email} onChange={e => setEmail(e.target.value)} /></div>
            <div className="input-wrap" style={{ flex: 1, minWidth: 200 }}>
              <input type="text" placeholder="temporary password (6+ chars)"
                   value={password} onChange={e => setPassword(e.target.value)} /></div>
          </div>
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'center',
                        fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)' }}>
            {MODULE_DEFS.map(m => (
              <label key={m.id} style={{ display: 'flex', gap: 5, alignItems: 'center', cursor: 'pointer' }}>
                <input type="checkbox" checked={makeAdmin || newPerms.includes(m.id)} disabled={makeAdmin}
                       onChange={() => setNewPerms(p => p.includes(m.id) ? p.filter(x => x !== m.id) : [...p, m.id])} />
                {m.label}
              </label>
            ))}
            <label style={{ display: 'flex', gap: 5, alignItems: 'center', cursor: 'pointer', color: 'var(--ox)' }}>
              <input type="checkbox" checked={makeAdmin} onChange={e => setMakeAdmin(e.target.checked)} />
              admin (all modules + manage users)
            </label>
          </div>
          <button className="btn btn-primary" disabled={busy || !email || password.length < 6}
                  onClick={add} style={{ alignSelf: 'flex-start' }}>Add user</button>
        </div>
      </div>
    </div>
  )
}

const uth = extra => ({ padding: '6px 8px', textAlign: 'center', fontWeight: 600, fontSize: 9,
  letterSpacing: '0.06em', color: 'var(--muted)', borderBottom: '1px solid var(--border)',
  whiteSpace: 'nowrap', ...extra })
const utd = extra => ({ padding: '6px 8px', textAlign: 'center', ...extra })

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
                  : page === 'accruals'
                    ? <AccrualPage />
                    : <TrendsPage />
          }
        </div>

      </div>
    </div>
  )
}
