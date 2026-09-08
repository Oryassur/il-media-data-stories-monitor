# Archive: bibi-media-monitor (retired)

Snapshot of the Netanyahu-family media monitor that ran inside
`Oryassur/israel-media-monitor` as `bibi-media-monitor/` from 2026-08-31 until
its retirement. Its ingestion machinery (Israeli sources, Hebrew-aware
extraction) became this repo's pipeline; the Netanyahu-specific application
(keywords, rubric, dashboard) was retired.

Contents:

- `data/` — collected items (scored headlines) and hourly snapshot CSVs
- `dashboard-data/` — the last published dashboard JSON (docs/bibi/data)
- `config/`, `prompts/` — the Netanyahu keywords, source roster, rubric v1
- `bibi-pipeline.yml` — the workflow that ran it
- `README-original.md` — the monitor's own README
- `logs/runs.log` — run history

Full commit-by-commit history remains in the parent repo's git log.
