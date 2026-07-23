import sqlite3
import csv
import sys
from pathlib import Path

# --- Config ---
# Pass the .sqlite file path as a command-line argument, e.g.:
#   python extract_urls.py crawl-data-6.15-3.sqlite
# or edit the fallback path below.
DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "crawl-data.sqlite"
OUTPUT_PATH = "thirdparty_http_request_urls.csv"

# --- Query ---
QUERY = """
SELECT
    r.id            AS request_id,
    r.url           AS request_url,
    r.top_level_url AS top_level_url,
    s.site_url      AS site_visit_url
FROM http_requests r
JOIN site_visits s ON r.visit_id = s.visit_id
ORDER BY r.id
"""

# --- Run ---
db = Path(DB_PATH)
if not db.exists():
    print(f"Error: file not found: {DB_PATH}")
    sys.exit(1)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
cur.execute(QUERY)
rows = cur.fetchall()
con.close()

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["request_id", "request_url", "top_level_url", "site_visit_url"])
    writer.writerows(rows)

print(f"Done. {len(rows):,} rows written to {OUTPUT_PATH}")