#!/usr/bin/env python3
"""Batch upload MapX vectors described by geonode_title,local_source CSV.

Uses the existing upload_vector.sh function without reimplementing the API.
"""
import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys

PROJECT_ID = "MX-WLW-9SS-3MJ-2NY-EYF"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path(__file__).with_name("publication_catalog_vjuani.csv"))
    parser.add_argument("--data-root", type=Path, default=Path.cwd(),
                        help="Directory containing database/gpkg/... (default: current directory)")
    parser.add_argument("--uploader", type=Path, default=Path(__file__).with_name("upload_vector.sh"))
    parser.add_argument("--host", default="https://api.mapx.org", help="MapX API URL")
    parser.add_argument("--project", default=PROJECT_ID)
    parser.add_argument("--limit", type=int, help="Upload only the first N CSV records (pilot)")
    parser.add_argument("--dry-run", action="store_true", help="Show upload plan without contacting MapX")
    parser.add_argument("--skip-missing", action="store_true", help="Continue past nonexistent files")
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive number")
    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")
    if not args.dry_run and not args.uploader.is_file():
        parser.error(f"Uploader not found: {args.uploader}")
    if not args.dry_run:
        for key in ("MAPX_USER", "MAPX_TOKEN"):
            if not os.environ.get(key):
                parser.error(f"{key} must be set in the environment")

    with args.csv.open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        required = {"geonode_title", "local_source"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            parser.error(f"CSV must contain columns: {', '.join(sorted(required))}")
        rows = list(reader)
    if args.limit:
        rows = rows[:args.limit]

    successes = failures = missing = 0
    for index, row in enumerate(rows, start=1):
        title = (row.get("geonode_title") or "").strip()
        relative = (row.get("local_source") or "").strip()
        if not title or not relative:
            print(f"[{index}/{len(rows)}] ERROR: blank title/path", file=sys.stderr, flush=True)
            failures += 1
            continue
        source = Path(relative)
        if not source.is_absolute():
            source = args.data_root / source
        source = source.resolve()
        print(f"[{index}/{len(rows)}] {title}\n  File: {source}", flush=True)
        if not source.is_file():
            print("  MISSING: file not found", file=sys.stderr, flush=True)
            missing += 1
            if not args.skip_missing and not args.dry_run:
                print("Stopping; check --data-root (or use --skip-missing).", file=sys.stderr)
                break
            continue
        if args.dry_run:
            successes += 1
            continue

        # Positional arguments keep filenames/titles safe, including spaces and quotes.
        cmd = ["bash", "-c", 'source "$1"; shift; upload_mapx "$@"',
               "batch-mapx", str(args.uploader.resolve()),
               "--host", args.host, "--project", args.project,
               "--create-view", "--enable-wms", "--enable-download",
               "--title", title, str(source)]
        try:
            result = subprocess.run(cmd, check=False, env=os.environ.copy())
            if result.returncode == 0:
                successes += 1
            else:
                failures += 1
        except OSError as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            failures += 1

    print(f"\nSummary: {successes} successful/planned, {failures} failed, {missing} missing (of {len(rows)} records)")
    return 1 if failures or missing else 0


if __name__ == "__main__":
    sys.exit(main())
