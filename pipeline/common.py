"""Shared paths, config loading, and small helpers."""
import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
DATA = ROOT / "data"
LOGS = ROOT / "logs"

METHOD_VERSION = "v2"  # prominence weighting: 10/5/3/1 over top-20, 0 beyond

# How many ranked headlines to archive per homepage per run. Covers the whole
# weighted top-20 window plus a below-fold margin; keeps the raw store bounded.
RAW_TOP_N = 30


def load_sources():
    with open(CONFIG / "sources.yaml") as f:
        return yaml.safe_load(f)["sources"]


def day_key(ts_iso: str) -> str:
    return ts_iso[:10]  # YYYY-MM-DD


def month_key(ts_iso: str) -> str:
    return ts_iso[:7]  # YYYY-MM


def read_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
