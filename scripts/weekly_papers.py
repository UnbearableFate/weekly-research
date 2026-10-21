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
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote, urlencode, unquote, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ARXIV = re.compile(r"(?<!\w)(\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7})(?:v\d+)?", re.I)
MAX_FILENAME_BYTES = 240
MAX_ENGLISH_WORDS = 100


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


def filename_identity(name):
    """Compare names conservatively on case-insensitive, normalization-aware disks."""
    return unicodedata.normalize("NFD", name).casefold()


def pdf_filename(title, suffix=""):
    title = unicodedata.normalize("NFC", title)
    title = "".join(" - " if c in '<>:"/\\|?*' else
                    " " if unicodedata.category(c).startswith("C") else c for c in title)
    title = " ".join(title.split()).strip(" .") or "Untitled paper"
    ending = suffix + ".pdf"
    while any(len(unicodedata.normalize(form, title + ending).encode("utf-8")) > MAX_FILENAME_BYTES
              for form in ("NFC", "NFD")):
        title = title[:-1]
    return title.rstrip(" .") + ending


def materialize(source, target):
    """Place a real PDF file atomically, reusing disk blocks when hard links work."""
    source, target = Path(source), Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and not target.is_symlink() and digest(source) == digest(target):
        return
    handle, name = tempfile.mkstemp(dir=target.parent, suffix=".part")
    os.close(handle)
    tmp = Path(name)
    try:
        tmp.unlink()
        try:
            os.link(source, tmp)
        except OSError:
            shutil.copyfile(source, tmp)
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()


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
            CREATE TABLE IF NOT EXISTS run_files(
                run_date TEXT NOT NULL REFERENCES runs(date),
                paper_key TEXT NOT NULL REFERENCES papers(key),
                filename TEXT NOT NULL, normalized_filename TEXT NOT NULL,
                PRIMARY KEY(run_date,paper_key), UNIQUE(run_date,normalized_filename));
            CREATE TABLE IF NOT EXISTS exclusions(
                run_date TEXT NOT NULL REFERENCES runs(date),
                paper_key TEXT NOT NULL REFERENCES papers(key), role TEXT NOT NULL,
                reason TEXT NOT NULL, PRIMARY KEY(run_date,paper_key,role));
        """)

    def close(self):
        self.db.close()

    def day(self, value=None):
        return date.fromisoformat(value) if value else datetime.now(
            ZoneInfo(self.config["timezone"])).date()

    def directory(self, value=None):
        return self.papers / self.day(value).strftime(self.config["date_format"])

    def run_state(self, value=None):
        return self.state / "runs" / self.day(value).strftime(self.config["date_format"])

    def work(self, value=None):
        return self.run_state(value) / "work"

    def prepare(self, value=None):
        day = self.day(value)
        folder = self.directory(value)
        if (folder / "run.json").exists():
            raise ValueError("Historical archive uses the previous layout; use a new run date")
        folder.mkdir(parents=True, exist_ok=True)
        work = self.work(value)
        work.mkdir(parents=True, exist_ok=True)
        receipt = self.run_state(value) / "run.json"
        if receipt.exists() and read_json(receipt)["date"] != day.isoformat():
            raise ValueError("Date-directory collision")
        if not receipt.exists():
            write_json(receipt, {
                "date": day.isoformat(), "timezone": self.config["timezone"],
                "window_start": (day - timedelta(days=self.config["days"] - 1)).isoformat(),
                "window_end": day.isoformat(), "created_at": now(),
                "requested_model": self.config["model"],
                "requested_reasoning_effort": self.config["reasoning_effort"],
                "status": "prepared", "config": self.config, "layout": "weekly-brief-v1",
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
        if kind != "pdf":
            raise ValueError("Use the report command for weekly summaries")
        path = self.inside(path)
        if not path.is_file():
            raise ValueError("Artifact file missing")
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO artifacts VALUES (?,?,?,?,?)",
                            (key, kind, str(path.relative_to(self.root)), digest(path), now()))

    def allocate_filename(self, value, key, title):
        day = self.day(value).isoformat()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT filename FROM run_files WHERE run_date=? AND paper_key=?", (day, key)).fetchone()
            if existing:
                self.db.commit()
                return existing[0]
            occupied = {filename_identity(p.name) for p in self.directory(value).iterdir()}
            occupied.update(r[0] for r in self.db.execute(
                "SELECT normalized_filename FROM run_files WHERE run_date=?", (day,)))
            name = pdf_filename(title)
            counter = 0
            tag = hashlib.sha256(key.encode()).hexdigest()[:10]
            while filename_identity(name) in occupied:
                counter += 1
                suffix = f" [{tag}]" if counter == 1 else f" [{tag}-{counter}]"
                name = pdf_filename(title, suffix)
            self.db.execute("INSERT INTO run_files VALUES (?,?,?,?)",
                            (day, key, name, filename_identity(name)))
            self.db.commit()
            return name
        except Exception:
            self.db.rollback()
            raise

    def entries(self, value):
        rows = self.db.execute(
            "SELECT m.paper_key,m.observation,f.filename FROM membership m "
            "LEFT JOIN run_files f ON f.run_date=m.run_date AND f.paper_key=m.paper_key "
            "WHERE m.run_date=? AND m.role='recent' ORDER BY m.rowid",
            (self.day(value).isoformat(),)).fetchall()
        return [{"key": r["paper_key"], "title": json.loads(r["observation"])["title"],
                 "metadata": json.loads(r["observation"]), "pdf": r["filename"]} for r in rows]

    def ingest(self, value, records, role="recent"):
        if role != "recent":
            raise ValueError("Only selected recent-attention papers are collected")
        folder = self.prepare(value)
        result = []
        for record in records:
            key, p = self.resolve(record)
            with self.db:
                self.db.execute("INSERT OR REPLACE INTO membership VALUES (?,?,?,?)",
                                (self.day(value).isoformat(), key, role, json.dumps(p, ensure_ascii=False)))
                self.db.execute("DELETE FROM exclusions WHERE run_date=? AND paper_key=? AND role=?",
                                (self.day(value).isoformat(), key, role))
            filename = self.allocate_filename(value, key, p["title"])
            cache = self.state / "papers" / key
            cache.mkdir(parents=True, exist_ok=True)
            write_json(cache / "metadata.json", p)
            outcome = {"key": key, "pdf": str(folder / filename), "filename": filename,
                       "text": str(cache / "original.txt")}
            try:
                original = cache / "original.pdf"
                pdf = self.artifact(key, "pdf")
                if pdf:
                    materialize(pdf, original)
                    outcome["download"] = "reused"
                else:
                    download_pdf(p["pdf_url"], original)
                    outcome["download"] = "downloaded"
                self.register(key, "pdf", original)
                checksum = digest(original)
                extraction = cache / "extraction.json"
                text_path = cache / "original.txt"
                if (not text_path.exists() or not extraction.exists()
                        or read_json(extraction).get("pdf_sha256") != checksum):
                    subprocess.run(["pdftotext", "-layout", str(original), str(text_path)],
                                   check=True, capture_output=True, timeout=60)
                    write_json(extraction, {"pdf_sha256": checksum, "extracted_at": now()})
                materialize(original, folder / filename)
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                outcome["error"] = str(exc)
            write_json(self.work(value) / "ingest" / f"{key}.json", outcome)
            result.append(outcome)
        return result

    def exclude(self, value, key, role, reason):
        """Withdraw a selection, keeping its cache and any previous visible copy."""
        if role != "recent" or not reason.strip():
            raise ValueError("Exclude requires a recent selection and a reason")
        day = self.day(value).isoformat()
        assigned = self.db.execute(
            "SELECT filename FROM run_files WHERE run_date=? AND paper_key=?", (day, key)).fetchone()
        if assigned:
            source = self.directory(value) / assigned[0]
            if source.exists():
                excluded = self.run_state(value) / "excluded"
                excluded.mkdir(exist_ok=True)
                destination = excluded / f"{key}-{datetime.now(timezone.utc):%H%M%S%f}.pdf"
                source.rename(destination)
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO exclusions VALUES (?,?,?,?)", (day, key, role, reason))
            self.db.execute("DELETE FROM membership WHERE run_date=? AND paper_key=? AND role=?", (day, key, role))

    def render_report(self, value, records):
        if not isinstance(records, list):
            raise ValueError("Briefs must be a JSON array")
        entries = {p["key"]: p for p in self.entries(value)}
        keys = [r.get("key") for r in records]
        if len(keys) != len(set(keys)) or set(keys) != set(entries):
            raise ValueError("Provide exactly one brief per included paper")
        blocks, receipt = [], []
        for record in records:
            entry = entries[record["key"]]
            values = {}
            for name in ("why_en", "how_en", "why_zh", "how_zh"):
                value_text = record.get(name)
                if not isinstance(value_text, str) or not value_text.strip():
                    raise ValueError(f"{record['key']}: missing {name}")
                values[name] = value_text.strip()
                if "\n" in values[name] or "\r" in values[name]:
                    raise ValueError(f"{record['key']}: {name} must be a single concise paragraph")
            english_words = len((values["why_en"] + " " + values["how_en"]).split())
            if english_words > MAX_ENGLISH_WORDS:
                raise ValueError(f"{record['key']}: WHY + HOW has {english_words} English words; maximum 100")
            if not all(re.search(r"[A-Za-z]", values[n]) for n in ("why_en", "how_en")):
                raise ValueError("English WHY and HOW are required")
            if not all(re.search(r"[\u3400-\u9fff]", values[n]) for n in ("why_zh", "how_zh")):
                raise ValueError("Chinese WHY and HOW are required")
            uploaded = record.get("published_at", "")
            if date.fromisoformat(uploaded).isoformat() != uploaded:
                raise ValueError("Use an ISO YYYY-MM-DD first-upload date")
            if uploaded != entry["metadata"].get("published_at", "")[:10]:
                raise ValueError(f"{record['key']}: upload date disagrees with registered metadata")
            if not entry["pdf"]:
                raise ValueError(f"{record['key']}: PDF filename is missing")
            pdf = self.directory(value) / entry["pdf"]
            artifact = self.artifact(record["key"], "pdf")
            if not artifact or not pdf.is_file() or pdf.is_symlink() or digest(pdf) != digest(artifact):
                raise ValueError(f"{record['key']}: missing or corrupted original PDF")
            title = entry["title"].replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
            blocks.append(
                f"## [{title}]({quote(entry['pdf'])})\n\n"
                f"上传日期：{uploaded}\n\n"
                f"**WHY (EN):** {values['why_en']}\n\n"
                f"**HOW (EN):** {values['how_en']}\n\n"
                f"**WHY（中文）：** {values['why_zh']}\n\n"
                f"**HOW（中文）：** {values['how_zh']}\n")
            receipt.append({"key": record["key"], "pdf": entry["pdf"],
                            "pdf_sha256": digest(pdf), "published_at": uploaded,
                            "english_words": english_words})
        return ("\n".join(blocks) if blocks else "本周没有符合筛选条件的论文。\n"), receipt

    def report(self, value, records):
        content, entries = self.render_report(value, records)
        path = self.directory(value) / "README.md"
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False, suffix=".tmp") as output:
            output.write(content)
            temporary = output.name
        os.replace(temporary, path)
        write_json(self.work(value) / "briefs.json", records)
        write_json(self.run_state(value) / "report.json", {
            "generated_at": now(), "sha256": digest(path), "papers": entries})
        return {"report": str(path), "papers": len(entries),
                "max_english_words": max((r["english_words"] for r in entries), default=0)}

    def finalize(self, value):
        day = self.day(value).isoformat()
        folder, work, run_state = self.directory(value), self.work(value), self.run_state(value)
        problems, entries = [], self.entries(value)
        exclusions = [dict(r) for r in self.db.execute(
            "SELECT paper_key,role,reason FROM exclusions WHERE run_date=?", (day,))]
        for entry in entries:
            pdf = folder / entry["pdf"] if entry["pdf"] else None
            original = self.artifact(entry["key"], "pdf")
            if (not original or not pdf or not pdf.is_file() or pdf.is_symlink()
                    or digest(original) != digest(pdf)):
                problems.append(f"{entry['key']}: missing or corrupted original PDF")
            else:
                entry["pdf_sha256"] = digest(pdf)
        report_path = folder / "README.md"
        report_receipt = run_state / "report.json"
        briefs_path = work / "briefs.json"
        if not report_path.is_file() or not report_receipt.is_file() or not briefs_path.is_file():
            problems.append("Weekly report or its validation receipt is missing")
        else:
            try:
                expected, details = self.render_report(value, read_json(briefs_path))
                recorded = read_json(report_receipt)
                if report_path.read_text(encoding="utf-8") != expected or digest(report_path) != recorded["sha256"]:
                    problems.append("Weekly report differs from the validated concise format")
                if details != recorded["papers"]:
                    problems.append("Weekly report metadata or original PDF changed; review and regenerate")
            except (ValueError, TypeError, KeyError, OSError) as exc:
                problems.append(f"Invalid weekly brief: {exc}")
        allowed = {e["pdf"] for e in entries} | {"README.md"}
        if folder.exists():
            unexpected = sorted(p.name for p in folder.iterdir() if p.name not in allowed)
            if unexpected:
                problems.append("Unexpected files in weekly directory: " + ", ".join(unexpected))
        discovery_path = work / "discovery.json"
        discovery = read_json(discovery_path) if discovery_path.exists() else {}
        if not discovery.get("healthy_sources"):
            problems.append("No successful discovery source; cannot claim an empty week")
        if discovery.get("failed_sources"):
            problems.append("Some discovery sources failed; coverage is partial")
        ranking_path = work / "daily_papers_ranking.json"
        if not ranking_path.exists() or read_json(ranking_path).get("status") != "complete":
            problems.append("Semantic ranking is incomplete")
        else:
            request_path = work / "daily_papers_candidates.json"
            ranking = read_json(ranking_path)
            if not request_path.exists() or ranking.get("run_id") != read_json(request_path).get("run_id"):
                problems.append("Ranking receipt belongs to a different discovery request")
        selected_path = work / "daily_papers_selected.json"
        if not selected_path.exists():
            problems.append("Selected-paper list is missing")
        else:
            selected_ids = {arxiv_id(s.get("url")) for s in read_json(selected_path)}
            for identity in selected_ids:
                if identity and not any(e["metadata"].get("arxiv_id") == identity for e in entries):
                    alias = self.db.execute(
                        "SELECT paper_key FROM identifiers WHERE kind='arxiv_id' AND value=?", (identity,)).fetchone()
                    if not alias or not any(e["paper_key"] == alias[0] for e in exclusions):
                        problems.append(f"Selected paper not archived: {identity}")
            for entry in entries:
                if entry["metadata"].get("arxiv_id") not in selected_ids:
                    problems.append(f"Unselected paper in weekly report: {entry['key']}")
        status = "partial" if problems else "complete"
        manifest = {"date": day, "status": status, "validated_at": now(), "layout": "weekly-brief-v1",
                    "report": "README.md", "papers": entries, "exclusions": exclusions, "problems": problems}
        write_json(run_state / "manifest.json", manifest)
        receipt_path = run_state / "run.json"
        if receipt_path.exists():
            receipt = read_json(receipt_path)
            receipt.update(status=status, finalized_at=now())
            write_json(receipt_path, receipt)
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
    work = archive.work(value)
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
                             "raw_file": str((raw_dir / f"hf-{label}.json").relative_to(archive.root))}
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
    work = archive.work(value)
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
    ingest_parser.add_argument("--role", choices=("recent",), required=True)
    report_parser = commands.add_parser("report")
    report_parser.add_argument("--date")
    report_parser.add_argument("--input", type=Path, required=True)
    exclusion = commands.add_parser("exclude")
    exclusion.add_argument("--date")
    exclusion.add_argument("--key", required=True)
    exclusion.add_argument("--role", choices=("recent",), required=True)
    exclusion.add_argument("--reason", required=True)
    commands.add_parser("status")
    args = parser.parse_args()
    archive = Archive(args.root)
    try:
        if args.command == "prepare":
            result = {"directory": str(archive.prepare(args.date)),
                      "work": str(archive.work(args.date)), "state": str(archive.run_state(args.date))}
        elif args.command == "discover":
            result = discover(archive, args.date)
        elif args.command == "rank":
            result = rank(archive, args.date)
        elif args.command == "ingest":
            records = read_json(args.input)
            result = archive.ingest(args.date, records if isinstance(records, list) else [records], args.role)
        elif args.command == "report":
            result = archive.report(args.date, read_json(args.input))
        elif args.command == "exclude":
            archive.exclude(args.date, args.key, args.role, args.reason)
            result = {"excluded": args.key, "role": args.role, "cached_artifacts_preserved": True}
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
