#!/usr/bin/env python3
"""Build the static site and Sphinx docs into dist/."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    site_dir = repo_root / "site"
    docs_dir = repo_root / "docs"
    dist_dir = repo_root / "dist"
    docs_out_dir = dist_dir / "docs"

    if not site_dir.is_dir():
        raise FileNotFoundError(f"missing site directory: {site_dir}")
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"missing docs directory: {docs_dir}")

    shutil.rmtree(dist_dir, ignore_errors=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(site_dir, dist_dir, dirs_exist_ok=True)
    (dist_dir / ".nojekyll").write_text("", encoding="utf-8")

    subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html", str(docs_dir), str(docs_out_dir)],
        check=True,
        cwd=repo_root,
    )

    print(f"Built site in {dist_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
