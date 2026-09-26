# Vireo Audio Refund Analyser

A small Python + Streamlit tool for analysing Vireo Audio's support-ticket refund data.

The main question I used to frame the analysis was:

> Where are refunds coming from, how much is being refunded, and which cases need attention?

## What it does

The pipeline:

* reconciles the `helpdesk` and `legacy_fd` ticket records
* calculates refund totals by month and quarter
* breaks refunds down by reason code and agent
* flags tickets where a refund and replacement were both issued
* produces a short reconciliation note and board-pack memo

The application is based on the supplied task-pack export. It is a batch analysis tool rather than a live helpdesk integration.

## Run it

Requirements: Python 3.9+

From the project folder:

```bash
python -m pip install -r requirements.txt
python analyse.py
python generate_memo.py
python -m streamlit run app.py
```

On Windows, `run.bat` can be used as a shortcut.

The input files should be placed in:

```text
original task data/
```

The analysis looks for the supplied CSV files by their filenames rather than relying on the original UUID names.

No API key or external service is required.

## Main outputs

After running the pipeline, the `output/` folder contains:

```text
refund_by_reason_agent_month.csv   reason × agent × month breakdown
refund_by_reason_month.csv         reason totals by month
refund_by_agent_month.csv          agent totals by month
refund_by_quarter.csv              quarterly refund totals
top_reasons.csv                    highest-volume refund reasons
top_agents.csv                     agent-level refund totals
double_dip_tickets.csv             refund + replacement cases
validation_sample.csv              sample records for review
reconciliation_note.txt            explanation of the source reconciliation
memo_to_arjun_mehta.txt            one-page summary for Finance
```

## Data reconciliation

The raw ticket export contains records from two source systems.

There are 11,600 unique ticket IDs:

* 638 appear in both sources
* 7,726 appear only in `helpdesk`
* 3,236 appear only in `legacy_fd`

For the 125 overlapping ticket IDs that contain refund amounts, the `legacy_fd` amount is exactly 100 times the corresponding `helpdesk` amount, while the other ticket fields match.

The pipeline therefore:

1. uses the `helpdesk` record when the same ticket exists in both systems
2. keeps `legacy_fd` records that have no helpdesk counterpart
3. converts the monetary value of legacy-only records using the same 100× relationship observed in the matched records

The 100× conversion for legacy-only historical records is an assumption supported by the cross-system matches; those records cannot be verified ticket-by-ticket because there is no corresponding helpdesk row.

## Main result

Across the 18-month period:

* Refund value: **₹67,09,932**
* Refund tickets: **2,340**
* Average refund value: **₹11,18,322 per quarter**
* Refund + replacement ("double-dip") cases: **166**

The main operational control identified is the double-dip case. The support policy does not allow a customer to receive both a refund and a replacement for the same order.

The 166 flagged cases represent about **7.1% of refund tickets** and about **₹95.7K per quarter of associated refund value**, before considering any replacement cost.

These are review cases rather than automatic deductions from agents.

## Validation

The main results were independently recalculated from the raw ticket export without reusing the analysis pipeline.

The reconciliation checks covered:

* total refund amount
* refund ticket count
* quarterly totals
* double-dip count
* cross-system ticket matches
* refund amount relationship between matched records

The headline figures matched with zero difference.

For the 638 ticket IDs appearing in both systems:

* all non-amount ticket fields matched
* all 125 overlapping refund records had the expected 100× amount relationship
* no mismatches were found in these checks

The main known limitation is the legacy-only historical data, where the 100× conversion is inferred from matched records rather than verified against a second row for each ticket.

## Why there is no LLM in the pipeline

The task allowed AI/LLM use, but the refund reason is already provided as a structured field in the export.

Because of that, I used a direct mapping for reason codes rather than adding an LLM classifier. This keeps the runtime deterministic, cheaper and easier to audit.

AI tools were used during development for coding, debugging and review. The production run itself makes no paid API or LLM calls.

## Deliberate scope

I kept the tool focused on the Finance question and did not add:

* LLM/NLP classification of free-text notes
* live helpdesk integration
* sentiment analysis
* broader customer/product analysis

Those could be useful later, but they were not necessary to answer the immediate refund question.

## Limitations

This is an analysis of an exported dataset, not a production integration.

The double-dip report is a review queue and should be checked by Finance/Support before action.

`GW-OTHER` cases above the ₹500 goodwill limit are treated as policy-exception signals, not as confirmed savings, because the current data does not establish that every such case is an incorrect goodwill payment.

Agent-volume comparisons should also be interpreted with the Tier 1 / Tier 2 distinction in the supplied support policy.

## Project structure

```text
vireo_refund_analyser/
├── analyse.py
├── app.py
├── generate_memo.py
├── validate.py
├── requirements.txt
├── run.bat
├── README.md
├── submission_form_answers.md
├── output/
└── original task data/
```
