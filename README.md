# Weekly paper brief

Find papers receiving attention during the last week on **LLM optimizers,
distributed learning, PEFT and continual learning**. The workflow is in
[workflows/weekly-papers.md](workflows/weekly-papers.md).

## Output

```text
papers/
  YYMMDD/
    README.md
    Original Paper Title.pdf
    Another Original Title.pdf
  .state/
    catalog.sqlite3
    papers/<paper-key>/       # verified PDF cache and extracted text
    runs/YYMMDD/              # receipts, manifest and private work records
    logs/
```

Each weekly report entry contains only the title linked to its local PDF, first
upload date, and WHY/HOW. The English WHY/HOW total is at most **100 words**, followed
by concise Chinese counterparts. The report command enforces this limit and renders
one weekly file. There are no separate paper-summary files or foundation searches.

PDF filenames use original titles with incompatible characters replaced. Unicode is
normalized, both NFC and NFD UTF-8 lengths are capped at 240 bytes, and names that
collide under case/Unicode normalization receive a stable identity suffix. These
rules support Ubuntu and common macOS filesystems. Full titles appear in the report.

## Configuration

Edit [weekly-papers.json](weekly-papers.json). Changes are read on each run.

| Setting | Meaning |
| --- | --- |
| `topics` | Editable keywords and synonyms |
| `research_interests` | Semantic relevance instructions |
| `fuzzy.enabled` / `threshold` | Spelling-tolerant recall; similarity defaults to 0.88 |
| `fuzzy.min_token_length` | Short acronyms stay exact; default 5 |
| `negative_keywords` | Explicit exclusions |
| `arxiv_categories` | Discovery categories |
| `top_n` | Weekly selection cap; default 10 |
| `min_hf_upvotes` | Minimum observed cumulative HF votes; default 5 |
| `model` / `reasoning_effort` | `gpt-6-luna` / `xhigh` |
| `timezone` / `schedule` | `Asia/Shanghai` / `Fri 17:00` |

Fuzzy matches recall candidates; the executor judges actual relevance. HF placement
or a current Trending snapshot provides attention evidence. Publication can be older
than the attention window, and the report always uses the true first-upload date.
Discovery is bounded to 100 HF records per endpoint, 500 arXiv records and a default
60-candidate semantic review pool. Private receipts record coverage and failures.

## Run

Requires Python 3.13+, `uv`, authenticated `codex`, Poppler (`pdfinfo`, `pdftotext`),
and the local skills named in the workflow. Archive scripts use the Python stdlib.

```bash
uv run python scripts/run_weekly_papers.py
uv run python scripts/run_weekly_papers.py --date 2026-10-21
uv run python scripts/run_weekly_papers.py --dry-run
uv run python scripts/weekly_papers.py status
uv run python scripts/weekly_papers.py finalize --date 2026-10-21
```

The launcher reads the workflow, runs Codex with the configured model/effort, and
validates completion. Its lock prevents concurrent launcher runs; the timeout is
four hours. Execution logs and failures remain under `.state/`.

## Schedule

The user timer runs every Friday at **17:00 Asia/Shanghai** (09:00 UTC), beginning
2026-10-23. User lingering keeps the timer available after logout. The host must be
powered on and connected. Persistent scheduling catches up after a missed trigger.

```bash
uv run python scripts/install_weekly_timer.py --install
systemctl --user list-timers ml-research-weekly-papers.timer
journalctl --user -u ml-research-weekly-papers.service
systemctl --user disable --now ml-research-weekly-papers.timer
```

Rerun the installer after changing `schedule` or `timezone`.

## Deduplication

SQLite deduplicates paper identity using normalized arXiv IDs, DOI aliases and a
conservative title/first-author/year fallback. A paper appears once in each report.
Verified PDFs are reused across weeks from the private cache using hard links, or
copies on filesystems without hard-link support. SHA-256 detects corruption before
reuse; failed downloads remain incomplete. The first archived revision is reused.
Back up the whole `papers/` tree to retain both readable reports and the catalog.
