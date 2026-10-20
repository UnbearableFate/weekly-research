#!/usr/bin/env python3
"""Install this project's Friday timer in the current user's systemd manager."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

from weekly_papers import ROOT, read_json


def quoted(value):
    # systemd ExecStart/WorkingDirectory quoting; escape specifier expansion too.
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Write and enable the user timer")
    args = parser.parse_args()
    config = read_json(ROOT / "weekly-papers.json")
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is unavailable on PATH")
    name = "ml-research-weekly-papers"
    service = f"""[Unit]
Description=Weekly papers: bilingual summaries and methodological foundations

[Service]
Type=oneshot
WorkingDirectory={str(ROOT).replace('%', '%%')}
Environment="PATH={Path(uv).parent}:/usr/local/bin:/usr/bin:/bin"
Environment="TZ={config['timezone']}"
ExecStart={quoted(uv)} run --project {quoted(ROOT)} python {quoted(ROOT / 'scripts/run_weekly_papers.py')}
TimeoutStartSec=4h
KillMode=control-group
"""
    timer = f"""[Unit]
Description=Weekly paper research on Friday at 17:00 {config['timezone']}

[Timer]
OnCalendar={config['schedule']}:00 {config['timezone']}
Persistent=true
AccuracySec=1s
Unit={name}.service

[Install]
WantedBy=timers.target
"""
    folder = ROOT / "automation"
    folder.mkdir(exist_ok=True)
    for suffix, content in (("service", service), ("timer", timer)):
        (folder / f"{name}.{suffix}").write_text(content)
    subprocess.run(["systemd-analyze", "--user", "verify", str(folder / f"{name}.service"),
                    str(folder / f"{name}.timer")], check=True)
    if not args.install:
        print(f"Validated unit files in {folder}; pass --install to enable.")
        return
    destination = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "systemd/user"
    destination.mkdir(parents=True, exist_ok=True)
    for suffix in ("service", "timer"):
        source = folder / f"{name}.{suffix}"
        target = destination / source.name
        # Idempotent installation of this task's exact named units only.
        target.write_text(source.read_text())
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", f"{name}.timer"], check=True)
    subprocess.run(["systemctl", "--user", "list-timers", f"{name}.timer", "--no-pager"], check=True)


if __name__ == "__main__":
    main()
