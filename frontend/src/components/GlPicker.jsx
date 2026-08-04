import { useState, useEffect } from 'react'
import { glStatus, uploadGl, deleteGlOverride } from '../api'
import DropZone from './DropZone'

// Per-module GL control. Default: the user's shared GL (upload once, every
// module reads it). Optionally: a module-specific GL that overrides shared
// for THIS module only, revertable anytime. All strictly per-user.
export default function GlPicker({ module, moduleLabel, onChanged }) {
  const [status, setStatus]   = useState(null)
  const [uploadTo, setUploadTo] = useState(null)   // null | 'shared' | module
  const [files, setFiles]     = useState([])
  const [busy, setBusy]       = useState(false)
  const [err, setErr]         = useState('')

  const refresh = () => glStatus().then(setStatus).catch(() => {})
  useEffect(() => { refresh() }, [])

  const shared = status?.shared
  const override = status?.overrides?.[module]
  const active = override || shared     // what this module will actually use

  async function doUpload() {
    if (!files[0]) return
    setBusy(true); setErr('')
    try {
      await uploadGl(files[0], uploadTo)
      setFiles([]); setUploadTo(null)
      await refresh()
      onChanged && onChanged()
    } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }
  async function revert() {
    setBusy(true); setErr('')
    try {
      await deleteGlOverride(module)
      await refresh()
      onChanged && onChanged()
    } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }

  const when = ts => ts ? new Date(ts).toLocaleString() : ''

  return (
    <div className="card" style={{ padding: '10px 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px 16px',
                    fontFamily: 'var(--mono)', fontSize: 11 }}>
        <span style={{ fontSize: 10, color: 'var(--ox)', letterSpacing: '0.1em',
                       textTransform: 'uppercase' }}>GL Source</span>

        {active ? (
          <>
            <span>
              {override
                ? <><b style={{ color: 'var(--ox)' }}>{moduleLabel}-specific:</b> <b>{override.filename}</b></>
                : <>shared GL: <b>{shared.filename}</b></>}
            </span>
            <span style={{ color: 'var(--muted)' }}>updated {when((override || shared).uploaded_at)}</span>
          </>
        ) : (
          <span style={{ color: 'var(--warn)' }}>
            No GL on file for your account — upload one to use {moduleLabel}.
          </span>
        )}

        <span style={{ flex: 1 }} />
        <button className="btn btn-icon" style={{ padding: '2px 10px', fontSize: 10 }}
                onClick={() => { setUploadTo(uploadTo === 'shared' ? null : 'shared'); setFiles([]) }}>
          {uploadTo === 'shared' ? 'Cancel' : shared ? 'Update shared GL' : 'Upload shared GL'}
        </button>
        <button className="btn btn-icon" style={{ padding: '2px 10px', fontSize: 10 }}
                onClick={() => { setUploadTo(uploadTo === module ? null : module); setFiles([]) }}>
          {uploadTo === module ? 'Cancel' : `Use different GL for ${moduleLabel} only`}
        </button>
        {override && (
          <button className="btn btn-icon" style={{ padding: '2px 10px', fontSize: 10, color: 'var(--warn)' }}
                  disabled={busy} onClick={revert}>
            Revert to shared GL
          </button>
        )}
      </div>

      {uploadTo && (
        <div style={{ marginTop: 12 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', marginBottom: 8 }}>
            {uploadTo === 'shared'
              ? 'This replaces YOUR shared GL — every module reading the shared GL will use it. Other users are unaffected; each account has its own GLs.'
              : `This GL applies to ${moduleLabel} ONLY — other modules keep using your shared GL.`}
          </div>
          <DropZone label="Drop GL CSV here" accept={['csv']} files={files} onChange={setFiles} />
          <button className="btn btn-primary" disabled={!files.length || busy}
                  onClick={doUpload} style={{ marginTop: 10 }}>
            {busy ? 'Uploading…' : 'Upload →'}
          </button>
          {err && <div style={{ color: 'var(--err)', fontFamily: 'var(--mono)', fontSize: 11, marginTop: 8 }}>{err}</div>}
        </div>
      )}
    </div>
  )
}
