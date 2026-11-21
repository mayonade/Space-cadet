#!/usr/bin/env python3
"""Lead ops for the marketing team: ingest, score, assign to tests, export per channel, test math.

Standard library only. All lead files live in data/ (gitignored).

  mkt.py ingest  <crm_export.csv> [--suppress data/suppression.csv]
  mkt.py assign  <EXP-ID> --arms control,variant [--tier A,B] [--weights 50,50]
  mkt.py export  [--exp EXP-ID]
  mkt.py size    --baseline 0.02 --lift 0.5
  mkt.py readout --arm control:1000:12 --arm variant:1000:25
"""
import argparse
import csv
import hashlib
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from statistics import NormalDist

DATA = Path(__file__).resolve().parent.parent / "data"
HOLDOUT_PCT = 10  # global no-contact holdout; measures what outreach actually adds

CANON = ["id", "first_name", "last_name", "email", "phone", "linkedin_url", "address1", "city",
         "state", "zip", "source", "status", "created_date", "liquid_capital", "net_worth",
         "timeframe_months", "email_opt_out", "sms_consent", "do_not_mail", "replied",
         "email_clicks", "site_visits", "booked_call"]

ALIASES = {
    "id": ["id", "record_id", "lead_id"],
    "first_name": ["first_name", "firstname", "first"],
    "last_name": ["last_name", "lastname", "last"],
    "email": ["email", "email_address"],
    "phone": ["phone", "mobile", "phone_number", "mobile_phone"],
    "linkedin_url": ["linkedin_url", "linkedin", "linkedin_profile"],
    "address1": ["address1", "street", "mailing_street", "address", "street_address"],
    "city": ["city", "mailing_city"],
    "state": ["state", "mailing_state", "province"],
    "zip": ["zip", "zip_code", "mailing_zip", "postal_code", "zipcode"],
    "source": ["source", "lead_source"],
    "status": ["status", "lead_status"],
    "created_date": ["created_date", "created_time", "created", "date_created", "inquiry_date"],
    "liquid_capital": ["liquid_capital", "liquidity", "cash_available", "available_capital",
                       "investment_level", "capital_to_invest"],
    "net_worth": ["net_worth", "networth"],
    "timeframe_months": ["timeframe_months", "timeframe", "time_frame", "purchase_timeframe"],
    "email_opt_out": ["email_opt_out", "unsubscribed", "opt_out"],
    "sms_consent": ["sms_consent", "sms_opt_in", "text_consent"],
    "do_not_mail": ["do_not_mail"],
    "replied": ["replied", "has_replied"],
    "email_clicks": ["email_clicks", "clicks"],
    "site_visits": ["site_visits", "visits"],
    "booked_call": ["booked_call", "call_booked"],
}
DEAD_STATUSES = {"closed", "closed won", "client", "not interested", "do not contact", "dnc",
                 "junk lead", "junk", "lost lead", "unqualified", "deceased"}


def norm_key(k):
    return re.sub(r"[^a-z0-9]+", "_", k.strip().lower()).strip("_")


def truthy(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y", "x"}


def to_num(v):
    """'$100,000' -> 100000; '100k' -> 100000; '100-250k' -> 100000 (low end); '' -> 0."""
    s = str(v).lower().replace(",", "").replace("$", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|m)?", s)
    if not m:
        return 0.0
    n = float(m.group(1))
    unit = m.group(2) or ("k" if re.search(r"\d\s*-\s*\d+(\.\d+)?\s*k", s) else
                          "m" if re.search(r"\d\s*-\s*\d+(\.\d+)?\s*m", s) else "")
    return n * {"k": 1e3, "m": 1e6, "": 1}[unit]


def to_date(v):
    s = str(v).strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%m/%d/%Y", 10), ("%m/%d/%y", 8), ("%d-%b-%Y", 11)):
        try:
            return datetime.strptime(s[:n].strip(), fmt).date()
        except ValueError:
            continue
    return None


def bucket(*parts):
    """Stable 0-9999 bucket. Same lead + same salt always lands in the same place."""
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest(), 16) % 10000


def score(lead, today):
    """Transparent points. Fit + recency + engagement. Edit freely; the tiers follow."""
    pts, why = 0, []

    def add(n, reason):
        nonlocal pts
        pts += n
        why.append(f"{reason}+{n}")

    liquid, nw = to_num(lead["liquid_capital"]), to_num(lead["net_worth"])
    if liquid >= 100_000: add(30, "liquid100k")
    elif liquid >= 50_000: add(15, "liquid50k")
    if nw >= 500_000: add(15, "nw500k")
    elif nw >= 250_000: add(8, "nw250k")
    tf = to_num(lead["timeframe_months"])
    if 0 < tf <= 3: add(20, "buy<=3mo")
    elif 0 < tf <= 6: add(10, "buy<=6mo")
    created = to_date(lead["created_date"])
    if created:
        age = (today - created).days
        if age <= 30: add(20, "new30d")
        elif age <= 90: add(10, "new90d")
        elif age <= 365: add(5, "new1y")
    if truthy(lead["replied"]): add(30, "replied")
    if to_num(lead["email_clicks"]) >= 1: add(15, "clicked")
    if to_num(lead["site_visits"]) >= 1: add(10, "visited")
    if lead["phone"]: add(5, "phone")
    if lead["address1"] and lead["zip"]: add(5, "mailable")
    return pts, ("A" if pts >= 60 else "B" if pts >= 30 else "C"), " ".join(why)


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def cmd_ingest(a):
    raw = read_csv(a.file)
    if not raw:
        sys.exit("No rows in file.")
    lookup = {alias: canon for canon, als in ALIASES.items() for alias in als}
    header_map = {h: lookup[norm_key(h)] for h in raw[0] if norm_key(h) in lookup}
    unmapped = [h for h in raw[0] if h not in header_map]
    suppressed_emails = set()
    if a.suppress and Path(a.suppress).exists():
        suppressed_emails = {r.get("email", "").strip().lower() for r in read_csv(a.suppress)}

    today, seen, out = date.today(), set(), []
    stats = {"rows": len(raw), "dupes": 0, "no_contact": 0, "suppressed": 0}
    for r in raw:
        lead = dict.fromkeys(CANON, "")
        for h, canon in header_map.items():
            if not lead[canon]:
                lead[canon] = (r.get(h) or "").strip()
        lead["email"] = lead["email"].lower()
        key = lead["email"] or re.sub(r"\D", "", lead["phone"])
        if not key:
            stats["no_contact"] += 1
            continue
        if key in seen:
            stats["dupes"] += 1
            continue
        seen.add(key)
        lead["id"] = lead["id"] or hashlib.sha256(key.encode()).hexdigest()[:12]
        reasons = []
        if lead["status"].lower() in DEAD_STATUSES: reasons.append("status")
        if truthy(lead["booked_call"]): reasons.append("already_booked")
        if lead["email"] in suppressed_emails: reasons.append("suppression_list")
        lead["suppressed"] = ",".join(reasons)
        if reasons:
            stats["suppressed"] += 1
        lead["score"], lead["tier"], lead["score_why"] = score(lead, today)
        lead["holdout"] = "1" if bucket("global-holdout", lead["id"]) < HOLDOUT_PCT * 100 else ""
        out.append(lead)

    write_csv(DATA / "leads.csv", out, CANON + ["score", "tier", "score_why", "suppressed", "holdout"])
    live = [l for l in out if not l["suppressed"]]
    print(f"Read {stats['rows']} rows -> {len(out)} leads "
          f"({stats['dupes']} dupes, {stats['no_contact']} with no email/phone dropped)")
    print(f"Suppressed: {stats['suppressed']}   Contactable: {len(live)}   "
          f"Holdout: {sum(1 for l in live if l['holdout'])}")
    for t in "ABC":
        n = sum(1 for l in live if l["tier"] == t)
        print(f"  Tier {t}: {n:>6}  ({n / max(len(live), 1):.0%})")
    cov = lambda f: sum(1 for l in live if l[f]) / max(len(live), 1)
    print("Reach: " + "  ".join(f"{n} {cov(f):.0%}" for n, f in
          [("email", "email"), ("phone", "phone"), ("mail", "address1"), ("linkedin", "linkedin_url")]))
    if unmapped:
        print(f"Unmapped columns (ignored): {', '.join(unmapped)}")
    print(f"Wrote {DATA / 'leads.csv'}")


def eligible(leads):
    return [l for l in leads if not l["suppressed"] and not l["holdout"]]


def cmd_assign(a):
    arms = a.arms.split(",")
    weights = [float(w) for w in a.weights.split(",")] if a.weights else [1.0] * len(arms)
    if len(weights) != len(arms) or len(arms) < 2:
        sys.exit("Need 2+ arms and one weight per arm.")
    tiers = set(a.tier.upper().split(",")) if a.tier else {"A", "B", "C"}
    cuts, acc = [], 0.0
    for w in weights:
        acc += w / sum(weights) * 10000
        cuts.append(acc)
    rows = []
    for l in eligible(read_csv(DATA / "leads.csv")):
        if l["tier"] not in tiers:
            continue
        b = bucket(a.exp, l["id"])
        arm = next(arm for arm, c in zip(arms, cuts) if b < c or c == cuts[-1])
        rows.append({"exp": a.exp, "id": l["id"], "arm": arm, "tier": l["tier"]})
    out = DATA / "assignments" / f"{a.exp}.csv"
    write_csv(out, rows, ["exp", "id", "arm", "tier"])
    for arm in arms:
        print(f"  {arm}: {sum(1 for r in rows if r['arm'] == arm)}")
    print(f"Wrote {out}  (deterministic: re-running gives the same split)")


def cmd_export(a):
    leads = eligible(read_csv(DATA / "leads.csv"))
    arm = {}
    if a.exp:
        arm = {r["id"]: r["arm"] for r in read_csv(DATA / "assignments" / f"{a.exp}.csv")}
        leads = [l for l in leads if l["id"] in arm]
    for l in leads:
        l["arm"] = arm.get(l["id"], "")
    out = DATA / "exports" / (a.exp or "all")
    base = ["id", "first_name", "last_name", "tier", "arm"]

    email = [l for l in leads if l["email"] and not truthy(l["email_opt_out"])]
    write_csv(out / "email.csv", email, base + ["email", "source", "state"])
    # Ad platforms match on normalized, SHA-256 hashed email. Opt-outs stay out of ads too.
    ads = [{"email_sha256": hashlib.sha256(l["email"].encode()).hexdigest()} for l in email]
    write_csv(out / "ads_audience.csv", ads, ["email_sha256"])
    mail = [l for l in leads if l["tier"] == "A" and l["address1"] and l["zip"]
            and not truthy(l["do_not_mail"])]
    write_csv(out / "direct_mail.csv", mail, base + ["address1", "city", "state", "zip"])
    li = [l for l in leads if l["tier"] in "AB" and l["linkedin_url"]]
    write_csv(out / "linkedin_queue.csv", li, base + ["linkedin_url"])
    sms = [l for l in leads if l["phone"] and truthy(l["sms_consent"])]
    write_csv(out / "sms_consented.csv", sms, base + ["phone"])
    for name, rows in [("email", email), ("ads_audience", ads), ("direct_mail (tier A)", mail),
                       ("linkedin_queue (tier A/B)", li), ("sms_consented", sms)]:
        print(f"  {name}: {len(rows)}")
    print(f"Wrote {out}/")


def cmd_size(a):
    p1, p2 = a.baseline, a.baseline * (1 + a.lift)
    za, zb = NormalDist().inv_cdf(1 - a.alpha / 2), NormalDist().inv_cdf(a.power)
    pbar = (p1 + p2) / 2
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = math.ceil(n / (p2 - p1) ** 2)
    print(f"Baseline {p1:.2%} -> {p2:.2%} (+{a.lift:.0%} relative), alpha {a.alpha}, power {a.power}")
    print(f"Need {n:,} leads per arm ({2 * n:,} total for two arms).")


def cmd_readout(a):
    arms = []
    for spec in a.arm:
        name, n, x = spec.split(":")
        arms.append((name, int(n), int(x)))
    (cn, n1, x1), rest = arms[0], arms[1:]
    p1 = x1 / n1
    print(f"{cn} (control): {x1}/{n1} = {p1:.2%}")
    for name, n2, x2 in rest:
        p2 = x2 / n2
        pool = (x1 + x2) / (n1 + n2)
        se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
        z = (p2 - p1) / se if se else 0.0
        pval = 2 * (1 - NormalDist().cdf(abs(z)))
        se_d = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        lo, hi = (p2 - p1) - 1.96 * se_d, (p2 - p1) + 1.96 * se_d
        rel = f"{(p2 / p1 - 1):+.0%}" if p1 else "n/a"
        thin = min(x1, x2, n1 - x1, n2 - x2) < 5
        verdict = ("TOO THIN - fewer than 5 conversions in an arm, keep running" if thin else
                   "WIN" if pval < a.alpha and p2 > p1 else
                   "LOSS" if pval < a.alpha else "NO CALL - difference is within noise")
        print(f"{name}: {x2}/{n2} = {p2:.2%}  lift {rel}  diff 95% CI [{lo:+.2%}, {hi:+.2%}]  "
              f"p={pval:.3f}  -> {verdict}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("ingest"); x.add_argument("file"); x.add_argument("--suppress", default=str(DATA / "suppression.csv")); x.set_defaults(f=cmd_ingest)
    x = s.add_parser("assign"); x.add_argument("exp"); x.add_argument("--arms", required=True); x.add_argument("--weights"); x.add_argument("--tier"); x.set_defaults(f=cmd_assign)
    x = s.add_parser("export"); x.add_argument("--exp"); x.set_defaults(f=cmd_export)
    x = s.add_parser("size"); x.add_argument("--baseline", type=float, required=True); x.add_argument("--lift", type=float, required=True); x.add_argument("--alpha", type=float, default=0.05); x.add_argument("--power", type=float, default=0.8); x.set_defaults(f=cmd_size)
    x = s.add_parser("readout"); x.add_argument("--arm", action="append", required=True); x.add_argument("--alpha", type=float, default=0.05); x.set_defaults(f=cmd_readout)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
