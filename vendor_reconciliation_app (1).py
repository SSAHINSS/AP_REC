"""
AP Reconciliation — Streamlit Interface v6
"""
import os, tempfile, shutil
import streamlit as st
import streamlit.components.v1 as _stc
from reconciliation_engine import run_reconciliation

LOGO_SVG = """<svg width="100%" viewBox="0 0 716 158" xmlns="http://www.w3.org/2000/svg">
<defs>
  <filter id="ds" x="-20%" y="-20%" width="150%" height="150%">
    <feDropShadow dx="3" dy="4" stdDeviation="4" flood-color="#1A0800" flood-opacity="0.7"/>
  </filter>
</defs>
<g filter="url(#ds)">
<rect x="34" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="52" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="70" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="88" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="16" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="34" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="88" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="106" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="16" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="34" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="88" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="106" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="16" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="34" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="52" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="70" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="88" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="106" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="16" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="34" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="88" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="106" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="16" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="34" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="88" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="106" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="16" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="34" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="88" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="106" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="142" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="160" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="178" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="196" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="214" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="142" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="160" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="214" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="232" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="142" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="160" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="214" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="232" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="142" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="160" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="178" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="196" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="214" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="142" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="160" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="142" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="160" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="142" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="160" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="286" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="304" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="286" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="304" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="340" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="358" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="376" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="394" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="412" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="340" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="358" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="412" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="430" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="340" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="358" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="412" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="430" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="340" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="358" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="376" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="394" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="412" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="340" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="358" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="376" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="394" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="340" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="358" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="394" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="412" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="340" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="358" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="412" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="430" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="466" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="484" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="502" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="520" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="538" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="556" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="466" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="484" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="466" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="484" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="466" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="484" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="502" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="520" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="538" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="466" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="484" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="466" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="484" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="466" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="484" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="502" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="520" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="538" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="556" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="610" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="628" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="646" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="664" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="682" y="16" width="18" height="18" fill="#FFA868"/>
<rect x="592" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="610" y="34" width="18" height="18" fill="#FF9050"/>
<rect x="592" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="610" y="52" width="18" height="18" fill="#FF7A38"/>
<rect x="592" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="610" y="70" width="18" height="18" fill="#EE6422"/>
<rect x="592" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="610" y="88" width="18" height="18" fill="#DC5418"/>
<rect x="592" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="610" y="106" width="18" height="18" fill="#CC4412"/>
<rect x="610" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="628" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="646" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="664" y="124" width="18" height="18" fill="#BE380E"/>
<rect x="682" y="124" width="18" height="18" fill="#BE380E"/>
</g>
</svg>"""


def main():
    st.set_page_config(
        page_title="AP · Reconciliation",
        page_icon="◈",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
    :root {
        --bg:       #1E1B17;
        --surface:  #26211C;
        --hi:       #302820;
        --ox:       #FF7030;
        --ox-d:     #E85520;
        --ox-dk:    #C03808;
        --ox-glow:  rgba(255,112,48,0.12);
        --ox-b:     rgba(255,112,48,0.38);
        --text:     #DDD0C4;
        --muted:    #7A6A5A;
        --dim:      #4A3A2C;
        --border:   #332820;
        --shadow:   #0A0100;
        --mono:     'JetBrains Mono', monospace;
        --sans:     'IBM Plex Sans', system-ui, sans-serif;
    }

    #MainMenu, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"] { display: none !important; }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stBottom"] { background: var(--bg) !important; }
    .main .block-container {
        background: var(--bg) !important;
        max-width: 700px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }

    .stApp p, .stApp div, .stApp span,
    .stApp label, .stMarkdown {
        color: var(--text) !important;
        font-family: var(--sans) !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 2px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--ox-b) !important;
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
    [data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: var(--hi) !important;
        border: 1px solid var(--dim) !important;
        border-radius: 2px !important;
        color: var(--text) !important;
        padding: 8px 20px !important;
        transition: all 0.15s !important;
        filter: drop-shadow(2px 2px 0px var(--shadow)) !important;
    }
    [data-testid="stFileUploaderDropzone"] button p {
        font-family: var(--mono) !important;
        font-size: 11px !important;
        letter-spacing: 0.06em !important;
        color: var(--text) !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        width: 100% !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--ox-b) !important;
        filter: drop-shadow(2px 2px 0px var(--shadow)) !important;
    }
    [data-testid="stFileUploaderDropzone"] button:hover p { color: var(--ox) !important; }

    /* ── File chips ── */
    [data-testid="stFileChip"] {
        background: var(--hi) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
    }
    [data-testid="stFileChip"] > div:first-child { display: none !important; }
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
        width: 20px !important; height: 20px !important;
        padding: 0 !important;
        transition: all 0.15s !important;
    }
    [data-testid="stFileChipDeleteBtn"] button:hover {
        border-color: #F87171 !important;
        color: #F87171 !important;
    }

    /* ── Run button ── */
    .stButton > button {
        background: transparent !important;
        border: 2px solid var(--ox-d) !important;
        color: var(--ox) !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 14px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        filter: drop-shadow(3px 3px 0px var(--shadow)) !important;
    }
    .stButton > button:hover:not(:disabled) {
        background: var(--ox-glow) !important;
        border-color: var(--ox) !important;
        filter: drop-shadow(3px 3px 0px var(--shadow)),
                drop-shadow(0 0 18px var(--ox-glow)) !important;
    }
    .stButton > button:disabled {
        border-color: var(--dim) !important;
        color: var(--dim) !important;
        opacity: 1 !important;
        filter: none !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: var(--ox-dk) !important;
        border: none !important;
        color: #FFF0E8 !important;
        font-family: var(--mono) !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        padding: 15px !important;
        border-radius: 2px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        filter: drop-shadow(4px 4px 0px var(--shadow)) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: var(--ox-d) !important;
        filter: drop-shadow(4px 4px 0px var(--shadow)),
                drop-shadow(0 0 22px var(--ox-glow)) !important;
    }

    /* ── Password input ── */
    .stTextInput > div > div > input {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 2px !important;
        color: var(--ox) !important;
        font-family: var(--mono) !important;
        font-size: 14px !important;
        caret-color: var(--ox) !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--ox-d) !important;
        box-shadow: 0 0 0 1px var(--ox-d),
                    0 0 16px var(--ox-glow) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--dim) !important; }
    /* Kill Streamlit/BaseWeb blue focus ring on the outer wrapper */
    [data-baseweb="base-input"],
    [data-baseweb="input"] {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-baseweb="base-input"]:focus-within,
    [data-baseweb="input"]:focus-within {
        border-color: var(--ox-d) !important;
        box-shadow: 0 0 0 1px var(--ox-d),
                    0 0 16px var(--ox-glow) !important;
        outline: none !important;
    }

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div { border-top-color: var(--ox) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ox-d); }

    /* ── Auth badge ── */
    .auth-badge {
        display: inline-flex; align-items: center; gap: 8px;
        font-family: var(--mono); font-size: 11px; color: var(--ox);
        letter-spacing: 0.08em; padding: 6px 12px;
        border: 1px solid var(--ox-b); border-radius: 2px;
        background: var(--ox-glow);
        filter: drop-shadow(2px 2px 0px var(--shadow));
        animation: badgeIn 0.4s ease forwards;
    }
    @keyframes badgeIn {
        from { opacity:0; transform:scale(0.95); }
        to   { opacity:1; transform:scale(1); }
    }

    /* ── Section reveal ── */
    .section-row {
        display: flex; align-items: center; margin-bottom: 10px;
        animation: sectionIn 0.4s ease forwards;
    }
    @keyframes sectionIn {
        from { opacity:0; transform:translateY(6px); }
        to   { opacity:1; transform:translateY(0); }
    }
    </style>

    <script>
    (function() {
        function focusPw() {
            var inp = window.parent.document.querySelector('[data-testid="stTextInput"] input');
            if (inp) inp.focus();
            else setTimeout(focusPw, 120);
        }
        setTimeout(focusPw, 400);
    })();
    </script>
    """)

    # ── Helpers ───────────────────────────────────────────────────────────
    def section(num, title, hint="", delay=0):
        h = (f'<span style="font-family:var(--sans);font-size:12px;color:var(--dim);'
             f'font-weight:300;margin-left:10px;">{hint}</span>') if hint else ""
        st.html(f"""<div class="section-row" style="animation-delay:{delay}ms;">
            <span style="font-family:var(--mono);font-size:10px;color:var(--dim);
                letter-spacing:0.2em;">{num}</span>
            <span style="font-family:var(--mono);font-size:12px;font-weight:600;
                color:#DDD0C4;letter-spacing:0.1em;text-transform:uppercase;
                margin-left:12px;">{title}</span>{h}
        </div>""")

    def gap(px=24):
        st.html(f'<div style="margin-bottom:{px}px;"></div>')

    def note(msg, color="#FF7030", icon="✓"):
        st.html(f'<div style="font-family:var(--mono);font-size:12px;'
                f'color:{color};margin-top:6px;">{icon}&nbsp;&nbsp;{msg}</div>')

    # ── Logo ─────────────────────────────────────────────────────────────
    logo_html = (
        '<div style="border-bottom:1px solid #2A2018;padding-bottom:20px;margin-bottom:36px;">'
        + LOGO_SVG
        + '''<div style="display:flex;align-items:center;gap:14px;margin-top:14px;">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&family=IBM+Plex+Sans:wght@300&display=swap" rel="stylesheet">
            <div style="display:flex;align-items:center;gap:12px;margin-top:16px;padding:0 4px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#4A3A2C;letter-spacing:0.16em;text-transform:uppercase;">v6.0</span>
                <span style="font-family:'IBM Plex Sans',sans-serif;font-size:12px;color:#7A6A5A;font-weight:300;letter-spacing:0.04em;">vendor statement reconciliation processor</span>
            </div>
        </div></div>
        <style>
        svg rect{transform-box:fill-box;transform-origin:center bottom;}
        @keyframes pixelFall{
          0%  {opacity:0;transform:translateY(-160px) scaleY(1.4);}
          55% {opacity:1;transform:translateY(10px) scaleY(0.75);}
          70% {transform:translateY(-5px) scaleY(1.08);}
          83% {transform:translateY(3px) scaleY(0.97);}
          91% {transform:translateY(-1px) scaleY(1.01);}
          100%{opacity:1;transform:translateY(0) scaleY(1);}
        }
        </style>
        <script>
        (function(){
            var rects=Array.from(document.querySelectorAll("svg rect"));
            rects.sort(function(a,b){
                var ay=parseFloat(a.getAttribute("y")),by=parseFloat(b.getAttribute("y"));
                if(ay!==by)return by-ay;
                return parseFloat(a.getAttribute("x"))-parseFloat(b.getAttribute("x"));
            });
            rects.forEach(function(r,i){
                var delay=(60+i*24)+"ms";
                r.style.animationName="pixelFall";
                r.style.animationDuration="0.45s";
                r.style.animationTimingFunction="cubic-bezier(0.22,1,0.36,1)";
                r.style.animationFillMode="both";
                r.style.animationDelay=delay;
            });
        })();
        </script>'''
    )
    _stc.html(logo_html, height=230, scrolling=False)

    # ── 01  Access Key ────────────────────────────────────────────────────
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
        st.html('<div style="margin-bottom:36px;">'
                '<span class="auth-badge">authenticated</span></div>')

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
                skip_html = f"""<div style="border-top:1px solid rgba(255,107,0,0.25);
                    margin-top:14px;padding-top:12px;">
                    <div style="font-size:10px;color:#FF6B00;letter-spacing:0.16em;
                        text-transform:uppercase;margin-bottom:8px;">
                        ✕&nbsp;&nbsp;Not Reconciled</div>{rows}</div>"""

            ok = n_skip == 0
            st.html(f"""
            <div style="background:var(--surface);
                border:2px solid var(--ox-d);border-radius:2px;
                padding:20px 22px;font-family:var(--mono);
                filter:drop-shadow(4px 4px 0px var(--shadow));
                animation:sectionIn 0.4s ease forwards;">
                <div style="font-size:22px;font-weight:700;
                    color:#FFA868;letter-spacing:-0.01em;margin-bottom:6px;">
                    ◈&nbsp;&nbsp;{n_rec} / {total}&nbsp;&nbsp;files reconciled
                </div>
                <div style="font-size:11px;color:rgba(255,168,104,0.4);
                    letter-spacing:0.08em;margin-bottom:10px;">
                    {bar}&nbsp;&nbsp;{pct}%
                </div>
                <div style="font-size:11px;letter-spacing:0.04em;
                    color:{'#FFA868' if ok else '#FF6B00'};">
                    {'✓&nbsp;&nbsp;all files processed' if ok
                     else f'✕&nbsp;&nbsp;{n_skip} file{"s" if n_skip!=1 else ""} not reconciled'}
                </div>{skip_html}
            </div>""")

    # ── Footer ────────────────────────────────────────────────────────────
    st.html("""
    <div style="border-top:1px solid #2A2018;margin-top:52px;padding-top:16px;
        display:flex;justify-content:space-between;font-family:var(--mono);
        font-size:10px;color:var(--dim);letter-spacing:0.1em;text-transform:uppercase;">
        <span>internal use only</span>
        <span>◈&nbsp;ap·rec&nbsp;·&nbsp;v6</span>
    </div>""")


if __name__ == "__main__":
    main()
