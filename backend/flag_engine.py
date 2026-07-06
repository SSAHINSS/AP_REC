"""
Reconciliation Flag Engine — Tiers 1–2.

Operates on the Sage Intacct GL export alone (GL = source of truth). Buckets
every line into the calendar month of its Posting date, then flags anomalies
across the trailing 12 periods (inclusive of the analysis month).

GL parsing (column contract, entity derivation, group mapping, balance-sheet /
income exclusions) is REUSED from trends_engine.load_gl so the two features can
never drift apart.

Grain of analysis: (Vendor name, Entity, Group) per Period.
  - Entity = prefix of Location ID before the dash (LIB-96100 -> LIB)
  - Rows with no vendor collapse into "(blank)" and are excluded from the
    vendor-behaviour flags (they are journal entries / accruals, not bills).

Flags (v1):
  1. Vanished Vendor    — present >= 9 of the prior 11 months, current = $0.
  2. Trailing Off / Dip — current below (mean - 2*sigma) of its own history.
  3. Spike              — current above (mean + 2*sigma) of trailing-12 history.
  4. Duplicate          — SAME invoice number, SAME entity, whose entire GL
                          line-set appears 2+ complete times (bill keyed twice).
                          A legitimate recurring charge always carries a
                          DIFFERENT invoice number each period, so identical
                          amounts under different invoice numbers are NOT dupes.

Every flag "shows its work": history mean, sigma, months present, current,
last doc #, plain-English explain, and the 12-month series for sparklines.
Severity = consistency * dollar-deviation, sorted worst-first.
"""
from collections import Counter

import numpy as np
import pandas as pd

from trends_engine import load_gl, SALES_GROUPS

ENGINE_VERSION = "flags-v1.1"

# ── Tunables ───────────────────────────────────────────────────────────────
MIN_MONTHS_VANISHED = 9       # present >= N of prior 11 to count as "recurring"
MIN_MONTHS_STATS    = 4       # need >= N months of history for spike/dip/trailing
SIGMA               = 2.0     # standard-deviation band
MATERIALITY         = 100.0   # ignore deviations smaller than this ($)
SD_FLOOR_PCT        = 0.15    # sigma floor as % of mean (avoids hair-triggers)
SD_FLOOR_ABS        = 25.0    # absolute sigma floor ($)


def _stats(prior_vals):
    """mean, sigma (sample), floored sigma, count of present (non-zero) months."""
    present = prior_vals[prior_vals != 0]
    n = len(present)
    if n == 0:
        return 0.0, 0.0, 0.0, 0
    mean = float(present.mean())
    sd = float(present.std(ddof=1)) if n > 1 else 0.0
    sd_floor = max(sd, abs(mean) * SD_FLOOR_PCT, SD_FLOOR_ABS)
    return mean, sd, sd_floor, n


def _severity(consistency, deviation):
    return round(float(consistency) * float(abs(deviation)), 2)


def analyze_flags(gl_path, entity=None, period=None):
    """
    entity : entity prefix (e.g. "LIB") or None for whole org
    period : "YYYY-MM" analysis month; trailing 12 END here. Defaults to latest.
    Returns a JSON-ready dict.
    """
    df = load_gl(gl_path)

    entities = sorted(df["Entity"].unique().tolist())
    all_months = sorted(df["Period"].unique())
    available_months = [str(m) for m in all_months]
    if not all_months:
        return {"engine": ENGINE_VERSION, "months": [], "available_months": [],
                "period": None, "entities": entities, "entity": entity,
                "counts": {}, "total_flags": 0, "flags": [], "error": "No dated rows in GL"}

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
    prior = window[:-1]
    cur = window[-1]
    month_labels = [str(m) for m in window]

    if entity:
        df = df[df["Entity"] == entity.upper()]
    df = df[df["Period"].isin(window)]

    df_exp = df[~df["Group"].isin(SALES_GROUPS)]

    flags = []

    vend = df_exp[df_exp["Vendor name"] != "(blank)"]
    if not vend.empty:
        piv = (vend.groupby(["Vendor name", "Entity", "Group", "Period"])["Amount"]
                   .sum().unstack("Period").reindex(columns=window).fillna(0.0))

        cur_rows = vend[vend["Period"] == cur]
        last_doc = (cur_rows.sort_values("Posting date")
                    .groupby(["Vendor name", "Entity", "Group"])["Document number"]
                    .last().to_dict())

        for (vn, ent, grp), row in piv.iterrows():
            vals = row.values.astype(float)
            prior_vals = row[prior].values.astype(float)
            current = float(row[cur])
            mean, sd, sd_floor, n_present = _stats(prior_vals)
            consistency = n_present / len(prior) if len(prior) else 0.0
            doc = last_doc.get((vn, ent, grp), "")

            base = {
                "vendor": vn, "entity": ent, "group": grp,
                "months_present": int(n_present), "months_history": int(len(prior)),
                "history_mean": round(mean, 2), "history_sd": round(sd, 2),
                "current": round(current, 2), "last_doc": doc,
                "series": [round(float(v), 2) for v in vals],
            }

            if n_present >= MIN_MONTHS_VANISHED and abs(current) < 0.01:
                dev = abs(mean)
                flags.append({**base, "type": "Vanished Vendor",
                              "deviation": round(dev, 2),
                              "severity": _severity(consistency, dev),
                              "explain": f"Present {n_present}/{len(prior)} prior months "
                                         f"(avg ${mean:,.0f}), $0 this month."})
                continue

            if n_present >= MIN_MONTHS_STATS and current != 0:
                hi = mean + SIGMA * sd_floor
                lo = mean - SIGMA * sd_floor
                if current > hi and (current - mean) > MATERIALITY:
                    dev = current - mean
                    flags.append({**base, "type": "Spike",
                                  "deviation": round(dev, 2),
                                  "severity": _severity(consistency, dev),
                                  "explain": f"${current:,.0f} vs avg ${mean:,.0f} "
                                             f"(+{(current-mean)/(sd_floor or 1):.1f}\u03c3)."})
                elif current < lo and (mean - current) > MATERIALITY:
                    dev = mean - current
                    label = "Trailing Off" if current < mean - SIGMA * sd_floor else "Dip"
                    flags.append({**base, "type": label,
                                  "deviation": round(dev, 2),
                                  "severity": _severity(consistency, dev),
                                  "explain": f"${current:,.0f} vs avg ${mean:,.0f} "
                                             f"(-{(mean-current)/(sd_floor or 1):.1f}\u03c3)."})

    # ── Flag 4 — duplicate invoice (same vendor / entity / invoice#, re-entered) ──
    # Invoice number is the bill's identity. Same invoice#, same entity, whose
    # entire line-set appears 2+ complete times = the bill was keyed in again.
    # Does NOT flag: an invoice split across accounts (lines distinct), a
    # multi-meter utility bill with repeated line amounts (whole set not doubled),
    # or the same shared invoice spread across entities (grain is per-entity).
    dup_src = df_exp[(df_exp["Vendor name"] != "(blank)")
                     & (df_exp["Document number"] != "")
                     & (df_exp["Period"] == cur)].copy()
    if not dup_src.empty:
        for (vn, ent, doc), g in dup_src.groupby(["Vendor name", "Entity", "Document number"]):
            if len(g) < 2:
                continue
            sig = Counter((r[0], round(r[1], 2))
                          for r in g[["Account no", "Amount"]].itertuples(index=False))
            counts = list(sig.values())
            if not (min(counts) >= 2 and all(c % 2 == 0 for c in counts)):
                continue
            repeat_factor = min(counts)
            one_copy = sum(amt for (_a, amt) in sig.keys())
            overbill = one_copy * (repeat_factor - 1)
            dates = sorted(g["Posting date"].dt.strftime("%Y-%m-%d").unique().tolist())
            flags.append({
                "type": "Duplicate", "vendor": vn, "entity": ent,
                "group": g["Group"].iloc[0],
                "current": round(float(one_copy), 2),
                "count": int(repeat_factor),
                "dates": dates, "docs": [doc],
                "deviation": round(abs(float(overbill)), 2),
                "severity": _severity(1.0, abs(float(overbill))),
                "months_present": None, "months_history": None,
                "history_mean": None, "history_sd": None, "last_doc": doc,
                "series": None,
                "explain": f"Invoice {doc} appears {repeat_factor}x at {ent} "
                           f"(${one_copy:,.2f} each; ${abs(overbill):,.2f} over-stated).",
            })

    flags.sort(key=lambda f: -f["severity"])
    counts = {}
    for f in flags:
        counts[f["type"]] = counts.get(f["type"], 0) + 1

    return {
        "engine": ENGINE_VERSION,
        "months": month_labels,
        "available_months": available_months,
        "period": str(end),
        "entities": entities,
        "entity": entity.upper() if entity else None,
        "counts": counts,
        "total_flags": len(flags),
        "flags": flags,
    }
