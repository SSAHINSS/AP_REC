"""
File Rename Engine
Reuses parsers from reconciliation_engine to extract vendor, entity, date
and propose consistent filenames: EntityName_VendorName_DDMMYY
"""
import os, re, io, zipfile
from datetime import datetime
from pathlib import Path
import pdfplumber

# ── Entity display names (DBA, no legal suffix) ───────────────────────────
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

# ── Vendor display names (DBA, stripped of legal suffixes) ─────────────────
VENDOR_NAMES = {
    "BUCCANEER":       "Buccaneer Linen",
    "CKS BAR":         "CKS Produce",
    "CKS":             "CKS Produce",
    "ED DON":          "Edward Don",
    "ROMANOS COF BAR": "Romanos Bakery",
    "ROMANOS":         "Romanos Bakery",
    "CINTAS":          "Cintas",
    "CW":              "Chefs Warehouse",
    "DEX IMAGING":     "Dex Imaging",
    "GOURMET FOODS":   "Gourmet Foods",
    "HALPERNS":        "Halperns Steak",
    "PIPER FIRE":      "Piper Fire",
    "PROPANE NINJA":   "Propane Ninja",
    "MR GREENS":       "Mr Greens Produce",
    "BUSH BROS":       "Bush Brothers",
    "US PAPER":        "US Paper",
    "AMAZON":          "Amazon",
    "FRANK GAY":       "Frank Gay",
    "PENGUIN":         "Penguin Books",
    "GFS":             "Gordon Food Service",
    "COF BAR":         "Gordon Food Service",
    "ZWIESEL FORTESSA":"Fortessa",
    "FORTESSA":        "Fortessa",
    "UNIFIRST":        "Unifirst",
    "CULIGAN":         "Culligan Water",
    "CULLIGAN":        "Culligan Water",
    "SAMUELS":         "Samuels Seafood",
    "WRI":             "Wrights Gourmet",
    "COZZINI":         "Cozzini Bros",
}

LOC_KEYS = ["SH19","SH","LIB","MD","OE","PRED","OCMGT","JTS"]
VENDOR_KEYS = sorted(VENDOR_NAMES.keys(), key=len, reverse=True)

def _strip_legal(name):
    """Remove common legal suffixes from vendor/entity names."""
    suffixes = [
        r',?\s+LLC\.?$', r',?\s+Inc\.?$', r',?\s+Corp\.?$',
        r',?\s+Co\.?$',  r',?\s+Ltd\.?$', r',?\s+L\.L\.C\.?$',
    ]
    for s in suffixes:
        name = re.sub(s, '', name, flags=re.IGNORECASE).strip()
    return name

def _pdf_text(fp):
    try:
        pdf = pdfplumber.open(fp)
        t = "\n".join(p.extract_text() or "" for p in pdf.pages)
        pdf.close()
        return t
    except Exception:
        return ""

def _parse_date(t):
    """Find the earliest date in the text."""
    dates = []
    patterns = [
        r'\b(\d{2}/\d{2}/\d{4})\b',
        r'\b(\d{1,2}/\d{1,2}/\d{2})\b',
        r'\b(\d{4}-\d{2}-\d{2})\b',
        r'\b(\w+ \d{1,2},?\s+\d{4})\b',
    ]
    fmts = ["%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%B %d %Y", "%B %d, %Y", "%b %d %Y", "%b %d, %Y"]
    for pat in patterns:
        for m in re.findall(pat, t):
            for fmt in fmts:
                try:
                    d = datetime.strptime(m.strip(), fmt)
                    dates.append(d)
                    break
                except ValueError:
                    continue
    if dates:
        dates.sort()
        return dates[0]
    return None

def _fi(fn):
    """Parse location + vendor key from filename."""
    n = fn.replace(".pdf","").replace(".xlsx","").upper()
    loc = None
    for p in LOC_KEYS:
        if n.startswith(p + " ") or n.startswith(p + "_"):
            loc = p; break
    rem = n[len(loc):].strip() if loc else n
    vk = None
    for k in VENDOR_KEYS:
        if rem.startswith(k):
            vk = k; break
    return loc, vk

# US Paper multi-entity sub-section headers
US_PAPER_ENTITIES = {
    "MAD DOGS AND ENGLISHMEN": "MD",
    "OXFORD EXCHANGE LLC":      "OE",
    "Predalina LLC":            "PRED",
    "SH-19":                   "SH19",
    "The Library St Pete":      "LIB",
    "The Stovall House":        "SH",
}

def _us_paper_splits(t, date_str):
    """Return list of proposed names for US Paper multi-entity file."""
    results = []
    for header, loc_key in US_PAPER_ENTITIES.items():
        if header.upper() in t.upper():
            entity = ENTITY_NAMES.get(loc_key, loc_key)
            results.append({
                "entity":  entity,
                "vendor":  "US Paper",
                "date":    date_str,
                "note":    f"Split from multi-entity file ({header})",
                "multi":   True,
            })
    return results

def propose_renames(file_paths, log_fn=None):
    """
    For each file, extract entity/vendor/date and propose a new name.
    Returns list of dicts:
      { original, entity, vendor, date, proposed, note, multi }
    """
    def log(m):
        if log_fn: log_fn(m)

    results = []

    for fp in file_paths:
        fn  = os.path.basename(fp)
        ext = Path(fp).suffix.lower()
        log(f"Reading: {fn}")

        text = _pdf_text(fp) if ext == ".pdf" else ""

        # Parse date
        dt = _parse_date(text)
        date_str = dt.strftime("%d%m%y") if dt else "UNKNOWN"

        # Get loc/vendor from filename
        loc, vk = _fi(fn)

        # US Paper — split into multiple entities
        if vk == "US PAPER":
            splits = _us_paper_splits(text, date_str)
            if splits:
                for s in splits:
                    s["original"] = fn
                    s["proposed"] = f"{s['entity']}_{s['vendor']}_{s['date']}{ext}".replace(" ","_")
                    results.append(s)
                log(f"  → {len(splits)} entities found (multi-entity file)")
                continue

        entity = ENTITY_NAMES.get(loc, loc or "Unknown")
        vendor = VENDOR_NAMES.get(vk, "")

        # Fallback: try to detect vendor from text
        if not vendor:
            for vk2, vname in VENDOR_NAMES.items():
                if vk2.lower() in text.lower()[:500]:
                    vendor = vname; break

        if not vendor:
            vendor = fn.replace(ext,"")[:20]

        proposed = f"{entity}_{vendor}_{date_str}{ext}".replace(" ","_")

        results.append({
            "original": fn,
            "entity":   entity,
            "vendor":   vendor,
            "date":     date_str,
            "proposed": proposed,
            "note":     "",
            "multi":    False,
        })
        log(f"  → {proposed}")

    return results


def build_zip(file_paths, rename_map):
    """
    rename_map: { original_filename: new_filename }
    Returns zip bytes.
    """
    buf = io.BytesIO()
    path_map = {os.path.basename(p): p for p in file_paths}
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for orig, new_name in rename_map.items():
            fp = path_map.get(orig)
            if fp and os.path.exists(fp):
                zf.write(fp, new_name)
    buf.seek(0)
    return buf.getvalue()
