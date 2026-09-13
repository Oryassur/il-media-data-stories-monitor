# Data stories — audit spec

Defines what counts as a "data story" in the ingested archive, what claims
get audited, the verdict taxonomy, and the report/persistence format for the
daily audit routine. Reconstructed from two prior manual runs against this
repo's archive (see "Precedent" below) — this is the durable version of
rules that previously existed only inside a one-off prompt.

## Pipeline

1. **Collect** — read the last N days of `data/raw/YYYY-MM-DD.jsonl`, unique
   top-20 items per outlet, deduped by URL. Skip anything already listed in
   `data/audits/audited_urls.txt`.
2. **Triage** (cheap model) — classify each headline `yes` / `maybe` / `no`
   for "is this a data story", with a guessed source type. Apply the detect
   exclusions below before triage counts as final — an excluded item keeps
   its triage label but is marked excluded, never silently dropped (so the
   count of what was seen vs. what was in-scope stays auditable).
3. **Fetch** — article bodies for flagged items only. JS-rendered pages
   (ynet/N12/mako/Kan, etc.): extract `articleBody` from JSON-LD. Missing
   body → `body_ok: 0`, never guessed.
4. **Cluster** — group the same story across outlets. Cap at 12 stories per
   day; prefer cross-outlet clusters and higher homepage ranks when culling.
5. **Audit** (one subagent per story, parallel, capable model + web search) —
   find the primary source (Hebrew + English search), extract verified
   figures, verdict each in-scope claim. A failed subagent audit is recorded
   and skipped, never allowed to abort the run.
6. **Report** — one Hebrew RTL artifact per day (see Report format).
7. **Persist** — per-story JSON + updated `audited_urls.txt`, committed.
8. **Notify** — short Hebrew summary, worst verdicts first.

## Detect exclusions

A headline is not a data story — regardless of how many numbers it
contains — if it is:

- an **official registry / factual tally**: candidate-list filings, court
  rulings, appointments, headcounts of a fixed, undisputed process. There is
  nothing to verify against a primary source because the outlet *is* citing
  the primary source directly and mechanically.
- an **event measurement**: earthquake magnitude, casualty/damage counts
  from a single reported incident, weather readings. These are point
  observations, not a "study" or "report" that could be misread or
  cherry-picked.
- **stock/market/rates data**: index closes, interest rate decisions,
  company valuations, single-day trading moves. High-frequency market data
  is definitionally accurate at the moment reported and out of scope even
  when framed dramatically ("קפיצה של 3,000%").
- **election polls**: house-effect and methodology disputes around polling
  are a distinct, ongoing story of their own — not what this audit is built
  to adjudicate.

Everything else that rests on a citable source (an academic study, official
statistics, a published report, an institutional survey, a program's own
press release) and makes a specific empirical claim is in scope.

## Auditable-claim scope rule

Within an in-scope story, judge **only data/analysis claims** — statements
of fact about data, or conclusions inferred from data. Do **not** judge:

- **event logistics** (who spoke where, when a conference happened, who was
  quoted) — even inside an otherwise data-heavy article;
- **framing/editorial observations** that assert no verifiable figure of
  their own;
- **publication ordinals** ("first studio in 2026 to...", "the sixth
  report") *unless* the ordinal itself is the empirical claim being
  disputed (e.g. a claim that the underlying archive metadata mislabels
  a report's edition number is in scope; a claim that a movie is a studio's
  third $3bn release since 2019 vs. the source's own "first in 2026" is a
  misinterpretation and squarely in scope).

Because of this, a story's own headline can carry a claim that its own body
text does not — verdict the headline separately from the body when they
diverge (this happened repeatedly in the precedent run: headlines converted
program-level figures into national ones, or self-reported pilot-survey
percentages into "families" in general).

## Verdict taxonomy

Exactly these nine values, applied per claim. Never use "lie" or any
intent-based word — intent is not measurable from a homepage headline.

| verdict | meaning |
|---|---|
| `accurate` | Matches the primary source within normal rounding/caveats. |
| `imprecise` | Directionally correct but the baseline, denominator, methodology, or date is undefined, shifted, or omitted in a way that changes what the number means. |
| `overstated` | The underlying figure is real, but the headline/framing inflates its magnitude, scope, or novelty beyond what the source supports (e.g. generalizing one program's numbers to a national trend). |
| `cherry_picked` | Real, accurate figures assembled with a favorable time window, baseline, or subset chosen specifically to produce a misleading overall impression. |
| `misinterpreted` | The source figure is correctly quoted but attached to the wrong meaning or relationship (unit conflation, wrong comparison basis, "first ever" vs. "first this year"). |
| `unsupported` | The article states a number that no reachable version of the primary source corroborates, even though that source is otherwise reachable and on-topic. |
| `contradicted` | The primary source's own published figure directly conflicts with the article's claim. |
| `source_not_found` | A genuine multilingual search failed to locate any primary source (e.g. an unpublished report cited only by the outlet). Never used in place of "didn't look." |
| `source_unreadable` | The primary source was located but could not be accessed (paywall, dead link, blocked request). |

A story where every claim clears `accurate`/`imprecise` still gets a card in
the report — it's evidence the pipeline is working, not just an alert list.
A story that, on inspection, turns out to carry zero judgable claims (all
content is logistics/framing) is dropped from the day's 12 rather than
forced into the table — record it in the story's JSON with
`"claims": []` and a one-line note, so it's traceable but doesn't need a
tenth taxonomy value invented for it.

## Report format

Hebrew, RTL, `dir="auto"` on headline text, IBM Plex Sans Hebrew (+ IBM Plex
Mono for numerals), light + dark theme tokens (`prefers-color-scheme` and
`data-theme` override, per the artifact-design convention). Per the
precedent run's structure:

- Header: scan totals (headlines scanned, data articles analyzed, stories,
  claims checked) + one line stating how many claims were excluded by scope
  and why the taxonomy avoids "lie".
- Verdict-distribution bar + legend, in the same fixed verdict order as the
  table above.
- One card per story: verdict pill (worst verdict in the story), headline +
  outlet + article link(s), per-verdict count chips, a 5–10 sentence Hebrew
  summary leading with the most consequential mistake, then an expandable
  claims table (פסיקה / הטענה בכתבה / הנתון במקור / הערה / כלי).
- Footer: one-line methodology trail (triage model → fetch → audit model +
  web search → scope filter) and an explicit "draft, not yet blind-QA'd"
  disclaimer — verdicts are automated and should be treated as a first pass
  until the blind-QA review flow (per the western monitor) is applied.
- Favicon ⚖️, title `ביקורת סיפורי דאטה — YYYY-MM-DD`.

## Persistence

- `data/audits/YYYY-MM-DD/<story-slug>.json` — one file per story, written
  as a skeleton first (headline cluster, primary-source search status) then
  updated with claims as the audit subagent completes them, so a crash
  mid-audit doesn't lose the day's work.
- `data/audits/audited_urls.txt` — one URL per line, append-only, the
  cross-day dedup key. Created on first run if missing.

## Precedent

Two artifacts from a prior manual run against this repo's archive informed
this spec and are the closest thing to a "wave 1" reference implementation:

- **ביקורת סיפורי דאטה — גל ראשון** (favicon ⚖️) — full audit report, 8–9
  Sep 2026: 602 headlines scanned, 29 data articles, 11 stories, 124 claims.
- **Data-Story Triage Review** (favicon 🔎) — the triage step's own output,
  showing the yes/maybe/no/excluded calibration in practice, including the
  2026-09-10 owner calibration pass that added the exclusion rules above.

Both are private artifacts owned by the repo owner; not reproduced here in
full since triage/audit output is data, not spec.
