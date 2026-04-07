"""
File Rename Engine v3
- Ignores filenames entirely
- Extracts vendor, entity, date 100% from PDF content
- Handles both text PDFs (pdfplumber) and scanned image PDFs (PyMuPDF + OCR)
- Zero failed renames
"""
import os, re, io, zipfile
from datetime import datetime
from pathlib import Path

# ── Entity display names ───────────────────────────────────────────────────
ENTITY_NAMES = {
    "SH19":  "Stovall 19",
    "SH":    "Stovall House",
    "LIB":   "The Library",
    "MD":    "Mad Dogs",
    "OE":    "Oxford Exchange",
    "PRED":  "Predalina",
    "OCMGT": "OC Management",
    "JTS":   "JTS",
}

# ── Entity detection patterns (order matters — most specific first) ─────────
ENTITY_PATTERNS = [
    (r'SH[\s\-]?19|STOVALL\s+19|6914\s+INTERBAY',              "SH19"),
    (r'THE\s+STOVALL\s+HOUSE|4621\s+BAYSHORE',                  "SH"),
    (r'STOVALL\s+HOUSE',                                         "SH"),
    (r'THE\s+LIBRARY|LIBRARY\s+ST\.?\s*PETE',                   "LIB"),
    (r'MAD\s+DOGS?\s+(AND\s+ENGLISHMEN)?|MAD-80041',            "MD"),
    (r'OXFORD\s+EXCHANGE|420\s+WEST\s+KENNEDY',                 "OE"),
    (r'PREDALINA|1001\s+E[\.\s]+CUMBERLAND',                    "PRED"),
    (r'OC\s+MANAGEMENT|OCMGT',                                   "OCMGT"),
]

# ── Vendor detection patterns ──────────────────────────────────────────────
VENDOR_PATTERNS = [
    (r"WRIGHT'?S\s+GOURMET",                    "Wrights Gourmet"),
    (r"BUCCANEER\s+LINEN",                      "Buccaneer Linen"),
    (r"C[\-\s]K\s+PRODUCE|CK'?S\s+PRODUCE",    "CKS Produce"),
    (r"EDWARD\s+DON",                           "Edward Don"),
    (r"CHEFS?\s+WAREHOUSE",                     "Chefs Warehouse"),
    (r"GORDON\s+FOOD\s+SERVICE",                "Gordon Food Service"),
    (r"HALPERN'?S\s+STEAK|HALPERN'?S",         "Halperns Steak"),
    (r"BUSH\s+BROTHERS?\s+PROVISION",           "Bush Brothers"),
    (r"CINTAS\s+CORP",                          "Cintas"),
    (r"UNIFIRST\s+CORP",                        "Unifirst"),
    (r"CULLIGAN\s+WATER|CULLIGAN",              "Culligan Water"),
    (r"SAMUELS?\s+AND\s+SON|SAMUELS?\s+SEAFOOD","Samuels Seafood"),
    (r"ROMANOS?\s+BAKERY",                      "Romanos Bakery"),
    (r"GOURMET\s+FOODS?\s+INT",                 "Gourmet Foods"),
    (r"FRANK\s+GAY\s+SERVICES",                 "Frank Gay"),
    (r"FORTESSA|ZWIESEL",                       "Fortessa"),
    (r"COZZINI\s+BROS",                         "Cozzini Bros"),
    (r"DEX\s+IMAGING",                          "Dex Imaging"),
    (r"PROPANE\s+NINJA",                        "Propane Ninja"),
    (r"US\s+PAPER\s+CORP",                      "US Paper"),
    (r"AMAZON\s+CAPITAL",                       "Amazon"),
    (r"PENGUIN\s+RANDOM\s+HOUSE",               "Penguin Books"),
    (r"PIPER\s+FIRE",                           "Piper Fire"),
    (r"MR\.?\s*GREEN'?S\s+PRODUCE",            "Mr Greens Produce"),
    (r"GOURMET\s+FOODS?\s+INT",                 "Gourmet Foods"),
]

# ── PDF text extraction — tries everything ─────────────────────────────────
def _extract_text(fp):
    """
    1. pdfplumber  (best for native text PDFs)
    2. PyMuPDF native text  (fallback for complex text PDFs)
    3. PyMuPDF render + pytesseract OCR  (for scanned image PDFs)
    """
    # Method 1: pdfplumber
    try:
        import pdfplumber
        pdf = pdfplumber.open(fp)
        t = "\n".join(p.extract_text() or "" for p in pdf.pages)
        pdf.close()
        if len(t.strip()) > 50:
            return t
    except Exception:
        pass

    # Method 2: PyMuPDF native text
    try:
        import fitz
        doc = fitz.open(fp)
        t = "\n".join(page.get_text() for page in doc)
        doc.close()
        if len(t.strip()) > 50:
            return t
    except Exception:
        pass

    # Method 3: OCR — render each page and run tesseract
    try:
        import fitz
        import pytesseract
        from PIL import Image
        doc = fitz.open(fp)
        pages_text = []
        for page in doc:
            mat = fitz.Matrix(2.5, 2.5)  # ~180dpi for good OCR accuracy
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pages_text.append(pytesseract.image_to_string(img, config='--psm 6'))
        doc.close()
        t = "\n".join(pages_text)
        if t.strip():
            return t
    except Exception as e:
        pass

    return ""

# ── Date extraction ────────────────────────────────────────────────────────
def _extract_date(text):
    """
    Priority 1: explicit STATEMENT DATE label
    Priority 2: date labeled near 'Statement', 'Date', or top of document
    Priority 3: latest date in document (statement date > old transactions)
    """
    fmts = ["%m/%d/%Y", "%m/%d/%y", "%m/%d/%Y", "%m/%d/%y",
            "%Y-%m-%d", "%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]

    def try_parse(s):
        s = re.sub(r'\s+', ' ', s.strip())
        for fmt in fmts:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None

    # Priority 1: "STATEMENT DATE 04/02/26" or "Statement Date: 03/30/2026"
    m = re.search(r'STATEMENT\s+DATE[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})', text, re.IGNORECASE)
    if m:
        d = try_parse(m.group(1))
        if d: return d

    # Priority 2: date near top of document (first 600 chars)
    header = text[:600]
    for pat in [r'(\d{1,2}/\d{1,2}/\d{4})', r'(\d{1,2}/\d{1,2}/\d{2})']:
        for m in re.finditer(pat, header):
            d = try_parse(m.group(1))
            if d and d.year >= 2020: return d

    # Priority 3: latest date in full document
    dates = []
    for pat in [r'\b(\d{1,2}/\d{1,2}/\d{4})\b', r'\b(\d{1,2}/\d{1,2}/\d{2})\b']:
        for match in re.findall(pat, text):
            d = try_parse(match)
            if d and d.year >= 2020:
                dates.append(d)
    if dates:
        return max(dates)

    return None

# ── Vendor extraction ──────────────────────────────────────────────────────
def _extract_vendor(text):
    upper = text[:800].upper()
    for pattern, name in VENDOR_PATTERNS:
        if re.search(pattern, upper, re.IGNORECASE):
            return name
    # Wider search if not found in header
    upper_full = text.upper()
    for pattern, name in VENDOR_PATTERNS:
        if re.search(pattern, upper_full, re.IGNORECASE):
            return name
    return "Unknown Vendor"

# ── Entity extraction ──────────────────────────────────────────────────────
def _extract_entity(text):
    upper = text.upper()
    for pattern, key in ENTITY_PATTERNS:
        if re.search(pattern, upper):
            return ENTITY_NAMES.get(key, key)
    # Check for known entity names directly
    direct = {
        "CASPER'S COMPANY": "Caspers Company",
        "CASPERS COMPANY":  "Caspers Company",
    }
    for k, v in direct.items():
        if k in upper:
            return v
    return "Unknown Entity"

# ── US Paper multi-entity split ────────────────────────────────────────────
US_PAPER_SECTIONS = [
    ("MAD DOGS AND ENGLISHMEN", "Mad Dogs"),
    ("OXFORD EXCHANGE",          "Oxford Exchange"),
    ("PREDALINA",                "Predalina"),
    ("SH-19",                    "Stovall 19"),
    ("THE LIBRARY",              "The Library"),
    ("THE STOVALL HOUSE",        "Stovall House"),
]

def _us_paper_splits(text, date_str, ext):
    results = []
    for header, entity in US_PAPER_SECTIONS:
        if header.upper() in text.upper():
            results.append({
                "entity":   entity,
                "vendor":   "US Paper",
                "date":     date_str,
                "note":     f"Split from multi-entity file ({header})",
                "multi":    True,
                "proposed": f"{entity}_US_Paper_{date_str}{ext}".replace(" ","_"),
            })
    return results

# ── Build zip ──────────────────────────────────────────────────────────────
def build_zip(file_paths, rename_map):
    buf = io.BytesIO()
    path_map = {os.path.basename(p): p for p in file_paths}
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for orig, new_name in rename_map.items():
            fp = path_map.get(orig)
            if fp and os.path.exists(fp):
                zf.write(fp, new_name)
    buf.seek(0)
    return buf.getvalue()

# ── Main ───────────────────────────────────────────────────────────────────
def propose_renames(file_paths, log_fn=None):
    def log(m):
        if log_fn: log_fn(m)

    results = []

    for fp in file_paths:
        fn  = os.path.basename(fp)
        ext = Path(fp).suffix.lower()
        log(f"Processing: {fn}")

        # Extract ALL info from content — filename ignored
        text = _extract_text(fp)

        if not text.strip():
            log(f"  ⚠ Could not extract text — OCR failed")
            results.append({
                "original": fn, "entity": "Unknown Entity",
                "vendor": "Unknown Vendor", "date": "UNKNOWN",
                "proposed": f"UNKNOWN_{fn}", "note": "Text extraction failed", "multi": False,
            })
            continue

        # Date
        dt       = _extract_date(text)
        date_str = dt.strftime("%m%d%y") if dt else "UNKNOWN"

        # US Paper special case
        vendor = _extract_vendor(text)
        if "US PAPER" in vendor.upper():
            splits = _us_paper_splits(text, date_str, ext)
            if splits:
                for s in splits:
                    s["original"] = fn
                    results.append(s)
                log(f"  → {len(splits)} entities (multi-entity US Paper)")
                continue

        entity = _extract_entity(text)

        proposed = f"{entity}_{vendor}_{date_str}{ext}".replace(" ","_")
        log(f"  → {proposed}")

        results.append({
            "original": fn, "entity": entity,
            "vendor": vendor, "date": date_str,
            "proposed": proposed, "note": "", "multi": False,
        })

    return results
