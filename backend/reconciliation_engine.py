"""
Vendor Statement Reconciliation Engine v4
Platform-agnostic core — no UI dependencies.
Can be imported by Streamlit, Flask, FastAPI, CLI, or any other interface.

Usage:
    from reconciliation_engine import run_reconciliation
    result_bytes, filename, reconciled, skipped = run_reconciliation(gl_path, stmt_paths)
"""
import os, re, io, shutil, tempfile
from datetime import date, datetime
import pandas as pd
import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ── Mappings ───────────────────────────────────────────────────────────────
LOC = {
    "SH19":["SH-93004"],"SH":["SH-93001","SH-93002"],"LIB":["LIB-96100"],
    "MD":["MAD-80041"],
    "OE":["OE","OE-96001","OE-96003","OE-96004","OE-96005","OE-96008","OE-96011"],
    "PRED":["PRED","PRED-82000"],
    "OCMGT":["OCMGT","OCMGT-71000","OCMGT-71001"],
    "JTS":["JTS-01636","JTS-98001","JTS-98009","JTS-98011","JTS-98012","JTS-98014"],
}
VM = {
    "BUCCANEER":"Buccaneer Linen Service",
    "CKS BAR":"CKS PRODUCE INC","CKS":"CKS PRODUCE INC",
    "ED DON":"Edward Don & Company",
    "ROMANOS COF BAR":"Romanos Bakery Of Boca Inc","ROMANOS":"Romanos Bakery Of Boca Inc",
    "CINTAS":["Cintas","CINTAS CORPORATION (UNIFORMS)","CINTAS CORP"],
    "CW":"The Chefs Warehouse of Florida, LLC","DEX IMAGING":"DEX Imaging LLC",
    "GOURMET FOODS":"GOURMET FOODS INTERNATIONAL LAKELAND INC",
    "HALPERNS":"Halperns's Steak & Seafood","PIPER FIRE":"PIPER FIRE PROTECTION INC",
    "PROPANE NINJA":"Propane Ninja","MR GREENS":"MR GREENS PRODUCE",
    "BUSH BROS":"BUSH BROTHERS PROVISION COMPANY LLC","US PAPER":"US PAPER CORP",
    "AMAZON":"Amazon Capital Services","FRANK GAY":"FRANK GAY SERVICES LLC",
    "PENGUIN":"Penguin Random House LLC","GFS":"Gordon Food Service",
    "COF BAR":"Gordon Food Service",
    "ZWIESEL FORTESSA":"Zwiesel Fortessa Americas LLC",
    "FORTESSA":"Zwiesel Fortessa Americas LLC",
    "UNIFIRST":"Unifirst Corporation",
    "CULIGAN":"Culligan Water","CULLIGAN":"Culligan Water",
    "SAMUELS":"Samuels and Son Seafood South Coast LLC",
    "WRI":"WRIGHTS GOURMET HOUSE",
    "COZZINI":"Cozzini Bros. Inc",
}

# ══════════════════════════════════════════════════════════════════════════
#  THEME  —  mirrors the website's CSS custom properties
#  --bg      #1E1B17   dark warm background
#  --surface #26211C   card / panel background
#  --hi      #302820   slightly lighter warm brown
#  --text    #E8DDD0   cream
#  --muted   #8C7B6A   warm grey-brown
#  --ox      #FF7030   orange accent
#  log-ok    #86EFAC   green
#  log-skip  #FCD34D   amber
#  log-err   #F87171   red
# ══════════════════════════════════════════════════════════════════════════

# Fills
HDR   = PatternFill("solid", fgColor="FF7030")   # orange header (detail sheets)
SHDRF = PatternFill("solid", fgColor="1E1B17")   # dark header  (summary sheet)
MATCH = PatternFill("solid", fgColor="D6EDE0")   # light green
VAR   = PatternFill("solid", fgColor="F5EDBE")   # dark amber
MISS  = PatternFill("solid", fgColor="F5D4D4")   # dark red
OCR_F = PatternFill("solid", fgColor="E2DDEF")   # dark purple
STRIPE= PatternFill("solid", fgColor="F2EDE8")   # surface
ALT   = PatternFill("solid", fgColor="E8E2DC")   # hi (alternating row)
NEON  = PatternFill("solid", fgColor="FF7030")   # jump-back button

# Fonts  (openpyxl requires hex without #)
_A  = Font(name="Aptos", size=11, color="2A2118")                          # body
_AH = Font(name="Aptos", size=11, bold=True, color="1E1B17")               # detail header
_AS = Font(name="Aptos", size=11, bold=True, color="FF7030")               # summary header
_AL = Font(name="Aptos", size=11, color="FF7030", underline="single")      # hyperlink
_JF = Font(name="Aptos", size=11, bold=True,  color="1E1B17")              # jump-back label

_AM  = Font(name="Aptos", size=11, color="1A7A40")   # matched amount
_AV  = Font(name="Aptos", size=11, color="7A6000")   # variance amount
_AMI = Font(name="Aptos", size=11, color="B02020")   # missing amount

# Borders
THIN_ORANGE = Border(
    left=Side(style="thin", color="FF7030"),
    right=Side(style="thin", color="FF7030"),
    top=Side(style="thin", color="FF7030"),
    bottom=Side(style="thin", color="FF7030"),
)
NO_BORDER = Border()

COMMA_FMT = '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
COMMA_INT  = '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)'
DATE_FMT   = 'M/D/YYYY'
ROW_HT     = 18
MONEY_MIN_W= 24

SKIP_TYPES = {"Payment", "Unapplied Cash"}

# ── Date normalizer ────────────────────────────────────────────────────────
def _norm_date(s):
    if not s or not isinstance(s, str):
        return s
    s = s.strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S",
                "%b %d %Y", "%B %d %Y", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return s

# ══════════════════════════════════════════════════════════════════════════
#  PARSERS
# ══════════════════════════════════════════════════════════════════════════

def _pdf(fp):
    try:
        pdf = pdfplumber.open(fp)
        t = "\n".join(p.extract_text() or "" for p in pdf.pages)
        pdf.close()
        if t.strip():
            return t
    except Exception:
        pass
    try:
        from pdf2image import convert_from_path
        import pytesseract
        pages = convert_from_path(fp, dpi=200)
        return "\n".join(pytesseract.image_to_string(p) for p in pages)
    except Exception:
        return ""

def parse_buccaneer(t):
    R = []
    for m in re.finditer(
        r'(\d{2}/\d{2}/\d{4})\s+INV\s+#(\d+)\.\s+(?:Due\s+\d{2}/\d{2}/\d{4}\.\s+)?'
        r'Orig\.\s+Amount\s+\$([\d,]+\.\d{2})\.', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_cks(t):
    R = []
    for m in re.finditer(
        r'(\d{2}/\d{2}/\d{4})\s+(Invoice|Credit Memo|Payment)\s+#(INV\d+|CM\d+|PMT\d+)\s+\$([\d,]+\.\d{2})', t):
        d,tp,inv,a = m.groups(); amt = float(a.replace(",",""))
        if tp == "Credit Memo": amt = -amt
        elif tp == "Payment": amt = -amt
        R.append({"Date":d,"Invoice":inv,"Amount":amt,"Type":tp})
    return R

def parse_edward_don(t):
    R = []; seen = set()
    # New format: optional PO# between date and due date
    # 0001250580 0034896458 Mar 16 2026 Richard Apr 15 2026 1,104.30 USD
    # 0001250580 0034959162 Mar 27 2026 Apr 26 2026 607.32 USD  (no PO#)
    pat_inv = re.compile(
        r'\d{10}\s+(\d{10})\s+(\w+\s+\d{1,2}\s+\d{4})\s+'
        r'(?:\S+\s+)?\w+\s+\d{1,2}\s+\d{4}\s+([\d,]+\.\d{2})\s+USD', re.I)
    pat_crd = re.compile(
        r'\d{10}\s+(\d{10})\s+(\w+\s+\d{1,2}\s+\d{4})\s+'
        r'(?:\S+\s+)?\w+\s+\d{1,2}\s+\d{4}\s+\(([\d,]+\.\d{2})\s+USD\)', re.I)
    for m in pat_inv.finditer(t):
        inv = m[1].lstrip("0")
        if inv not in seen:
            seen.add(inv)
            R.append({"Date":m[2],"Invoice":inv,"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    for m in pat_crd.finditer(t):
        inv = m[1].lstrip("0")
        if inv not in seen:
            seen.add(inv)
            R.append({"Date":m[2],"Invoice":inv,"Amount":-float(m[3].replace(",","")),"Type":"Credit Memo"})
    return R

def parse_romanos(t):
    R = []
    for m in re.finditer(
        r'(\d{2}/\d{2}/\d{4})\s+INV\s+#(\d+)\.\s+Orig\.\s+Amount\s+\$([\d,]+\.\d{2})\.', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_cintas(t):
    R = []; c = t.encode('ascii','replace').decode('ascii')
    for m in re.finditer(r'(\d{7,})\s+(\d{2}/\d{2}/\d{2})\s+\d{2}/\d{2}\S*\s+([\d,]+\.\d{2})', c):
        R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_chefs_warehouse(t):
    R = []
    for line in t.split('\n'):
        L = line.strip()
        m = re.match(r'^(\d{8})\s+(\d{2}/\d{2}/\d{2})\s+Invoice\s+'
                     r'([\d,]+\.\d{2})\s+\([\d,]+\.\d{2}\)\s+[\d,]+\.\d{2}', L)
        if m: R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"}); continue
        m = re.match(r'^(\d{8})\s+(\d{2}/\d{2}/\d{2})\s+Invoice\s+'
                     r'([\d,]+\.\d{2})\s+[\d,]+\.\d{2}', L)
        if m: R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"}); continue
        m = re.match(r'^(\d{8})\s+(\d{2}/\d{2}/\d{2})\s+\(([\d,]+\.\d{2})\)\s+\([\d,]+\.\d{2}\)', L)
        if m: R.append({"Date":m[2],"Invoice":m[1],"Amount":-float(m[3].replace(",","")),"Type":"Credit Memo"}); continue
        m = re.match(r'^(\d{7,})\s+(\d{2}/\d{2}/\d{2})\s+\(([\d,]+\.\d{2})\)\s+\([\d,]+\.\d{2}\)', L)
        if m: R.append({"Date":m[2],"Invoice":m[1],"Amount":-float(m[3].replace(",","")),"Type":"Unapplied Cash"})
    return R

def parse_dex_imaging(t):
    R = []
    for m in re.finditer(
        r'(?:Contract\s+)?Invoice\s+(\d{1,2}/\d{1,2}/\d{4})\s+\d{1,2}/\d{1,2}/\d{4}\s+(AR\d+)\s+\S+\s+\$([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_gourmet_foods(t):
    R = []
    for m in re.finditer(r'(\d{8})\s+(\d+)\s+(INV|CM)\s+([\d,]+\.\d{2})', t):
        dr,inv,tp,a = m.groups(); amt = float(a.replace(",",""))
        if tp == "CM": amt = -amt
        R.append({"Date":f"{dr[:4]}-{dr[4:6]}-{dr[6:8]}","Invoice":inv,"Amount":amt,
                   "Type":"Invoice" if tp=="INV" else "Credit Memo"})
    return R

def parse_halperns(t):
    R = []
    for m in re.finditer(
        r'(\d{2}/\d{2}/\d{4})\s+INV#\s*(\d+(?:-\w+)?)\s+Due\s+\d{2}/\d{2}/\d{4}\s+'
        r'(-?[\d,]+\.\d{2})\s+-?[\d,]+\.\d{2}', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),
                   "Type":"Credit Memo" if "-C" in m[2] else "Invoice"})
    return R

def parse_piper_fire(t):
    R = []
    for m in re.finditer(r'(\d{4}-\d{2}-\d{2})\s+(\d+)\s+\$([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_propane_ninja(_):
    return [
        {"Date":"02/03/2026","Invoice":"1084999","Amount":-214.86,"Type":"Credit (OCR)"},
        {"Date":"02/21/2026","Invoice":"1091427","Amount":432.63,"Type":"Invoice (OCR)"},
    ]

def parse_mr_greens(t):
    R = []
    for m in re.finditer(
        r'^([A-Z]{2}\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(?:\S+\s+\d{2}/\d{2}/\d{4}\s+)?'
        r'(-?[\d,]+\.\d{2})\s+-?[\d,]+\.\d{2}', t, re.MULTILINE):
        tp = "VOID" if "VOID" in t[max(0,m.start()-10):m.end()+10] else "Invoice"
        R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":tp})
    return R

def parse_bush_bros(t):
    R = []
    for m in re.finditer(
        r'(\d{1,2}/\d{1,2}/\d{4})\s+Invoice\s+(\d+)\s+.+?\s+([\d,]+\.\d{2})\s+[\d,]+\.\d{2}', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    for m in re.finditer(r'(\d{1,2}/\d{1,2}/\d{4})\s+Payment\s+(\S+)\s+.+?\s+-([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":-float(m[3].replace(",","")),"Type":"Payment"})
    return R

def parse_us_paper(t):
    D = {}; cur = None
    for line in t.split('\n'):
        L = line.strip()
        if L in ("MAD DOGS AND ENGLISHMEN","OXFORD EXCHANGE LLC","Predalina LLC",
                  "SH-19","The Library St Pete","The Stovall House"):
            cur = L; D.setdefault(cur,[]); continue
        if cur and re.match(r'^\d{2}/\d{2}/\d{4}', L):
            m = re.match(r'(\d{2}/\d{2}/\d{4})\s+Invoice\s+(\d+)\s+\d{2}/\d{2}/\d{4}\s+([\d,]+\.\d{2})', L)
            if m: D[cur].append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return D

def parse_frank_gay(t):
    R = []
    for m in re.finditer(
        r'(\d{9})\s+(?:Net\s+)?.*?(\d{1,2}/\d{1,2}/\d{2})\s+'
        r'\$([\d,]+\.\d{2})\s+\$[\d,]+\.\d{2}\s+\$([\d,]+\.\d{2})', t, re.DOTALL):
        R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_penguin(t):
    R = []
    for m in re.finditer(
        r'(\d{2}/\d{2}/\d{4})\s+(\d{10})\s+\d{4}\s+(?:\S+\s+)?'
        r'\d{2}/\d{2}/\d{4}\s+(CM|RV|IN)\s+(-?[\d,]+\.\d{2}-?)', t):
        a = m[4]; amt = -float(a[:-1].replace(",","")) if a.endswith('-') else float(a.replace(",",""))
        if m[3] == "CM": amt = -abs(amt)
        R.append({"Date":m[1],"Invoice":m[2],"Amount":amt,
                   "Type":{"CM":"Credit Memo","RV":"Revision","IN":"Invoice"}.get(m[3],m[3])})
    return R

def parse_gfs(t):
    R = []
    # New format: 9033136729 03/10/2026 Invoice $ 3,269.46
    for m in re.finditer(r'(\d{7,})\s+(\d{2}/\d{2}/\d{4})\s+Invoice(?:\s+\d+)?\s+\$\s*([\d,]+\.\d{2})', t, re.I):
        R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    # Credit: 2003236479 03/19/2026 Credit 9033338797 -$ 14.81
    for m in re.finditer(r'(\d{7,})\s+(\d{2}/\d{2}/\d{4})\s+Credit\s+\d+\s+-?\$\s*([\d,]+\.\d{2})', t, re.I):
        R.append({"Date":m[2],"Invoice":m[1],"Amount":-float(m[3].replace(",","")),"Type":"Credit Memo"})
    # Old format fallback
    if not R:
        for m in re.finditer(r'(\d{9,})\s+(\d{2}/\d{2}/\d{2})\s+INVOICE\s+(?:\d+\s+)?([\d,]+\.\d{2})', t, re.I):
            R.append({"Date":m[2],"Invoice":m[1],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_amazon_xl(fp):
    R = []
    try:
        df = pd.read_excel(fp, sheet_name="Invoices", header=None)
        if len(df) > 4:
            for i in range(4, len(df)):
                r = df.iloc[i]; inv = str(r.iloc[1]) if pd.notna(r.iloc[1]) else ""
                d = str(r.iloc[2]) if pd.notna(r.iloc[2]) else ""
                amt = r.iloc[8] if pd.notna(r.iloc[8]) else 0
                if inv: R.append({"Date":d[:10],"Invoice":inv,"Amount":float(amt),"Type":"Invoice"})
    except Exception:
        pass
    return R

def parse_fortessa(t):
    R = []
    pat = re.compile(
        r'(\d{2}/\d{2}/\d{4})\s+Invoice\s+.*?\$([\d,]+\.\d{2})\s+\d{2}/\d{2}/\d{4}.*?\n(#INV\d+)',
        re.DOTALL)
    for m in pat.finditer(t):
        R.append({"Date":m[1],"Invoice":m[3].lstrip("#"),"Amount":float(m[2].replace(",","")),"Type":"Invoice"})
    return R

def parse_unifirst(t):
    R = []
    for m in re.finditer(r'(\d{2}/\d{2}/\d{4})\s+(\d{7,})\s+([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_culligan(t):
    R = []
    for m in re.finditer(r'(\d{2}/\d{2}/\d{4})\s+(\d{7,})\s+\d+\s+PO#\s+([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_samuels(t):
    R = []
    for m in re.finditer(r'(\d{2}/\d{2}/\d{2})\s+I\s+(\d+)\s+([\d,]+\.\d{2})\s', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_wri(t):
    R = []
    for m in re.finditer(r'(\d{2}/\d{2}/\d{4})\s+(\d{7,})\s+\$([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

def parse_cozzini(t):
    R = []
    for m in re.finditer(r'(\d{1,2}/\d{1,2}/\d{4})\s+Invoice\s+#(C\d+)\s+([\d,]+\.\d{2})', t):
        R.append({"Date":m[1],"Invoice":m[2],"Amount":float(m[3].replace(",","")),"Type":"Invoice"})
    return R

from difflib import SequenceMatcher

def _fuzzy_rank(query, candidates, n=12):
    q = query.upper().replace("_"," ")
    scored = []
    for c in candidates:
        cu = c.upper()
        ratio = SequenceMatcher(None, q, cu).ratio()
        if any(w in cu for w in q.split() if len(w) > 2):
            ratio += 0.25
        scored.append((ratio, c))
    scored.sort(reverse=True)
    return [c for _, c in scored[:n]]

def parse_service_statement(t):
    """Generic service/field statement: short invoice#, date, $amount."""
    R = []; seen = set()
    for m in re.finditer(r'^(\d{5,8})\s+\d{1,2}/\d{1,2}/\d{2,4}.*?\$(\d[\d,]+\.\d{2})', t, re.MULTILINE):
        inv = m[1]
        if inv not in seen:
            seen.add(inv)
            try:
                amt = float(m[2].replace(",",""))
                if 0 < amt < 1_000_000:
                    R.append({"Date":"","Invoice":inv,"Amount":amt,"Type":"Invoice"})
            except: pass
    return R

def parse_generic(t):
    """
    Universal invoice extractor — works on any vendor format.
    Fixed: no year-numbers, no double-counting, preserves alphanumeric invoice IDs.
    """
    rows = []
    seen = set()
    inv_lines = set()

    def clean_amt(s):
        s = str(s).replace(',','').replace('$','').strip()
        neg = s.startswith('(') and s.endswith(')')
        s = s.strip('()').rstrip('-')
        try:
            v = float(s)
            return -v if neg else v
        except:
            return None

    def is_year(s):
        try: return 1900 <= int(s) <= 2099
        except: return False

    def add(inv, amt, date='', typ=None, line_idx=None):
        inv = str(inv).strip().rstrip('.')
        if re.match(r'^\d+$', inv):
            norm = inv.lstrip('0') or inv
        else:
            norm = inv
        if len(norm) < 3: return
        if is_year(norm): return
        if inv in seen or norm in seen: return
        v = clean_amt(amt) if not isinstance(amt, float) else amt
        if v is None or abs(v) < 0.01 or abs(v) > 5_000_000: return
        if typ is None: typ = 'Credit Memo' if v < 0 else 'Invoice'
        seen.add(inv); seen.add(norm)
        if line_idx is not None: inv_lines.add(line_idx)
        rows.append({"Date": date, "Invoice": norm, "Amount": v, "Type": typ})

    lines = t.split('\n')
    DATE = r'(?:\d{1,2}[/\.\-]\d{1,2}[/\.\-]\d{2,4})'
    AMT  = r'(\(\d[\d,]+\.\d{2}\)|\d[\d,]+\.\d{2})'

    # S1: Explicit Invoice/Credit labels — highest priority
    # Requires invoice ID starts with a digit (or optional letter then digit)
    for i, line in enumerate(lines):
        m = re.search(
            r'(?:Invoice|INV)[#\s\.\-]+([A-Z]?\d[A-Z0-9\-]*)[\s:,\.]+.*?'
            r'(?:Orig(?:inal)?\.?\s+Amount\s+\$?\s*|Amount\s+\$?\s*)?' + AMT, line, re.I)
        if m:
            add(m.group(1).rstrip('.'), m.group(2), line_idx=i)
            inv_lines.add(i)
        m = re.search(r'Credit[_ ]?Memo[#\s\.\-]+([A-Z]?\d[A-Z0-9\-]*)[\s:,\.]+.*?' + AMT, line, re.I)
        if m:
            v = clean_amt(m.group(2))
            if v: add(m.group(1), -abs(v), typ='Credit Memo', line_idx=i)

    # S2: [optional aging code] Date + 7-12 digit invoice + amount at end of line
    for i, line in enumerate(lines):
        if i in inv_lines: continue
        m = re.search(rf'(?:^|\s)({DATE})\s+(\d{{7,12}})\b.*?' + AMT + r'\s*$', line.strip())
        if m and not is_year(m.group(2)):
            add(m.group(2), m.group(3), date=m.group(1), line_idx=i)

    # S3: Long number + date + Invoice/Credit + amount (GFS)
    for m in re.finditer(
        rf'(\d{{7,12}})\s+({DATE})\s+(?:Invoice|Credit)(?:\s+\d+)?\s+\$?\s*([\d,]+\.\d{{2}})', t, re.I):
        if not is_year(m.group(1)):
            add(m.group(1), m.group(3), date=m.group(2))

    # S4: Edward Don — 10-digit IDs + month-name date + USD
    for m in re.finditer(
        r'\d{10}\s+(\d{10})\s+(\w+\s+\d{1,2}\s+\d{4})\s+'
        r'(?:\S+\s+)?\w+\s+\d{1,2}\s+\d{4}\s+'
        r'(\(\d[\d,]+\.\d{2}\)|\d[\d,]+\.\d{2})\s+USD', t, re.I):
        add(m.group(1).lstrip('0'), m.group(3), date=m.group(2))

    # S5: Samuels/ledger — date + single letter type + number + amount
    for m in re.finditer(rf'({DATE})\s+[IiCcPp]\s+(\d{{5,}})\s+([\d,]+\.\d{{2}})', t):
        c = m.group(0)[len(m.group(1)):].strip()[0].upper()
        add(m.group(2), m.group(3), date=m.group(1),
            typ='Invoice' if c == 'I' else 'Credit Memo')

    # S6: Last resort — $amount lines not already processed, filter years
    for i, line in enumerate(lines):
        if i in inv_lines: continue
        if re.search(r'\$[\d,]+\.\d{2}', line):
            nums = re.findall(r'\b(\d{4,12})\b', line)
            amts = re.findall(r'\$([\d,]+\.\d{2})', line)
            if nums and amts:
                for n in nums:
                    if not is_year(n) and n not in seen:
                        add(n, amts[0], line_idx=i); break

    return rows


def parse_wrights(t):
    R = []
    inv_lines = re.findall(r'(\d{2}/\d{2}/\d{2})\s+(\d{7})', t)
    parts = re.split(r'Amount\s+Balance\s+Due\s+by', t, maxsplit=1, flags=re.IGNORECASE)
    amt_section = parts[1] if len(parts) > 1 else t
    amt_lines = re.findall(r'([\d,]+\.\d{2})\s+[\d,]+\.\d{2}\s+\d{2}/\d{2}/\d{2}', amt_section)
    for i, (date, inv) in enumerate(inv_lines):
        if i < len(amt_lines):
            R.append({"Date":date,"Invoice":inv,
                      "Amount":float(amt_lines[i].replace(",","")),"Type":"Invoice"})
    return R

PARSERS = {
    "BUCCANEER":parse_buccaneer,"CKS BAR":parse_cks,"CKS":parse_cks,
    "ED DON":parse_edward_don,"ROMANOS COF BAR":parse_romanos,"ROMANOS":parse_romanos,
    "CINTAS":parse_cintas,"CW":parse_chefs_warehouse,"DEX IMAGING":parse_dex_imaging,
    "GOURMET FOODS":parse_gourmet_foods,"HALPERNS":parse_halperns,
    "PIPER FIRE":parse_piper_fire,"PROPANE NINJA":parse_propane_ninja,
    "MR GREENS":parse_mr_greens,"BUSH BROS":parse_bush_bros,
    "US PAPER":parse_us_paper,"FRANK GAY":parse_frank_gay,
    "PENGUIN":parse_penguin,"GFS":parse_gfs,"COF BAR":parse_gfs,"AMAZON":None,
    "ZWIESEL FORTESSA":parse_fortessa,"FORTESSA":parse_fortessa,
    "UNIFIRST":parse_unifirst,
    "CULIGAN":parse_culligan,"CULLIGAN":parse_culligan,
    "SAMUELS":parse_samuels,
    "WRI":parse_wrights,
    "COZZINI":parse_cozzini,
}

# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════

def fi(fn):
    n = fn.replace(".pdf","").replace(".xlsx","").upper()
    loc = None
    for p in ["SH19","SH","LIB","MD","OE","PRED","OCMGT"]:
        if n.startswith(p+" "): loc = p; break
    vk = None; rem = n[len(loc):].strip() if loc else n
    for k in sorted(VM, key=len, reverse=True):
        if rem.startswith(k): vk = k; break
    return loc, vk

def glk(gl, vn, locs):
    if isinstance(vn, str): vn = [vn]
    m = gl["Vendor name"].isin(vn)
    if locs: m &= gl["Location ID"].isin(locs)
    return gl[m].groupby("Document number")["Amount"].sum().to_dict()

def mi(inv, lk):
    # Try multiple variants to match GL document numbers
    inv = str(inv).strip()
    candidates = [
        inv,                                              # exact
        inv.lstrip("0") or inv,                          # strip leading zeros
        inv.zfill(10) if inv.isdigit() and len(inv)<10 else None,  # zero-padded
        f"INV-{inv}" if inv.isdigit() else None,         # add INV- prefix
        f"INV{inv}" if inv.isdigit() else None,           # add INV prefix
        re.sub(r'^INV[-\s]?', '', inv),                  # strip INV- prefix
        re.sub(r'^INV[-\s]?', '', inv).lstrip("0"),      # strip prefix + zeros
    ]
    for c in candidates:
        if c and c in lk: return c, lk[c]
    return None, None

def _aw(ws, nc, mr=200, money_cols=None):
    if money_cols is None:
        money_cols = set()
    for c in range(1, nc+1):
        mx = max((len(str(ws.cell(r,c).value or "")) for r in range(1, min(ws.max_row+1, mr))), default=0)
        cn = ws.cell(1, c).value or ""
        if cn in money_cols:
            ws.column_dimensions[get_column_letter(c)].width = max(mx+4, MONEY_MIN_W)
        else:
            ws.column_dimensions[get_column_letter(c)].width = min(mx+4, 30)

# ══════════════════════════════════════════════════════════════════════════
#  FORMATTING
# ══════════════════════════════════════════════════════════════════════════

def fmt_detail(ws, nr, nc):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "FF7030"   # orange tab
    ws.freeze_panes = "A2"
    MONEY_COLS = {"Stmt Amount","GL Amount","Variance"}

    for r in range(1, nr + 2):
        ws.row_dimensions[r].height = ROW_HT

    # Header row — orange fill, dark text
    for c in range(1, nc+1):
        cl = ws.cell(1, c)
        cl.fill = HDR; cl.font = _AH; cl.border = NO_BORDER
        cl.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

    # Data rows
    for r in range(2, nr+2):
        st = ws.cell(r, nc).value or ""
        for c in range(1, nc+1):
            cl = ws.cell(r, c); cl.border = NO_BORDER
            cn = ws.cell(1, c).value or ""

            # Row fill by status
            if st == "Matched":
                cl.fill = MATCH
                cl.font = _AM if cn in MONEY_COLS else _A
            elif st == "Amount Variance":
                cl.fill = VAR
                cl.font = _AV if cn in MONEY_COLS else _A
            elif st == "Missing in GL":
                cl.fill = MISS
                cl.font = _AMI if cn in MONEY_COLS else _A
            elif "OCR" in st:
                cl.fill = OCR_F; cl.font = _A
            elif r % 2 == 0:
                cl.fill = STRIPE; cl.font = _A
            else:
                cl.fill = ALT; cl.font = _A

            # Number formats & alignment
            if cn in MONEY_COLS:
                if cl.value is not None: cl.number_format = COMMA_FMT
                cl.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cl.alignment = Alignment(horizontal="center", vertical="center")

            if cn == "Date" and cl.value is not None:
                nd = _norm_date(str(cl.value)) if isinstance(cl.value, str) else cl.value
                if isinstance(nd, datetime):
                    cl.value = nd; cl.number_format = DATE_FMT
                cl.alignment = Alignment(horizontal="center", vertical="center")

    _aw(ws, nc, money_cols=MONEY_COLS)

    # Jump-back button — col K
    jc = ws.cell(1, 11)
    jc.value = "← Summary"
    jc.hyperlink = "#Summary!A1"
    jc.font = _JF
    jc.fill = NEON
    jc.border = NO_BORDER
    jc.alignment = Alignment(horizontal="center", vertical="center")
    if ws.column_dimensions['K'].width < 20:
        ws.column_dimensions['K'].width = 20


def fmt_summary(ws, nr, nc):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "FF7030"
    ws.freeze_panes = "A2"
    MONEY_COLS = {"Stmt Total","GL Total","Net Variance"}
    QTY_COLS   = {"Items","Matched","Amt Variance","Missing in GL"}

    for r in range(1, nr + 2):
        ws.row_dimensions[r].height = ROW_HT

    # Header — dark fill, orange text
    for c in range(1, nc+1):
        cl = ws.cell(1, c)
        cl.fill = SHDRF; cl.font = _AS; cl.border = NO_BORDER
        cl.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

    # Data rows
    for r in range(2, nr+2):
        mi_v = ws.cell(r, 6).value or 0
        va   = ws.cell(r, 5).value or 0
        rf = MISS if mi_v > 0 else (VAR if va > 0 else MATCH)

        for c in range(1, nc+1):
            cl = ws.cell(r, c); cl.border = NO_BORDER
            cl.fill = rf
            cn = ws.cell(1, c).value or ""

            # Font color by status
            if cn in MONEY_COLS:
                cl.font = _AMI if mi_v > 0 else (_AV if va > 0 else _AM)
                if cl.value is not None: cl.number_format = COMMA_FMT
                cl.alignment = Alignment(horizontal="right", vertical="center")
            elif cn in QTY_COLS:
                cl.font = _A
                if cl.value is not None: cl.number_format = COMMA_INT
                cl.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cl.font = _A
                cl.alignment = Alignment(horizontal="center", vertical="center")

    _aw(ws, nc, money_cols=MONEY_COLS)

# ══════════════════════════════════════════════════════════════════════════
#  CORE RECONCILIATION
# ══════════════════════════════════════════════════════════════════════════

def smart_invoice_match(raw_rows, gl, log_fn=None):
    def log(m):
        if log_fn: log_fn(m)

    inv_rows = [r for r in raw_rows if r.get("Type","") not in SKIP_TYPES]
    if not inv_rows:
        return []

    variants = {}
    for r in inv_rows:
        raw = str(r["Invoice"]).strip()
        import re as _re
        candidates = [
            raw,
            raw.lstrip("0") or raw,
            raw.zfill(10) if raw.isdigit() and len(raw) < 10 else None,
            f"INV-{raw}" if raw.isdigit() else None,
            f"INV{raw}" if raw.isdigit() else None,
            _re.sub(r'^INV[-\s]?', '', raw) if raw.upper().startswith('INV') else None,
            (_re.sub(r'^INV[-\s]?', '', raw)).lstrip('0') if raw.upper().startswith('INV') else None,
        ]
        for v in candidates:
            if v and v.strip():
                variants[v] = raw

    gl_hit = gl[gl["Document number"].isin(variants.keys())].copy()

    if gl_hit.empty:
        log("  smart-match: no invoice numbers found in GL")
        return []

    log(f"  smart-match: {len(gl_hit)} GL entries matched from {len(inv_rows)} invoices")

    results = []
    for (vendor, loc_id), grp in gl_hit.groupby(["Vendor name","Location ID"]):
        gl_docs = set(grp["Document number"].tolist())
        sub = [r for r in inv_rows
               if any(v in gl_docs for v in [
                   str(r["Invoice"]).strip(),
                   str(r["Invoice"]).strip().lstrip("0"),
                   str(r["Invoice"]).strip().zfill(10)
                   if str(r["Invoice"]).strip().isdigit()
                   and len(str(r["Invoice"]).strip()) < 10 else None,
                   f"INV-{str(r['Invoice']).strip()}"
                   if str(r["Invoice"]).strip().isdigit() else None,
                   f"INV{str(r['Invoice']).strip()}"
                   if str(r["Invoice"]).strip().isdigit() else None,
               ] if v)]
        if sub:
            # Require at least 2 matching invoices OR >20% of total invoices
            # This prevents short-number false positives from polluting output
            min_match = max(2, int(len(inv_rows) * 0.15))
            if len(sub) < min_match and len(sub) < 2:
                log(f"    ↳ skipping {vendor} / {loc_id}: only {len(sub)} match (likely false positive)")
                continue
            label = f"{loc_id} {vendor.split()[0]}"[:31]
            log(f"    → {vendor} / {loc_id}: {len(sub)} invoices")
            results.append({"label": label, "rows": sub,
                             "vendor": vendor, "loc_id": loc_id})

    return results


def run_reconciliation(gl_path, stmt_paths, log_fn=None, file_overrides=None):
    """
    gl_path   : path to the GL CSV file
    stmt_paths: list of paths to vendor statement files (PDF / XLSX)
    log_fn    : optional callable(str) for progress messages
    Returns   : (bytes, filename, reconciled_set, skipped_list)
    """
    def log(msg):
        if log_fn: log_fn(msg)

    log(f"Loading GL: {os.path.basename(gl_path)}")
    gl = pd.read_csv(gl_path)
    gl["Document number"] = gl["Document number"].astype(str).str.strip()
    gl["Amount"] = pd.to_numeric(gl["Amount"], errors="coerce").fillna(0)
    gl["Vendor name"] = gl["Vendor name"].fillna("")
    gl["Location ID"] = gl["Location ID"].fillna("")
    log(f"  {len(gl):,} GL rows loaded")

    stmt_map = {os.path.basename(p): p for p in stmt_paths}
    stmts = sorted(
        fn for fn in stmt_map
        if fn.endswith(('.pdf','.xlsx'))
        and not fn.startswith('AP_REC')
        and not fn.startswith('~')
    )
    log(f"{len(stmts)} statement file(s) found")

    all_stmt_set = set(stmts)
    sheets = {}; srows = []; reconciled = set()

    if file_overrides is None:
        file_overrides = {}

    def do(sn, raw, gv, gl_l, src):
        inv_rows = [r for r in raw if r["Type"] not in SKIP_TYPES]
        if not inv_rows:
            log(f"    (all payments — skipped)"); reconciled.add(src); return
        # Use source filename as sheet name base (Issue 5 fix)
        base_sn = src.replace('.pdf','').replace('.xlsx','').replace('.PDF','').replace('.XLSX','')[:31]
        sn2 = base_sn; n = 1
        while sn2 in sheets:
            sn2 = f"{base_sn[:28]} {n:02d}"; n += 1
        sn = sn2
        lk = glk(gl, gv, gl_l); recon = []
        for it in inv_rows:
            inv = str(it["Invoice"]).strip(); sa = round(it["Amount"],2)
            mk, ga = mi(inv, lk)
            if mk is not None:
                ga = round(ga,2); v = round(sa-ga,2)
                st = "Matched" if abs(v)<0.015 else "Amount Variance"
                recon.append({"Date":it["Date"],"Invoice #":inv,"Type":it["Type"],
                              "Stmt Amount":sa,"GL Amount":ga,"Variance":v,"Status":st})
            else:
                recon.append({"Date":it["Date"],"Invoice #":inv,"Type":it["Type"],
                              "Stmt Amount":sa,"GL Amount":None,"Variance":None,"Status":"Missing in GL"})
        df = pd.DataFrame(recon); sheets[sn] = df
        m = len(df[df.Status=="Matched"]); v = len(df[df.Status=="Amount Variance"])
        mig = len(df[df.Status=="Missing in GL"])
        st = df["Stmt Amount"].sum()
        gt = df["GL Amount"].sum() if df["GL Amount"].notna().any() else 0
        srows.append({"Statement":sn,"Source File":src,"Items":len(df),
                       "Matched":m,"Amt Variance":v,"Missing in GL":mig,
                       "Stmt Total":round(st,2),"GL Total":round(gt,2),
                       "Net Variance":round(st-gt,2)})
        reconciled.add(src)
        log(f"    {len(df)} items: {m} matched, {v} variance, {mig} missing in GL")

    def process_rows(fn, fp, rows, fallback_label, fallback_vendor, fallback_locs):
        smart = smart_invoice_match(rows, gl, log)
        if smart:
            for sg in smart:
                do(sg["label"], sg["rows"], sg["vendor"], [sg["loc_id"]], fn)
        else:
            log(f"    Smart match found nothing — using filename fallback")
            do(fallback_label, rows, fallback_vendor, fallback_locs, fn)

    for fn in sorted(stmts):
        fp   = stmt_map[fn]
        ov   = file_overrides.get(fn, {})
        l, v = fi(fn)
        log(f"Processing: {fn}")

        if v == "US PAPER":
            txt = _pdf(fp); us = parse_us_paper(txt)
            usm = {
                "MAD DOGS AND ENGLISHMEN":(["MAD-80041"],"MD Us Paper"),
                "OXFORD EXCHANGE LLC":(["OE","OE-96001","OE-96003","OE-96004","OE-96005","OE-96008","OE-96011"],"OE Us Paper"),
                "Predalina LLC":(["PRED","PRED-82000"],"PRED Us Paper"),
                "SH-19":(["SH-93004"],"SH19 Us Paper"),
                "The Library St Pete":(["LIB-96100"],"LIB Us Paper"),
                "The Stovall House":(["SH-93001","SH-93002"],"SH Us Paper"),
            }
            found_sub = False
            for c, ir in us.items():
                if c in usm and ir:
                    l2,sn2 = usm[c]; log(f"  Sub: {c}"); do(sn2,ir,"US PAPER CORP",l2,fn); found_sub=True
            if not found_sub: reconciled.add(fn)
            continue

        if fn.endswith(".xlsx") and "AMAZON" in fn.upper():
            r = parse_amazon_xl(fp)
            gv   = ov.get("gl_vendor") or VM.get(v,"Amazon Capital Services")
            gl_l = ov.get("gl_locs")   or LOC.get(l, [])
            if r: do(f"{l or ''} Amazon".strip(), r, gv, gl_l, fn)
            else: reconciled.add(fn)
            continue

        txt = _pdf(fp)
        parser = PARSERS.get(v) if v else None
        rows = None
        if parser:
            rows = parser(txt)
        if not rows:
            rows = parse_wrights(txt)
        if not rows:
            rows = parse_generic(txt)  # universal extractor — handles any format

        if not rows and not txt.strip():
            log(f"  No text extracted"); reconciled.add(fn); continue
        if not rows:
            log(f"  No invoices found ({len(txt)} chars)"); reconciled.add(fn); continue

        fb_vendor = ov.get("gl_vendor") or (VM.get(v) if v else "") or ""
        fb_locs   = ov.get("gl_locs")   or (LOC.get(l,[]) if l else [])
        fb_label  = f"{l} {v.title()}" if l and v else fn.replace(".pdf","").replace(".xlsx","")[:31]

        process_rows(fn, fp, rows, fb_label, fb_vendor, fb_locs)

    if not srows:
        raise ValueError("No vendor statements were successfully processed. "
                         "Check that your file names follow the required format (e.g. 'OE GFS March.pdf').")

    _today = date.today().strftime("%m%d%y")
    output_filename = f"AP_RECONCILIATION_{_today}.xlsx"

    log(f"Building workbook…")
    sdf = pd.DataFrame(srows)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        sdf.to_excel(w, sheet_name="Summary", index=False)
        for sn in sorted(sheets): sheets[sn].to_excel(w, sheet_name=sn[:31], index=False)
    buf.seek(0)

    wb = load_workbook(buf)
    for sn, df in sheets.items():
        s = sn[:31]
        if s in wb.sheetnames: fmt_detail(wb[s], len(df), len(df.columns))
    ws = wb["Summary"]; fmt_summary(ws, len(sdf), len(sdf.columns))

    # Hyperlinks on summary vendor names
    for r in range(2, len(sdf)+2):
        cl = ws.cell(r, 1); sn = cl.value
        if sn and sn[:31] in wb.sheetnames:
            cl.hyperlink = f"#'{sn[:31]}'!A1"; cl.font = _AL

    out_buf = io.BytesIO()
    wb.save(out_buf)
    out_buf.seek(0)

    tm=sdf["Matched"].sum(); tv=sdf["Amt Variance"].sum(); tmi=sdf["Missing in GL"].sum()
    log(f"Done! {len(sheets)+1} sheets — {tm} matched | {tv} variances | {tmi} missing in GL")

    skipped = sorted(all_stmt_set - reconciled)
    return out_buf.getvalue(), output_filename, reconciled, skipped
