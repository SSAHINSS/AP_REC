import { useState } from 'react'
import { isLoggedIn } from './api'
import LoginPage from './pages/LoginPage'
import AppPage from './pages/AppPage'
import './index.css'

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn)

  return authed
    ? <AppPage onLogout={() => setAuthed(false)} />
    : <LoginPage onLogin={() => setAuthed(true)} />
}
