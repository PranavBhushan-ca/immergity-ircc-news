# scripts/ircc_latest.py
import json, hashlib, os
from datetime import datetime
from dateutil import tz
import feedparser

# IRCC Atom (English). You can add a FR feed later and pick based on locale.
FEED_URL = (
    "https://api.io.canada.ca/io-server/gc/news/en/v2"
    "?dept=departmentofcitizenshipandimmigration"
    "&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23"
    "&pick=50&format=atom&atomtitle=Immigration,%20Refugees%20and%20Citizenship%20Canada"
)

def to_iso_toronto(struct_time) -> str:
    if not struct_time:
        return datetime.now(tz=tz.gettz("America/Toronto")).isoformat()
    dt_utc = datetime(*struct_time[:6], tzinfo=tz.tzutc())
    return dt_utc.astimezone(tz.gettz("America/Toronto")).isoformat()

def main():
    d = feedparser.parse(FEED_URL)
    if not d.entries:
        raise SystemExit("No entries in IRCC feed")

    e = d.entries[0]  # newest
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
        "image": "",  # can be populated later if the feed exposes media
        "published_at": to_iso_toronto(published),
        "last_built_at": datetime.now(tz=tz.gettz("America/Toronto")).isoformat(),
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/ircc_latest.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Wrote docs/ircc_latest.json")

if __name__ == "__main__":
    main()
