"""Regression checks for identity, fuzzy recall, recovery and evidence boundaries."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/weekly_papers.py"
spec = importlib.util.spec_from_file_location("weekly", SCRIPT)
weekly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weekly)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = weekly.read_json(SCRIPT.parents[1] / "weekly-papers.json")
        self.store = weekly.Archive(self.root, self.config)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def record(self, **changes):
        return {"title": "Memory-efficient LLM Optimization", "authors": ["A. Researcher"],
                "year": 2026, **changes}

    def test_arxiv_versions_doi_and_title_alias_reuse(self):
        first, _ = self.store.resolve(self.record(arxiv_id="https://arxiv.org/abs/2610.12345v1"))
        second, _ = self.store.resolve(self.record(arxiv_id="2610.12345v3", doi="https://doi.org/10.1234/ABC"))
        third, _ = self.store.resolve(self.record(doi="DOI:10.1234/abc"))
        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM papers").fetchone()[0], 1)
        self.assertEqual(weekly.arxiv_id("https://arxiv.org/pdf/cs/9901001v2.pdf"), "cs/9901001")

    def test_same_title_other_author_is_distinct(self):
        one, _ = self.store.resolve(self.record())
        two, _ = self.store.resolve(self.record(authors=["Another Author"]))
        self.assertNotEqual(one, two)

    def test_conflicting_strong_ids_do_not_merge(self):
        one, _ = self.store.resolve(self.record(arxiv_id="2610.12345"))
        two, _ = self.store.resolve(self.record(arxiv_id="2610.54321", doi="10.1234/other"))
        self.assertNotEqual(one, two)
        with self.assertRaisesRegex(ValueError, "conflict"):
            self.store.resolve(self.record(arxiv_id="2610.12345", doi="10.1234/other"))
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM papers").fetchone()[0], 2)

    def test_missing_or_corrupt_artifact_is_not_reused(self):
        key, _ = self.store.resolve(self.record(arxiv_id="2610.12345"))
        path = self.store.papers / "source.pdf"
        path.write_bytes(b"%PDF-1.7 original")
        self.store.register(key, "pdf", path)
        self.assertEqual(self.store.artifact(key, "pdf"), path)
        path.write_bytes(b"corrupted")
        self.assertIsNone(self.store.artifact(key, "pdf"))
        path.unlink()
        self.assertIsNone(self.store.artifact(key, "pdf"))

    def test_failed_download_remains_retryable(self):
        with patch.object(weekly, "download_pdf", side_effect=OSError("network failure")):
            result = self.store.ingest("2026-10-20", [self.record(arxiv_id="2610.12345")], "recent")
        self.assertIn("error", result[0])
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM artifacts").fetchone()[0], 0)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM membership").fetchone()[0], 1)

    def test_cross_week_reuses_without_download(self):
        key, _ = self.store.resolve(self.record(arxiv_id="2610.12345"))
        old = self.store.papers / "261016" / key
        old.mkdir(parents=True)
        path = old / "original.pdf"
        path.write_bytes(b"%PDF-1.7 reused")
        self.store.register(key, "pdf", path)
        with patch.object(weekly, "download_pdf") as download, patch.object(weekly.subprocess, "run"):
            result = self.store.ingest("2026-10-23", [self.record(arxiv_id="2610.12345v2")], "recent")
        download.assert_not_called()
        self.assertEqual(result[0]["download"], "reused")
        visible = Path(result[0]["pdf"])
        self.assertEqual(visible.parent, self.store.papers / "261023")
        self.assertFalse(visible.is_symlink())
        self.assertEqual(visible.read_bytes(), path.read_bytes())

    def test_full_text_exclusion_preserves_cached_original(self):
        self.store.prepare("2026-10-20")
        key, _ = self.store.resolve(self.record(arxiv_id="2610.12345"))
        path = self.store.papers / "cached.pdf"
        path.write_bytes(b"%PDF-1.7 preserved")
        self.store.register(key, "pdf", path)
        with self.store.db:
            self.store.db.execute("INSERT INTO membership VALUES (?,?,?,?)",
                                  ("2026-10-20", key, "recent", "{}"))
        self.store.exclude("2026-10-20", key, "recent", "Full text is outside the configured interests.")
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM membership").fetchone()[0], 0)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM exclusions").fetchone()[0], 1)
        self.assertEqual(self.store.artifact(key, "pdf"), path)

    def test_empty_failed_discovery_never_completes(self):
        folder = self.store.prepare("2026-10-20")
        (folder / "README.md").write_text("No reliable source response.")
        work = self.store.work("2026-10-20")
        weekly.write_json(work / "discovery.json", {"healthy_sources": 0, "failed_sources": 9})
        weekly.write_json(work / "daily_papers_candidates.json", {"run_id": "new"})
        weekly.write_json(work / "daily_papers_ranking.json", {"run_id": "new", "status": "complete"})
        result = self.store.finalize("2026-10-20")
        self.assertEqual(result["status"], "partial")
        self.assertTrue(any("No successful discovery" in x for x in result["problems"]))

    def test_stale_ranking_receipt_never_completes(self):
        folder = self.store.prepare("2026-10-20")
        (folder / "README.md").write_text("Nothing selected.")
        work = self.store.work("2026-10-20")
        weekly.write_json(work / "discovery.json", {"healthy_sources": 9, "failed_sources": 0})
        weekly.write_json(work / "daily_papers_candidates.json", {"run_id": "new"})
        weekly.write_json(work / "daily_papers_ranking.json", {"run_id": "old", "status": "complete"})
        result = self.store.finalize("2026-10-20")
        self.assertEqual(result["status"], "partial")
        self.assertIn("Ranking receipt belongs to a different discovery request", result["problems"])


class RecallTests(unittest.TestCase):
    def test_hyphens_case_and_long_word_typo(self):
        topics = {"PEFT": ["parameter efficient fine tuning"], "Optimizer": ["optimizer"]}
        hits = weekly.keyword_matches("Parameter-efficient fine-tuning uses an optimzer", topics,
                                      {"enabled": True, "threshold": 0.88, "min_token_length": 5})
        self.assertEqual({h["topic"] for h in hits}, {"PEFT", "Optimizer"})
        self.assertTrue(any(h["similarity"] < 1 for h in hits))

    def test_short_acronym_is_not_fuzzy_or_substring(self):
        topics = {"PEFT": ["PEFT", "LoRA"]}
        self.assertEqual(weekly.keyword_matches("deft floral exploration", topics,
                                               {"enabled": True, "threshold": 0.88}), [])
        self.assertEqual(len(weekly.keyword_matches("LoRA and PEFT", topics, {})), 2)

    def test_fuzzy_can_be_disabled(self):
        self.assertEqual(weekly.keyword_matches("optimzer", {"optimizer": ["optimizer"]},
                                               {"enabled": False}), [])


if __name__ == "__main__":
    unittest.main()
