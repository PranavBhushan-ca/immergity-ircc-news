# scripts/ircc_latest.py
import json, hashlib
from pathlib import Path
from datetime import datetime
from dateutil import tz
import feedparser
import sys

FEED_URL = (
    "https://api.io.canada.ca/io-server/gc/news/en/v2"
    "?dept=departmentofcitizenshipandimmigration"
    "&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23"
    "&pick=50&format=atom&atomtitle=Immigration,%20Refugees%20and%20Citizenship%20Canada"
)

DOCS_DIR = Path("docs")
OUT_PATH = DOCS_DIR / "ircc_latest.json"

def to_iso_toronto(struct_time) -> str:
    if not struct_time:
        return datetime.now(tz=tz.gettz("America/Toronto")).isoformat()
    dt_utc = datetime(*struct_time[:6], tzinfo=tz.tzutc())
    return dt_utc.astimezone(tz.gettz("America/Toronto")).isoformat()

def main():
    # Guard: docs must be a directory, not a file
    if DOCS_DIR.exists() and not DOCS_DIR.is_dir():
        sys.exit("Error: A file named 'docs' exists at repo root. "
                 "Please delete/rename it and create a folder named 'docs/'.")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / ".nojekyll").touch(exist_ok=True)  # helps GitHub Pages

    d = feedparser.parse(FEED_URL)
    if not d.entries:
        sys.exit("No entries in IRCC feed")

    e = d.entries[0]
    title = (e.get("title") or "").strip()
    link  = e.get("link") or ""
    summary = (e.get("summary") or e.get("subtitle") or "").strip()
    published = e.get("published_parsed") or e.get("updated_parsed")

    payload = {
        "id": hashlib.sha256(f"{link}{title}".encode()).hexdigest(),
        "source": "IRCC Newsroom",
        "title": title,
        "summary": summary,
        "link": link,
        "image": "",
        "published_at": to_iso_toronto(published),
        "last_built_at": datetime.now(tz=tz.gettz("America/Toronto")).isoformat(),
    }

    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
