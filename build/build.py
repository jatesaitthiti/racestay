#!/usr/bin/env python3
"""RaceStay build — single source of truth → static HTML.

Reads data/events.json and regenerates the two auto-scrolling marquees on the
home page: an events marquee (sorted by soonest upcoming date) and a cities
marquee. Each marquee duplicates its cards into two groups so the CSS animation
can loop seamlessly. Run from the site root:

    python3 build/build.py

It only rewrites the regions between the marker comments below; the hero,
teasers, newsletter and everything else stay untouched. Idempotent.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "events.json"
INDEX = ROOT / "index.html"
TODAY = date.today()

# Short uppercase category tag shown in the colored cover header.
SPORT_CODE = {"road": "ROAD", "trail": "TRAIL", "tri": "TRI", "bike": "BIKE", "hyrox": "HYROX"}

EVENTS_START, EVENTS_END = "<!-- EVENTS:START -->", "<!-- EVENTS:END -->"
CITIES_START, CITIES_END = "<!-- CITIES:START -->", "<!-- CITIES:END -->"


def short_date(label: str) -> str:
    """Drop the trailing year so the cover shows a compact date (e.g. '28–29 NOV')."""
    import re
    return re.sub(r"\s*\d{4}\s*$", "", label).strip()


def upcoming_days(ev: dict) -> int:
    """Days until the event's next occurrence (wraps to next year if already past)."""
    _, m, d = (int(x) for x in ev["date"].split("-"))
    def mk(y):
        try:
            return date(y, m, d)
        except ValueError:
            return date(y, m, 1)
    occ = mk(TODAY.year)
    if occ < TODAY:
        occ = mk(TODAY.year + 1)
    return (occ - TODAY).days


def event_card(ev: dict) -> str:
    sport = ev["sport"]
    if sport not in SPORT_CODE:
        raise SystemExit(f"Unknown sport '{sport}' for event '{ev['slug']}'")
    code = SPORT_CODE[sport]
    return (
        f'        <a class="evcard" href="{ev["slug"]}.html" data-sport="{sport}">\n'
        f'          <div class="dcover s-{sport}">\n'
        f'            <span class="sp">{code}</span>\n'
        f'            <span class="dd">{short_date(ev["dateLabel"])}</span>\n'
        f'          </div>\n'
        f'          <div class="dbody">\n'
        f'            <h3>{ev["name"]}</h3>\n'
        f'            <div class="desc" data-th="{ev["blurbTh"]}" data-en="{ev["blurbEn"]}">{ev["blurbTh"]}</div>\n'
        f'          </div>\n'
        f'        </a>'
    )


def city_card(c: dict) -> str:
    return (
        f'        <a class="mqcity" href="{c["slug"]}.html">\n'
        f'          <h3>{c["name"]}</h3>\n'
        f'          <div class="desc" data-th="{c["blurbTh"]}" data-en="{c["blurbEn"]}">{c["blurbTh"]}</div>\n'
        f'          <span class="go" data-th="ดูเมือง →" data-en="View city →">ดูเมือง →</span>\n'
        f'        </a>'
    )


def marquee_body(cards: list) -> str:
    """Two identical groups (second hidden from assistive tech) for a seamless loop."""
    block = "\n".join(cards)
    g1 = f'      <div class="mq-group">\n{block}\n      </div>'
    g2 = f'      <div class="mq-group" aria-hidden="true">\n{block}\n      </div>'
    return "\n" + g1 + "\n" + g2 + "\n    "


def splice(html: str, start: str, end: str, body: str) -> str:
    try:
        s = html.index(start) + len(start)
        e = html.index(end)
    except ValueError:
        raise SystemExit(f"Could not find markers {start} … {end} in index.html")
    if e < s:
        raise SystemExit(f"Markers out of order: {start} … {end}")
    return html[:s] + body + html[e:]


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    events = sorted(data["events"], key=upcoming_days)
    cities = data.get("cities", [])

    html = INDEX.read_text(encoding="utf-8")
    html = splice(html, EVENTS_START, EVENTS_END, marquee_body([event_card(e) for e in events]))
    html = splice(html, CITIES_START, CITIES_END, marquee_body([city_card(c) for c in cities]))

    INDEX.write_text(html, encoding="utf-8")
    print(f"✓ index.html rebuilt — {len(events)} events, {len(cities)} cities (marquees x2 copies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
