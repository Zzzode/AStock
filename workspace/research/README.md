# Research Workspace Layout

Each deep research project is a self-contained case directory:

```text
workspace/research/<topic-slug>-<YYYYMMDD>/
├── main.tex / main.pdf
├── sections/
├── analysis/
├── data/
├── sources/
├── rendered/
├── review_log.md
└── visual_review.md
```

## Directory Roles

- `main.tex`, `main.pdf`: final report source and compiled deliverable.
- `sections/`: LaTeX chapter files.
- `analysis/`: agent-produced house view, valuation, risk and exhibit planning.
- `data/`: normalized evidence packets, extracted tables, quality gates, audit manifests and machine-readable JSON.
- `sources/`: raw source archive for the case.
- `rendered/`: rendered PDF pages used for visual review.

## Source Archive Rules

Raw source files belong under the current case's `sources/` tree, not under a global report pool.

Use these subdirectory patterns:

| Pattern | Purpose |
|---|---|
| `sources/broker-reports/<YYYY-MM-DD>/` | Ad hoc `/reports` collections. |
| `sources/broker-*` | Curated sell-side PDFs and extracted text. |
| `sources/official-*` | Company filings, exchange documents, HKEX documents and refinancing documents. |
| `sources/ir-*` | Investor-relations records and official Q&A. |
| `sources/probe-*` | Failed source probes, customer-side pages, customs/BOL pages and access-boundary evidence. |

`workspace/reports/` is deprecated. Do not create new files there.

## Quick Research Reports

Short `/team` decision reports belong under:

```text
workspace/research/quick/<CODE>-<YYYYMMDD>/
├── report.tex or report.md
├── report.pdf
└── packet.json
```

`workspace/team/` is deprecated. Do not create new files there.
