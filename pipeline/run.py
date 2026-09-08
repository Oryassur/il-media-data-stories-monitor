"""One ingestion cycle: fetch every homepage -> extract ranked headlines -> archive.

Run:  python -m pipeline.run

This repo currently runs ingestion only — it archives the raw ranked top-N of
each Israeli homepage every hour. The analysis layer (data-story detection,
scoring, dashboard) plugs in on top of this archive once specified.
"""
import sys
import time
from datetime import datetime, timezone

from .common import LOGS, RAW_TOP_N, load_sources
from .extract import extract_items, fetch_html, prominence_weight
from .store import append_raw, append_snapshots


def log(msg):
    print(msg, flush=True)


def run():
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    sources = load_sources()

    raw_rows, snap_rows = [], []
    for src in sources:
        name = src["name"]
        try:
            html = fetch_html(src["url"])
            extracted = extract_items(html, src["url"], src.get("selector"), src["lang"])
        except Exception as e:  # noqa: BLE001 — one dead source must not kill the run
            log(f"FETCH FAIL {name}: {e}")
            raw_rows.append({"ts": ts, "source": name, "ok": 0, "total": 0, "items": []})
            snap_rows.append({"ts": ts, "source": name, "fetch_ok": 0,
                              "total_items": 0, "total_weight": 0})
            continue

        total = len(extracted)
        total_weight = sum(prominence_weight(it["rank"], total) for it in extracted)
        raw_rows.append({
            "ts": ts, "source": name, "ok": 1, "total": total,
            "items": [{"r": it["rank"], "h": it["headline"], "u": it["url"]}
                      for it in extracted[:RAW_TOP_N]],
        })
        snap_rows.append({"ts": ts, "source": name, "fetch_ok": 1,
                          "total_items": total, "total_weight": total_weight})
        log(f"{name}: {total} items" + ("" if total else "  <-- EMPTY EXTRACTION, check parser"))
        time.sleep(1)  # be polite between hosts

    append_raw(ts, raw_rows)
    append_snapshots(ts, snap_rows)

    ok = sum(1 for r in raw_rows if r["ok"])
    LOGS.mkdir(exist_ok=True)
    with open(LOGS / "runs.log", "a") as f:
        f.write(f"{ts} sources_ok={ok}/{len(sources)} "
                f"headlines={sum(len(r['items']) for r in raw_rows)}\n")
    log(f"done: {ok}/{len(sources)} sources ok")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
