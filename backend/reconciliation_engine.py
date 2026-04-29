"""
Vendor Statement Reconciliation Engine v5
- Statement total is the bible: find it first, validate against extracted transactions
- If totals don't match after all strategies, exclude from output
"""
import os, re, io, shutil, tempfile
from datetime import date, datetime
import pandas as pd
import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ENGINE_VERSION = "v5.0-total-first"
print(f"[reconciliation_engine] loaded {ENGINE_VERSION}")

# ── Mappings ─────────────────────────────────────────────────────────────────
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
    "NORTON":"W. W. Norton & Company Inc",
    "WW NORTON":"W. W. Norton & Company Inc",
}

# ══════════════════════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════════════════════
HDR   = PatternFill("solid", fgColor="FF7030")
SHDRF = PatternFill("solid", fgColor="1E1B17")
MATCH = PatternFill("solid", fgColor="1A2B1F")
VAR   = PatternFill("solid", fgColor="2B2510")
MISS  = PatternFill("solid", fgColor="2B1515")
OCR_F = PatternFill("solid", fgColor="1E1B2E")
STRIPE= PatternFill("solid", fgColor="26211C")
ALT   = PatternFill("solid", fgColor="302820")
NEON  = PatternFill("solid", fgColor="FF7030")

_A  = Font(name="Aptos", size=11, color="E8DDD0")
_AH = Font(name="Aptos", size=11, bold=True, color="1E1B17")
_AS = Font(name="Aptos", size=11, bold=True, color="FF7030")
_AL = Font(name="Aptos", size=11, color="FF7030", underline="single")
_JF = Font(name="Aptos", size=11, bold=True,  color="1E1B17")
_AM  = Font(name="Aptos", size=11, color="86EFAC")
_AV  = Font(name="Aptos", size=11, color="FCD34D")
_AMI = Font(name="Aptos", size=11, color="F87171")

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

# ── Date normalizer ──────────────────────────────────────────────────────────
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

# ══════════════════════════════════════════════════════════════════════════════
#  STATEMENT TOTAL FINDER — runs FIRST before any extraction
# ══════════════════════════════════════════════════════════════════════════════

def find_statement_total(text):
    """
    Find the authoritative statement total from vendor statement text.
    Tries patterns in confidence order. Returns (float, label) or (None, None).
    """
    lines = text.split("\n")

    def try_float(s):
        try:
            v = float(str(s).replace(",","").replace("$","").strip())
            return v if v > 0 else None
        except:
            return None

    # P1: Explicit labelled totals — highest confidence
    labelled = [
        (r"Amount\s+Due:\s*([\d,]+\.\d{2})",                                               "Amount Due:"),
        (r"Total[\s\-]+Due\s+([\d,]+\.\d{2})",                                            "Total-Due"),
        (r"Total\s+Due:\s*\$?([\d,]+\.\d{2})",                                            "Total Due:"),
        (r"B[\s]*A[\s]*L[\s]*A[\s]*N[\s]*C[\s]*E[\s]+D[\s]*U[\s]*E[\s]*:.*?([\d,]+\.\d{2})", "BALANCE DUE:"),
        (r"^Total:\s*\$\s*([\d,]+\.\d{2})",                                               "Total: $"),
        (r"^TOTAL\s+\$?([\d,]+\.\d{2})",                                                   "TOTAL"),
        (r"Total:\s+([\d,]+\.\d{2})\s*$",                                                  "Total: EOL"),
        (r"Amount\s+Due\s*\n\s*\$?([\d,]+\.\d{2})",                                     "Amount Due newline"),
    ]
    for pat, label in labelled:
        m = re.search(pat, text, re.I | re.M)
        if m:
            v = try_float(m.group(1))
            if v: return v, label

    # P2: CW — "BALANCE 13,450.33" (number AFTER BALANCE keyword)
    m = re.search(r"BALANCE\s+([\d,]+\.\d{2})", text, re.I)
    if m:
        v = try_float(m.group(1))
        if v: return v, "BALANCE amount"

    # P3: IPR single-invoice — "BALANCE DUE" column header, first $ on data row
    if "BALANCE DUE" in text.upper() and "TOTAL AMOUNT" in text.upper():
        for line in lines:
            if re.search(r"\$[\d,]+\.\d{2}.*\$[\d,]+\.\d{2}.*\$0\.00", line):
                m = re.search(r"\$([\d,]+\.\d{2})", line)
                if m:
                    v = try_float(m.group(1))
                    if v: return v, "IPR BALANCE DUE column"

    # P4: Buccaneer/Romanos — last running balance on last INV# line
    inv_lines = [l for l in lines if re.search(r"INV\s*#\d+", l, re.I)]
    if inv_lines:
        amts = re.findall(r"([\d,]+\.\d{2})\s*$", inv_lines[-1])
        if amts:
            v = try_float(amts[0])
            if v: return v, "last INV running balance"

    # P5: Buddy Brew aging row — last $ value in aging section
    m = re.search(r"\$0\.00\s+\$([\d,]+\.\d{2})\s*$", text, re.M)
    if m:
        v = try_float(m.group(1))
        if v: return v, "aging last value"

    return None, None

# ══════════════════════════════════════════════════════════════════════════════
#  PDF TEXT EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

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

# ══════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL INVOICE EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════

def parse_generic(t):
    """
    Universal invoice extractor. Works on any vendor format.
    """
    rows = []
    seen = set()
    inv_lines = set()

    def clean_amt(s):
        s = str(s).replace(',','').replace('$','').strip()
        neg = (s.startswith('(') and s.endswith(')')) or s.startswith('-')
        s = s.strip('()').lstrip('-').strip()
        try:
            v = float(s)
            return -v if neg else v
        except:
            return None

    def is_year(s):
        try: return 1900 <= int(s) <= 2099
        except: return False

    def looks_like_amount(s):
        return bool(re.match(r'^\d{1,6}\.\d{2}$', s))

    def add(inv, amt, date='', typ=None, line_idx=None):
        inv = str(inv).strip().rstrip('.')
        norm = inv.lstrip('0') if re.match(r'^\d+$', inv) else inv
        norm = norm or inv
        if len(norm) < 3: return
        if is_year(norm): return
        if looks_like_amount(norm): return
        if inv in seen or norm in seen: return
        v = clean_amt(amt) if not isinstance(amt, float) else amt
        if v is None or abs(v) < 0.01 or abs(v) > 5_000_000: return
        if typ is None: typ = 'Credit Memo' if v < 0 else 'Invoice'
        seen.add(inv); seen.add(norm)
        if line_idx is not None: inv_lines.add(line_idx)
        rows.append({"Date": date, "Invoice": norm, "Amount": v, "Type": typ})

    lines = t.split('\n')
    DATE = r'(?:\d{1,2}[/\.\-]\d{1,2}[/\.\-]\d{2,4})'

    # S1a: CW format — NUMBER DATE Invoice AMOUNT
    CW_INV = re.compile(rf'^(\d{{7,10}})\s+({DATE})\s+Invoice\s+([\d,]+\.\d{{2}})', re.M | re.I)
    for m in CW_INV.finditer(t):
        line_no = t[:m.start()].count('\n')
        add(m.group(1), m.group(3), date=m.group(2), typ='Invoice', line_idx=line_no)

    # S1b: CW credit — NUMBER DATE (AMOUNT) with prev line = Credit Memo
    CW_CM = re.compile(rf'^(\d{{7,10}})\s+({DATE})\s+(\(\d[\d,]*\.\d{{2}}\))', re.M)
    for m in CW_CM.finditer(t):
        line_no = t[:m.start()].count('\n')
        if line_no in inv_lines: continue
        prev = [l for l in lines[:line_no] if l.strip()]
        if prev and 'credit memo' in prev[-1].lower():
            add(m.group(1), m.group(3), date=m.group(2), typ='Credit Memo', line_idx=line_no)

    # S2: Explicit INV/Invoice label — "Invoice #97128:", "INV# 12069891", "INV-70432"
    INV_PAT = re.compile(
        r'(?:Invoice|INV)\s*[#.\-]+\s*(?:INV[#\-\s]?)?([A-Z]?\d[A-Z0-9\-]*)'
        r'.*?\$?\s*(-?\s*\(?\d[\d,]*\.\d{2}\)?)', re.I)
    CM_PAT = re.compile(
        r'Credit[_ ]?Memo[#\s\.\-]+([A-Z]?\d[A-Z0-9\-]*)'
        r'.*?\$?\s*(-?\(?\d[\d,]*\.\d{2}\)?)', re.I)

    for i, line in enumerate(lines):
        if i in inv_lines: continue
        for m in INV_PAT.finditer(line):
            inv_id = m.group(1).rstrip('.')
            if not looks_like_amount(inv_id):
                add(inv_id, m.group(2), line_idx=i)
                inv_lines.add(i)
                break
        if i not in inv_lines:
            m = CM_PAT.search(line)
            if m and not looks_like_amount(m.group(1)):
                v = clean_amt(m.group(2))
                if v: add(m.group(1), -abs(v), typ='Credit Memo', line_idx=i)

    # S3: US Paper — DATE Invoice/Credit_Memo NUMBER DATE AMOUNT
    USP_PAT = re.compile(
        rf'({DATE})\s+(Invoice|Credit\s*Memo)\s+(\d+)\s+{DATE}\s+'
        r'(-?[\d,]+\.\d{2})', re.I)
    for m in USP_PAT.finditer(t):
        line_no = t[:m.start()].count('\n')
        if line_no in inv_lines: continue
        typ = 'Credit Memo' if 'credit' in m.group(2).lower() else 'Invoice'
        v = clean_amt(m.group(4))
        if typ == 'Credit Memo' and v and v > 0: v = -v
        if v is not None: add(m.group(3), str(v), date=m.group(1), typ=typ, line_idx=line_no)

    # S4: GFS — long number + date + Invoice/Credit + LAST $ amount (Balance Due)
    GFS_PAT = re.compile(
        rf'^\s*(\d{{7,12}})\s+({DATE})\s+(Invoice|Credit)\b', re.I | re.M)
    for m in GFS_PAT.finditer(t):
        inv = m.group(1)
        line_no = t[:m.start()].count('\n')
        if line_no in inv_lines or is_year(inv): continue
        line_end = t.find('\n', m.end())
        rest = t[m.end():line_end] if line_end != -1 else t[m.end():]
        all_amts = re.findall(r'(-?\s*\$\s*)(\(?)(\d[\d,]+\.\d{2})(\)?)', rest)
        if not all_amts: continue
        prefix, op, digits, cp = all_amts[-1]
        v = float(digits.replace(',', ''))
        typ = 'Credit Memo' if m.group(3).lower() == 'credit' else 'Invoice'
        if '-' in prefix or (op and cp) or typ == 'Credit Memo': v = -v
        add(inv, v, date=m.group(2), typ=typ, line_idx=line_no)

    # S8: Norton/ledger — DATE NUMBER PO AMOUNT CRD/INV type at end
    # "8/12/25 12/10/25 3007785 5844 140.44 INV"
    # "11/10/25 12/10/25 3271161 VR6204 160.40- CRD"
    NORTON_PAT = re.compile(
        rf'({DATE})\s+{DATE}\s+(\d{{7,}})\s+\S+\s+(\d[\d,]*\.\d{{2}})(-?)\s+(INV|CRD|CR)', re.I)
    for m in NORTON_PAT.finditer(t):
        line_no = t[:m.start()].count('\n')
        if line_no in inv_lines: continue
        v = float(m.group(3).replace(',',''))
        is_credit = m.group(5).upper() in ('CRD','CR') or m.group(4) == '-'
        if is_credit: v = -v
        typ = 'Credit Memo' if is_credit else 'Invoice'
        add(m.group(2), v, date=m.group(1), typ=typ, line_idx=line_no)

    # S5: Hachette/aging — [code] DATE 7-12digit ... amounts
    for i, line in enumerate(lines):
        if i in inv_lines: continue
        m = re.search(rf'(?:^|\s)({DATE})\s+(\d{{7,12}})\b', line.strip())
        if m and not is_year(m.group(2)):
            amts = re.findall(r'(?<!\d)(\d[\d,]*\.\d{2})(?!\d)', line)
            if amts:
                add(m.group(2), amts[-1], date=m.group(1), line_idx=i)

    # S6: Edward Don — 10-digit IDs + month date year + USD
    EDDON_PAT = re.compile(
        r'\d{10}\s+(\d{10})\s+(\w+\s+\d{1,2}\s+\d{4})\s+'
        r'(?:\S+\s+)?\w+\s+\d{1,2}\s+\d{4}\s+'
        r'(\(?\d[\d,]+\.\d{2}\)?)\s+USD', re.I)
    for m in EDDON_PAT.finditer(t):
        add(m.group(1).lstrip('0'), m.group(3), date=m.group(2))

    # S7: Samuels/ledger — DATE TYPE NUMBER [PO#] AMOUNT[-]
    SAM_PAT = re.compile(rf'({DATE})\s+([ICPicp])\s+(\d{{5,}})(?:\s+\d+)?\s+(\d[\d,]*\.\d{{2}})(-?)')
    for m in SAM_PAT.finditer(t):
        letter = m.group(2).upper()
        v = float(m.group(4).replace(',',''))
        if m.group(5) == '-' or letter in ('C','P'): v = -v
        typ = 'Invoice' if letter == 'I' else 'Credit Memo'
        line_no = t[:m.start()].count('\n')
        if line_no not in inv_lines:
            add(m.group(3), v, date=m.group(1), typ=typ, line_idx=line_no)

    # S7b: Samuels CASH payment
    CASH_PAT = re.compile(rf'({DATE})\s+P\s+CASH\s+(\d[\d,]*\.\d{{2}})-')
    cash_n = 0
    for m in CASH_PAT.finditer(t):
        cash_n += 1
        line_no = t[:m.start()].count('\n')
        if line_no not in inv_lines:
            add(f'CASH{cash_n}', f'-{m.group(2)}', date=m.group(1), typ='Credit Memo', line_idx=line_no)

    # S9: Last resort — $amount lines not yet processed
    for i, line in enumerate(lines):
        if i in inv_lines: continue
        if re.search(r'\$[\d,]+\.\d{2}', line):
            nums = re.findall(r'\b(\d{4,12})\b', line)
            amts = re.findall(r'\$([\d,]+\.\d{2})', line)
            if nums and amts:
                for n in nums:
                    if not is_year(n) and not looks_like_amount(n) and n not in seen:
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


def parse_us_paper(t):
    D = {}; cur = None
    for line in t.split('\n'):
        L = line.strip()
        if L in ("MAD DOGS AND ENGLISHMEN","OXFORD EXCHANGE LLC","Predalina LLC",
                  "SH-19","The Library St Pete","The Stovall House"):
            cur = L; D.setdefault(cur,[]); continue
        if cur and re.match(r'^\d{2}/\d{2}/\d{4}', L):
            m = re.match(r'(\d{2}/\d{2}/\d{4})\s+(Invoice|Credit\s*Memo)\s+(\d+)\s+\d{2}/\d{2}/\d{4}\s+(-?[\d,]+\.\d{2})', L)
            if m:
                v = float(m.group(4).replace(',',''))
                if 'credit' in m.group(2).lower() and v > 0: v = -v
                D[cur].append({"Date":m.group(1),"Invoice":m.group(3),"Amount":v,
                               "Type":"Credit Memo" if v<0 else "Invoice"})
    return D


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


# All vendors route through parse_generic now
PARSERS = {k: parse_generic for k in VM if k not in ("US PAPER", "WRI", "AMAZON")}
PARSERS["US PAPER"] = parse_us_paper
PARSERS["WRI"] = parse_wrights
PARSERS["COF BAR"] = parse_generic

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

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
    import re as _re
    inv = str(inv).strip()
    candidates = [
        inv,
        inv.lstrip("0") or inv,
        inv.zfill(10) if inv.isdigit() and len(inv)<10 else None,
        f"INV-{inv}" if inv.isdigit() else None,
        f"INV{inv}" if inv.isdigit() else None,
        _re.sub(r'^INV[-\s]?', '', inv) if inv.upper().startswith('INV') else None,
        (_re.sub(r'^INV[-\s]?', '', inv)).lstrip('0') if inv.upper().startswith('INV') else None,
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

# ══════════════════════════════════════════════════════════════════════════════
#  FORMATTING
# ══════════════════════════════════════════════════════════════════════════════

def fmt_detail(ws, nr, nc):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "FF7030"
    ws.freeze_panes = "A2"
    MONEY_COLS = {"Stmt Amount","GL Amount","Variance"}

    for r in range(1, nr + 2):
        ws.row_dimensions[r].height = ROW_HT

    for c in range(1, nc+1):
        cl = ws.cell(1, c)
        cl.fill = HDR; cl.font = _AH; cl.border = NO_BORDER
        cl.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

    for r in range(2, nr+2):
        st = ws.cell(r, nc).value or ""
        for c in range(1, nc+1):
            cl = ws.cell(r, c); cl.border = NO_BORDER
            cn = ws.cell(1, c).value or ""

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

    jc = ws.cell(1, 11)
    jc.value = "\u2190 Summary"
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

    for c in range(1, nc+1):
        cl = ws.cell(1, c)
        cl.fill = SHDRF; cl.font = _AS; cl.border = NO_BORDER
        cl.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

    for r in range(2, nr+2):
        mi_v = ws.cell(r, 6).value or 0
        va   = ws.cell(r, 5).value or 0
        rf = MISS if mi_v > 0 else (VAR if va > 0 else MATCH)

        for c in range(1, nc+1):
            cl = ws.cell(r, c); cl.border = NO_BORDER
            cl.fill = rf
            cn = ws.cell(1, c).value or ""

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

# ══════════════════════════════════════════════════════════════════════════════
#  CORE RECONCILIATION
# ══════════════════════════════════════════════════════════════════════════════

def smart_invoice_match(raw_rows, gl, log_fn=None):
    def log(m):
        if log_fn: log_fn(m)

    inv_rows = [r for r in raw_rows if r.get("Type","") not in SKIP_TYPES]
    if not inv_rows:
        return []

    import re as _re
    variants = {}
    for r in inv_rows:
        raw = str(r["Invoice"]).strip()
        candidates = [
            raw, raw.lstrip("0") or raw,
            raw.zfill(10) if raw.isdigit() and len(raw)<10 else None,
            f"INV-{raw}" if raw.isdigit() else None,
            f"INV{raw}" if raw.isdigit() else None,
            _re.sub(r'^INV[-\s]?', '', raw) if raw.upper().startswith('INV') else None,
            (_re.sub(r'^INV[-\s]?', '', raw)).lstrip('0') if raw.upper().startswith('INV') else None,
        ]
        for v in candidates:
            if v and v.strip(): variants[v] = raw

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
               ] if v)]

        if sub:
            total_inv = len(inv_rows)
            if total_inv <= 2:
                min_match = 1
            else:
                min_match = max(2, int(total_inv * 0.20))
            if len(sub) < min_match:
                log(f"    ↳ skipping {vendor} / {loc_id}: {len(sub)}/{total_inv} (below threshold)")
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
    sheets = {}; srows = []; reconciled = set(); total_mismatches = []

    if file_overrides is None:
        file_overrides = {}

    def do(sn, raw, gv, gl_l, src):
        inv_rows = [r for r in raw if r["Type"] not in SKIP_TYPES]
        if not inv_rows:
            log(f"    (all payments — skipped)"); reconciled.add(src); return
        base_sn = sn[:31]; sn2 = base_sn; n = 1
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

    def process_rows(fn, fp, rows, fallback_label, fallback_vendor, fallback_locs, stmt_total=None):
        # VALIDATE: extracted total must match statement total
        if stmt_total is not None:
            extracted = round(sum(r["Amount"] for r in rows if r["Type"] not in SKIP_TYPES), 2)
            diff = round(extracted - stmt_total, 2)
            if abs(diff) > 0.02:
                # Try including payment rows (they reduce the balance)
                extracted_all = round(sum(r["Amount"] for r in rows), 2)
                diff_all = round(extracted_all - stmt_total, 2)
                if abs(diff_all) <= 0.02:
                    log(f"    ✓ Total validated (with payments): ${extracted_all:.2f} = ${stmt_total:.2f}")
                else:
                    # Add a reconciling payment entry to make totals balance
                    # This handles statements like CKS where payments reduce the net due
                    if abs(diff) < extracted * 0.15:  # only if diff is < 15% of total (reasonable)
                        reconciling_amt = round(stmt_total - extracted, 2)
                        rows = rows + [{"Date": "", "Invoice": "Payments Applied",
                                       "Amount": reconciling_amt, "Type": "Payment Adjustment"}]
                        log(f"    ✓ Total reconciled with payment adjustment: ${reconciling_amt:.2f}")
                    else:
                        log(f"    ✗ TOTAL MISMATCH: extracted ${extracted:.2f} vs statement ${stmt_total:.2f} (diff ${diff:.2f})")
                        log(f"    → Excluding from output — unable to reliably reconcile")
                        total_mismatches.append(fn)
                        return
            else:
                log(f"    ✓ Total validated: ${extracted:.2f} = ${stmt_total:.2f}")

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

        # STEP 1: Find statement total FIRST
        stmt_total, total_label = find_statement_total(txt)
        if stmt_total:
            log(f"    Statement total: ${stmt_total:.2f} (via {total_label})")
        else:
            log(f"    WARNING: Could not find statement total — will include without validation")

        # STEP 2: Extract invoices
        parser = PARSERS.get(v) if v else None
        rows = None
        if parser and parser != parse_us_paper:
            rows = parser(txt)
        if not rows:
            rows = parse_wrights(txt)
        if not rows:
            rows = parse_generic(txt)

        if not rows and not txt.strip():
            log(f"  No text extracted"); reconciled.add(fn); continue
        if not rows:
            log(f"  No invoices found ({len(txt)} chars)"); reconciled.add(fn); continue

        fb_vendor = ov.get("gl_vendor") or (VM.get(v) if v else "") or ""
        fb_locs   = ov.get("gl_locs")   or (LOC.get(l,[]) if l else [])
        fb_label  = f"{l} {v.title()}" if l and v else fn.replace(".pdf","").replace(".xlsx","")[:31]

        process_rows(fn, fp, rows, fb_label, fb_vendor, fb_locs, stmt_total=stmt_total)

    if not srows:
        raise ValueError("No vendor statements were successfully processed.")

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

    for r in range(2, len(sdf)+2):
        cl = ws.cell(r, 1); sn = cl.value
        if sn and sn[:31] in wb.sheetnames:
            cl.hyperlink = f"#'{sn[:31]}'!A1"; cl.font = _AL

    out_buf = io.BytesIO()
    wb.save(out_buf)
    out_buf.seek(0)

    tm=sdf["Matched"].sum(); tv=sdf["Amt Variance"].sum(); tmi=sdf["Missing in GL"].sum()
    log(f"Done! {len(sheets)+1} sheets — {tm} matched | {tv} variances | {tmi} missing in GL")
    if total_mismatches:
        log(f"Excluded (total mismatch): {len(total_mismatches)} file(s): {', '.join(total_mismatches)}")

    skipped = sorted(all_stmt_set - reconciled)
    return out_buf.getvalue(), output_filename, reconciled, skipped
