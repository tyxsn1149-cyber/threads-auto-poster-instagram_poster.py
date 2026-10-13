#!/usr/bin/env python3
"""Delete old social-post media from this repository.

Retention is based on the first Git commit that added each eligible media file.
Only recognized post-media filenames are eligible; source code, workflows,
README files, and other assets are never removed.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

RETENTION_DAYS = 10
MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}

POST_MEDIA_PATTERNS = (
    re.compile(r"^ig\d{3}(?:[-_].*)?\.(?:jpg|jpeg|png|webp|mp4|mov)$", re.I),
    re.compile(r"^nurse-(?:career|workplace|shift|relations)-\d+\.(?:jpg|jpeg|png|webp)$", re.I),
    re.compile(r"^threads-\d{8}\.(?:jpg|jpeg|png|webp|mp4|mov)$", re.I),
)

EXCLUDED_TOP_LEVEL = {".git", ".github"}


def is_post_media(path: Path) -> bool:
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        return False
    if any(part in EXCLUDED_TOP_LEVEL for part in path.parts):
        return False
    return any(pattern.match(path.name) for pattern in POST_MEDIA_PATTERNS)


def first_added_at(path: Path) -> datetime | None:
    result = subprocess.run(
        [
            "git",
            "log",
            "--diff-filter=A",
            "--follow",
            "--format=%aI",
            "--reverse",
            "--",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    parsed = datetime.fromisoformat(lines[0].replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def find_expired(root: Path, now: datetime) -> list[tuple[Path, datetime]]:
    cutoff = now - timedelta(days=RETENTION_DAYS)
    expired: list[tuple[Path, datetime]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if not is_post_media(relative):
            continue
        added_at = first_added_at(relative)
        if added_at is None:
            print(f"SKIP no git add timestamp: {relative}")
            continue
        if added_at <= cutoff:
            expired.append((relative, added_at))
    return expired


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    now = datetime.now(timezone.utc)
    expired = find_expired(root, now)

    print(f"Retention: {RETENTION_DAYS} days")
    print(f"Expired media: {len(expired)}")

    for relative, added_at in expired:
        print(f"DELETE {relative} (added {added_at.isoformat()})")
        if not args.dry_run:
            (root / relative).unlink()

    if args.dry_run:
        print("Dry run only; no files deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
