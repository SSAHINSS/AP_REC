"""
AP Reconciliation — Streamlit Interface v6
"""
import os, tempfile, shutil
import streamlit as st
import streamlit.components.v1 as _stc
from reconciliation_engine import run_reconciliation

# ─── Design tokens — used in both CSS and inline st.html() ───────────────────
BG      = "#1E1B17"
SURFACE = "#26211C"
HI      = "#302820"
BORDER  = "#3A2A1C"
DIM     = "#5A4030"
MUTED   = "#8A7060"
TEXT    = "#E0D0C0"
OX      = "#FF7030"       # primary orange
OX_D    = "#E85520"       # darker
OX_DK   = "#C03808"       # darkest (download btn)
OX_B    = "rgba(255,112,48,0.38)"
OX_GLOW = "rgba(255,112,48,0.12)"
SHADOW  = "#0A0100"
MONO    = "'JetBrains Mono', 'Courier New', monospace"
SANS    = "'IBM Plex Sans', system-ui, sans-serif"
# Soft drop shadow matching the logo — used everywhere
SOFT_SHADOW = "drop-shadow(3px 4px 5px rgba(10,1,0,0.65))"

LOGO_SVG = """<svg width="100%" viewBox="0 0 716 158" xmlns="http://www.w3.org/2000/svg">
<defs>
  <filter id="ds" x="-20%" y="-20%" width="150%" height="150%">
    <feDropShadow dx="3" dy="4" stdDeviation="4" flood-color="#1A0800" flood-opacity="0.7"/>
  </filter>
</defs>
<g filter="url(#ds)" shape-rendering="crispEdges">
<rect x="34" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="52" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="70" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="88" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="16" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="34" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="88" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="106" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="16" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="34" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="88" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="106" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="16" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="34" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="52" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="70" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="88" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="106" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="16" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="34" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="88" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="106" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="16" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="34" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="88" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="106" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="16" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="34" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="88" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="106" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="142" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="160" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="178" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="196" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="214" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="142" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="160" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="214" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="232" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="142" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="160" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="214" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="232" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="142" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="160" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="178" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="196" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="214" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="142" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="160" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="142" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="160" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="142" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="160" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="286" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="304" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="286" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="304" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="340" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="358" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="376" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="394" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="412" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="340" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="358" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="412" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="430" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="340" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="358" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="412" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="430" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="340" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="358" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="376" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="394" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="412" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="340" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="358" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="376" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="394" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="340" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="358" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="394" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="412" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="340" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="358" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="412" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="430" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="466" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="484" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="502" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="520" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="538" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="556" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="466" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="484" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="466" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="484" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="466" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="484" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="502" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="520" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="538" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="466" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="484" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="466" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="484" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="466" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="484" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="502" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="520" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="538" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="556" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="610" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="628" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="646" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="664" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="682" y="16" width="19" height="19" fill="#FFA868"/>
<rect x="592" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="610" y="34" width="19" height="19" fill="#FF9050"/>
<rect x="592" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="610" y="52" width="19" height="19" fill="#FF7A38"/>
<rect x="592" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="610" y="70" width="19" height="19" fill="#EE6422"/>
<rect x="592" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="610" y="88" width="19" height="19" fill="#DC5418"/>
<rect x="592" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="610" y="106" width="19" height="19" fill="#CC4412"/>
<rect x="610" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="628" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="646" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="664" y="124" width="19" height="19" fill="#BE380E"/>
<rect x="682" y="124" width="19" height="19" fill="#BE380E"/>
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

    # ── Global CSS + page sequencing JS ──────────────────────────────────────
    st.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>

    /* Chrome */
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stHeader"] {{ display:none !important; }}

    /* Background — warm charcoal */
    .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stBottom"] {{
        background: #1E1B17 !important;
        background-color: #1E1B17 !important;
    }}
    .main .block-container {{
        background: #1E1B17 !important;
        max-width: 720px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }}

    /* Global text */
    .stApp p, .stApp div, .stApp span,
    .stApp label, .stMarkdown {{
        color: #E0D0C0 !important;
        font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
        font-size: 15px !important;
    }}

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {{
        background: #26211C !important;
        border: 2px solid #3A2A1C !important;
        border-radius: 3px !important;
        transition: border-color 0.2s, filter 0.2s !important;
        filter: {SOFT_SHADOW} !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: rgba(255,112,48,0.38) !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] span {{
        color: #8A7060 !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 14px !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: #5A4030 !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 12px !important;
    }}
    [data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"] {{
        display: none !important;
    }}
    /* Button shell */
    [data-testid="stFileUploaderDropzone"] button {{
        background: #302820 !important;
        border: 1px solid #5A4030 !important;
        border-radius: 3px !important;
        color: #E0D0C0 !important;
        padding: 9px 22px !important;
        transition: all 0.15s !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        filter: {SOFT_SHADOW} !important;
    }}
    /* Every div layer inside the button — force flex centering */
    [data-testid="stFileUploaderDropzone"] button > div,
    [data-testid="stFileUploaderDropzone"] button > div > div {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    /* The <p> tag where Streamlit puts the label text */
    [data-testid="stFileUploaderDropzone"] button p {{
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 13px !important;
        letter-spacing: 0.06em !important;
        color: #E0D0C0 !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        width: 100% !important;
        display: block !important;
    }}
    [data-testid="stFileUploaderDropzone"] button:hover {{
        border-color: rgba(255,112,48,0.38) !important;
    }}
    [data-testid="stFileUploaderDropzone"] button:hover p {{
        color: #FF7030 !important;
    }}
    [data-testid="stFileChip"] {{
        background: #302820 !important;
        border: 1px solid #3A2A1C !important;
        border-radius: 2px !important;
    }}
    [data-testid="stFileChip"] > div:first-child {{ display: none !important; }}
    [data-testid="stFileChipName"] {{
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 13px !important;
        color: #E0D0C0 !important;
    }}
    [data-testid="stFileChipDeleteBtn"] button {{
        background: transparent !important;
        border: 1px solid #5A4030 !important;
        color: #8A7060 !important;
        border-radius: 2px !important;
        width: 22px !important; height: 22px !important;
        padding: 0 !important;
        font-size: 12px !important;
        transition: all 0.15s !important;
    }}
    [data-testid="stFileChipDeleteBtn"] button:hover {{
        border-color: #F87171 !important;
        color: #F87171 !important;
    }}

    /* ── Run button ── */
    .stButton > button {{
        background: transparent !important;
        border: 2px solid #E85520 !important;
        color: #FF7030 !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        padding: 16px !important;
        border-radius: 3px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        filter: {SOFT_SHADOW} !important;
    }}
    .stButton > button:hover:not(:disabled) {{
        background: rgba(255,112,48,0.12) !important;
        border-color: #FF7030 !important;
        filter: {SOFT_SHADOW} drop-shadow(0 0 18px {OX_GLOW}) !important;
    }}
    .stButton > button:disabled {{
        border-color: #5A4030 !important;
        color: #5A4030 !important;
        opacity: 1 !important;
        filter: none !important;
    }}

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {{
        background: #C03808 !important;
        border: none !important;
        color: #FFF0E8 !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        padding: 16px !important;
        border-radius: 3px !important;
        width: 100% !important;
        transition: all 0.2s !important;
        filter: {SOFT_SHADOW} !important;
    }}
    [data-testid="stDownloadButton"] > button:hover {{
        background: #E85520 !important;
        filter: {SOFT_SHADOW} drop-shadow(0 0 22px {OX_GLOW}) !important;
    }}

    /* ── Password input — single border on outer wrapper only ── */

    /* Outer container: the ONE border */
    [data-testid="stTextInput"] [data-baseweb="input"] {{
        background: #26211C !important;
        border: 2px solid #3A2A1C !important;
        border-radius: 4px !important;
        overflow: hidden !important;
        box-shadow: none !important;
        outline: none !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }}
    [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stTextInput"] [data-baseweb="input"]:focus {{
        border-color: #E85520 !important;
        box-shadow: 0 0 18px rgba(255,112,48,0.12) !important;
        outline: none !important;
    }}
    /* Kill every possible blue focus ring Streamlit/BaseWeb adds */
    [data-testid="stTextInput"] * {{
        outline: none !important;
    }}
    [data-testid="stTextInput"] *:focus,
    [data-testid="stTextInput"] *:focus-visible,
    [data-testid="stTextInput"] *:focus-within {{
        outline: none !important;
        box-shadow: none !important;
    }}

    /* Inner wrapper — no border, no background, no radius */
    [data-testid="stTextInput"] [data-baseweb="base-input"] {{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    /* The actual input element — no border */
    [data-testid="stTextInput"] input {{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        color: {OX} !important;
        font-family: {MONO} !important;
        font-size: 17px !important;
        caret-color: {OX} !important;
        padding: 13px 16px !important;
    }}
    [data-testid="stTextInput"] input:focus {{
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{ color: {DIM} !important; }}

    /* Eye icon container — no border, no background */
    [data-testid="stTextInput"] [data-baseweb="base-input"] > div {{
        background: transparent !important;
        border: none !important;
        border-left: none !important;
        box-shadow: none !important;
    }}
    /* Eye icon button */
    [data-testid="stTextInput"] button {{
        background: transparent !important;
        border: none !important;
        color: {DIM} !important;
        padding: 0 12px !important;
        cursor: pointer !important;
        transition: color 0.15s !important;
    }}
    [data-testid="stTextInput"] button:hover {{
        color: {OX} !important;
    }}

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div {{ border-top-color: #FF7030 !important; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
    ::-webkit-scrollbar-track {{ background: #1E1B17; }}
    ::-webkit-scrollbar-thumb {{ background: #5A4030; border-radius: 2px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #E85520; }}
    </style>

    <script>
    (function() {{
        var doc = window.parent.document;

        // Hide everything below logo immediately
        function hideContent() {{
            var blocks = Array.from(doc.querySelectorAll('[data-testid="stVerticalBlock"] > div'));
            if (blocks.length < 2) {{ setTimeout(hideContent, 80); return; }}
            blocks.slice(1).forEach(function(el) {{
                el.style.opacity = "0";
                el.style.transform = "translateY(14px)";
                el.style.pointerEvents = "none";
            }});
        }}
        hideContent();

        // Reveal sequentially after logo completes (~5.8s)
        setTimeout(function() {{
            var blocks = Array.from(doc.querySelectorAll('[data-testid="stVerticalBlock"] > div')).slice(1);
            blocks.forEach(function(el, i) {{
                setTimeout(function() {{
                    el.style.transition = "opacity 0.6s cubic-bezier(0.4,0,0.2,1), transform 0.6s cubic-bezier(0.4,0,0.2,1)";
                    el.style.opacity = "1";
                    el.style.transform = "translateY(0)";
                    el.style.pointerEvents = "";
                }}, i * 220);
            }});
            // Focus password after it appears
            setTimeout(function() {{
                var inp = doc.querySelector('[data-testid="stTextInput"] input');
                if (inp) inp.focus();
            }}, blocks.length * 220 + 100);
        }}, 5800);
    }})();
    </script>
    """)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def section(num, title, hint=""):
        hint_html = (
            f'<span style="font-family:{SANS};font-size:14px;color:{DIM};'
            f'font-weight:300;margin-left:12px;">{hint}</span>'
        ) if hint else ""
        st.html(f"""
        <div style="display:flex;align-items:center;margin-bottom:12px;margin-top:4px;">
            <span style="font-family:{MONO};font-size:12px;color:{DIM};
                letter-spacing:0.18em;">{num}</span>
            <span style="font-family:{MONO};font-size:16px;font-weight:700;
                color:{TEXT};letter-spacing:0.08em;text-transform:uppercase;
                margin-left:14px;">{title}</span>
            {hint_html}
        </div>""")

    def gap(px=24):
        st.html(f'<div style="margin-bottom:{px}px;"></div>')

    def note(msg, color=OX, icon="✓"):
        st.html(
            f'<div style="font-family:{MONO};font-size:14px;color:{color};'
            f'margin-top:8px;letter-spacing:0.02em;">'
            f'{icon}&nbsp;&nbsp;{msg}</div>'
        )

    # ── Logo component ─────────────────────────────────────────────────────────
    logo_html = (
        f'<div style="border-bottom:1px solid {BORDER};padding-bottom:20px;margin-bottom:0;">'
        + LOGO_SVG
        + f"""
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&family=IBM+Plex+Sans:wght@300&display=swap" rel="stylesheet">
        <div style="display:flex;align-items:center;gap:14px;margin-top:16px;padding:0 4px;">
            <span style="font-family:{MONO};font-size:10px;color:{DIM};
                letter-spacing:0.16em;text-transform:uppercase;">v6.0</span>
            <span style="font-family:{SANS};font-size:13px;color:{MUTED};
                font-weight:300;letter-spacing:0.04em;">
                vendor statement reconciliation processor</span>
        </div>
        </div>
        <style>
        svg rect{{transform-box:fill-box;transform-origin:center;}}
        @keyframes pixelFall{{
          0%   {{opacity:0;transform:translateY(-150px);}}
          75%  {{opacity:1;transform:translateY(3px);}}
          100% {{opacity:1;transform:translateY(0);}}
        }}
        </style>
        <script>
        (function(){{
            var P=18,ns="http://www.w3.org/2000/svg";
            var rects=Array.from(document.querySelectorAll("svg rect"));
            var maxY=Math.max.apply(null,rects.map(function(r){{return parseFloat(r.getAttribute("y"));}}));
            var minY=Math.min.apply(null,rects.map(function(r){{return parseFloat(r.getAttribute("y"));}}));
            var initDelay=800,rowGap=200,animDur="0.9s",lastLand=0;

            rects.forEach(function(r){{
                var y=parseFloat(r.getAttribute("y")),x=parseFloat(r.getAttribute("x"));
                var rowIndex=Math.round((maxY-y)/P);
                var jitter=((x*7+y*3)%60)-30;
                var delay=initDelay+80+(rowIndex*rowGap)+jitter;
                delay=Math.max(initDelay,delay);
                lastLand=Math.max(lastLand,delay);
                r.style.animationName="pixelFall";
                r.style.animationDuration=animDur;
                r.style.animationTimingFunction="cubic-bezier(0.2,0.8,0.4,1)";
                r.style.animationFillMode="both";
                r.style.animationDelay=delay+"ms";
            }});

            // Gradient merge via SVG SMIL after all pixels land
            var mergeStart=lastLand+950;
            function lerp(a,b,t){{return Math.round(a+(b-a)*t);}}
            function hex2(n){{return("0"+Math.min(255,Math.max(0,n)).toString(16)).slice(-2);}}

            setTimeout(function(){{
                rects.forEach(function(r){{
                    var y=parseFloat(r.getAttribute("y"));
                    var t=(y-minY)/(maxY-minY);
                    var from=r.getAttribute("fill");
                    var to="#"+hex2(lerp(255,190,t))+hex2(lerp(168,56,t))+hex2(lerp(104,14,t));
                    var anim=document.createElementNS(ns,"animate");
                    anim.setAttribute("attributeName","fill");
                    anim.setAttribute("from",from);
                    anim.setAttribute("to",to);
                    anim.setAttribute("dur","2.4s");
                    anim.setAttribute("fill","freeze");
                    anim.setAttribute("calcMode","spline");
                    anim.setAttribute("keyTimes","0;1");
                    anim.setAttribute("keySplines","0.4 0 0.2 1");
                    anim.setAttribute("begin","indefinite");
                    r.appendChild(anim);
                    anim.beginElement();
                }});
            }},mergeStart);
        }})();
        </script>"""
    )
    _stc.html(logo_html, height=240, scrolling=False)

    # ── 01  Access Key ────────────────────────────────────────────────────────
    if not st.session_state.authenticated:
        gap(32)
        section("01", "Access Key")
        st.html(
            f'<div style="font-family:{MONO};font-size:14px;color:{DIM};'
            f'margin-bottom:12px;letter-spacing:0.03em;">enter access key to continue</div>'
        )
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
        gap(28)
        st.html(
            f'<div style="margin-bottom:32px;">'
            f'<span style="font-family:{MONO};font-size:14px;color:{OX};'
            f'letter-spacing:0.08em;padding:7px 14px;'
            f'border:1px solid {OX_B};border-radius:3px;'
            f'background:{OX_GLOW};'
            f'filter:{SOFT_SHADOW};">authenticated</span></div>'
        )

    # ── 02  GL Export ─────────────────────────────────────────────────────────
    section("02", "GL Export", "accepts .csv")
    gl_upload = st.file_uploader(
        "GL CSV", type=["csv"],
        key="gl_file", label_visibility="collapsed")
    if gl_upload:
        note(gl_upload.name)
    gap(28)

    # ── 03  Vendor Statements ─────────────────────────────────────────────────
    section("03", "Vendor Statements", "accepts .pdf · .xlsx · multiple files OK")
    stmt_uploads = st.file_uploader(
        "Vendor Statements", type=["pdf", "xlsx"],
        accept_multiple_files=True,
        key="stmt_files", label_visibility="collapsed")
    if stmt_uploads:
        n = len(stmt_uploads)
        note(f'{n} file{"s" if n != 1 else ""} loaded')
    gap(32)

    # ── 04  Execute ───────────────────────────────────────────────────────────
    section("04", "Execute")
    run_disabled = not (gl_upload and stmt_uploads)
    run_clicked = st.button(
        "▶   RUN RECONCILIATION" if not run_disabled else "─   AWAITING INPUT",
        disabled=run_disabled,
        use_container_width=True)

    # ── Processing ────────────────────────────────────────────────────────────
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
            gap(14)

            n_rec  = len(reconciled)
            n_skip = len(skipped)
            total  = n_rec + n_skip
            pct    = int(n_rec / total * 100) if total else 0
            bar    = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

            skip_html = ""
            if skipped:
                rows = "".join(
                    f'<div style="padding:4px 0;font-size:14px;color:{OX};">'
                    f'✕&nbsp;&nbsp;{f}</div>' for f in skipped)
                skip_html = (
                    f'<div style="border-top:1px solid rgba(255,107,0,0.25);'
                    f'margin-top:16px;padding-top:14px;">'
                    f'<div style="font-size:12px;color:{OX};letter-spacing:0.14em;'
                    f'text-transform:uppercase;margin-bottom:10px;font-family:{MONO};">'
                    f'✕&nbsp;&nbsp;Not Reconciled</div>{rows}</div>'
                )

            ok = n_skip == 0
            st.html(
                f'<div style="background:{SURFACE};border:2px solid {OX_D};'
                f'border-radius:3px;padding:22px 26px;font-family:{MONO};'
                f'filter:{SOFT_SHADOW};">'
                f'<div style="font-size:24px;font-weight:700;color:#FFA868;'
                f'letter-spacing:-0.01em;margin-bottom:8px;">'
                f'◈&nbsp;&nbsp;{n_rec} / {total}&nbsp;&nbsp;files reconciled</div>'
                f'<div style="font-size:13px;color:rgba(255,168,104,0.4);'
                f'letter-spacing:0.08em;margin-bottom:12px;">{bar}&nbsp;&nbsp;{pct}%</div>'
                f'<div style="font-size:15px;letter-spacing:0.04em;'
                f'color:{"#FFA868" if ok else OX};">'
                f'{"✓&nbsp;&nbsp;all files processed" if ok else f"✕&nbsp;&nbsp;{n_skip} file{'s' if n_skip!=1 else ''} not reconciled"}'
                f'</div>{skip_html}</div>'
            )

    # ── Footer ────────────────────────────────────────────────────────────────
    st.html(
        f'<div style="border-top:1px solid {BORDER};margin-top:56px;padding-top:18px;'
        f'display:flex;justify-content:space-between;font-family:{MONO};'
        f'font-size:12px;color:{DIM};letter-spacing:0.1em;text-transform:uppercase;">'
        f'<span>internal use only</span>'
        f'<span>◈&nbsp;ap·rec&nbsp;·&nbsp;v6</span></div>'
    )


if __name__ == "__main__":
    main()
