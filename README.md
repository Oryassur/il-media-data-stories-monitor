# IL media — Data stories monitor

Hourly ingestion of 12 major Israeli news homepages: every run archives each
homepage's ranked top-30 headlines (rank = DOM order ≈ editorial prominence).
The analysis layer — what counts as a "data story", how it is scored, and the
dashboard — is being specified and will plug in on top of this archive.

Sibling projects, same architecture:

- [israel-media-monitor](https://github.com/Oryassur/israel-media-monitor) —
  Israel's perception in western media (attention + framing sentiment).
- `archive/bibi-monitor/` — the retired Netanyahu-family monitor this repo's
  ingestion machinery came from, preserved with its collected data.

## Layout

```
config/sources.yaml      12 Israeli outlets: url, lang, lean (owner-assigned, Israeli spectrum), type, econ tag
pipeline/
  run.py                 hourly cycle: fetch -> extract -> archive
  extract.py             homepage HTML -> ranked headlines (Hebrew-aware); prominence weights v2
  store.py               data/raw/YYYY-MM-DD.jsonl + data/snapshots/YYYY-MM.csv
data/raw/                one row per source per run: ranked top-30 headlines with URLs
data/snapshots/          compact per-run health rows (fetch_ok, totals)
.github/workflows/pipeline.yml   hourly cron (no secrets needed yet)
```

## Known limitations

Four outlets block GitHub runner IPs and fail from Actions (they work from
residential IPs): Israel Hayom, Channel 14, Makor Rishon, Calcalist. Expect
`sources_ok=8/12` on scheduled runs. Two of the four lean right — remember
this skew when the analysis layer lands.

## Local run

```bash
pip install -r requirements.txt
python -m pipeline.run
```
