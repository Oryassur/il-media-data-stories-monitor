# IL media — Data stories monitor

Hourly ingestion of 12 Israeli news homepages, archiving each one's ranked
top-30 headlines. The analysis layer ("data stories" detection, scoring,
dashboard) is **not yet specified** — this repo currently runs ingestion only,
building the raw archive that layer will consume.

Ported from the retired `bibi-media-monitor` (Netanyahu-family monitor), which
lives in `archive/bibi-monitor/` together with its collected data. The sibling
western monitor is `Oryassur/israel-media-monitor` (local: ~/Desktop/DJ1).

## Invariants — keep these true

- **Raw-first**: every hourly run appends each homepage's ranked top-30 to
  `data/raw/YYYY-MM-DD.jsonl` (append-only, never rewritten). Analysis layers
  derive from this archive; they never replace it.
- Prominence weights (method v2): rank 1 ×10, 2–5 ×5, 6–10 ×3, 11–20 ×1,
  21+ ×0. Rank = DOM order of first appearance.
- Hebrew headlines: extraction min-length is 15 chars for `he` (vs 25 for
  `en`); render with `dir="auto"` in any future UI.
- Failed fetches are recorded as `ok: 0` rows — missing, never zero.
- Lean is owner-assigned on the Israeli spectrum (no AllSides equivalent
  exists); `econ: true` tags Globes/TheMarker/Calcalist.
- **Known-blocked from GitHub runner IPs** (keep in config, expect 8/12 ok):
  Israel Hayom, Channel 14, Makor Rishon, Calcalist.
- When scoring is added: versioned rubric + model recorded per score, own
  repo secret for the API key (never reuse another monitor's key), and the
  blind-QA review flow from the western monitor applies unchanged.
- A third sibling repo ("IL media — headlines alignment", TBD) should consume
  this repo's raw archive rather than re-fetching the same homepages.
