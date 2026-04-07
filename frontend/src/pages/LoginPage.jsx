import { useState } from 'react'
import { login } from '../api'
import AnimatedLogo from '../components/AnimatedLogo'

export default function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(password)
      onLogin()
    } catch {
      setError('Incorrect password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 32,
      padding: 24,
    }}>
      {/* Clickable logo — scrolls to top */}
      <div
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        style={{ cursor: 'pointer' }}
      >
        <AnimatedLogo width={200} />
      </div>

      <div style={{ textAlign: 'center' }}>
        <h1 style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.02em' }}>
          AP Reconciliation
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 6, fontFamily: 'var(--mono)' }}>
          vendor statement processor
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 360 }}>
        <div className="input-wrap" style={{ marginBottom: 12 }}>
          <input
            type={show ? 'text' : 'password'}
            placeholder="enter password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            autoFocus
          />
          <button type="button" onClick={() => setShow(s => !s)}>
            {show ? '🙈' : '👁'}
          </button>
        </div>

        {error && (
          <div style={{
            color: '#F87171',
            fontFamily: 'var(--mono)',
            fontSize: 12,
            marginBottom: 12,
            textAlign: 'center',
          }}>
            {error}
          </div>
        )}

        <button
          className="btn btn-primary"
          type="submit"
          disabled={loading || !password}
        >
          {loading ? 'Checking…' : 'Enter →'}
        </button>
      </form>
    </div>
  )
}
