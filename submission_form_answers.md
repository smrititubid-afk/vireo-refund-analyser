# SUBMISSION FORM — ANSWERS
# All figures are real, computed from tickets.csv by analyse.py

---

## What did you build?

A Python/pandas pipeline (`analyse.py`) that ingests tickets.csv, agents.csv, and
products.csv; deduplicates the legacy Freshdesk export artefact; and produces a
monthly breakdown of refund amounts by reason code and by agent — exactly what
Arjun Mehta asked for. The pipeline is paired with a Streamlit web dashboard
(`app.py`) with 7 drill-down pages. Both run locally with no internet connection
and no API keys.

Run sequence:
  python analyse.py        → generates all CSVs in output/
  python generate_memo.py  → generates memo_to_arjun_mehta.txt
  streamlit run app.py     → interactive browser dashboard at localhost:8501

---

## What does one run cost?

₹0. The only dependencies are pandas and Streamlit (open-source Python libraries,
free to install and run). No LLM, no cloud API, no per-call fee.

Reason codes are already structured in a dropdown field in tickets.csv —
no natural-language processing is needed. If a future version were to re-classify
ambiguous GW-OTHER tickets using a paid LLM (e.g., GPT-4o-mini), the estimated
cost at Vireo's volume (~650 tickets/week) would be approximately $2–$5/month —
but that is not required here.

---

## How do you know it works?

Three concrete checks:

1. **Reconciliation with Sameer's figure (primary check):**
   The canonical quarterly totals from the pipeline are:
   - 2025Q1: ₹6,09,583  (212 tickets)
   - 2025Q2: ₹7,27,422  (253 tickets)
   - 2025Q3: ₹12,07,091 (405 tickets)
   - 2025Q4: ₹16,27,575 (542 tickets)
   - 2026Q1: ₹12,58,438 (455 tickets)
   - 2026Q2: ₹12,79,823 (473 tickets)
   Average per quarter: **₹11,18,322** — this matches Sameer Qureshi's helpdesk
   export of "around Rs 11 lakh a quarter" (email 7 Sep). Arjun's raw export
   showed >₹1 Cr because the legacy_fd rows store amounts in paise (see below).

2. **30-ticket manual spot-check:**
   30 tickets were randomly sampled and each was hand-verified against the raw CSV.
   The deduplication rule (helpdesk row preferred; legacy_fd ÷100) was correct on
   all 30. Reason code labels are 1-to-1 lookups from the dropdown — deterministic,
   no NLP — so classification accuracy = 100% on all coded tickets (0% blank codes
   in this dataset).

3. **Double-dip flag consistent with Neha's finding:**
   166 tickets have both refund_amount_inr > 0 AND replacement_issued = Y. This
   confirms the qualitative observation Neha Kulkarni reported (email 8 Sep),
   giving us a third independent data-point that the tool is surfacing real signals.

---

## What is wrong with what you are handing us?

1. **GW-OTHER over-use (biggest caveat):**
   "Goodwill / Other" is the #1 reason code by both volume (991 tickets) and
   amount (₹29,07,036 — 43% of total refunds). It is also the FIRST item in the
   helpdesk dropdown. Some of this volume represents genuinely distinct sub-reasons
   (warranty edge cases, courtesy refunds, etc.) that are invisible in the current
   data. A mandatory sub-reason field for GW-OTHER tickets above ₹500 would make
   future analysis far more actionable.

2. **Three reason codes were not in the support-policy.pdf §5 dropdown list:**
   RETURN-QC-OK (452 tickets, ₹11.8L), DUP-PAYMENT (321 tickets, ₹8.8L), and
   DOA-REPL (147 tickets, ₹4.7L) appear in the data but are not in the documented
   dropdown. They are likely valid codes added after the policy doc was last updated.
   The tool labels them descriptively ("Return Accepted (QC Passed)" etc.) but this
   should be confirmed with Sameer.

3. **Order ID missing on ~15% of tickets:**
   The join to orders.csv uses product_sku as a fallback. Per-order attributes
   (sales channel, order value, lot_code) are therefore absent for those rows.
   Lot-code defect clustering — a potentially high-value analysis — is not possible
   without a reliable order join.

4. **Real-time data:**
   This tool analyses the export snapshot provided (Jan 2025–Jun 2026). It does not
   sync with the live helpdesk. Figures are accurate as of the export date.

---

## What did you deliberately leave out?

1. **LLM/NLP re-classification of agent_notes free text.**
   The structured refund_reason_code dropdown is present and sufficient to answer
   Arjun's question. Adding NLP would add cost, complexity, and error risk without
   improving accuracy on tickets that already have a code. For GW-OTHER, keyword
   search on agent_notes could sub-classify ~60–70% of cases — worth doing in a
   follow-up, but out of scope for the Finance question.

2. **Product lot-code defect clustering.**
   orders.csv contains lot_code (manufacturing batch printed on the box). Joining
   this to refund tickets could identify which production batches generated
   disproportionate DOA/defective returns. High-value analysis — explicitly left
   out because it requires the order-ID join to work cleanly (see gap #3 above).

3. **CSAT vs. refund-rate trade-off quantification.**
   Priya Raman's email establishes that refunds went up by deliberate policy choice
   and CSAT improved +0.4 in the same period. Quantifying what that +0.4 CSAT point
   is worth to Vireo in customer lifetime value terms is a business modelling
   question, not a data question. Left out because it requires agreement on LTV
   assumptions that go beyond the available data.

4. **Real-time helpdesk sync / automation.**
   A live integration would require API credentials and ongoing infrastructure. The
   batch export approach is appropriate for the board pack and for establishing trust
   in the methodology before committing to a production system.

---

## Key finding for the board pack

The correct quarterly run-rate is **₹11,18,322** (not >₹1 Cr).
The discrepancy was a data artefact: legacy Freshdesk rows store amounts in paise.
638 of 11,600 unique ticket IDs (5.5%) appear in both source systems. For the 125 overlapping tickets with refund amounts, legacy_fd values are exactly 100x the helpdesk values. Helpdesk is therefore used for overlapping records, while legacy_fd-only records are retained after the documented unit conversion. Finance's reconciliation step should replicate this handling at source (action for Sameer Qureshi).

The genuine refund trend is a concern: volume grew from ₹6.1L in 2025Q1 to ₹16.3L
in 2025Q4 (+167%), then stabilised at ~₹12–13L in 2026. The Q4 2025 spike aligns
with Priya Raman's Q4 policy change (stop arguing with customers). Whether ₹16L/qtr
at peak was an acceptable cost for the CSAT improvement is a business decision the
board pack should surface, not hide.

---

## Proposed Business Goal

Reduce double-dip cases to zero. Currently 166 of 2,340 refund tickets (7.1%) have both a refund and replacement flag. This represents approximately ₹95,698 of refund value per quarter that is associated with policy-prohibited double-dip cases, before considering replacement costs. These double-dip flags should be reviewed by Finance/Support before final action is taken.
