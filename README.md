# Messi vs Ronaldo: how the metric changes the story

An extension of my CISC7204 Practice 07 visualization, prepared for Practice 09.
Author: **LI SIWEI** · Status: **ongoing** (source validation and peer review).

## Research question

How does the apparent leader change when we compare goals, assists, and goals
plus assists, and how do annual peaks differ from sustained scoring?

## Data source and usage permissions

- Source: [MessiXRonaldo calendar-year table](https://messixronaldo.com/calendar-year-stats).
- Scope: 24 calendar years, 2002–2025, senior club and international statistics
  as represented by this source. Checked against the visible table on 21 October 2026.
- [Source methodology](https://messixronaldo.com/methodology) describes a broad
  historical assist definition. That definition can differ from other trackers.
- The source is publicly readable, but an explicit open-data reuse license was
  not found on the inspected pages. Public availability is not an open license.
  **No raw dataset, source HTML, photographs, or website assets are redistributed.**
  The script reads the public table on demand; use remains subject to the
  source's terms. The original code and derived, attributed charts are shared
  as coursework. This repository does not grant rights to third-party data.
- Only aggregate professional sports statistics are used. No credentials,
  private contact details, or restricted course datasets are included.
- For unrestricted downstream reuse, first establish data permission or replace
  the source with an explicitly licensed dataset.

## Methods and tools

Python standard-library HTML parsing, schema validation, deterministic aggregation,
and Pillow chart rendering. Missing pre-debut Messi observations remain missing;
they are excluded from his totals and the annual line. Neither player receives
invented observations. The incomplete 2026 calendar year is excluded.
Each player's own available years are used; career durations are unequal.
G+A assigns equal weight to goals and assists as a descriptive choice.
No hypothesis test, causal inference, or predictive model is claimed.

## Key findings — for this source snapshot only

| Measure | Messi | Ronaldo |
|---|---:|---:|
| Goals | 856 | 935 |
| Assists | 455 | 305 |
| Goals + assists | 1,311 | 1,240 |
| Appearances | 1,096 | 1,174 |
| G+A per appearance | 1.196 | 1.056 |
| Years with at least 40 goals | 11 | 14 |

Ronaldo leads by **79 goals**, while Messi leads by **71 goals plus assists**.
Messi's highest annual value is **91 (2012)**; Ronaldo's is **69 (2013)**.
The lesson is about metric selection, not an objective ranking of greatness.

![Goals, assists, and combined contributions compared](figures/metric_comparison.png)

![Annual goals by player from 2002 to 2025](figures/annual_goals.png)

## Limitations and next steps

These calculations reproduce a fan-maintained source table; they do not verify
the accuracy of that table. Annual figures require independent match-level
auditing before use as authoritative career statistics. Assist definitions,
unequal career windows, minutes, league strength, roles, and competition mix
affect interpretation. Per-appearance rates do not adjust for minutes played.
Next: cross-check annual records, resolve reuse permissions, compare a common
time window, and add uncertainty/context rather than a single winner.

## Reproduce

Requires Python 3.10+ and Internet access to the public source on the first route.

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/analyze.py
```

The script creates `results.json` and both PNG files in `figures/`.
No sign-in or API key is needed. It validates all years, missingness, nonnegative
counts, and a SHA-256 hash of normalized observations. If the source changes,
the script stops rather than silently producing different published results.
Review the new source before changing the expected hash or findings.

If you already have a lawfully obtained local CSV matching the source snapshot:

```sh
python scripts/analyze.py --data path/to/calendar_year_stats.csv
```

Schema: `year,messi_goals,messi_assists,messi_apps,ronaldo_goals,ronaldo_assists,ronaldo_apps`.
Empty cells are missing values. The local CSV is intentionally ignored by Git.
Expected normalized-data SHA-256:
`bb4fff0129c81656889772206fb58e40acb6456d27db8ddec052483d47d1de3f`.
Both the local-snapshot route and live-source retrieval were executed successfully
on 21 October 2026 and returned the same normalized-data hash and findings.

## Peer review

Pending: ask a classmate to identify the research question, main finding, and
limitation; record their actual feedback and commit an improvement. See
[PEER_REVIEW.md](PEER_REVIEW.md). AI review is not classmate feedback.

## AI assistance

GPT-6 through the Codex desktop app helped reorganize the analysis, write code,
create charts, draft documentation, and prepare the portfolio. This extension
builds on the earlier AI-assisted Practice 07 work. The author must review the
outputs and the source limitations before submission.
