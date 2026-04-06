"""
AP Reconciliation — Streamlit Interface
UI layer only. All reconciliation logic lives in reconciliation_engine.py.
"""
import os, io, base64, tempfile, shutil
import streamlit as st
import streamlit.components.v1 as _stc
from reconciliation_engine import run_reconciliation


# ══════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG & GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="AP · Reconciliation",
        page_icon="◈",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
    :root {
        --bg:          #1A1D21;
        --surface:     #22262D;
        --surface-hi:  #292E38;
        --teal:        #2DD4BF;
        --teal-dim:    #14B8A6;
        --teal-glow:   rgba(45,212,191,0.10);
        --teal-border: rgba(45,212,191,0.50);
        --text:        #CDD5E0;
        --text-bright: #E8EDF3;
        --muted:       #6B7A8D;
        --dim:         #3A4255;
        --border:      #252C3A;
        --orange:      #FF6B00;
        --mono: 'JetBrains Mono', monospace;
        --sans: 'IBM Plex Sans', system-ui, sans-serif;
    }
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stHeader"] { display:none !important; }
    .stApp, [data-testid="stAppViewContainer"] { background-color: var(--bg) !important; }
    .main .block-container {
        background-color: var(--bg) !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 680px !important;
    }
    /* Run button */
    .stButton > button {
        background: transparent !important;
        border: 2px solid var(--teal-dim) !important;
        color: var(--teal) !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 14px 24px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover:not(:disabled) {
        background: var(--teal-glow) !important;
        border-color: var(--teal) !important;
        box-shadow: 0 0 20px var(--teal-glow) !important;
    }
    .stButton > button:disabled {
        border-color: var(--dim) !important;
        color: var(--dim) !important;
        opacity: 1 !important;
    }
    /* Download button */
    [data-testid="stDownloadButton"] > button {
        background: var(--teal-dim) !important;
        border: none !important;
        color: #081413 !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 15px 24px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: var(--teal) !important;
        box-shadow: 0 0 28px var(--teal-glow) !important;
    }
    /* Password input */
    .stTextInput > div > div > input {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 2px !important;
        color: var(--teal) !important;
        font-family: var(--mono) !important;
        font-size: 14px !important;
        caret-color: var(--teal) !important;
        padding: 10px 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--teal-dim) !important;
        box-shadow: 0 0 0 1px var(--teal-dim), 0 0 14px var(--teal-glow) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--dim) !important; }
    [data-testid="stSpinner"] > div { border-top-color: var(--teal) !important; }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--teal-dim); }
    .stApp p, .stApp div, .stApp span, .stApp label,
    .stMarkdown { color: var(--text) !important; font-family: var(--sans) !important; }
    </style>
    """)

    # ── Helpers ──────────────────────────────────────────────────────────
    def section(num, title, hint=""):
        hint_html = (f'<span style="font-family:var(--sans);font-size:12px;'
                     f'color:#3A4255;font-weight:300;margin-left:10px;">{hint}</span>') if hint else ""
        st.html(f"""<div style="margin-bottom:10px;display:flex;align-items:center;">
            <span style="font-family:var(--mono);font-size:10px;color:#3A4255;letter-spacing:0.2em;">// {num}</span>
            <span style="font-family:var(--mono);font-size:12px;font-weight:600;color:#CDD5E0;
                         letter-spacing:0.1em;text-transform:uppercase;margin-left:12px;">{title}</span>
            {hint_html}</div>""")

    def gap(px=24):
        st.html(f'<div style="margin-bottom:{px}px;"></div>')

    # ── Header ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-bottom:1px solid #252C3A;padding-bottom:20px;margin-bottom:36px;">
        <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:5px;">
            <span style="font-family:var(--mono);font-size:21px;font-weight:700;color:#2DD4BF;">◈ AP·REC</span>
            <span style="font-family:var(--mono);font-size:10px;color:#3A4255;letter-spacing:0.18em;text-transform:uppercase;">v5.0</span>
        </div>
        <div style="font-family:var(--sans);font-size:13px;color:#6B7A8D;font-weight:300;">
            vendor statement reconciliation processor
        </div>
    </div>
    """)

    # ── 01  Access Key ────────────────────────────────────────────────────
    section("01", "Access Key")
    password = st.text_input("key", type="password",
                             placeholder="enter access key…",
                             label_visibility="collapsed")
    if password != "reconcile2026":
        if password:
            st.html('<div style="font-family:var(--mono);font-size:12px;color:#F87171;margin-top:6px;">✕&nbsp;&nbsp;incorrect key</div>')
        else:
            st.html('<div style="font-family:var(--mono);font-size:12px;color:#3A4255;margin-top:6px;">─&nbsp;&nbsp;awaiting authentication</div>')
        st.stop()
    st.html('<div style="font-family:var(--mono);font-size:12px;color:#2DD4BF;margin-top:6px;">✓&nbsp;&nbsp;authenticated</div>')
    gap(32)

    # ── 02 & 03  Custom drag-and-drop file zones ──────────────────────────
    # Pure HTML/CSS/JS uploader — zero Streamlit widget quirks
    upload_result = _stc.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: transparent; font-family: 'JetBrains Mono', monospace; }

        .zone-wrap { margin-bottom: 28px; }
        .zone-label {
            font-size: 10px; color: #3A4255; letter-spacing: 0.2em;
            text-transform: uppercase; margin-bottom: 6px; display: flex; align-items: center; gap: 12px;
        }
        .zone-label b { font-size: 12px; color: #CDD5E0; letter-spacing: 0.1em; }
        .zone-label span { font-size: 11px; color: #3A4255; font-weight: 300; letter-spacing: 0.05em; text-transform: none; }

        .dropzone {
            border: 2px solid #252C3A;
            border-radius: 3px;
            background: #22262D;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.2s, background 0.2s;
            min-height: 80px;
            display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 8px;
        }
        .dropzone:hover, .dropzone.over {
            border-color: rgba(45,212,191,0.5);
            background: #292E38;
        }
        .dropzone .hint {
            font-size: 11px; color: #6B7A8D; letter-spacing: 0.05em;
        }
        .dropzone .browse-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
            background: transparent; border: 1px solid #3A4255;
            color: #CDD5E0; padding: 6px 14px; border-radius: 2px;
            cursor: pointer; transition: all 0.15s; margin-top: 4px;
        }
        .dropzone .browse-btn:hover { border-color: #2DD4BF; color: #2DD4BF; }

        .file-list { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; }
        .file-chip {
            display: flex; align-items: center; justify-content: space-between;
            background: #1A1D21; border: 1px solid #252C3A; border-radius: 2px;
            padding: 6px 10px; font-size: 11px; color: #CDD5E0;
        }
        .file-chip .fname { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .file-chip .fsize { color: #6B7A8D; font-size: 10px; margin: 0 10px; white-space: nowrap; }
        .file-chip .remove {
            background: transparent; border: 1px solid #3A4255;
            color: #6B7A8D; width: 18px; height: 18px; border-radius: 2px;
            cursor: pointer; font-size: 10px; line-height: 1;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: all 0.15s;
        }
        .file-chip .remove:hover { border-color: #F87171; color: #F87171; }
        .count-line { font-size: 12px; color: #2DD4BF; margin-top: 6px; }
    </style>
    </head>
    <body>

    <div class="zone-wrap">
        <div class="zone-label">
            <span>// 02</span>
            <b>GL EXPORT</b>
            <span>accepts .csv</span>
        </div>
        <div class="dropzone" id="gl-zone" onclick="document.getElementById('gl-input').click()">
            <div class="hint">drag & drop or click to browse</div>
            <button class="browse-btn" onclick="event.stopPropagation();document.getElementById('gl-input').click()">Browse files</button>
        </div>
        <input type="file" id="gl-input" accept=".csv" style="display:none">
        <div class="file-list" id="gl-list"></div>
    </div>

    <div class="zone-wrap">
        <div class="zone-label">
            <span>// 03</span>
            <b>VENDOR STATEMENTS</b>
            <span>accepts .pdf · .xlsx · multiple files OK</span>
        </div>
        <div class="dropzone" id="stmt-zone" onclick="document.getElementById('stmt-input').click()">
            <div class="hint">drag & drop or click to browse — select all files at once</div>
            <button class="browse-btn" onclick="event.stopPropagation();document.getElementById('stmt-input').click()">Browse files</button>
        </div>
        <input type="file" id="stmt-input" accept=".pdf,.xlsx" multiple style="display:none">
        <div class="file-list" id="stmt-list"></div>
        <div class="count-line" id="stmt-count" style="display:none"></div>
    </div>

    <script>
    var glFile   = null;
    var stmtFiles = [];

    function fmtSize(b) {
        if (b < 1024) return b + ' B';
        if (b < 1024*1024) return (b/1024).toFixed(1) + ' KB';
        return (b/1024/1024).toFixed(1) + ' MB';
    }

    function renderGL() {
        var list = document.getElementById('gl-list');
        list.innerHTML = '';
        if (!glFile) return;
        var chip = document.createElement('div');
        chip.className = 'file-chip';
        chip.innerHTML = '<span class="fname">✓&nbsp;&nbsp;' + glFile.name + '</span>'
            + '<span class="fsize">' + fmtSize(glFile.size) + '</span>'
            + '<button class="remove" title="Remove" onclick="removeGL()">✕</button>';
        list.appendChild(chip);
        sendState();
    }

    function renderStmts() {
        var list  = document.getElementById('stmt-list');
        var count = document.getElementById('stmt-count');
        list.innerHTML = '';
        stmtFiles.forEach(function(f, i) {
            var chip = document.createElement('div');
            chip.className = 'file-chip';
            chip.innerHTML = '<span class="fname">✓&nbsp;&nbsp;' + f.name + '</span>'
                + '<span class="fsize">' + fmtSize(f.size) + '</span>'
                + '<button class="remove" title="Remove" onclick="removeStmt(' + i + ')">✕</button>';
            list.appendChild(chip);
        });
        if (stmtFiles.length > 0) {
            count.style.display = 'block';
            count.textContent = '✓  ' + stmtFiles.length + ' file' + (stmtFiles.length !== 1 ? 's' : '') + ' loaded';
        } else {
            count.style.display = 'none';
        }
        sendState();
    }

    function removeGL()       { glFile = null; renderGL(); }
    function removeStmt(i)    { stmtFiles.splice(i, 1); renderStmts(); }

    // Convert files to base64 and send to Streamlit
    function sendState() {
        var payload = { gl: null, stmts: [] };
        var pending = 0;

        function done() {
            pending--;
            if (pending === 0) {
                window.parent.postMessage({type:'ap-rec-files', payload: payload}, '*');
            }
        }

        // GL file
        if (glFile) {
            pending++;
            var r = new FileReader();
            r.onload = function(e) {
                payload.gl = { name: glFile.name, data: e.target.result.split(',')[1] };
                done();
            };
            r.readAsDataURL(glFile);
        }

        // Statement files
        if (stmtFiles.length > 0) {
            stmtFiles.forEach(function(f) {
                pending++;
                var r = new FileReader();
                r.onload = (function(file) {
                    return function(e) {
                        payload.stmts.push({ name: file.name, data: e.target.result.split(',')[1] });
                        done();
                    };
                })(f);
                r.readAsDataURL(f);
            });
        }

        if (pending === 0) {
            window.parent.postMessage({type:'ap-rec-files', payload: payload}, '*');
        }
    }

    // Input change handlers
    document.getElementById('gl-input').addEventListener('change', function(e) {
        if (e.target.files[0]) { glFile = e.target.files[0]; renderGL(); }
    });
    document.getElementById('stmt-input').addEventListener('change', function(e) {
        Array.from(e.target.files).forEach(function(f) { stmtFiles.push(f); });
        renderStmts();
    });

    // Drag and drop — GL
    setupDrop('gl-zone', function(files) {
        var csv = Array.from(files).find(function(f) { return f.name.endsWith('.csv'); });
        if (csv) { glFile = csv; renderGL(); }
    });

    // Drag and drop — Statements
    setupDrop('stmt-zone', function(files) {
        Array.from(files).forEach(function(f) {
            if (f.name.endsWith('.pdf') || f.name.endsWith('.xlsx')) stmtFiles.push(f);
        });
        renderStmts();
    });

    function setupDrop(id, handler) {
        var zone = document.getElementById(id);
        zone.addEventListener('dragover',  function(e) { e.preventDefault(); zone.classList.add('over'); });
        zone.addEventListener('dragleave', function()  { zone.classList.remove('over'); });
        zone.addEventListener('drop',      function(e) {
            e.preventDefault(); zone.classList.remove('over');
            handler(e.dataTransfer.files);
        });
    }
    </script>
    </body>
    </html>
    """, height=520, scrolling=False)

    gap(8)

    # ── Session state for files passed from the HTML component ───────────
    # The component sends file data via postMessage; we receive it via
    # a hidden Streamlit component that listens for the message.
    # Since _stc.html can't return values directly via postMessage in all
    # Streamlit versions, we use standard st.file_uploader as the actual
    # data transfer mechanism but hide it completely, showing only our
    # custom UI above.
    #
    # PRAGMATIC BRIDGE: use standard uploaders (hidden) as the data source,
    # custom component above as the visual layer.

    st.html("""<style>
    /* Hide Streamlit's native uploaders — our custom UI above handles visuals */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderFileData"],
    [data-testid="stFileUploaderFile"] { display: none !important; }
    section[data-testid="stFileUploader"] > label { display: none !important; }
    section[data-testid="stFileUploader"] {
        border: none !important; background: none !important;
        padding: 0 !important; margin: 0 !important; min-height: 0 !important;
    }
    </style>""")

    gl_upload   = st.file_uploader("GL",    type=["csv"],           key="gl_file",   label_visibility="collapsed")
    stmt_uploads= st.file_uploader("Stmts", type=["pdf","xlsx"],    key="stmt_files", label_visibility="collapsed", accept_multiple_files=True)

    gap(28)

    # ── 04  Execute ───────────────────────────────────────────────────────
    section("04", "Execute")
    run_disabled = not (gl_upload and stmt_uploads)
    run_clicked  = st.button(
        "▶   RUN RECONCILIATION" if not run_disabled else "─   AWAITING INPUT",
        disabled=run_disabled,
        use_container_width=True
    )
    gap(8)

    if not run_disabled:
        n = len(stmt_uploads)
        st.html(f'<div style="font-family:var(--mono);font-size:12px;color:#2DD4BF;margin-top:4px;">'
                f'✓&nbsp;&nbsp;GL loaded &nbsp;·&nbsp; {n} statement{"s" if n!=1 else ""} loaded</div>')

    # ── Processing ────────────────────────────────────────────────────────
    if run_clicked:
        result_bytes = None
        result_fn    = None

        tmpdir = tempfile.mkdtemp()
        try:
            with st.spinner("processing…"):
                gl_path = os.path.join(tmpdir, gl_upload.name)
                with open(gl_path, "wb") as f:
                    f.write(gl_upload.getvalue())
                stmt_paths = []
                for su in stmt_uploads:
                    sp = os.path.join(tmpdir, su.name)
                    with open(sp, "wb") as f:
                        f.write(su.getvalue())
                    stmt_paths.append(sp)
                result_bytes, result_fn, reconciled, skipped = run_reconciliation(
                    gl_path, stmt_paths)
        except ValueError as e:
            st.html(f'<div style="font-family:var(--mono);font-size:12px;color:#F87171;margin-top:12px;">✕&nbsp;&nbsp;{e}</div>')
            reconciled = set(); skipped = []
        except Exception as e:
            st.html(f'<div style="font-family:var(--mono);font-size:12px;color:#F87171;margin-top:12px;">✕&nbsp;&nbsp;unexpected error: {e}</div>')
            reconciled = set(); skipped = []
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        if result_bytes:
            gap(16)

            # Download button first — always visible without scrolling
            st.download_button(
                label="⬇   DOWNLOAD REPORT",
                data=result_bytes,
                file_name=result_fn,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
            gap(12)

            # Results banner
            n_rec  = len(reconciled)
            n_skip = len(skipped)
            total  = n_rec + n_skip
            pct    = int(n_rec / total * 100) if total else 0
            bar    = "█" * int(pct/5) + "░" * (20 - int(pct/5))

            skip_section = ""
            if skipped:
                rows = "".join(
                    f'<div style="padding:3px 0;font-size:12px;color:#FF6B00;">✕&nbsp;&nbsp;{f}</div>'
                    for f in skipped)
                skip_section = f"""
                <div style="border-top:1px solid #FF6B0044;margin-top:14px;padding-top:12px;">
                    <div style="font-size:10px;color:#FF6B00;letter-spacing:0.18em;
                                text-transform:uppercase;margin-bottom:8px;">✕ Not Reconciled</div>
                    <div style="line-height:1.8;">{rows}</div>
                </div>"""

            status = ('<span style="color:#CCFF00;">✓ all files processed</span>' if n_skip == 0
                      else f'<span style="color:#FF6B00;">{n_skip} file{"s" if n_skip!=1 else ""} not reconciled</span>')

            st.html(f"""
            <div style="background:#22262D;border:2px solid #FF6B00;border-radius:4px;padding:20px 22px;font-family:var(--mono);">
                <div style="font-size:22px;font-weight:700;color:#CCFF00;margin-bottom:6px;">
                    ◈ &nbsp;{n_rec} / {total} &nbsp;files reconciled
                </div>
                <div style="font-size:11px;color:#CCFF0088;letter-spacing:0.08em;margin-bottom:10px;">
                    {bar} &nbsp;{pct}%
                </div>
                <div style="font-size:11px;letter-spacing:0.05em;">{status}</div>
                {skip_section}
            </div>""")

    # ── Footer ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-top:1px solid #252C3A;margin-top:52px;padding-top:16px;
                display:flex;justify-content:space-between;
                font-family:var(--mono);font-size:10px;color:#3A4255;
                letter-spacing:0.1em;text-transform:uppercase;">
        <span>internal use only</span>
        <span>◈ ap·rec · v5</span>
    </div>""")


if __name__ == "__main__":
    main()
