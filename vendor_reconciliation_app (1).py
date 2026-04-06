"""
AP Reconciliation — Streamlit Interface v5
UI layer only. All reconciliation logic lives in reconciliation_engine.py.
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

    # ── Global styles ─────────────────────────────────────────────────────
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
    :root {
        --bg:         #1A1D21;
        --surface:    #22262D;
        --surface-hi: #292E38;
        --teal:       #2DD4BF;
        --teal-dim:   #14B8A6;
        --teal-glow:  rgba(45,212,191,0.10);
        --teal-b:     rgba(45,212,191,0.45);
        --text:       #CDD5E0;
        --muted:      #6B7A8D;
        --dim:        #3A4255;
        --border:     #252C3A;
        --mono: 'JetBrains Mono', monospace;
        --sans: 'IBM Plex Sans', system-ui, sans-serif;
    }

    /* ── Chrome strip ── */
    #MainMenu, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"] { display: none !important; }

    /* ── Page background ── */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stBottom"] { background: var(--bg) !important; }
    .main .block-container {
        background: var(--bg) !important;
        max-width: 680px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* ── Global text ── */
    .stApp p, .stApp div, .stApp span,
    .stApp label, .stMarkdown {
        color: var(--text) !important;
        font-family: var(--sans) !important;
    }

    /* ── File uploader container ── */
    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 3px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:focus-within,
    [data-testid="stFileUploader"]:hover {
        border-color: var(--teal-b) !important;
    }

    /* ── Dropzone text ── */
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--muted) !important;
        font-family: var(--mono) !important;
        font-size: 12px !important;
    }

    /* ── Browse button — let Streamlit handle it, just restyle ── */
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--surface-hi) !important;
        border: 1px solid var(--dim) !important;
        border-radius: 2px !important;
        color: var(--text) !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        letter-spacing: 0.05em !important;
        padding: 5px 14px !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--teal-b) !important;
        color: var(--teal) !important;
    }

    /* ── File chips after upload ── */
    [data-testid="stFileUploaderFile"] {
        background: var(--surface-hi) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
    }
    [data-testid="stFileUploaderFileName"] {
        font-family: var(--mono) !important;
        font-size: 11px !important;
        color: var(--text) !important;
    }
    [data-testid="stFileUploaderFileSize"] {
        font-family: var(--mono) !important;
        font-size: 10px !important;
        color: var(--muted) !important;
    }

    /* ── Hide thumbnail preview boxes ── */
    [data-testid="stFileUploaderFileData"] > div:first-child {
        display: none !important;
    }

    /* ── Delete X on chips ── */
    [data-testid="stFileUploaderDeleteBtn"] button {
        background: transparent !important;
        border: 1px solid var(--dim) !important;
        color: var(--muted) !important;
        border-radius: 2px !important;
        width: 20px !important;
        height: 20px !important;
        padding: 0 !important;
        font-size: 10px !important;
        line-height: 1 !important;
    }
    [data-testid="stFileUploaderDeleteBtn"] button:hover {
        border-color: #F87171 !important;
        color: #F87171 !important;
    }

    /* ── Run button ── */
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

    /* ── Download button ── */
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

    /* ── Password input ── */
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

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div { border-top-color: var(--teal) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--teal-dim); }
    </style>
    """)

    # ── Helpers ───────────────────────────────────────────────────────────
    def section(num, title, hint=""):
        hint_html = (f'<span style="font-family:var(--sans);font-size:12px;'
                     f'color:#3A4255;font-weight:300;margin-left:10px;">{hint}</span>'
                     ) if hint else ""
        st.html(f"""
        <div style="margin-bottom:10px;display:flex;align-items:center;">
            <span style="font-family:var(--mono);font-size:10px;color:#3A4255;
                         letter-spacing:0.2em;">// {num}</span>
            <span style="font-family:var(--mono);font-size:12px;font-weight:600;
                         color:#CDD5E0;letter-spacing:0.1em;text-transform:uppercase;
                         margin-left:12px;">{title}</span>
            {hint_html}
        </div>""")

    def gap(px=24):
        st.html(f'<div style="margin-bottom:{px}px;"></div>')

    def mono(msg, color="#2DD4BF", prefix="✓"):
        st.html(f'<div style="font-family:var(--mono);font-size:12px;'
                f'color:{color};margin-top:6px;">{prefix}&nbsp;&nbsp;{msg}</div>')

    # ── Header ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-bottom:1px solid #252C3A;padding-bottom:20px;margin-bottom:36px;">
        <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:5px;">
            <span style="font-family:var(--mono);font-size:21px;font-weight:700;
                         color:#2DD4BF;">◈ AP·REC</span>
            <span style="font-family:var(--mono);font-size:10px;color:#3A4255;
                         letter-spacing:0.18em;text-transform:uppercase;">v5.0</span>
        </div>
        <div style="font-family:var(--sans);font-size:13px;color:#6B7A8D;font-weight:300;">
            vendor statement reconciliation processor
        </div>
    </div>
    """)

    # ── 01  Access Key ────────────────────────────────────────────────────
    section("01", "Access Key")
    password = st.text_input(
        "key", type="password",
        placeholder="enter access key…",
        label_visibility="collapsed"
    )
    if password != "reconcile2026":
        if password:
            mono("incorrect key — try again", color="#F87171", prefix="✕")
        else:
            st.html('<div style="font-family:var(--mono);font-size:12px;'
                    'color:#3A4255;margin-top:6px;">─&nbsp;&nbsp;awaiting authentication</div>')
        st.stop()
    mono("authenticated")
    gap(32)

    # ── 02  GL Export ─────────────────────────────────────────────────────
    section("02", "GL Export", "accepts .csv")
    gl_upload = st.file_uploader(
        "GL CSV", type=["csv"],
        key="gl_file",
        label_visibility="collapsed"
    )
    if gl_upload:
        mono(gl_upload.name)
    gap(28)

    # ── 03  Vendor Statements ─────────────────────────────────────────────
    section("03", "Vendor Statements", "accepts .pdf · .xlsx · multiple files OK")
    stmt_uploads = st.file_uploader(
        "Vendor Statements", type=["pdf", "xlsx"],
        accept_multiple_files=True,
        key="stmt_files",
        label_visibility="collapsed"
    )
    if stmt_uploads:
        n = len(stmt_uploads)
        mono(f'{n} file{"s" if n != 1 else ""} loaded')
    gap(32)

    # ── 04  Execute ───────────────────────────────────────────────────────
    section("04", "Execute")
    run_disabled = not (gl_upload and stmt_uploads)
    run_clicked = st.button(
        "▶   RUN RECONCILIATION" if not run_disabled else "─   AWAITING INPUT",
        disabled=run_disabled,
        use_container_width=True
    )
    gap(8)

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
            mono(str(e), color="#F87171", prefix="✕")
        except Exception as e:
            mono(f"unexpected error: {e}", color="#F87171", prefix="✕")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        if result_bytes:
            gap(16)

            # Download button first — always visible right where spinner was
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
            bar    = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

            skip_section = ""
            if skipped:
                rows = "".join(
                    f'<div style="padding:3px 0;font-size:12px;color:#FF6B00;">'
                    f'✕&nbsp;&nbsp;{fname}</div>'
                    for fname in skipped
                )
                skip_section = f"""
                <div style="border-top:1px solid #FF6B0044;margin-top:14px;padding-top:12px;">
                    <div style="font-size:10px;color:#FF6B00;letter-spacing:0.18em;
                                text-transform:uppercase;margin-bottom:8px;">
                        ✕ Not Reconciled
                    </div>
                    <div style="line-height:1.8;">{rows}</div>
                </div>"""

            status = (
                '<span style="color:#CCFF00;">✓ all files processed</span>'
                if n_skip == 0 else
                f'<span style="color:#FF6B00;">'
                f'{n_skip} file{"s" if n_skip != 1 else ""} not reconciled'
                f'</span>'
            )

            st.html(f"""
            <div style="background:#22262D;border:2px solid #FF6B00;border-radius:4px;
                        padding:20px 22px;font-family:var(--mono);">
                <div style="font-size:22px;font-weight:700;color:#CCFF00;margin-bottom:6px;">
                    ◈ &nbsp;{n_rec} / {total} &nbsp;files reconciled
                </div>
                <div style="font-size:11px;color:#CCFF0088;
                            letter-spacing:0.08em;margin-bottom:10px;">
                    {bar} &nbsp;{pct}%
                </div>
                <div style="font-size:11px;letter-spacing:0.05em;">{status}</div>
                {skip_section}
            </div>""")

    # ── Footer ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-top:1px solid #252C3A;margin-top:52px;padding-top:16px;
                display:flex;justify-content:space-between;font-family:var(--mono);
                font-size:10px;color:#3A4255;letter-spacing:0.1em;text-transform:uppercase;">
        <span>internal use only</span>
        <span>◈ ap·rec · v5</span>
    </div>
    """)


if __name__ == "__main__":
    main()
