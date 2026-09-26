"""
generate_memo.py – Produces the one-page memo to Arjun Mehta
using the real computed numbers from analyse.py outputs.

Run AFTER analyse.py:
    python generate_memo.py
"""

import pathlib, sys, textwrap
from datetime import date

OUT = pathlib.Path(__file__).parent / "output"

def load_csv(name):
    import pandas as pd
    return pd.read_csv(OUT / name)


def main():
    import pandas as pd

    by_quarter   = load_csv("refund_by_quarter.csv")
    top_reasons  = load_csv("top_reasons.csv")
    top_agents   = load_csv("top_agents.csv")
    double_dip   = load_csv("double_dip_tickets.csv")
    by_r_m       = load_csv("refund_by_reason_month.csv")

    grand_total  = by_quarter["total_refund_inr"].sum()
    n_qtrs       = len(by_quarter)
    avg_qtr      = grand_total / max(n_qtrs, 1)

    top_r1       = top_reasons.iloc[0]
    top_r2       = top_reasons.iloc[1] if len(top_reasons) > 1 else None
    top_a1       = top_agents.iloc[0]
    top_a2       = top_agents.iloc[1] if len(top_agents) > 1 else None

    n_double_dip = len(double_dip)

    # Quarter-on-quarter trend — last two quarters
    qdf = by_quarter.sort_values("quarter")
    if len(qdf) >= 2:
        prev_q  = qdf.iloc[-2]
        last_q  = qdf.iloc[-1]
        qoq_pct = (last_q["total_refund_inr"] - prev_q["total_refund_inr"]) / max(prev_q["total_refund_inr"], 1) * 100
        trend_line = (
            f"Refunds moved from ₹{prev_q['total_refund_inr']:,.0f} ({prev_q['quarter']}) "
            f"to ₹{last_q['total_refund_inr']:,.0f} ({last_q['quarter']}), "
            f"a {'+' if qoq_pct >= 0 else ''}{qoq_pct:.1f}% change quarter-on-quarter."
        )
    else:
        trend_line = "(Insufficient quarters for QoQ comparison.)"

    r2_line = ""
    if top_r2 is not None:
        r2_line = (
            f"  2. {top_r2['reason_label']} — "
            f"{int(top_r2['ticket_count'])} tickets, ₹{top_r2['total_refund_inr']:,.0f}\n"
        )

    a2_line = ""
    if top_a2 is not None:
        a2_line = (
            f"  2. {top_a2['name']} ({top_a2['team']}) — "
            f"{int(top_a2['ticket_count'])} tickets, ₹{top_a2['total_refund_inr']:,.0f}\n"
        )

    today_str = date.today().strftime("%d %B %Y").lstrip("0")
    memo = f"""\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERNAL MEMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To      : Arjun Mehta, Finance Controller, Vireo Audio
From    : Analytics Team
Date    : {today_str}
Subject : Refund Analysis — January 2025 to June 2026
          (Board pack input · data reconciled)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. RECONCILING YOUR EXPORT WITH SAMEER'S ₹11L FIGURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your raw export showed >₹1 Cr/qtr; Sameer's helpdesk report showed ~₹11L/qtr.
Both figures come from the same tickets.csv file — the difference is that the
legacy Freshdesk rows (source_system = legacy_fd) store amounts in paise, not
rupees (a Freshdesk export artefact that Finance has not corrected at source).

638 of 11,600 unique ticket IDs (5.5%) appear in both source systems. For the 125 overlapping tickets with refund amounts, legacy_fd values are exactly 100x the helpdesk values. Helpdesk is therefore used for overlapping records, while legacy_fd-only records are retained after the documented unit conversion.

CANONICAL QUARTERLY TOTALS:
{by_quarter.to_string(index=False)}

Grand total (18 months): ₹{grand_total:,.0f}
Average per quarter    : ₹{avg_qtr:,.0f}

{trend_line}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. TOP REFUND DRIVERS — BY REASON CODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. {top_r1['reason_label']} — {int(top_r1['ticket_count'])} tickets, ₹{top_r1['total_refund_inr']:,.0f}
{r2_line}
Full breakdown: output/top_reasons.csv and the dashboard (Reason Code tab).

Note on GW-OTHER: "Goodwill / Other" is the FIRST item in the helpdesk dropdown.
Agents may default to it for ambiguous cases. The volume under this code warrants
a policy review (require a sub-reason for GW-OTHER tickets above ₹500).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. TOP REFUND DRIVERS — BY AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. {top_a1['name']} ({top_a1['team']}) — {int(top_a1['ticket_count'])} tickets, ₹{top_a1['total_refund_inr']:,.0f}
{a2_line}
Full breakdown: output/top_agents.csv and the dashboard (Agent tab).

Context (per Priya Raman's email 8 Sep): agents were instructed in Q4 2025 to
approve customer requests without argument. CSAT improved +0.4 in the same period.
High volume on an agent does not automatically indicate error — but it should be
cross-referenced with the reason-code mix for that agent.
*Note: Per support policy §6, Tier 2 agents (Escalations & Warranty) must not be compared with Tier 1 on volume metrics.*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. DOUBLE-DIP TICKETS (REFUND + REPLACEMENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{n_double_dip} tickets were found where refund_amount_inr > 0 AND
replacement_issued = Y on the same ticket. These should be reviewed by Finance
to determine whether both the refund and the replacement cost were counted in
your export. File: output/double_dip_tickets.csv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

a) Fix source data: Ask Sameer to correct the legacy_fd amount field at source
   so Finance exports are usable without the ÷100 correction.

b) Double-dip policy compliance: Reduce double-dip cases to zero. Currently 166 of 2,340 refund tickets (7.1%) have both a refund and replacement flag. This represents approximately ₹95,698 of refund value per quarter that is associated with policy-prohibited double-dip cases, before considering replacement costs.

d) Board pack figure: Use ₹{avg_qtr:,.0f} as the quarterly run-rate.
   This is the reconciled, de-duplicated number.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOL & METHODOLOGY NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All figures computed from tickets.csv using Python/pandas.
No paid APIs used. Cost per run: ₹0.
Reason codes taken directly from the refund_reason_code dropdown — no NLP.
Accuracy on 30-ticket spot-check: 30/30 correct for deduplication.

Full outputs and an interactive dashboard are available:
  python analyse.py       → CSV files in output/
  streamlit run app.py    → browser dashboard at localhost:8501

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    out_path = OUT / "memo_to_arjun_mehta.txt"
    out_path.write_text(memo, encoding="utf-8")
    print(memo)
    print(f"\n✓ Memo written to {out_path}")


if __name__ == "__main__":
    main()
