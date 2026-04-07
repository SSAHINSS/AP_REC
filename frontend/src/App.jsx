import { useState } from 'react'
import { isLoggedIn } from './api'
import LoginPage from './pages/LoginPage'
import AppPage from './pages/AppPage'
import FileNamerPage from './pages/FileNamerPage'
import Sidebar from './components/Sidebar'
import './index.css'

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn)
  const [page,   setPage]   = useState('aprec')

  if (!authed) return <LoginPage onLogin={() => setAuthed(true)} />

  return (
    <div style={{ display: 'flex' }}>
      <Sidebar page={page} setPage={setPage} />
      <div style={{ marginLeft: 64, flex: 1, minWidth: 0 }}>
        {page === 'aprec'
          ? <AppPage     onLogout={() => setAuthed(false)} />
          : <FileNamerPage onLogout={() => setAuthed(false)} />
        }
      </div>
    </div>
  )
}
