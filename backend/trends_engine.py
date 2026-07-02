"""
Expense Trends Engine — vendor x month analysis with anomaly flags.
Mirrors the manual EXPENSE_TRENDS workbook:
  - Group mapping (Account no -> P&L group) applied automatically
  - Vendor x month pivot per group, trailing 12 months
  - Flags: Possibly Missing / Possibly High / Possibly Low (with the math shown)
Entity = prefix of Location ID before the dash (LIB-96100 -> LIB).
"""
import pandas as pd
import numpy as np

ENGINE_VERSION = "trends-v1.0"

# ── P&L group mapping (extracted from EXPENSE_TRENDS workbook Group sheet) ──
GROUP_MAP = {
"50000": "Other Sales",
"55100": "Food Sales",
"55101": "Food Sales",
"55103": "Food Sales",
"55105": "Food Sales",
"55106": "Alcohol Sales",
"55107": "Alcohol Sales",
"55108": "Food Sales",
"55109": "Food Sales",
"55113": "Other Sales",
"55114": "Other Sales",
"55115": "Other Sales",
"55116": "Other Sales",
"55117": "Other Sales",
"55120": "Food Sales",
"55150": "Book Store Sales",
"55151": "Retail Sales",
"55152": "Food Sales",
"55153": "Other Sales",
"55157": "Other Sales",
"55159": "Other Sales",
"55160": "Other Sales",
"55162": "Other Sales",
"55164": "Other Sales",
"55174": "Other Sales",
"55175": "Other Sales",
"55177": "Other Sales",
"55178": "Other Sales",
"55180": "Other Sales",
"55181": "Other Sales",
"55182": "Other Sales",
"55190": "Other Sales",
"55192": "Other Sales",
"55194": "Other Sales",
"55196": "Other Sales",
"55198": "Other Sales",
"55200": "Other Sales",
"55300": "Other Sales",
"55400": "Other Sales",
"55610": "Other Sales",
"55611": "Other Sales",
"55613": "Other Sales",
"55614": "Other Sales",
"55615": "Other Sales",
"55616": "Other Sales",
"55617": "Other Sales",
"55618": "Other Sales",
"55620": "Other Sales",
"55621": "Other Sales",
"55622": "Other Sales",
"55623": "Other Sales",
"55630": "Other Sales",
"55631": "Other Sales",
"55641": "Other Sales",
"55642": "Other Sales",
"55643": "Other Sales",
"55644": "Other Sales",
"55645": "Other Sales",
"55646": "Other Sales",
"55900": "Other Sales",
"60100": "Food COS",
"60108": "Food COS",
"60400": "Packaging COS",
"60401": "Packaging COS",
"60700": "Retail COS",
"60701": "Alcohol COS",
"60702": "Book Store COS",
"60704": "Other COS",
"60705": "Other COS",
"60706": "Other COS",
"60710": "Other COS",
"60712": "Other COS",
"60714": "Other COS",
"60720": "Other COS",
"60721": "Other COS",
"60725": "Other COS",
"60726": "Other COS",
"60727": "Other COS",
"60728": "Other COS",
"61010": "Other COS",
"61011": "Other COS",
"61012": "Other COS",
"63001": "Other COS",
"63003": "Other COS",
"63020": "Other COS",
"63050": "Other COS",
"63051": "Other COS",
"63052": "Other COS",
"63053": "Other COS",
"63055": "Other COS",
"64001": "Other COS",
"64002": "Other COS",
"64500": "Other COS",
"64501": "Other COS",
"70000": "Misc. Non Controllable",
"70001": "Misc. Non Controllable",
"70002": "Misc. Non Controllable",
"70003": "Misc. Non Controllable",
"70004": "Misc. Non Controllable",
"70100": "Hourly Labor",
"70101": "Hourly Labor",
"70102": "Hourly Labor",
"70103": "Hourly Labor",
"70104": "Hourly Labor",
"70106": "Hourly Labor",
"70107": "Hourly Labor",
"70108": "Hourly Labor",
"70109": "Hourly Labor",
"70110": "Hourly Labor",
"70111": "Hourly Labor",
"70112": "Hourly Labor",
"70113": "Hourly Labor",
"70114": "Hourly Labor",
"70115": "Hourly Labor",
"70116": "Hourly Labor",
"70117": "Hourly Labor",
"70118": "Hourly Labor",
"70120": "Hourly Labor",
"70130": "Hourly Labor",
"70140": "Hourly Labor",
"70141": "Hourly Labor",
"70145": "Hourly Labor",
"70150": "Hourly Labor",
"70200": "Salaried Labor",
"70201": "Salaried Labor",
"70202": "Salaried Labor",
"70203": "Salaried Labor",
"70204": "Salaried Labor",
"70205": "Salaried Labor",
"70206": "Salaried Labor",
"70207": "Salaried Labor",
"70208": "Salaried Labor",
"70209": "Salaried Labor",
"70210": "Salaried Labor",
"70211": "Salaried Labor",
"70212": "Salaried Labor",
"70213": "Salaried Labor",
"70214": "Salaried Labor",
"70215": "Salaried Labor",
"70220": "Salaried Labor",
"70221": "Salaried Labor",
"70222": "Salaried Labor",
"70223": "Salaried Labor",
"70224": "Salaried Labor",
"70230": "Salaried Labor",
"70231": "Salaried Labor",
"70233": "Hourly Labor",
"70240": "Salaried Labor",
"70241": "Salaried Labor",
"70242": "Salaried Labor",
"70245": "Salaried Labor",
"70252": "Salaried Labor",
"70262": "Salaried Labor",
"70263": "Hourly Labor",
"70270": "Salaried Labor",
"70272": "Salaried Labor",
"70298": "Hourly Labor",
"70299": "Hourly Labor",
"70302": "Salaried Labor",
"70305": "Salaried Labor",
"70307": "Salaried Labor",
"70309": "Salaried Labor",
"70311": "Salaried Labor",
"70313": "Salaried Labor",
"70315": "Salaried Labor",
"70600": "Salaried Labor",
"70601": "Misc. Non Controllable",
"71000": "Misc. Controllable - Other",
"71003": "Misc. Controllable - Other",
"71300": "Payroll Taxes",
"71400": "Hourly Labor",
"71600": "Travel Expenses",
"71601": "Travel Expenses",
"71602": "Travel Expenses",
"71603": "Travel Expenses",
"71604": "Travel Expenses",
"71606": "Travel Expenses",
"71607": "Travel Expenses",
"71608": "Travel Expenses",
"71700": "Travel Expenses",
"71703": "Travel Expenses",
"71704": "Travel Expenses",
"71800": "Misc. Controllable - Other",
"71801": "Misc. Controllable - Other",
"71901": "Misc. Controllable - Other",
"71905": "Misc. Controllable - Other",
"72000": "Misc. Non Controllable",
"72003": "Misc. Non Controllable",
"72004": "Misc. Non Controllable",
"72100": "Advertising Expense",
"72101": "Delivery Fees",
"72102": "Advertising Expense",
"72103": "Advertising Expense",
"72112": "Advertising Expense",
"72200": "Promotions",
"72201": "Misc. Non Controllable",
"72202": "Misc. Controllable - Other",
"72253": "Misc. Controllable - Other",
"72258": "Misc. Controllable - Other",
"72259": "Misc. Controllable - Other",
"72600": "Utilities Expense",
"72700": "Outside Services",
"73000": "Misc. Non Controllable",
"73100": "Linen/Decor Expense",
"73101": "Uniforms",
"73103": "Uniforms",
"73110": "Linen/Decor Expense",
"73160": "Misc. Controllable - Other",
"73200": "Operating Supplies",
"73210": "Misc. Non Controllable",
"73211": "Misc. Non Controllable",
"73220": "Operating Supplies",
"73260": "Operating Supplies",
"73900": "M&R",
"73901": "M&R",
"73915": "M&R",
"73918": "M&R",
"74000": "Misc. Non Controllable",
"74600": "Utilities Expense",
"74700": "Utilities Expense",
"74800": "Utilities Expense",
"74910": "Credit/Bank Fees",
"75000": "Misc. Non Controllable",
"75100": "Credit/Bank Fees",
"75200": "Subscriptions",
"75202": "Misc. Controllable - Other",
"75300": "Office Supplies",
"75301": "Misc. Controllable - Other",
"75302": "Misc. Controllable - Other",
"75310": "Misc. Controllable - Other",
"75400": "Misc. Controllable - Other",
"75401": "Misc. Controllable - Other",
"75402": "Misc. Controllable - Other",
"75501": "Misc. Controllable - Other",
"75600": "Utilities Expense",
"75901": "Misc. Non Controllable",
"76000": "Misc. Controllable - Other",
"77000": "Misc. Controllable - Other",
"77001": "Misc. Controllable - Other",
"77002": "Misc. Controllable - Other",
"77005": "Misc. Controllable - Other",
"77009": "Misc. Controllable - Other",
"77011": "Misc. Controllable - Other",
"77020": "Misc. Non Controllable",
"77021": "Misc. Non Controllable",
"77022": "Misc. Non Controllable",
"77025": "Misc. Non Controllable",
"77100": "Rent Expense",
"77200": "Services Fees",
"77201": "Misc. Non Controllable",
"77300": "Legal and Accounting",
"77302": "Legal and Accounting",
"77400": "Insurance",
"77401": "Insurance",
"77402": "Insurance",
"77403": "Insurance",
"77404": "Insurance",
"77405": "Insurance",
"77410": "Insurance",
"77414": "Insurance",
"77415": "Insurance",
"77416": "Insurance",
"77420": "Insurance",
"77421": "Insurance",
"77422": "Insurance",
"77500": "Insurance",
"77600": "Taxes",
"77601": "Taxes",
"77602": "Taxes",
"77603": "Taxes",
"77606": "Taxes",
"77700": "Depreciation",
"77705": "Depreciation",
"77800": "Interest Expense",
"77802": "Misc. Non Controllable",
"77806": "Misc. Non Controllable",
"77807": "Misc. Non Controllable",
"77816": "Misc. Non Controllable",
"77817": "Misc. Non Controllable",
"79201": "Misc. Non Controllable",
"72610": "M&R"
}

GROUP_ORDER = [
"Other Sales",
"Food Sales",
"Alcohol Sales",
"Book Store Sales",
"Retail Sales",
"Food COS",
"Packaging COS",
"Retail COS",
"Alcohol COS",
"Book Store COS",
"Other COS",
"Misc. Non Controllable",
"Hourly Labor",
"Salaried Labor",
"Misc. Controllable - Other",
"Payroll Taxes",
"Travel Expenses",
"Advertising Expense",
"Delivery Fees",
"Promotions",
"Utilities Expense",
"M&R",
"Outside Services",
"Linen/Decor Expense",
"Uniforms",
"Operating Supplies",
"Credit/Bank Fees",
"Subscriptions",
"Office Supplies",
"Rent Expense",
"Services Fees",
"Legal and Accounting",
"Insurance",
"Taxes",
"Depreciation",
"Interest Expense"
]


# Sales groups are excluded from expense analysis by default
SALES_GROUPS = {g for g in GROUP_ORDER if "Sales" in g}


def load_gl(gl_path):
    df = pd.read_csv(gl_path)
    df["Account no"] = df["Account no"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Vendor name"] = df["Vendor name"].fillna("(blank)").astype(str).str.strip().replace("", "(blank)")
    df["Location ID"] = df["Location ID"].fillna("").astype(str).str.strip()
    df["Posting date"] = pd.to_datetime(df["Posting date"], errors="coerce")
    df = df.dropna(subset=["Posting date"])
    df["Entity"] = df["Location ID"].str.split("-").str[0].str.upper()
    df["Period"] = df["Posting date"].dt.to_period("M")
    df["Group"] = df["Account no"].map(GROUP_MAP).fillna("Unmapped")
    df["Document number"] = (df.get("Document number", pd.Series(dtype=str))
                             .fillna("").astype(str).str.strip()
                             .str.replace(r"\.0$", "", regex=True)
                             .replace({"nan": "", "None": ""}))
    return df


def _flag_row(series_by_month, months):
    """
    Given a vendor's amounts across the trailing months (list aligned to `months`,
    last = current month), compute flag + stats. Returns dict or None.
    """
    vals = np.array(series_by_month, dtype=float)
    current = vals[-1]
    prior = vals[:-1]
    present_prior = prior != 0
    n_present = int(present_prior.sum())

    if n_present < 4:
        return None  # not enough history to judge

    hist = prior[present_prior]
    mean = float(hist.mean())
    sd = float(hist.std(ddof=1)) if len(hist) > 1 else 0.0
    sd_floor = max(sd, abs(mean) * 0.15, 25.0)  # avoid zero-variance hair triggers

    consistency = n_present / len(prior)
    flag = None

    if current == 0 and n_present >= 6:
        flag = "Possibly Missing"
        deviation = abs(mean)
    elif current > mean + 2 * sd_floor and current - mean > 100:
        flag = "Possibly High"
        deviation = current - mean
    elif current != 0 and current < mean - 2 * sd_floor and mean - current > 100:
        flag = "Possibly Low"
        deviation = mean - current
    else:
        return None

    severity = consistency * deviation
    return {
        "flag": flag,
        "months_present": n_present,
        "months_history": len(prior),
        "history_mean": round(mean, 2),
        "history_sd": round(sd, 2),
        "current": round(float(current), 2),
        "deviation": round(float(deviation), 2),
        "severity": round(float(severity), 2),
    }


def analyze(gl_path, entity=None, view="vendor", include_sales=False):
    """
    entity : entity prefix (e.g. "LIB") or None for whole org
    view   : "vendor" (rows = vendor) or "account" (rows = GL account)
    Returns dict ready for JSON:
      { months, entities, groups: [ {name, rows:[{label, values[12], total, flag?}], totals[12]} ], flags:[...] }
    """
    df = load_gl(gl_path)

    entities = sorted(df["Entity"].unique().tolist())
    if entity:
        df = df[df["Entity"] == entity.upper()]
        if df.empty:
            return {"months": [], "entities": entities, "groups": [], "flags": [],
                    "error": f"No rows for entity {entity}"}

    # Trailing 12 months present in the data
    months = sorted(df["Period"].unique())[-12:]
    df = df[df["Period"].isin(months)]
    month_labels = [str(m) for m in months]

    row_key = "Vendor name" if view == "vendor" else "Account title"

    groups_out, flags_out = [], []
    group_names = [g for g in GROUP_ORDER if include_sales or g not in SALES_GROUPS]
    group_names.append("Unmapped")

    for gname in group_names:
        gdf = df[df["Group"] == gname]
        if gdf.empty:
            continue

        pivot = gdf.pivot_table(index=row_key, columns="Period",
                                values="Amount", aggfunc="sum").reindex(columns=months).fillna(0.0)
        if pivot.empty:
            continue

        # Last doc number in current month per row label (for "show your work")
        cur = months[-1]
        last_docs = (gdf[gdf["Period"] == cur]
                     .sort_values("Posting date")
                     .groupby(row_key)["Document number"].last().to_dict())

        rows = []
        for label, r in pivot.iterrows():
            vals = [round(float(v), 2) for v in r.tolist()]
            row = {"label": str(label), "values": vals, "total": round(float(sum(vals)), 2)}
            f = _flag_row(vals, month_labels)
            if f:
                f["last_doc"] = last_docs.get(label, "")
                row["flag"] = f
                flags_out.append({"group": gname, "label": str(label), **f})
            rows.append(row)

        rows.sort(key=lambda r: -abs(r["total"]))
        totals = [round(float(pivot[m].sum()), 2) for m in months]
        groups_out.append({
            "name": gname,
            "rows": rows,
            "totals": totals,
            "total": round(float(sum(totals)), 2),
        })

    flags_out.sort(key=lambda f: -f["severity"])
    return {
        "engine": ENGINE_VERSION,
        "months": month_labels,
        "entities": entities,
        "entity": entity.upper() if entity else None,
        "view": view,
        "groups": groups_out,
        "flags": flags_out,
    }
