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

_REF = json.load(open(os.path.join(os.path.dirname(__file__), "sage_reference.json")))
VALID_ACCOUNTS = set(_REF["accounts"])
VALID_LOCATIONS = set(_REF["locations"])
VALID_VENDORS = _REF["vendors"]            # name -> V-#### id

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
    """Sage-valid liability accounts (3xxxx) for the credit side, with titles
    from the GL where known."""
    titles = {}
    try:
        raw = pd.read_csv(gl_path, usecols=["Account no", "Account title"], low_memory=False)
        raw["Account no"] = raw["Account no"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        titles = raw.drop_duplicates("Account no").set_index("Account no")["Account title"].to_dict()
    except Exception:
        pass
    out = []
    for a in sorted(VALID_ACCOUNTS):
        if a.startswith("3"):
            out.append({"account": a, "title": str(titles.get(a, "") or "")[:60]})
    return out


def row_defaults(gl_path, entity, group, label, period):
    """Dominant account + location for one vendor row (entity+group), from the
    trailing window ending at `period` — prefilled, editable, Sage-validated."""
    df = load_gl(gl_path)
    df = df[(df["Entity"] == entity.upper()) & (df["Group"] == group)
            & (df["Vendor name"].astype(str) == str(label))]
    end = pd.Period(period, freq="M")
    df = df[df["Period"].isin(pd.period_range(end - 12, end, freq="M"))]
    if df.empty:
        return {"acct_no": "", "location_id": "", "vendor_id": VALID_VENDORS.get(str(label), ""),
                "vendor_valid": str(label) in VALID_VENDORS}
    acct = (df.groupby("Account no")["Amount"].apply(lambda s: s.abs().sum())
              .sort_values(ascending=False).index[0])
    loc = (df.groupby("Location ID")["Amount"].apply(lambda s: s.abs().sum())
             .sort_values(ascending=False).index[0])
    return {"acct_no": str(acct), "location_id": str(loc),
            "vendor_id": VALID_VENDORS.get(str(label), ""),
            "acct_valid": str(acct) in VALID_ACCOUNTS,
            "location_valid": str(loc) in VALID_LOCATIONS,
            "vendor_valid": str(label) in VALID_VENDORS}


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

    problems = []
    if not lines:
        problems.append("No accrual lines selected.")
    if str(credit_acct) not in VALID_ACCOUNTS:
        problems.append(f"Credit account {credit_acct!r} is not in the Sage chart of accounts.")
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
        if acct not in VALID_ACCOUNTS:
            problems.append(f"{where}: account {acct!r} is not a valid Sage account.")
        if loc not in VALID_LOCATIONS:
            problems.append(f"{where}: location {loc!r} is not a valid Sage location.")
        if label not in VALID_VENDORS:
            problems.append(f"{where}: vendor {label!r} is not an active Sage vendor "
                            f"(memo must match the vendor list exactly).")
        clean.append({"label": label, "acct": acct, "loc": loc, "amount": amt})
    if problems:
        raise ValueError(problems)

    credit_loc = str(credit_location or "").strip() or entity_main_location(gl_path, entity)
    if credit_loc not in VALID_LOCATIONS:
        raise ValueError([f"Credit-line location {credit_loc!r} is not a valid Sage location."])

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
                       VALID_VENDORS.get(l["label"], "")))
    n += 1
    w.writerow(row(n, str(credit_acct), credit_loc,
                   f"Accrued AP - {month_end.strftime('%B %Y')}", 0, total))

    fname = f"JE_Import_{entity}_{y}_{mo:02d}.csv"
    return buf.getvalue().encode("utf-8"), fname, {
        "lines": len(clean), "total": total, "reference_no": ref_no,
        "date": fmt(month_end), "reverse_date": fmt(rev), "credit_account": str(credit_acct),
        "credit_location": credit_loc}
