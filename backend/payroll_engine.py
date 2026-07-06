"""
Payroll Engine — accrual calculator + payroll trends.
Path: backend/payroll_engine.py

PAY CALENDAR (from Caspers pay-period schedules):
  - Pay periods run Monday–Sunday.
  - Biweekly entities: two cohorts offset by one week.
      Cohort 1 anchor period-end: Sunday 2026-06-21 (checks 6/12, 6/26, ...)
      Cohort 2 anchor period-end: Sunday 2026-06-28 (checks 6/5, 6/19, 7/3, ...)
  - Wrights (WRI) is WEEKLY, same Mon–Sun convention.
  - Check date = period end + 5 days (the following Friday).

ACCRUAL LOGIC (mirrors the manual month-end process):
  Expense is recognized on check dates. At month-end E, the days worked but
  not yet expensed run from the day after the last period-end P whose check
  (P + 5 days) landed on or before E, through E:
      unaccrued_days = (E - P).days
  June 2026 check: Cohort 1 -> 9 days, Cohort 2 -> 16 days.  (Validated.)

DAILY RATE:
  Per (entity, category), from actual payroll-journal (PYRJ) postings over the
  trailing RATE_LOOKBACK_DAYS before month-end, divided by the days those pay
  runs covered. Falls back to all category activity (excluding month-end
  accrual/reversal noise) when an entity has no PYRJ rows (e.g. CRP).

Schedule per entity is AUTO-DETECTED from which known check dates its payroll
posts on, with a manual override available from the UI.
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd

from trends_engine import load_gl

ENGINE_VERSION = "payroll-v1.2-pyrj-only"

# ── Payroll account categories (from the Caspers chart of accounts) ────────
# Prefix-based so new sub-accounts are picked up automatically.
CATEGORY_RULES = [
    ("Hourly Labor",    lambda a: a.startswith("701")),
    ("Salaried Labor",  lambda a: a.startswith("702") or a.startswith("703") or a == "70600"),
    ("Payroll Taxes",   lambda a: a.startswith("713")),
    ("Labor COS",       lambda a: a in {"61012", "63003", "63050", "63051", "63052", "63053"}),
    ("Benefits",        lambda a: a in {"77020", "74000", "71000"}),   # 401k match, dental claims, benefit admin
    ("Contract/Temp",   lambda a: a in {"70298", "70299", "71400"}),
]
# Note: monthly-billed premiums (77400 Health Insurance, 77401 Workers Comp)
# are intentionally NOT day-accrued — they are period costs billed monthly,
# not pay-cycle wages. They still appear in the trends view.
TREND_EXTRA = {"77400": "Benefits", "77401": "Benefits", "77417": "Benefits"}

RATE_LOOKBACK_DAYS = 63   # ~4 biweekly / 9 weekly runs
CYCLE_DAYS = {"cohort1": 14, "cohort2": 14, "weekly": 7}

# Anchor period-end Sundays (any Sunday on the 14-day grid works as anchor)
ANCHOR = {"cohort1": date(2026, 6, 21), "cohort2": date(2026, 6, 28)}

# Known 2026 check dates for cohort detection
CHECKS_C1 = {"2026-01-09","2026-01-23","2026-02-06","2026-02-20","2026-03-06",
             "2026-03-20","2026-04-03","2026-04-17","2026-05-01","2026-05-15",
             "2026-05-29","2026-06-12","2026-06-26","2026-07-10","2026-07-24"}
CHECKS_C2 = {"2026-01-02","2026-01-16","2026-01-30","2026-02-13","2026-02-27",
             "2026-03-13","2026-03-27","2026-04-10","2026-04-24","2026-05-08",
             "2026-05-22","2026-06-05","2026-06-19","2026-07-03","2026-07-17"}


def _categorize(acct: str):
    for name, rule in CATEGORY_RULES:
        if rule(acct):
            return name
    return TREND_EXTRA.get(acct)


def _payroll_frame(df):
    """All GL rows in a payroll category, with Category column."""
    d = df.copy()
    d["Category"] = d["Account no"].map(_categorize)
    return d[d["Category"].notna()]


def _last_expensed_period_end(schedule: str, month_end: date) -> date:
    """Latest Sunday period-end P (on the schedule's grid) with check P+5 <= month_end."""
    if schedule == "weekly":
        # latest Sunday with Sunday+5 <= E
        p = month_end - timedelta(days=5)
        p = p - timedelta(days=(p.weekday() - 6) % 7)  # previous (or same) Sunday
        return p
    anchor = ANCHOR["cohort1" if schedule == "cohort1" else "cohort2"]
    # step the 14-day grid to the latest P with P+5 <= month_end
    delta = (month_end - timedelta(days=5) - anchor).days
    steps = delta // 14
    return anchor + timedelta(days=14 * steps)


def unaccrued_days(schedule: str, month_end: date) -> int:
    p = _last_expensed_period_end(schedule, month_end)
    return (month_end - p).days


def detect_schedules(df):
    """Auto-detect each entity's pay schedule from posting dates of payroll rows."""
    pay = _payroll_frame(df)
    pay = pay[pay["Category"].isin(["Hourly Labor", "Salaried Labor"])]
    pay = pay.copy()
    pay["d"] = pay["Posting date"].dt.strftime("%Y-%m-%d")
    out = {}
    for ent, g in pay.groupby("Entity"):
        c1 = g[g["d"].isin(CHECKS_C1)]["Amount"].abs().sum()
        c2 = g[g["d"].isin(CHECKS_C2)]["Amount"].abs().sum()
        recent = g[g["Posting date"] >= g["Posting date"].max() - pd.Timedelta(days=62)]
        fridays = recent[recent["Posting date"].dt.dayofweek == 4]["d"].nunique()
        if c1 > c2 * 3 and c1 > 0:
            out[ent] = {"schedule": "cohort1", "basis": f"pay-date match ${c1:,.0f} on cohort-1 checks"}
        elif c2 > c1 * 3 and c2 > 0:
            out[ent] = {"schedule": "cohort2", "basis": f"pay-date match ${c2:,.0f} on cohort-2 checks"}
        elif fridays >= 7:
            out[ent] = {"schedule": "weekly", "basis": f"{fridays} distinct Friday pay runs in 9 weeks"}
        else:
            out[ent] = {"schedule": "unknown", "basis": "no clear pay-date pattern — pick manually"}
    return out


def _daily_rates(df, entity, month_end: date, schedule: str):
    """
    Per-category daily cost for one entity — computed from PYRJ (payroll
    journal) postings ONLY. PYRJ is the ground truth: it never reverses.
    GJ/IJ adjusting entries, accruals, reversals, and transfers are excluded
    by construction. Entities with no PYRJ activity return no rates (the
    caller surfaces an explicit warning instead of a polluted estimate).
    Returns {category: {rate, basis_total, runs, days_covered, source}}.
    """
    pay = _payroll_frame(df)
    pay = pay[(pay["Entity"] == entity)
              & (pay["Posting date"] <= pd.Timestamp(month_end))
              & (pay["Posting date"] > pd.Timestamp(month_end) - pd.Timedelta(days=RATE_LOOKBACK_DAYS))]
    cycle = CYCLE_DAYS.get(schedule, 14)

    pyrj = pay[pay["Journal"] == "PYRJ"] if "Journal" in pay.columns else pay.iloc[0:0]
    rates = {}
    for cat in [c for c, _ in CATEGORY_RULES]:
        src = pyrj[pyrj["Category"] == cat]
        if src.empty:
            continue
        runs = src["Posting date"].dt.date.nunique()
        total = float(src["Amount"].sum())
        if total <= 0 or runs == 0:
            continue
        days_covered = max(runs, 1) * cycle  # each PYRJ posting date ≈ one pay run
        rates[cat] = {"rate": round(total / days_covered, 2),
                      "basis_total": round(total, 2),
                      "runs": int(runs), "days_covered": int(days_covered),
                      "source": "PYRJ pay runs"}
    return rates


def accrual(gl_path, month_end: str, entity=None, schedule_overrides=None):
    """
    Compute the month-end payroll accrual.
      month_end          : "YYYY-MM-DD" (the last day of the month being closed)
      entity             : entity prefix or None for all entities
      schedule_overrides : {entity: "cohort1"|"cohort2"|"weekly"} manual picks
    """
    df = load_gl(gl_path)
    E = pd.Timestamp(month_end).date()
    overrides = schedule_overrides or {}

    existing = detect_existing_accruals(gl_path, E)
    schedules = detect_schedules(df)
    entities = sorted(schedules.keys())
    targets = [entity.upper()] if entity else entities

    rows = []
    for ent in targets:
        det = schedules.get(ent, {"schedule": "unknown", "basis": "no payroll activity"})
        sched = overrides.get(ent) or det["schedule"]
        if sched == "unknown":
            rows.append({"entity": ent, "schedule": "unknown",
                         "schedule_basis": det["basis"], "days": None,
                         "categories": [], "total": 0.0,
                         "note": "Schedule unknown — select one to calculate",
                         "existing_accruals": existing.get(ent)})
            continue
        days = unaccrued_days(sched, E)
        p_end = _last_expensed_period_end(sched, E)
        rates = _daily_rates(df, ent, E, sched)
        cats = []
        total = 0.0
        for cat, r in rates.items():
            amt = round(r["rate"] * days, 2)
            total += amt
            cats.append({"category": cat, "daily_rate": r["rate"], "days": days,
                         "accrual": amt, "rate_source": r["source"],
                         "rate_basis_total": r["basis_total"], "rate_runs": r["runs"],
                         "rate_days_covered": r["days_covered"]})
        cats.sort(key=lambda c: -c["accrual"])
        no_pyrj_note = (None if cats else
                        "No PYRJ (payroll journal) postings for this entity — rate "
                        "cannot be computed from ground-truth pay runs. Accrue manually "
                        "or check how this entity posts payroll.")
        rows.append({"entity": ent, "schedule": sched,
                     "note": no_pyrj_note,
                     "schedule_basis": det["basis"],
                     "expensed_through": p_end.isoformat(),
                     "days": days, "categories": cats,
                     "total": round(total, 2),
                     "existing_accruals": existing.get(ent)})

    rows.sort(key=lambda r: -(r["total"] or 0))
    grand = round(sum(r["total"] for r in rows), 2)
    return {"engine": ENGINE_VERSION, "month_end": E.isoformat(),
            "reversal_date": (E + timedelta(days=1)).isoformat(),
            "entities": entities, "schedules": schedules,
            "rows": rows, "grand_total": grand}


def trends(gl_path, entity=None, period=None):
    """
    Payroll trends: category x month for trailing 12 months, plus
    YTD avg/month vs last-year-YTD avg/month.
    """
    df = load_gl(gl_path)
    pay = _payroll_frame(df)
    if entity:
        pay = pay[pay["Entity"] == entity.upper()]

    entities = sorted(_payroll_frame(df)["Entity"].unique().tolist())
    all_months = sorted(pay["Period"].unique())
    available_months = [str(m) for m in all_months]
    if not all_months:
        return {"engine": ENGINE_VERSION, "months": [], "available_months": [],
                "entities": entities, "rows": [], "error": "No payroll rows"}

    if period:
        try:
            end = pd.Period(period, freq="M")
        except Exception:
            end = all_months[-1]
        if end not in all_months:
            end = all_months[-1]
    else:
        end = all_months[-1]

    window = [m for m in all_months if m <= end][-12:]
    month_labels = [str(m) for m in window]

    # YTD windows
    ytd_months = [m for m in all_months if m.year == end.year and m <= end]
    ly_ytd = [pd.Period(f"{end.year-1}-{m.month:02d}", freq="M") for m in ytd_months]
    ly_ytd = [m for m in ly_ytd if m in all_months]

    piv = (pay.groupby(["Category", "Period"])["Amount"].sum()
              .unstack("Period").fillna(0.0))

    rows = []
    for cat in [c for c, _ in CATEGORY_RULES] + ["Benefits"]:
        if cat not in piv.index:
            continue
        r = piv.loc[cat]
        vals = [round(float(r.get(m, 0.0)), 2) for m in window]
        ytd_avg = round(float(np.mean([r.get(m, 0.0) for m in ytd_months])), 2) if ytd_months else None
        ly_avg = round(float(np.mean([r.get(m, 0.0) for m in ly_ytd])), 2) if ly_ytd else None
        delta_pct = (round((ytd_avg - ly_avg) / abs(ly_avg) * 100, 1)
                     if ytd_avg is not None and ly_avg not in (None, 0) else None)
        row = {"category": cat, "values": vals,
               "total": round(float(sum(vals)), 2),
               "ytd_avg": ytd_avg, "ly_ytd_avg": ly_avg, "delta_pct": delta_pct}
        if row not in rows:
            rows.append(row)
    # de-dup Benefits if added twice
    seen = set(); uniq = []
    for r in rows:
        if r["category"] in seen: continue
        seen.add(r["category"]); uniq.append(r)
    rows = uniq

    totals = [round(sum(r["values"][i] for r in rows), 2) for i in range(len(window))]
    return {"engine": ENGINE_VERSION, "months": month_labels,
            "available_months": available_months, "period": str(end),
            "entities": entities, "entity": entity.upper() if entity else None,
            "rows": rows, "totals": totals,
            "ytd_months": len(ytd_months), "ly_ytd_months": len(ly_ytd)}


# ── Existing-accrual detection (warn-only; never changes the math) ─────────
# The accrued-payroll liability accounts in the Caspers chart. Credits within
# the analysis month = an accrual being booked; debits = a reversal landing.
LIAB_ACCOUNTS = {
    "35600": "Accrued Wages",
    "35700": "Accrued Taxes",
    "30201": "Accrued 401k Match",
    "30205": "Accrued Workers Comp",
    "30206": "Accrued Health Insurance",
}


def _classify_accrual(desc: str, acct: str, day: int, last_day: int) -> str:
    """Classify a liability posting so payroll-days accruals stand out from
    standing bonus/401k/property-tax accruals that share the same accounts."""
    d = (desc or "").lower()
    if "bonus" in d:
        return "bonus"
    if "401k" in d or acct == "30201":
        return "401k match"
    if any(k in d for k in ("property", "re tax", "tpp", "real estate")):
        return "property tax"
    if acct == "30205":
        return "workers comp"
    if acct == "30206":
        return "health insurance"
    if any(k in d for k in ("payroll", "labor", "wage", "paychex")):
        return "payroll"
    # Blank-description month-end postings to wages/taxes are payroll accruals
    # in practice (e.g. RRT/CRP post these without descriptions).
    if (not d or d == "nan") and day >= last_day - 3 and acct in ("35600", "35700"):
        return "payroll"
    return "other"


def detect_existing_accruals(gl_path, month_end: date):
    """
    Scan the RAW GL (liability accounts are filtered out of the analysis frame)
    for accruals already booked in the analysis month. Returns per-entity:
      {entity: {"payroll": [rows...], "other": [rows...],
                "payroll_total": x, "other_total": y}}
    Row = {account, account_title, date, desc, doc, amount, kind}.
    """
    raw = pd.read_csv(gl_path, low_memory=False)
    raw["Account no"] = raw["Account no"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    raw = raw[raw["Account no"].isin(LIAB_ACCOUNTS)]
    if raw.empty:
        return {}
    raw["Posting date"] = pd.to_datetime(raw["Posting date"], errors="coerce")
    raw = raw[raw["Posting date"].dt.strftime("%Y-%m") == month_end.strftime("%Y-%m")]
    raw = raw[raw["Amount"] < 0]          # credits = accruals being booked
    if raw.empty:
        return {}
    raw["Entity"] = (raw["Location ID"].fillna("").astype(str)
                     .str.split("-").str[0].str.upper())
    out = {}
    for _, r in raw.iterrows():
        acct = r["Account no"]
        desc = str(r.get("Journal entry line description") or "")
        kind = _classify_accrual(desc, acct, int(r["Posting date"].day), month_end.day)
        row = {
            "account": acct,
            "account_title": LIAB_ACCOUNTS[acct],
            "date": r["Posting date"].strftime("%Y-%m-%d"),
            "desc": "" if desc.lower() == "nan" else desc[:80],
            "doc": str(r.get("Document number") or "")[:40],
            "amount": round(float(-r["Amount"]), 2),   # show as positive accrual $
            "kind": kind,
        }
        ent = out.setdefault(r["Entity"], {"payroll": [], "other": [],
                                           "payroll_total": 0.0, "other_total": 0.0})
        bucket = "payroll" if kind == "payroll" else "other"
        ent[bucket].append(row)
        ent[bucket + "_total"] = round(ent[bucket + "_total"] + row["amount"], 2)
    return out


# ── Drill-down: the rows behind any number ──────────────────────────────────
def _rows_payload(frame, cap=300):
    frame = frame.sort_values("Posting date")
    total = round(float(frame["Amount"].sum()), 2)
    rows = []
    for _, r in frame.head(cap).iterrows():
        rows.append({
            "date": r["Posting date"].strftime("%Y-%m-%d"),
            "journal": str(r.get("Journal") or ""),
            "account": str(r.get("Account no") or ""),
            "title": str(r.get("Account title") or "")[:40],
            "desc": str(r.get("Journal entry line description") or "")[:80].replace("nan", ""),
            "doc": str(r.get("Document number") or "")[:40],
            "amount": round(float(r["Amount"]), 2),
        })
    return {"rows": rows, "row_count": int(len(frame)), "total": total,
            "truncated": bool(len(frame) > cap)}


def rate_detail(gl_path, entity, month_end: str, category: str, schedule: str):
    """The exact postings that built (and were excluded from) a daily rate."""
    df = load_gl(gl_path)
    E = pd.Timestamp(month_end).date()
    pay = _payroll_frame(df)
    win = pay[(pay["Entity"] == entity.upper())
              & (pay["Category"] == category)
              & (pay["Posting date"] <= pd.Timestamp(E))
              & (pay["Posting date"] > pd.Timestamp(E) - pd.Timedelta(days=RATE_LOOKBACK_DAYS))]

    # PYRJ ONLY — the payroll journal is the single source of truth for rates.
    included = win[win["Journal"] == "PYRJ"]
    excluded = win[win["Journal"] != "PYRJ"]
    source = "PYRJ pay runs" if not included.empty else "none — no PYRJ postings in window"
    excl_reason = "not a PYRJ pay-run posting (GJ/IJ adjusting entries, accruals, reversals, transfers)"
    return {
        "entity": entity.upper(), "category": category, "month_end": str(E),
        "window_days": RATE_LOOKBACK_DAYS, "source": source,
        "included": _rows_payload(included),
        "excluded": {**_rows_payload(excluded), "reason": excl_reason},
    }


def cell_detail(gl_path, category: str, month: str, entity=None):
    """Every GL line behind one Payroll Trends cell (category x month)."""
    df = load_gl(gl_path)
    pay = _payroll_frame(df)
    if entity:
        pay = pay[pay["Entity"] == entity.upper()]
    frame = pay[(pay["Category"] == category) & (pay["Period"] == pd.Period(month, freq="M"))]
    return {"entity": entity.upper() if entity else None, "category": category,
            "month": month, **_rows_payload(frame, cap=500)}
