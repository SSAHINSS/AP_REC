"""
AP Reconciliation — Streamlit Interface v5
"""
import os, tempfile, shutil
import streamlit as st
from reconciliation_engine import run_reconciliation


def main():
    st.set_page_config(
        page_title="AP · Reconciliation",
        page_icon="◈",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # ── Authenticated state ───────────────────────────────────────────────
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
    :root {
        --bg:      #1A1D21;
        --surface: #22262D;
        --hi:      #292E38;
        --teal:    #2DD4BF;
        --teal-d:  #14B8A6;
        --glow:    rgba(45,212,191,0.10);
        --teal-b:  rgba(45,212,191,0.40);
        --text:    #CDD5E0;
        --muted:   #6B7A8D;
        --dim:     #3A4255;
        --border:  #2A3040;
        --mono:    'JetBrains Mono', monospace;
        --sans:    'IBM Plex Sans', system-ui, sans-serif;
    }

    /* ── Chrome ── */
    #MainMenu, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"] { display: none !important; }

    /* ── Background ── */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stBottom"] { background: var(--bg) !important; }
    .main .block-container {
        background: var(--bg) !important;
        max-width: 680px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* ── Text ── */
    .stApp p, .stApp div, .stApp span,
    .stApp label, .stMarkdown {
        color: var(--text) !important;
        font-family: var(--sans) !important;
    }

    /* ── Page fade-in on load ── */
    .main .block-container {
        animation: pageIn 0.5s ease forwards;
    }
    @keyframes pageIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Section reveal animation ── */
    .section-reveal {
        animation: sectionIn 0.4s ease forwards;
    }
    @keyframes sectionIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ════════════════════════════════════
       FILE UPLOADER
    ════════════════════════════════════ */
    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 3px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--teal-b) !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--muted) !important;
        font-family: var(--mono) !important;
        font-size: 12px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--dim) !important;
        font-family: var(--mono) !important;
        font-size: 10px !important;
    }
    /* Hide duplicate icon text, center button text */
    [data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--hi) !important;
        border: 1px solid var(--dim) !important;
        border-radius: 2px !important;
        color: var(--text) !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        letter-spacing: 0.06em !important;
        padding: 8px 20px 8px 20px !important;
        height: auto !important;
        min-height: 0 !important;
        line-height: 1.2 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        vertical-align: middle !important;
    }
    [data-testid="stFileUploaderDropzone"] button *:not([data-testid="stIconMaterial"]) {
        line-height: 1.2 !important;
        vertical-align: middle !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--teal-b) !important;
        color: var(--teal) !important;
    }

    /* ── File chips ── */
    [data-testid="stFileChip"] {
        background: var(--hi) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
    }
    /* Hide the white preview box */
    [data-testid="stFileChip"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileChipName"] {
        font-family: var(--mono) !important;
        font-size: 11px !important;
        color: var(--text) !important;
    }
    [data-testid="stFileChipDeleteBtn"] button {
        background: transparent !important;
        border: 1px solid var(--dim) !important;
        color: var(--muted) !important;
        border-radius: 2px !important;
        width: 20px !important;
        height: 20px !important;
        padding: 0 !important;
        transition: all 0.15s !important;
    }
    [data-testid="stFileChipDeleteBtn"] button:hover {
        border-color: #F87171 !important;
        color: #F87171 !important;
    }

    /* ════════════════════════════════════
       BUTTONS
    ════════════════════════════════════ */
    .stButton > button {
        background: transparent !important;
        border: 2px solid var(--teal-d) !important;
        color: var(--teal) !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 14px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover:not(:disabled) {
        background: var(--glow) !important;
        border-color: var(--teal) !important;
        box-shadow: 0 0 24px var(--glow) !important;
    }
    .stButton > button:disabled {
        border-color: var(--dim) !important;
        color: var(--dim) !important;
        opacity: 1 !important;
    }
    [data-testid="stDownloadButton"] > button {
        background: var(--teal-d) !important;
        border: none !important;
        color: #071210 !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 15px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: var(--teal) !important;
        box-shadow: 0 0 28px var(--glow) !important;
    }

    /* ════════════════════════════════════
       PASSWORD INPUT
    ════════════════════════════════════ */
    .stTextInput > div > div > input {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 2px !important;
        color: var(--teal) !important;
        font-family: var(--mono) !important;
        font-size: 14px !important;
        caret-color: var(--teal) !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--teal-d) !important;
        box-shadow: 0 0 0 1px var(--teal-d), 0 0 16px var(--glow) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--dim) !important; }

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div { border-top-color: var(--teal) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--teal-d); }

    /* ── Auth success badge ── */
    .auth-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: var(--mono);
        font-size: 11px;
        color: var(--teal);
        letter-spacing: 0.08em;
        padding: 6px 12px;
        border: 1px solid var(--teal-b);
        border-radius: 2px;
        background: rgba(45,212,191,0.06);
        animation: badgeIn 0.4s ease forwards;
    }
    @keyframes badgeIn {
        from { opacity: 0; transform: scale(0.95); }
        to   { opacity: 1; transform: scale(1); }
    }
    .auth-badge::before {
        content: '◈';
        color: var(--teal);
        font-size: 10px;
    }
    </style>

    <script>
    // Auto-focus the password input on page load
    (function autoFocus() {
        function tryFocus() {
            var inp = window.parent.document.querySelector(
                '[data-testid="stTextInput"] input'
            );
            if (inp) { inp.focus(); }
            else { setTimeout(tryFocus, 100); }
        }
        setTimeout(tryFocus, 300);
    })();
    </script>
    """)

    # ── Helpers ───────────────────────────────────────────────────────────
    def section(num, title, hint="", delay=0):
        h = (f'<span style="font-family:var(--sans);font-size:12px;color:var(--dim);'
             f'font-weight:300;margin-left:10px;">{hint}</span>') if hint else ""
        st.html(f"""
        <div class="section-reveal" style="margin-bottom:10px;display:flex;
            align-items:center;animation-delay:{delay}ms;">
            <span style="font-family:var(--mono);font-size:10px;color:var(--dim);
                letter-spacing:0.2em;">//&nbsp;{num}</span>
            <span style="font-family:var(--mono);font-size:12px;font-weight:600;
                color:#CDD5E0;letter-spacing:0.1em;text-transform:uppercase;
                margin-left:12px;">{title}</span>{h}
        </div>""")

    def gap(px=24):
        st.html(f'<div style="margin-bottom:{px}px;"></div>')

    def note(msg, color="#2DD4BF", icon="✓"):
        st.html(f'<div style="font-family:var(--mono);font-size:12px;'
                f'color:{color};margin-top:6px;animation:sectionIn 0.3s ease;">'
                f'{icon}&nbsp;&nbsp;{msg}</div>')

    # ── Header — pixel logo ───────────────────────────────────────────────
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
    .aprec-logo {
        font-family: 'Press Start 2P', monospace;
        font-size: 30px;
        line-height: 1.1;
        letter-spacing: 0.05em;
        background: linear-gradient(
            135deg,
            #FF8C42 0%,
            #E8541A 18%,
            #C23B0F 35%,
            #8B3A0F 50%,
            #B84A1A 65%,
            #E06030 80%,
            #FF6B2B 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(4px 4px 0px rgba(60,15,0,0.9))
                drop-shadow(7px 7px 0px rgba(30,5,0,0.5));
        display: inline-block;
        margin-bottom: 12px;
    }
    .aprec-sub {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .aprec-v {
        font-family: 'Press Start 2P', monospace;
        font-size: 6px;
        color: #3A4255;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .aprec-tag {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 12px;
        color: #6B7A8D;
        font-weight: 300;
        letter-spacing: 0.04em;
    }
    </style>
    <div style="border-bottom:1px solid #252C3A;padding-bottom:24px;margin-bottom:36px;">
        <div class="aprec-logo">AP·REC</div>
        <div class="aprec-sub">
            <span class="aprec-v">v5.0</span>
            <span class="aprec-tag">vendor statement reconciliation processor</span>
        </div>
    </div>""")

    # ── 01  Access Key — collapses after auth ─────────────────────────────
    if not st.session_state.authenticated:
        section("01", "Access Key")
        st.html("""<div style="font-family:var(--mono);font-size:11px;color:var(--dim);
            margin-bottom:10px;letter-spacing:0.04em;">enter access key to continue</div>""")
        password = st.text_input(
            "key", type="password",
            placeholder="••••••••••••",
            label_visibility="collapsed",
            key="pw_input"
        )
        if password:
            if password == "reconcile2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                note("incorrect key", color="#F87171", icon="✕")
        gap(32)
        st.stop()
    else:
        # Collapsed — just a small auth badge, no input box
        st.html("""
        <div style="margin-bottom:36px;display:flex;align-items:center;
            justify-content:space-between;">
            <span class="auth-badge">authenticated</span>
        </div>""")

    # ── 02  GL Export ─────────────────────────────────────────────────────
    section("02", "GL Export", "accepts .csv", delay=0)
    gl_upload = st.file_uploader(
        "GL CSV", type=["csv"],
        key="gl_file", label_visibility="collapsed")
    if gl_upload:
        note(gl_upload.name)
    gap(28)

    # ── 03  Vendor Statements ─────────────────────────────────────────────
    section("03", "Vendor Statements", "accepts .pdf · .xlsx · multiple files OK", delay=60)
    stmt_uploads = st.file_uploader(
        "Vendor Statements", type=["pdf", "xlsx"],
        accept_multiple_files=True,
        key="stmt_files", label_visibility="collapsed")
    if stmt_uploads:
        n = len(stmt_uploads)
        note(f'{n} file{"s" if n != 1 else ""} loaded')
    gap(32)

    # ── 04  Execute ───────────────────────────────────────────────────────
    section("04", "Execute", delay=120)
    run_disabled = not (gl_upload and stmt_uploads)
    run_clicked = st.button(
        "▶   RUN RECONCILIATION" if not run_disabled else "─   AWAITING INPUT",
        disabled=run_disabled,
        use_container_width=True)

    # ── Processing ────────────────────────────────────────────────────────
    if run_clicked:
        result_bytes = None
        result_fn    = None
        reconciled   = set()
        skipped      = []

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
            note(str(e), color="#F87171", icon="✕")
        except Exception as e:
            note(f"unexpected error: {e}", color="#F87171", icon="✕")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        if result_bytes:
            gap(16)
            st.download_button(
                label="⬇   DOWNLOAD REPORT",
                data=result_bytes,
                file_name=result_fn,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
            gap(12)

            n_rec  = len(reconciled)
            n_skip = len(skipped)
            total  = n_rec + n_skip
            pct    = int(n_rec / total * 100) if total else 0
            bar    = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

            skip_html = ""
            if skipped:
                rows = "".join(
                    f'<div style="padding:3px 0;font-size:12px;color:#FF6B00;">'
                    f'✕&nbsp;&nbsp;{f}</div>' for f in skipped)
                skip_html = f"""
                <div style="border-top:1px solid rgba(255,107,0,0.25);
                    margin-top:14px;padding-top:12px;">
                    <div style="font-size:10px;color:#FF6B00;letter-spacing:0.16em;
                        text-transform:uppercase;margin-bottom:8px;">
                        ✕&nbsp;&nbsp;Not Reconciled</div>
                    {rows}
                </div>"""

            ok = n_skip == 0
            st.html(f"""
            <div style="background:#22262D;border:2px solid #FF6B00;border-radius:3px;
                padding:20px 22px;font-family:var(--mono);
                animation:sectionIn 0.4s ease forwards;">
                <div style="font-size:22px;font-weight:700;color:#CCFF00;
                    letter-spacing:-0.01em;margin-bottom:6px;">
                    ◈&nbsp;&nbsp;{n_rec} / {total}&nbsp;&nbsp;files reconciled
                </div>
                <div style="font-size:11px;color:rgba(204,255,0,0.4);
                    letter-spacing:0.08em;margin-bottom:10px;">
                    {bar}&nbsp;&nbsp;{pct}%
                </div>
                <div style="font-size:11px;letter-spacing:0.04em;
                    color:{'#CCFF00' if ok else '#FF6B00'};">
                    {'✓&nbsp;&nbsp;all files processed' if ok
                     else f'✕&nbsp;&nbsp;{n_skip} file{"s" if n_skip!=1 else ""} not reconciled'}
                </div>
                {skip_html}
            </div>""")

    # ── Footer ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-top:1px solid #252C3A;margin-top:52px;padding-top:16px;
        display:flex;justify-content:space-between;font-family:var(--mono);
        font-size:10px;color:var(--dim);letter-spacing:0.1em;text-transform:uppercase;">
        <span>internal use only</span>
        <span>◈&nbsp;ap·rec&nbsp;·&nbsp;v5</span>
    </div>""")


if __name__ == "__main__":
    main()
