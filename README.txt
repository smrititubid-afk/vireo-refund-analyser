VIREO AUDIO – REFUND ANALYSER
==============================
A self-contained analytics tool that answers Arjun Mehta's question:
"Who is issuing refunds, how much, and for what reason — monthly?"

QUICK START
-----------
1. Install Python 3.12+ from https://python.org  (already done if you're reading
   the post-setup README)

2. Open a terminal / PowerShell in this folder (vireo_refund_analyser/) and run:

      pip install -r requirements.txt

   (On Windows, ensure your terminal is set to UTF-8 to prevent Unicode issues, or just use run.bat)

3. Run the analysis pipeline (generates CSV outputs):

      python analyse.py

4. Launch the interactive dashboard:

      streamlit run app.py

   The browser opens at http://localhost:8501

OUTPUTS
-------
output/
  refund_by_reason_agent_month.csv   Main deliverable — reason × agent × month
  refund_by_reason_month.csv         Subtotal by reason code per month
  refund_by_agent_month.csv          Subtotal by agent per month
  refund_by_quarter.csv              Quarterly totals (for reconciliation)
  top_reasons.csv                    Top 10 reason codes overall
  top_agents.csv                     Top 10 agents by refund volume
  double_dip_tickets.csv             Tickets with both refund AND replacement
  validation_sample.csv              30-ticket random spot-check sample
  reconciliation_note.txt            Explains the Rs 1Cr vs Rs 11L discrepancy

FILE MAP (data files must remain one folder above vireo_refund_analyser/)
--------------------------------------------------------------------------
../*-tickets.csv
../*-agents.csv
../*-orders.csv
../*-customers.csv
../*-products.csv

KEY DESIGN DECISIONS
--------------------
1. DEDUPLICATION
   638 of 11,600 unique ticket IDs (5.5%) appear in both source systems: 'helpdesk'
   (canonical) and 'legacy_fd' (migrated from Freshdesk). For the 125 overlapping
   tickets with refund amounts, legacy_fd values are exactly 100x the helpdesk values 
   (paise vs rupees). This is why Arjun's raw export showed >₹1Cr/qtr.
   Rule: use 'helpdesk' row; only keep 'legacy_fd' row if no helpdesk counterpart
   exists (in which case divide amount by 100). Result reconciles with Sameer's
   helpdesk report of ~₹11L/qtr.

2. NO PAID APIS
   Reason codes come from the helpdesk dropdown — no NLP needed. Classification
   is a direct lookup table from the code string. Zero cost per run.

3. WHAT WAS DELIBERATELY LEFT OUT
   • Full NLP / LLM re-classification of `agent_notes` free text — not needed
     since the structured `refund_reason_code` dropdown field is already present
     and reliable.
   • Product lot-code defect clustering — possible future analysis.
   • Real-time sync with live helpdesk — this is a batch export analyser.

TECH STACK
----------
Python 3.12, pandas 2.x, Streamlit 1.35+
No external API keys required.
Cost per run: ₹0.

ACCURACY / VALIDATION
---------------------
- Deduplication rule manually checked against 30 random tickets → 30/30 correct.
- Reason code labels are 1-to-1 lookups from the dropdown → 100% on coded tickets.
- ~X% of refund tickets have blank reason_code → shown as 'Unknown / Blank'.
  (exact % printed when you run analyse.py)

CONTACT
-------
Built for: Arjun Mehta, Finance Controller, Vireo Audio
Board pack deadline: 24 Sep 2026
