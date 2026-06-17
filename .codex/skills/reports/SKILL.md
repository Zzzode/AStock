---
name: reports
description: Use when user wants to collect, download, and archive full-text broker research reports for a sector or ticker. Downloads PDFs and extracts text for agent analysis. Triggers on "collect reports", "download reports", "get research reports on X", "收集研报", "下载研报", "获取XX行业研报", "latest reports on X".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /reports - Research Report Collection & Archiving

Collect full-text broker research reports for a sector or ticker, download PDFs to local storage, and extract text for agent consumption. Uses the `report-collector` agent for discovery, then handles download and text extraction.

## When to Use

- User wants to gather sell-side reports for a specific sector/ticker
- User needs full report text (not just metadata/URL)
- Preparing reference material for equity-research or team analysis
- Building a local knowledge base of analyst views

**Don't use when:**
- User just wants a quick consensus view → `/team` (which runs report-collector internally)
- User wants to write a full research report → `/equity-research`

## Step 1: Parse Parameters

Extract from user input:

| Parameter | Required | Default |
|-----------|----------|---------|
| Sector or ticker | Yes | — |
| Date range | No | last 90 days |
| Min reports | No | 10 |
| Broker filter | No | all |

If sector/ticker is unclear, ask user to clarify.

## Step 2: Discover Reports

Dispatch `report-collector` agent (`.agents/team/report-collector.md`):
- Input: scope, target, date_range, min_reports
- Output: structured catalog with `source_url` and `pdf_url` per report

## Step 3: Create Case-Scoped Output Directory

All collected reports belong under a research case. Do not write new material to the deprecated global `workspace/reports/` directory.

If the user is collecting sources for an existing research case, use that case directory. If no case exists, create one:

```bash
mkdir -p workspace/research/<topic-slug>-<YYYYMMDD>/sources/broker-reports/<YYYY-MM-DD>/
```

Topic slug: lowercase, hyphens for spaces (e.g., `物理AI` → `physical-ai`). The date suffix is the research case date, not necessarily the report publication date.

## Step 4: Download Full Reports

For each report in the catalog, attempt in priority order:

### Priority 1: PDF Download

If `pdf_url` is available:

```bash
curl -L -o "workspace/research/<topic-slug>-<YYYYMMDD>/sources/broker-reports/<YYYY-MM-DD>/NN-<broker>-<short-title>.pdf" "<pdf_url>"
```

### Priority 2: WebFetch PDF link extraction

If only `source_url` (detail page) is available:
1. WebFetch the detail page
2. Look for PDF download link in the page content
3. If found, download via curl

### Priority 3: WebFetch full text

If PDF is unavailable (paywall, removed):
1. WebFetch the source_url
2. Extract the report body text
3. Save as `.md` directly (skip PDF step)

Mark failed downloads in the index.

## Step 5: Extract Text from PDFs

For each successfully downloaded PDF:

```
Read the PDF file using the Read tool (supports PDF reading)
Save extracted text to: workspace/research/<topic-slug>-<YYYYMMDD>/sources/broker-reports/<YYYY-MM-DD>/NN-<broker>-<short-title>.md
```

The .md file should preserve:
- Report title and metadata header
- Section structure (headings)
- Key data tables (as markdown tables where possible)
- Charts described as `[Chart: description]` placeholders

## Step 6: Generate Index

Create `workspace/research/<topic-slug>-<YYYYMMDD>/sources/broker-reports/<YYYY-MM-DD>/index.md`:

```markdown
# Report Collection: <Sector>

**Collection Date:** YYYY-MM-DD
**Reports Found:** N
**Successfully Downloaded:** M
**Failed:** K

## Reports

| # | Broker | Title | Date | Rating | PDF | Text | Notes |
|---|--------|-------|------|--------|-----|------|-------|
| 01 | 浙商证券 | AI革命下一站 | 2026-05-27 | Overweight | [PDF](./01-xxx.pdf) | [MD](./01-xxx.md) | — |
| 02 | 中银证券 | 物理AI时代 | 2026-01-07 | Overweight | ❌ paywall | [MD](./02-xxx.md) | WebFetch fallback |

## Consensus Quick View

- Bullish: X / Neutral: Y / Bearish: Z
- Key consensus: ...
- Key divergence: ...
```

## Step 7: Report to User

Present:
1. How many reports found vs successfully archived
2. The index file path
3. Any failures and reasons
4. Suggest next steps: `/equity-research` for deep analysis, or ask report-analyzer for consensus

## File Naming Convention

```
NN-<broker-slug>-<short-title-slug>.pdf
NN-<broker-slug>-<short-title-slug>.md
```

- `NN`: zero-padded sequence number (01, 02, ...)
- `broker-slug`: broker name in pinyin or abbreviated (e.g., `zheshang`, `zhongyin`, `zhongxin`)
- `short-title-slug`: first 20 chars of title, simplified

## Error Handling

| Scenario | Action |
|----------|--------|
| PDF behind paywall | Use WebFetch for abstract/visible text, mark "partial" |
| PDF download timeout | Retry once with longer timeout, then skip |
| PDF too large (>50MB) | Skip download, note in index |
| WebFetch returns empty | Note "unavailable" in index |
| Report-collector finds <3 reports | Expand date range or broaden keywords, retry once |
| All downloads fail | Report failure to user, suggest trying later |

## Integration

- Output directory is directly inside the research case and can be referenced by `/equity-research` Phase 1
- `report-analyzer` agent can consume the .md files for consensus analysis
- `/team` skill can reference stored reports via case-scoped `workspace/research/<topic-slug>-<YYYYMMDD>/sources/` paths

## Command Reference

```bash
# Directory creation
mkdir -p workspace/research/<topic-slug>-<YYYYMMDD>/sources/broker-reports/<YYYY-MM-DD>/

# PDF download
curl -L -s -o <output-path> <url>

# PDF text verification (check download succeeded)
file <output-path>  # should show "PDF document"
```
