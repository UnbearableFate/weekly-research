#!/usr/bin/env python3
"""Discover, deduplicate and archive weekly papers using the Python stdlib."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode, unquote, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ARXIV = re.compile(r"(?<!\w)(\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7})(?:v\d+)?", re.I)


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False, suffix=".tmp") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
        name = f.name
    os.replace(name, path)


def normalize(text):
    text = unicodedata.normalize("NFKC", str(text)).casefold()
    return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))


def arxiv_id(value):
    value = unquote(str(value or ""))
    match = ARXIV.search(value)
    return match.group(1).lower() if match else ""


def doi_id(value):
    value = unquote(str(value or "")).strip()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value,
                   flags=re.I).strip().lower()
    if value and not re.fullmatch(r"10\.\d{4,9}/\S+", value):
        raise ValueError(f"Malformed DOI: {value}")
    return value


def digest(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def canonical_record(record):
    p = dict(record)
    p["title"] = " ".join(str(p.get("title", "")).split())
    if not p["title"]:
        raise ValueError("Paper title is required")
    authors = p.get("authors", [])
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(",") if a.strip()]
    p["authors"] = [a["name"] if isinstance(a, dict) else str(a) for a in authors]
    p["arxiv_id"] = arxiv_id(p.get("arxiv_id") or p.get("url") or p.get("pdf"))
    p["doi"] = doi_id(p.get("doi"))
    p["published_at"] = p.get("published_at") or p.get("date") or ""
    p["year"] = str(p.get("year") or p["published_at"][:4])
    if p["year"] and not re.fullmatch(r"\d{4}", p["year"]):
        raise ValueError("Publication year must have four digits")
    p["pdf_url"] = p.get("pdf_url") or p.get("pdf") or (
        f"https://arxiv.org/pdf/{p['arxiv_id']}" if p["arxiv_id"] else "")
    if not (p["arxiv_id"] or p["doi"] or (p["authors"] and p["year"])):
        raise ValueError("Require arXiv/DOI or title + author + year")
    return p


def fingerprint(p):
    if not p["authors"] or not p["year"]:
        return ""
    return "|".join((normalize(p["title"]), normalize(p["authors"][0]), p["year"]))


def keyword_matches(text, topics, fuzzy):
    """Bounded word-window fuzzy matching; never fuzzy-match short acronyms."""
    words = normalize(text).split()
    haystack = " " + " ".join(words) + " "
    threshold = float(fuzzy.get("threshold", 0.88))
    minimum = int(fuzzy.get("min_token_length", 5))
    if not 0.5 <= threshold <= 1 or minimum < 3:
        raise ValueError("Invalid fuzzy threshold or min_token_length")
    matches = []
    for topic, terms in topics.items():
        for term in terms:
            needle = normalize(term)
            if not needle:
                continue
            if f" {needle} " in haystack:
                matches.append({"topic": topic, "term": term, "matched": needle,
                                "similarity": 1.0})
                continue
            if not fuzzy.get("enabled", True):
                continue
            tokens = needle.split()
            if not any(len(t) >= minimum for t in tokens):
                continue
            for i in range(len(words) - len(tokens) + 1):
                window = words[i:i + len(tokens)]
                # Short words (including LoRA/PEFT) cannot become other acronyms.
                if any(len(t) < minimum and t != w for t, w in zip(tokens, window)):
                    continue
                candidate = " ".join(window)
                if abs(len(candidate) - len(needle)) > max(2, len(needle) // 5):
                    continue
                similarity = difflib.SequenceMatcher(None, needle, candidate).ratio()
                if similarity >= threshold:
                    matches.append({"topic": topic, "term": term, "matched": candidate,
                                    "similarity": round(similarity, 4)})
                    break
    return matches


class Archive:
    def __init__(self, root=ROOT, config=None):
        self.root = Path(root).resolve()
        self.config = config or read_json(self.root / "weekly-papers.json")
        self.papers = self.root / "papers"
        self.state = self.papers / ".state"
        self.state.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.state / "catalog.sqlite3", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS papers(
                key TEXT PRIMARY KEY, title TEXT NOT NULL, fingerprint TEXT,
                metadata TEXT NOT NULL, first_seen TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS paper_fingerprint ON papers(fingerprint);
            CREATE TABLE IF NOT EXISTS identifiers(
                kind TEXT NOT NULL, value TEXT NOT NULL,
                paper_key TEXT NOT NULL REFERENCES papers(key),
                PRIMARY KEY(kind,value));
            CREATE TABLE IF NOT EXISTS artifacts(
                paper_key TEXT NOT NULL REFERENCES papers(key), kind TEXT NOT NULL,
                path TEXT NOT NULL, sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY(paper_key,kind));
            CREATE TABLE IF NOT EXISTS runs(
                date TEXT PRIMARY KEY, directory TEXT NOT NULL,
                status TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS membership(
                run_date TEXT NOT NULL REFERENCES runs(date),
                paper_key TEXT NOT NULL REFERENCES papers(key), role TEXT NOT NULL,
                observation TEXT NOT NULL, PRIMARY KEY(run_date,paper_key,role));
            CREATE TABLE IF NOT EXISTS relations(
                run_date TEXT NOT NULL REFERENCES runs(date),
                source_key TEXT NOT NULL REFERENCES papers(key),
                target_key TEXT NOT NULL REFERENCES papers(key),
                relation_type TEXT NOT NULL, evidence TEXT NOT NULL,
                PRIMARY KEY(run_date,source_key,target_key,relation_type));
            CREATE TABLE IF NOT EXISTS foundation_checks(
                run_date TEXT NOT NULL REFERENCES runs(date),
                paper_key TEXT NOT NULL REFERENCES papers(key), note TEXT NOT NULL,
                PRIMARY KEY(run_date,paper_key));
        """)

    def close(self):
        self.db.close()

    def day(self, value=None):
        return date.fromisoformat(value) if value else datetime.now(
            ZoneInfo(self.config["timezone"])).date()

    def directory(self, value=None):
        return self.papers / self.day(value).strftime(self.config["date_format"])

    def prepare(self, value=None):
        day = self.day(value)
        folder = self.directory(value)
        work = folder / "_work"
        work.mkdir(parents=True, exist_ok=True)
        receipt = folder / "run.json"
        if receipt.exists() and read_json(receipt)["date"] != day.isoformat():
            raise ValueError("Date-directory collision")
        if not receipt.exists():
            write_json(receipt, {
                "date": day.isoformat(), "timezone": self.config["timezone"],
                "window_start": (day - timedelta(days=self.config["days"] - 1)).isoformat(),
                "window_end": day.isoformat(), "created_at": now(),
                "requested_model": self.config["model"],
                "requested_reasoning_effort": self.config["reasoning_effort"],
                "status": "prepared", "config": self.config,
            })
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO runs VALUES (?,?,?,?)",
                            (day.isoformat(), str(folder.relative_to(self.root)), "prepared", now()))
        skill_dir = self.root / self.config["daily_skills"]
        override = {
            "paths": {"obsidian_vault": str(folder), "paper_notes_folder": ".",
                      "daily_papers_folder": ".", "concepts_folder": "_concepts"},
            "daily_papers": {
                "keywords": [t for terms in self.config["topics"].values() for t in terms],
                "negative_keywords": self.config["negative_keywords"],
                "domain_boost_keywords": [],
                "arxiv_categories": self.config["arxiv_categories"],
                "research_interests": self.config["research_interests"],
                "top_n": self.config["top_n"], "candidate_pool_size": self.config["candidate_limit"],
                "min_score": 0, "ranking": {"backend": "agent", "min_score": 2},
            },
            "automation": {"auto_refresh_indexes": False, "git_commit": False, "git_push": False},
        }
        write_json(work / "daily-config.json", override)
        env = dict(os.environ, DAILYPAPER_CONFIG=str(work / "daily-config.json"),
                   DAILYPAPER_TEMP_DIR=str(work), OBSIDIAN_VAULT_PATH=str(folder),
                   OUTPUT_LANGUAGE="zh")
        script = skill_dir / "_shared/user_config.py"
        if script.exists():
            result = subprocess.run([sys.executable, str(script)], env=env,
                                    capture_output=True, text=True, check=True)
            write_json(work / "effective-config.json", json.loads(result.stdout))
        return folder

    def resolve(self, record):
        p = canonical_record(record)
        identities = [(k, p[k]) for k in ("arxiv_id", "doi") if p[k]]
        self.db.execute("BEGIN IMMEDIATE")
        try:
            keys = {r[0] for kind, ident in identities for r in self.db.execute(
                "SELECT paper_key FROM identifiers WHERE kind=? AND value=?", (kind, ident))}
            if len(keys) > 1:
                raise ValueError("Strong identifier conflict: manual reconciliation required")
            fp = fingerprint(p)
            if not keys and fp:
                candidates = list(self.db.execute("SELECT key,metadata FROM papers WHERE fingerprint=?", (fp,)))
                compatible = []
                for row in candidates:
                    old = json.loads(row["metadata"])
                    if not any(old.get(k) and p[k] and old[k] != p[k] for k in ("arxiv_id", "doi")):
                        compatible.append(row["key"])
                if len(compatible) == 1:
                    keys = {compatible[0]}
                elif len(compatible) > 1:
                    raise ValueError("Ambiguous title/author/year: provide stronger identifiers")
            if keys:
                key = keys.pop()
                old = json.loads(self.db.execute("SELECT metadata FROM papers WHERE key=?", (key,)).fetchone()[0])
                if any(old.get(k) and p[k] and old[k] != p[k] for k in ("arxiv_id", "doi")):
                    raise ValueError("Conflicting arXiv or DOI on existing paper")
                merged = {**old, **{k: v for k, v in p.items() if v not in ("", [], None)}}
                p = merged
                self.db.execute("UPDATE papers SET title=?,fingerprint=?,metadata=?,updated_at=? WHERE key=?",
                                (p["title"], fingerprint(p), json.dumps(p, ensure_ascii=False), now(), key))
            else:
                key = ("arxiv-" + p["arxiv_id"].replace("/", "-") if p["arxiv_id"] else
                       "paper-" + hashlib.sha256((p["doi"] or fp).encode()).hexdigest()[:20])
                self.db.execute("INSERT INTO papers VALUES (?,?,?,?,?,?)",
                                (key, p["title"], fp, json.dumps(p, ensure_ascii=False), now(), now()))
            for kind, ident in identities:
                self.db.execute("INSERT OR IGNORE INTO identifiers VALUES (?,?,?)", (kind, ident, key))
            self.db.commit()
            return key, p
        except Exception:
            self.db.rollback()
            raise

    def inside(self, path):
        path = Path(path).resolve()
        if not path.is_relative_to(self.papers.resolve()):
            raise ValueError("Artifact must resolve inside this project's papers/")
        return path

    def artifact(self, key, kind):
        row = self.db.execute("SELECT * FROM artifacts WHERE paper_key=? AND kind=?", (key, kind)).fetchone()
        if row:
            path = self.inside(self.root / row["path"])
            if path.is_file() and digest(path) == row["sha256"]:
                return path
        return None

    def register(self, key, kind, path):
        path = self.inside(path)
        if not path.is_file():
            raise ValueError("Artifact file missing")
        if kind == "summary":
            text = path.read_text(encoding="utf-8")
            if not all(token in text for token in ("WHY", "HOW", "WHAT", "中文")):
                raise ValueError("Bilingual summary requires WHY/HOW/WHAT and 中文 labels")
            if len(re.findall(r"[a-zA-Z]{2,}", text)) < 80 or len(re.findall(r"[\u3400-\u9fff]", text)) < 80:
                raise ValueError("Summary lacks substantive English/Chinese text")
        checksum = digest(path)
        with self.db:
            previous = self.db.execute(
                "SELECT sha256 FROM artifacts WHERE paper_key=? AND kind=?", (key, kind)).fetchone()
            if kind == "pdf" and previous and previous[0] != checksum:
                # Keep the note on disk, but require review against changed source bytes.
                self.db.execute("DELETE FROM artifacts WHERE paper_key=? AND kind='summary'", (key,))
            self.db.execute("INSERT OR REPLACE INTO artifacts VALUES (?,?,?,?,?)",
                            (key, kind, str(path.relative_to(self.root)), checksum, now()))

    def link(self, source, target):
        source = self.inside(source)
        target = Path(target)
        if target.resolve() == source:
            return
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            # Never replace an unrelated file while reusing a cached artifact.
            if digest(target) != digest(source):
                raise ValueError(f"Existing artifact differs: {target}")
            return
        target.symlink_to(os.path.relpath(source, target.parent))

    def ingest(self, value, records, role):
        folder = self.prepare(value)
        result = []
        for record in records:
            key, p = self.resolve(record)
            paper_dir = folder / key
            paper_dir.mkdir(exist_ok=True)
            with self.db:
                self.db.execute("INSERT OR REPLACE INTO membership VALUES (?,?,?,?)",
                                (self.day(value).isoformat(), key, role, json.dumps(p, ensure_ascii=False)))
            write_json(paper_dir / "metadata.json", p)
            outcome = {"key": key, "directory": str(paper_dir), "role": role}
            try:
                pdf = self.artifact(key, "pdf")
                if pdf:
                    self.link(pdf, paper_dir / "original.pdf")
                    outcome["download"] = "reused"
                else:
                    download_pdf(p["pdf_url"], paper_dir / "original.pdf")
                    self.register(key, "pdf", paper_dir / "original.pdf")
                    outcome["download"] = "downloaded"
                text_path = paper_dir / "original.txt"
                if outcome["download"] == "downloaded" or not text_path.exists():
                    subprocess.run(["pdftotext", "-layout", str(paper_dir / "original.pdf"), str(text_path)],
                                   check=True, capture_output=True, timeout=60)
                summary = self.artifact(key, "summary")
                if summary:
                    self.link(summary, paper_dir / "summary.md")
                    outcome["summary"] = "reused"
                else:
                    outcome["summary"] = "needed"
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                outcome["error"] = str(exc)
            write_json(paper_dir / "ingest.json", outcome)
            result.append(outcome)
        return result

    def relation(self, value, record):
        day = self.day(value).isoformat()
        required = ("source_key", "target_key", "relation_type", "evidence_quote",
                    "locator", "source_url", "rationale_zh")
        if any(not isinstance(record.get(k), str) or not record[k].strip() for k in required):
            raise ValueError("Relation needs identifiers, type, quote, locator, source URL and rationale")
        if record["relation_type"] not in ("based_on", "inspired_by", "method_dependency"):
            raise ValueError("Unknown relationship type")
        if record["source_key"] == record["target_key"]:
            raise ValueError("A paper cannot be its own foundation")
        for key in (record["source_key"], record["target_key"]):
            if not self.db.execute("SELECT 1 FROM membership WHERE run_date=? AND paper_key=?", (day, key)).fetchone():
                raise ValueError("Both relation endpoints must be registered in this run")
        for key, role in ((record["source_key"], "recent"), (record["target_key"], "foundation")):
            if not self.db.execute(
                "SELECT 1 FROM membership WHERE run_date=? AND paper_key=? AND role=?",
                (day, key, role)).fetchone():
                raise ValueError("Relations must point from a recent paper to a foundation")
        targets = {r[0] for r in self.db.execute(
            "SELECT target_key FROM relations WHERE run_date=? AND source_key=?", (day, record["source_key"]))}
        targets.add(record["target_key"])
        if len(targets) > self.config["max_foundations_per_paper"]:
            raise ValueError("Foundation count exceeds the configured per-paper limit")
        original = self.directory(value) / record["source_key"] / "original.txt"
        if not original.exists() or normalize(record["evidence_quote"]) not in normalize(original.read_text(errors="replace")):
            raise ValueError("Evidence quote does not match the locally extracted original")
        existing = [json.loads(r[0]) for r in self.db.execute(
            "SELECT evidence FROM relations WHERE run_date=? AND source_key=?", (day, record["source_key"]))]
        quotes = {r["evidence_quote"] for r in existing if (
            r["target_key"], r["relation_type"]) != (record["target_key"], record["relation_type"])}
        quotes.add(record["evidence_quote"])
        if sum(len(q.split()) for q in quotes) > 25:
            raise ValueError("More than 25 quoted words from one source; shorten excerpts")
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO relations VALUES (?,?,?,?,?)",
                            (day, record["source_key"], record["target_key"], record["relation_type"],
                             json.dumps(record, ensure_ascii=False)))

    def finalize(self, value):
        day = self.day(value).isoformat()
        folder = self.directory(value)
        problems, entries = [], []
        relations = [json.loads(r[0]) for r in self.db.execute(
            "SELECT evidence FROM relations WHERE run_date=?", (day,))]
        rows = self.db.execute(
            "SELECT p.key,p.title,m.role,m.observation FROM membership m JOIN papers p ON p.key=m.paper_key "
            "WHERE run_date=? ORDER BY m.role,p.key", (day,)).fetchall()
        for row in rows:
            key = row["key"]
            entry = {"key": key, "title": row["title"], "role": row["role"],
                     "metadata": json.loads(row["observation"])}
            for kind, filename in (("pdf", "original.pdf"), ("summary", "summary.md")):
                artifact = self.artifact(key, kind)
                target = folder / key / filename
                if artifact:
                    self.link(artifact, target)
                    entry[kind] = str(target.relative_to(folder))
                    entry[f"{kind}_sha256"] = digest(artifact)
                else:
                    problems.append(f"{key}: missing or corrupted {kind}")
            if row["role"] == "recent":
                checked = self.db.execute(
                    "SELECT note FROM foundation_checks WHERE run_date=? AND paper_key=?", (day, key)).fetchone()
                if not checked and not any(r["source_key"] == key for r in relations):
                    problems.append(f"{key}: foundation search not documented")
                if checked:
                    entry["foundation_search"] = checked[0]
            entries.append(entry)
        if not (folder / "README.md").is_file():
            problems.append("Weekly README.md is missing")
        discovery_path = folder / "_work/discovery.json"
        discovery = read_json(discovery_path) if discovery_path.exists() else {}
        if not discovery.get("healthy_sources"):
            problems.append("No successful discovery source; cannot claim an empty week")
        if discovery.get("failed_sources"):
            problems.append("Some discovery sources failed; coverage is partial")
        ranking_path = folder / "_work/daily_papers_ranking.json"
        if not ranking_path.exists() or read_json(ranking_path).get("status") != "complete":
            problems.append("Semantic ranking is incomplete")
        else:
            request_path = folder / "_work/daily_papers_candidates.json"
            report = read_json(ranking_path)
            if not request_path.exists() or report.get("run_id") != read_json(request_path).get("run_id"):
                problems.append("Ranking receipt belongs to a different discovery request")
        selected_path = folder / "_work/daily_papers_selected.json"
        if selected_path.exists():
            for selected in read_json(selected_path):
                identity = arxiv_id(selected.get("url"))
                if identity and not any(e["role"] == "recent" and
                                       e["metadata"].get("arxiv_id") == identity for e in entries):
                    problems.append(f"Selected paper not archived: {identity}")
        status = "partial" if problems else "complete"
        manifest = {"date": day, "status": status, "validated_at": now(),
                    "papers": entries, "relations": relations, "problems": problems}
        write_json(folder / "manifest.json", manifest)
        receipt = read_json(folder / "run.json")
        receipt.update(status=status, finalized_at=now())
        write_json(folder / "run.json", receipt)
        with self.db:
            self.db.execute("UPDATE runs SET status=?,updated_at=? WHERE date=?", (status, now(), day))
        return manifest


def download_pdf(url, destination):
    if urlparse(url).scheme not in ("https", "http"):
        raise ValueError("A public HTTP(S) PDF URL is required")
    destination = Path(destination)
    tmp = None
    try:
        request = Request(url, headers={"User-Agent": "ml-research-weekly/1.0"})
        with urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(
                dir=destination.parent, suffix=".part", delete=False) as output:
            tmp = Path(output.name)
            total = 0
            while block := response.read(1024 * 1024):
                if total == 0 and not block.startswith(b"%PDF-"):
                    raise ValueError("Server returned non-PDF content")
                total += len(block)
                if total > 100 * 1024 * 1024:
                    raise ValueError("PDF exceeds 100 MiB limit")
                output.write(block)
        if not total:
            raise ValueError("Empty PDF response")
        subprocess.run(["pdfinfo", str(tmp)], capture_output=True, check=True, timeout=30)
        # os.replace replaces the symlink itself, never the cached source it points at.
        os.replace(tmp, destination)
    finally:
        if tmp and tmp.exists():
            tmp.unlink()


def fetch_source(url, target, receipts):
    item = {"url": url, "retrieved_at": now()}
    try:
        request = Request(url, headers={"User-Agent": "ml-research-weekly/1.0"})
        with urlopen(request, timeout=30) as response:
            raw = response.read(20 * 1024 * 1024 + 1)
            if len(raw) > 20 * 1024 * 1024:
                raise ValueError("Discovery response exceeds 20 MiB")
            item["http_status"] = response.status
        target.write_bytes(raw)
        item.update(status="ok", raw_file=str(target), sha256=digest(target))
        return raw
    except Exception as exc:
        item.update(status="failed", error=str(exc))
        return None
    finally:
        receipts.append(item)


def discover(archive, value):
    folder = archive.prepare(value)
    work = folder / "_work"
    raw_dir = work / "sources"
    raw_dir.mkdir(exist_ok=True)
    config = archive.config
    day = archive.day(value)
    start = day - timedelta(days=config["days"] - 1)
    receipts, by_id = [], {}

    def add(p, attention=None):
        aid = arxiv_id(p.get("url"))
        if not aid:
            return
        p["keyword_matches"] = keyword_matches(p["title"] + " " + p["abstract"], config["topics"], config["fuzzy"])
        if not p["keyword_matches"]:
            return
        haystack = " " + normalize(p["title"] + " " + p["abstract"]) + " "
        if any(" " + normalize(k) + " " in haystack for k in config["negative_keywords"]):
            return
        previous = by_id.get(aid)
        if previous:
            if attention:
                previous["attention_evidence"].append(attention)
            previous["hf_upvotes"] = max(previous.get("hf_upvotes", 0), p.get("hf_upvotes", 0))
            return
        p["attention_evidence"] = [attention] if attention else []
        p["score"] = len(p["keyword_matches"])
        p["keyword_score"] = p["score"]
        by_id[aid] = p

    dates = [(start + timedelta(days=i)).isoformat() for i in range(config["days"])]
    endpoints = [(d, f"https://huggingface.co/api/daily_papers?date={d}&limit=100") for d in dates]
    if day == archive.day():
        endpoints.append(("trending", "https://huggingface.co/api/daily_papers?sort=trending&limit=100"))
    for label, url in endpoints:
        raw = fetch_source(url, raw_dir / f"hf-{label}.json", receipts)
        if raw is None:
            continue
        try:
            items = json.loads(raw)
            if not isinstance(items, list):
                raise ValueError("HF response is not a paper array")
            for item in items:
                p = item.get("paper", {})
                aid = arxiv_id(p.get("id"))
                if not aid or not p.get("title"):
                    continue
                observed = receipts[-1]["retrieved_at"]
                attention = {"source": "hf-trending" if label == "trending" else "hf-daily",
                             "url": url, "attention_date": day.isoformat() if label == "trending" else label,
                             "observed_at": observed, "hf_upvotes": p.get("upvotes", 0),
                             "raw_file": str((raw_dir / f"hf-{label}.json").relative_to(folder))}
                add({"title": p["title"], "abstract": p.get("summary", ""),
                     "authors": ", ".join(a.get("name", "") if isinstance(a, dict) else str(a)
                                          for a in p.get("authors", [])),
                     "url": f"https://arxiv.org/abs/{aid}", "pdf": f"https://arxiv.org/pdf/{aid}",
                     "date": (p.get("publishedAt") or "")[:10],
                     "source": attention["source"], "hf_upvotes": p.get("upvotes", 0) or 0}, attention)
        except (ValueError, TypeError, AttributeError) as exc:
            receipts[-1].update(status="failed", error=f"Invalid HF payload: {exc}")
    categories = " OR ".join(f"cat:{c}" for c in config["arxiv_categories"])
    query = f"({categories}) AND submittedDate:[{start:%Y%m%d}0000 TO {day:%Y%m%d}2359]"
    url = "https://export.arxiv.org/api/query?" + urlencode({
        "search_query": query, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 500})
    raw = fetch_source(url, raw_dir / "arxiv.xml", receipts)
    if raw:
        try:
            tree = ET.fromstring(raw)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for item in tree.findall("a:entry", ns):
                aid = arxiv_id(item.findtext("a:id", "", ns))
                if not aid:
                    continue
                add({"title": " ".join(item.findtext("a:title", "", ns).split()),
                     "abstract": " ".join(item.findtext("a:summary", "", ns).split()),
                     "authors": ", ".join(a.findtext("a:name", "", ns) for a in item.findall("a:author", ns)),
                     "url": f"https://arxiv.org/abs/{aid}", "pdf": f"https://arxiv.org/pdf/{aid}",
                     "date": item.findtext("a:published", "", ns)[:10], "source": "arxiv", "hf_upvotes": 0})
        except ET.ParseError as exc:
            receipts[-1].update(status="failed", error=f"Invalid arXiv XML: {exc}")
    candidates = sorted(by_id.values(), key=lambda p: (
        bool(p["attention_evidence"]), p.get("hf_upvotes", 0), p["score"]), reverse=True)[:config["candidate_limit"]]
    write_json(work / "discovery.json", {
        "sources": receipts, "healthy_sources": sum(r["status"] == "ok" for r in receipts),
        "failed_sources": sum(r["status"] != "ok" for r in receipts),
        "matched_count": len(by_id), "candidate_count": len(candidates),
        "coverage": "HF daily <=100/day + current trending <=100; arXiv <=500 newest in window"})
    shared = archive.root / config["daily_skills"] / "_shared"
    sys.path.insert(0, str(shared))
    from agent_ranker import prepare_request
    effective = read_json(work / "effective-config.json")["daily_papers"]
    # Rank every recalled candidate before applying weekly attention/quantity limits.
    request = prepare_request(candidates, effective, max(1, len(candidates)))
    request.update(date=day.isoformat(), days=config["days"])
    write_json(work / "daily_papers_candidates.json", request)
    return {"candidates": len(candidates), "output": str(work / "daily_papers_candidates.json")}


def rank(archive, value):
    work = archive.directory(value) / "_work"
    script = archive.root / archive.config["daily_skills"] / "_shared/agent_ranker.py"
    env = dict(os.environ, DAILYPAPER_CONFIG=str(work / "daily-config.json"),
               DAILYPAPER_TEMP_DIR=str(work), OBSIDIAN_VAULT_PATH=str(archive.directory(value)))
    subprocess.run([sys.executable, str(script), str(work / "daily_papers_candidates.json"),
                    str(work / "daily_papers_agent_scores.json"), "--output",
                    str(work / "semantic-selected.json")], check=True, env=env)
    eligible = read_json(work / "semantic-selected.json")
    accepted, excluded = [], []
    end = archive.day(value)
    start = end - timedelta(days=archive.config["days"] - 1)
    for p in eligible:
        evidence = p.get("attention_evidence", [])
        valid = [e for e in evidence if e.get("source") in ("hf-daily", "hf-trending") and
                 (e.get("hf_upvotes") or 0) >= archive.config["min_hf_upvotes"] and
                 start.isoformat() <= e.get("attention_date", "") <= end.isoformat()]
        (accepted if valid else excluded).append(p)
    accepted.sort(key=lambda p: (p.get("agent", {}).get("score", 0), p.get("hf_upvotes", 0),
                                 p.get("keyword_score", 0)), reverse=True)
    selected = accepted[:archive.config["top_n"]]
    write_json(work / "daily_papers_selected.json", selected)
    write_json(work / "attention-excluded.json", excluded)
    write_json(work / "qualified-overflow.json", accepted[archive.config["top_n"]:])
    report_path = work / "daily_papers_ranking.json"
    report = read_json(report_path)
    report.update(selected_count=len(selected), weekly_top_n=archive.config["top_n"],
                  attention_excluded_count=len(excluded), attention_min_votes=archive.config["min_hf_upvotes"],
                  selected_urls=[p["url"] for p in selected])
    write_json(report_path, report)
    return {"selected": len(selected), "attention_excluded": len(excluded)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "discover", "rank", "finalize"):
        sub = commands.add_parser(name)
        sub.add_argument("--date")
    ingest_parser = commands.add_parser("ingest")
    ingest_parser.add_argument("--date")
    ingest_parser.add_argument("--input", type=Path, required=True)
    ingest_parser.add_argument("--role", choices=("recent", "foundation"), required=True)
    relation_parser = commands.add_parser("relation")
    relation_parser.add_argument("--date")
    relation_parser.add_argument("--input", type=Path, required=True)
    summary_parser = commands.add_parser("register-summary")
    summary_parser.add_argument("--key", required=True)
    summary_parser.add_argument("--path", type=Path, required=True)
    check = commands.add_parser("foundation-check")
    check.add_argument("--date")
    check.add_argument("--key", required=True)
    check.add_argument("--note", required=True)
    commands.add_parser("status")
    args = parser.parse_args()
    archive = Archive(args.root)
    try:
        if args.command == "prepare":
            result = {"directory": str(archive.prepare(args.date))}
        elif args.command == "discover":
            result = discover(archive, args.date)
        elif args.command == "rank":
            result = rank(archive, args.date)
        elif args.command == "ingest":
            records = read_json(args.input)
            result = archive.ingest(args.date, records if isinstance(records, list) else [records], args.role)
        elif args.command == "relation":
            records = read_json(args.input)
            for record in records if isinstance(records, list) else [records]:
                archive.relation(args.date, record)
            result = {"registered": True}
        elif args.command == "register-summary":
            archive.register(args.key, "summary", args.path)
            result = {"registered": True}
        elif args.command == "foundation-check":
            with archive.db:
                archive.db.execute("INSERT OR REPLACE INTO foundation_checks VALUES (?,?,?)",
                                   (archive.day(args.date).isoformat(), args.key, args.note))
            result = {"registered": True}
        elif args.command == "finalize":
            result = archive.finalize(args.date)
        else:
            result = {"papers": archive.db.execute("SELECT count(*) FROM papers").fetchone()[0],
                      "runs": [dict(row) for row in archive.db.execute("SELECT * FROM runs ORDER BY date DESC")]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.command == "finalize" and result["status"] != "complete" else 0
    finally:
        archive.close()


if __name__ == "__main__":
    raise SystemExit(main())
