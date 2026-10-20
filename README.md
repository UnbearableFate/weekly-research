# Weekly paper research

Search public papers on **LLM optimizers, distributed learning, PEFT, and continual
learning**, identify their direct methodological foundations, and archive original
PDFs with **English-first, Chinese-second** summaries.

The executable instructions are in [workflows/weekly-papers.md](workflows/weekly-papers.md).
The selected subskills are daily-papers-fetch, daily-papers-review, and
academic-research-suite / deep-research / three-way-scan, with bibliography,
source-verification and synthesis role contracts.

## Configuration

Edit [weekly-papers.json](weekly-papers.json):

| Setting | Meaning |
| --- | --- |
| `topics` | Topic labels and editable keyword/synonym lists |
| `research_interests` | Semantic relevance instructions for the executor |
| `fuzzy.enabled` / `threshold` | Enable spelling-tolerant recall; default similarity 0.88 |
| `fuzzy.min_token_length` | Short acronyms remain exact matches; default 5 |
| `negative_keywords` | Explicit exclusions |
| `arxiv_categories` | arXiv discovery categories |
| `top_n` | Maximum recent/attention-qualified papers per week; default 10 |
| `min_hf_upvotes` | Minimum observed cumulative HF votes; default 5 |
| `max_foundations_per_paper` | Normal direct-foundation limit; default 2 |
| `model` / `reasoning_effort` | `gpt-6-luna` / `xhigh` |
| `timezone` / `schedule` | `Asia/Shanghai` / `Fri 17:00` |

For example, add `"GaLore"` under `topics.LLM优化器` or add a new topic with its
aliases. No code change is needed. A broad keyword such as `optimization` only
recalls candidates; the executing model must reject generic agent/prompt
optimization that does not address a configured research interest. Fuzzy matching
handles case, hyphens and small spelling differences; it is not an embedding search.
Semantic selection then reads each candidate's title and abstract.

## Run

Requires Python 3.13+, `uv`, the installed local skills listed in the workflow,
`codex` logged in with ChatGPT, and Poppler's `pdfinfo` / `pdftotext`.
Core scripts use the Python standard library; no separate model API key is needed.

```bash
# Inspect the launch arguments without invoking a model.
uv run python scripts/run_weekly_papers.py --dry-run

# Execute all stages using the configured model and reasoning effort.
uv run python scripts/run_weekly_papers.py

# Select an explicit run date (historical runs omit the current Trending snapshot).
uv run python scripts/run_weekly_papers.py --date 2026-10-20

# Inspect the archive and validate a completed run.
uv run python scripts/weekly_papers.py status
uv run python scripts/weekly_papers.py finalize --date 2026-10-20
```

The runner uses Codex's noninteractive interface with workspace-write permissions,
network access for public sources and approvals set to `never` for unattended
execution. It preserves configured security/rule files. Authentication/model
errors are visible in the execution receipt; it does not switch models.
See the official [noninteractive-mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode).

## Schedule

```bash
# Validate and install/refresh this project's user service and timer.
uv run python scripts/install_weekly_timer.py --install
systemctl --user list-timers ml-research-weekly-papers.timer

# Read service output or pause future runs.
journalctl --user -u ml-research-weekly-papers.service
systemctl --user disable --now ml-research-weekly-papers.timer
```

The installed schedule is every Friday at **17:00 Asia/Shanghai** (09:00 UTC).
After changing `schedule` or `timezone`, rerun the installer. Other settings are
read on each execution. `Persistent=true` catches up a missed trigger when the user
manager starts. User lingering is enabled on this host so logout does not stop
the timer. The host must be powered on and connected; the timer cannot wake a
powered-off machine. The first scheduled run is **2026-10-23 17:00 Asia/Shanghai**.

An advisory file lock prevents overlapping scheduled/manual launcher executions.
Each model run has a four-hour timeout and local stdout/stderr/exit-status receipts.
Failures preserve partial artifacts; `complete` requires archive validation.

## Archive

```text
papers/
  .state/
    catalog.sqlite3
    logs/
  YYMMDD/
    README.md
    run.json
    execution.json
    manifest.json
    _work/                 # candidates, scores, raw sources, search evidence
    <canonical-paper-key>/
      metadata.json
      original.pdf
      original.txt
      summary.md           # each section: English first, then Chinese
      ingest.json
```

SQLite tracks normalized arXiv IDs (ignoring version suffixes), DOI aliases,
conservative title/first-author/year identity, artifact SHA-256 hashes, weekly
membership and citation relationships. Same-title papers with different authors
remain distinct. Conflicting strong identifiers require reconciliation.

Verified originals and summaries are reused across weeks through relative
symlinks. Version changes currently reuse the first archived original: this
workflow deduplicates papers rather than archiving every arXiv revision.
Missing/corrupt files are refetched; failed downloads never count as complete.
Selections rejected after full-text inspection can be withdrawn with `exclude`;
the reason is recorded and cached originals are preserved.
Back up the **entire `papers/` directory including `.state/`** to preserve links
and deduplication history. Downloaded material and execution logs are Git-ignored.

HF Daily placement is dated attention evidence; Trending is a retrieval-time
snapshot. HF vote counts are cumulative, not weekly gains or quality scores.
Older work with current attention is labelled separately. Discovery is bounded
(up to 100 HF records per date, 100 Trending records, 500 arXiv records, and 60
fuzzy-matched candidates); this is a weekly reading selection, not an exhaustive
literature review. Empty or failing sources are reported explicitly.

Foundation relationships require a quote found in the saved citing paper plus
a section/equation locator and an explanation of the dependency. Explicit
`based_on` / `inspired_by` statements are distinguished from reader-inferred
`method_dependency`. Every included foundation gets an original and bilingual
summary too. Existence/hash checks do not prove semantic correctness; the research
executor must inspect the original passages.

## Validation

```bash
uv run python -m unittest discover -s tests -v
uv run python scripts/install_weekly_timer.py
```
