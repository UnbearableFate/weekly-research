#!/usr/bin/env python3
"""Run the configured weekly research workflow in an unattended Codex session."""
import argparse
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
from zoneinfo import ZoneInfo

from weekly_papers import Archive, ROOT, now, read_json, write_json


def command(root, config, final_path):
    codex = shutil.which("codex")
    if not codex:
        raise RuntimeError("Codex CLI is unavailable on PATH")
    return [
        codex, "--search", "-a", "never", "exec", "--model", config["model"],
        "-c", f'model_reasoning_effort="{config["reasoning_effort"]}"',
        "--sandbox", "workspace-write",
        "-c", "sandbox_workspace_write.network_access=true",
        "-C", str(root), "--json", "--output-last-message", str(final_path), "-",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date")
    parser.add_argument("--dry-run", action="store_true", help="Inspect launch configuration without model execution")
    args = parser.parse_args()
    config = read_json(ROOT / "weekly-papers.json")
    archive = Archive()
    day = archive.day(args.date).isoformat()
    logs = archive.state / "logs"
    logs.mkdir(exist_ok=True)
    stamp = datetime.now(ZoneInfo(config["timezone"])).strftime("%Y%m%d-%H%M%S-%f")
    final = logs / f"{stamp}.final.txt"
    argv = command(ROOT, config, final)
    if args.dry_run:
        print(json.dumps({"date": day, "argv": argv, "timezone": config["timezone"],
                          "workflow": str(ROOT / "workflows/weekly-papers.md")}, indent=2))
        archive.close()
        return 0
    with (archive.state / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another weekly research run is active; this invocation was skipped.", file=sys.stderr)
            archive.close()
            return 0
        folder = archive.prepare(day)
        execution = {
            "started_at": now(), "date": day, "mechanism": "codex-exec",
            "requested_model": config["model"], "requested_reasoning_effort": config["reasoning_effort"],
            "argv": argv, "status": "running",
            "events": str((logs / f"{stamp}.jsonl").relative_to(ROOT)),
            "stderr": str((logs / f"{stamp}.stderr.log").relative_to(ROOT)),
            "final_message": str(final.relative_to(ROOT)),
        }
        write_json(folder / "execution.json", execution)
        prompt = (
            f"Execute the authorized weekly paper research for run date {day} (Asia/Shanghai) "
            f"in {ROOT}. Read workflows/weekly-papers.md and weekly-papers.json, then execute all "
            "stages through archive validation. The workflow instructions are English; every paper "
            "summary must pair English first, then Chinese in each corresponding section. "
            "Use the selected daily-papers and academic-research-suite subworkflows. "
            "The configured research scope is LLM optimizers, distributed learning, PEFT, continual "
            "learning. You are the sole research executor; do not delegate or substitute models. "
            "Use the existing scripts, modify only papers/, preserve failures and partial results, "
            "and do not change scripts, schedules, skills or user configuration. "
            "Do not send notifications or messages, publish, commit/push, inspect credentials or "
            "launch separate model APIs. Finish this run without requesting routine confirmation."
        )
        env = dict(os.environ, TZ=config["timezone"], OUTPUT_LANGUAGE="zh")
        child = None

        def stop(signum, _frame):
            if child and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
            raise InterruptedError(f"Runner received signal {signum}")

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        try:
            with (logs / f"{stamp}.jsonl").open("w") as stdout, (
                logs / f"{stamp}.stderr.log"
            ).open("w") as stderr:
                child = subprocess.Popen(argv, cwd=ROOT, env=env, stdin=subprocess.PIPE,
                                         stdout=stdout, stderr=stderr, text=True, start_new_session=True)
                child.communicate(prompt, timeout=4 * 60 * 60)
            execution["exit_code"] = child.returncode
            if child.returncode:
                raise RuntimeError(f"Codex exited with code {child.returncode}; see local logs")
            manifest = archive.finalize(day)
            execution["status"] = manifest["status"]
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            if child and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            execution.update(status="failed", error=str(exc))
        finally:
            execution["finished_at"] = now()
            write_json(folder / "execution.json", execution)
            archive.close()
        print(json.dumps(execution, ensure_ascii=False, indent=2))
        return 0 if execution["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
