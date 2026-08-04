"""
Accrual Builder engine — turns reviewed vendor accruals into a Sage-ready
JE import CSV, validated line-by-line against the ERP's own reference lists
(extracted from JE_Import_Template_v2: accounts, locations, vendors).
Path: backend/accrual_engine.py
"""
import calendar
import csv
import io
import json
import os
from datetime import date

import pandas as pd

from trends_engine import load_gl

# The JE template defines the OUTPUT FORMAT only. All data validation —
# vendors, accounts, locations — comes from the user's own GL, which is a
# Sage export and therefore the live truth. Self-maintaining by definition.


def _gl_reference(gl_path):
    """Sage-valid values straight from the GL: account set (+titles),
    location set, vendor name -> V-#### id map."""
    df = pd.read_csv(gl_path,
                     usecols=["Account no", "Account title", "Location ID",
                              "Vendor name", "Vendor ID"], low_memory=False)
    acct = df["Account no"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    accounts = set(acct[acct.str.match(r"^\d{5}$", na=False)])
    titles = (pd.DataFrame({"a": acct, "t": df["Account title"]})
                .dropna().drop_duplicates("a").set_index("a")["t"].to_dict())
    locations = set(df["Location ID"].dropna().astype(str).str.strip())
    v = df.dropna(subset=["Vendor name"]).copy()
    v["Vendor name"] = v["Vendor name"].astype(str).str.strip()
    v["Vendor ID"] = v["Vendor ID"].astype(str).str.strip()
    v = v[v["Vendor ID"].str.match(r"^V-\d+", na=False)]
    vendors = v.drop_duplicates("Vendor name").set_index("Vendor name")["Vendor ID"].to_dict()
    return {"accounts": accounts, "titles": titles,
            "locations": locations, "vendors": vendors}



JE_HEADERS = ["DONOTIMPORT", "JOURNAL", "DATE", "REVERSEDATE", "DESCRIPTION",
              "REFERENCE_NO", "LINE_NO", "ACCT_NO", "LOCATION_ID", "DEPT_ID",
              "DOCUMENT", "MEMO", "DEBIT", "CREDIT", "SOURCEENTITY", "CURRENCY",
              "EXCH_RATE_DATE", "EXCH_RATE_TYPE_ID", "EXCHANGE_RATE", "STATE",
              "ALLOCATION_ID", "BILLABLE", "RPESENTRY", "RASSET",
              "RDEPRECIATION_SCHEDULE", "RASSET_ADJUSTMENT", "RASSET_CLASS",
              "RASSETOUTOFSERVICE", "RASSETTRANSFER", "RCIP_ASSET", "RCIP",
              "RASSET_DIMENSIONTRANSFER", "RDEPRECIATION_SUMMARY",
              "RFIXED_ASSETS_LOG", "RDEPRECIATION_SCHEDULE_SUMMARY",
              "GLENTRY_PROJECTID", "GLENTRY_CUSTOMERID", "GLENTRY_VENDORID",
              "GLENTRY_EMPLOYEEID", "GLENTRY_ITEMID", "GLENTRY_CLASSID"]


def account_choices(gl_path):
    """Liability accounts (3xxxx) present in the GL, for the credit side."""
    ref = _gl_reference(gl_path)
    return [{"account": a, "title": str(ref["titles"].get(a, "") or "")[:60]}
            for a in sorted(ref["accounts"]) if a.startswith("3")]


def row_defaults(gl_path, entity, group, label, period):
    """Dominant account + location for one vendor row (entity+group), from the
    trailing window ending at `period` — prefilled, editable, Sage-validated."""
    df = load_gl(gl_path)
    df = df[(df["Entity"] == entity.upper()) & (df["Group"] == group)
            & (df["Vendor name"].astype(str) == str(label))]
    end = pd.Period(period, freq="M")
    df = df[df["Period"].isin(pd.period_range(end - 12, end, freq="M"))]
    ref = _gl_reference(gl_path)
    if df.empty:
        return {"acct_no": "", "location_id": "",
                "vendor_id": ref["vendors"].get(str(label), ""),
                "vendor_valid": str(label) in ref["vendors"]}
    acct = (df.groupby("Account no")["Amount"].apply(lambda s: s.abs().sum())
              .sort_values(ascending=False).index[0])
    loc = (df.groupby("Location ID")["Amount"].apply(lambda s: s.abs().sum())
             .sort_values(ascending=False).index[0])
    return {"acct_no": str(acct), "location_id": str(loc),
            "vendor_id": ref["vendors"].get(str(label), ""),
            "acct_valid": str(acct) in ref["accounts"],
            "location_valid": str(loc) in ref["locations"],
            "vendor_valid": str(label) in ref["vendors"]}


def entity_main_location(gl_path, entity):
    df = load_gl(gl_path)
    df = df[df["Entity"] == entity.upper()]
    if df.empty:
        return ""
    return str(df.groupby("Location ID")["Amount"].apply(lambda s: s.abs().sum())
                 .sort_values(ascending=False).index[0])


def build_je_csv(gl_path, entity, period, credit_acct, lines, credit_location=None):
    """
    lines: [{label, group, amount, acct_no, location_id}]
    Returns (csv_bytes, filename, summary) or raises ValueError with a list of
    human-readable validation problems — NO file is produced unless every line
    passes Sage validation and the entry balances.
    """
    entity = entity.upper()
    y, mo = map(int, period.split("-"))
    month_end = date(y, mo, calendar.monthrange(y, mo)[1])
    rev = date(y + (1 if mo == 12 else 0), 1 if mo == 12 else mo + 1, 1)
    fmt = lambda d: d.strftime("%m/%d/%Y")
    ref_no = f"ACCR-{entity}-{y}{mo:02d}"
    desc = f"AP accrual {month_end.strftime('%B %Y')} - {entity}"

    ref = _gl_reference(gl_path)
    problems = []
    if not lines:
        problems.append("No accrual lines selected.")
    if str(credit_acct) not in ref["accounts"]:
        problems.append(f"Credit account {credit_acct!r} does not appear in your GL.")
    clean = []
    for i, ln in enumerate(lines, 1):
        label = str(ln.get("label") or "").strip()
        acct = str(ln.get("acct_no") or "").strip()
        loc = str(ln.get("location_id") or "").strip()
        try:
            amt = round(float(ln.get("amount") or 0), 2)
        except Exception:
            amt = 0
        where = f"line {i} ({label or 'no vendor'})"
        if amt <= 0:
            problems.append(f"{where}: amount must be a positive number.")
        if acct not in ref["accounts"]:
            problems.append(f"{where}: account {acct!r} does not appear in your GL.")
        if loc not in ref["locations"]:
            problems.append(f"{where}: location {loc!r} does not appear in your GL.")
        if label not in ref["vendors"]:
            problems.append(f"{where}: vendor {label!r} was not found in the GL "
                            f"with a Sage Vendor ID.")
        clean.append({"label": label, "acct": acct, "loc": loc, "amount": amt})
    if problems:
        raise ValueError(problems)

    credit_loc = str(credit_location or "").strip() or entity_main_location(gl_path, entity)
    if credit_loc not in ref["locations"]:
        raise ValueError([f"Credit-line location {credit_loc!r} does not appear in your GL."])

    total = round(sum(l["amount"] for l in clean), 2)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(JE_HEADERS)
    def row(line_no, acct, loc, memo, debit, credit, vendor_id=""):
        r = [""] * len(JE_HEADERS)
        r[1] = "GJ"
        r[2] = fmt(month_end)
        r[3] = fmt(rev)
        r[4] = desc
        r[5] = ref_no
        r[6] = str(line_no)
        r[7] = acct
        r[8] = loc
        r[10] = f"ACCR{y}{mo:02d}"
        r[11] = memo
        r[12] = f"{debit:.2f}" if debit else ""
        r[13] = f"{credit:.2f}" if credit else ""
        r[37] = vendor_id
        return r
    n = 0
    for l in clean:
        n += 1
        w.writerow(row(n, l["acct"], l["loc"], l["label"], l["amount"], 0,
                       ref["vendors"].get(l["label"], "")))
    n += 1
    w.writerow(row(n, str(credit_acct), credit_loc,
                   f"Accrued AP - {month_end.strftime('%B %Y')}", 0, total))

    fname = f"JE_Import_{entity}_{y}_{mo:02d}.csv"
    return buf.getvalue().encode("utf-8"), fname, {
        "lines": len(clean), "total": total, "reference_no": ref_no,
        "date": fmt(month_end), "reverse_date": fmt(rev), "credit_account": str(credit_acct),
        "credit_location": credit_loc}
