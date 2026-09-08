"""Persistence for the raw headline archive.

- data/raw/YYYY-MM-DD.jsonl : one row per source per hourly run, holding the
  ranked top-N headlines of that homepage at that moment (append-only).
- data/snapshots/YYYY-MM.csv : one compact health row per source per run
  (append-only) for quick fetch-rate checks without parsing the JSONL.
"""
import csv

from .common import DATA, append_jsonl, day_key, month_key, read_jsonl

RAW_DIR = DATA / "raw"
SNAPS_DIR = DATA / "snapshots"

SNAP_FIELDS = ["ts", "source", "fetch_ok", "total_items", "total_weight"]


def append_raw(ts, rows):
    """rows: [{"ts","source","ok","total","items":[{"r","h","u"}]}]"""
    append_jsonl(RAW_DIR / f"{day_key(ts)}.jsonl", rows)


def read_raw_day(day):
    return read_jsonl(RAW_DIR / f"{day}.jsonl")


def append_snapshots(ts, rows):
    path = SNAPS_DIR / f"{month_key(ts)}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SNAP_FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow(r)
