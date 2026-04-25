#!/usr/bin/env python3
"""Fetch Google Scholar profile stats and write to meta/scholar.json.

Designed for unattended runs in GitHub Actions. If Scholar blocks the
request the script exits non-zero, leaving the existing JSON intact so
the site keeps showing the last known values.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scholarly import ProxyGenerator, scholarly

SCHOLAR_USER_ID = "5u4mhmoAAAAJ"
OUTPUT_PATH = Path("meta/scholar.json")


def fetch():
    pg = ProxyGenerator()
    if pg.FreeProxies():
        scholarly.use_proxy(pg)
    else:
        print("warn: no free proxies, falling back to direct fetch", file=sys.stderr)

    author = scholarly.search_author_id(SCHOLAR_USER_ID)
    author = scholarly.fill(author, sections=["indices"])
    return {
        "citations": int(author.get("citedby", 0)),
        "h_index": int(author.get("hindex", 0)),
        "i10_index": int(author.get("i10index", 0)),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def main():
    try:
        data = fetch()
    except Exception as exc:
        print(f"error: scholar fetch failed: {exc}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {OUTPUT_PATH}: {data}")


if __name__ == "__main__":
    main()
