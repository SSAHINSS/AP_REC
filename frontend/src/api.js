const BASE = import.meta.env.VITE_API_URL || '/api'

function getToken() {
  return localStorage.getItem('ap_token')
}

// A 401 means the sign-in token is stale or expired (e.g. after an auth
// upgrade). Clear it and send the person back to the login screen instead
// of failing with a dead "Unauthorized".
function checkAuth(res) {
  if (res.status === 401) {
    logout()
    window.location.reload()
    throw new Error('Session expired — please sign in again')
  }
  return res
}

export async function login(email, password) {
  const res = await fetch(`${BASE}/auth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error('Wrong email or password')
  const data = await res.json()
  localStorage.setItem('ap_token', data.token)
  localStorage.setItem('ap_email', data.email)
  localStorage.setItem('ap_is_admin', data.is_admin ? '1' : '')
  return data
}

export function logout() {
  localStorage.removeItem('ap_token')
  localStorage.removeItem('ap_email')
  localStorage.removeItem('ap_is_admin')
}

export function isLoggedIn() {
  return !!getToken()
}

export function currentEmail() { return localStorage.getItem('ap_email') || '' }
export function isAdmin() { return localStorage.getItem('ap_is_admin') === '1' }

async function authedJson(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      ...(opts.headers || {}),
      Authorization: `Bearer ${getToken()}`,
      ...(opts.body && typeof opts.body === 'string' ? { 'Content-Type': 'application/json' } : {}),
    },
  })
  checkAuth(res)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

// ── User management (admin) ──
export function listUsers()            { return authedJson('/users') }
export function createUser(email, password, isAdminFlag = false) {
  return authedJson('/users', { method: 'POST', body: JSON.stringify({ email, password, is_admin: isAdminFlag }) })
}
export function deleteUser(id)         { return authedJson(`/users/${id}`, { method: 'DELETE' }) }

// ── Stored GL ──
export function glStatus()             { return authedJson('/gl/status') }

export async function uploadGl(glFile) {
  const form = new FormData()
  form.append('gl_file', glFile)
  const res = await fetch(`${BASE}/gl/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })
  checkAuth(res)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
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

  checkAuth(res)
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

// glFile may be null — the backend then uses your stored GL.
export async function analyzeTrends(glFile, entity = '', view = 'vendor', period = '') {
  const form = new FormData()
  if (glFile) form.append('gl_file', glFile)
  form.append('entity', entity)
  form.append('view', view)
  form.append('period', period)

  const res = await fetch(`${BASE}/trends/analyze`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })

  checkAuth(res)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Trends analysis failed')
  }
  return res.json()
}

// glFile optional — omit to use your saved GL.
export async function payrollAccrual(monthEnd, entity = '', overrides = {}) {
  const form = new FormData()
  form.append('month_end', monthEnd)
  form.append('entity', entity)
  form.append('overrides', JSON.stringify(overrides))

  const res = await fetch(`${BASE}/payroll/accrual`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })
  checkAuth(res)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Payroll accrual failed')
  }
  return res.json()
}

export async function payrollTrends(entity = '', period = '') {
  const form = new FormData()
  form.append('entity', entity)
  form.append('period', period)

  const res = await fetch(`${BASE}/payroll/trends`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
  })
  checkAuth(res)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Payroll trends failed')
  }
  return res.json()
}
