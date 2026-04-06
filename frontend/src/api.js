const BASE = import.meta.env.VITE_API_URL || '/api'

function getToken() {
  return localStorage.getItem('ap_token')
}

export async function login(password) {
  const res = await fetch(`${BASE}/auth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  if (!res.ok) throw new Error('Wrong password')
  const { token } = await res.json()
  localStorage.setItem('ap_token', token)
  return token
}

export function logout() {
  localStorage.removeItem('ap_token')
}

export function isLoggedIn() {
  return !!getToken()
}

export async function reconcile(glFile, statementFiles, onLog) {
  const form = new FormData()
  form.append('gl_file', glFile)
  for (const f of statementFiles) form.append('statements', f)

  const res = await fetch(`${BASE}/reconcile`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Reconciliation failed')
  }

  const data = await res.json()
  if (onLog && data.logs) data.logs.forEach(onLog)
  return data
}

export function downloadUrl(jobId) {
  return `${BASE}/download/${jobId}`
}

export function downloadFile(jobId) {
  const a = document.createElement('a')
  a.href = downloadUrl(jobId)
  a.setAttribute('Authorization', `Bearer ${getToken()}`)
  // Use fetch + blob for authenticated download
  fetch(downloadUrl(jobId), {
    headers: { Authorization: `Bearer ${getToken()}` }
  })
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob)
      a.href = url
      a.download = 'AP_REC_result.xlsx'
      a.click()
      URL.revokeObjectURL(url)
    })
}
