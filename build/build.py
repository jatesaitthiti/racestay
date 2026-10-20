#!/usr/bin/env python3
"""RaceStay build — single source of truth → static HTML.

Reads data/events.json and regenerates the event-card grid on index.html.
The page stays 100% static (good for SEO + GitHub Pages); this just removes
the need to hand-edit card markup. Run from the site root:

    python3 build/build.py

It only rewrites the region between the grid anchors below, leaving the hero,
teasers, newsletter and everything else untouched. Idempotent.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "events.json"
INDEX = ROOT / "index.html"

# Sport code -> (Thai label, English label)
SPORT = {
    "road":  ("วิ่งถนน", "Road"),
    "trail": ("วิ่งเทรล", "Trail"),
    "tri":   ("ไตรกีฬา", "Triathlon"),
    "bike":  ("จักรยาน", "Cycling"),
    "hyrox": ("HYROX", "HYROX"),
}

# Short uppercase category tag shown in the colored cover header (matches mockup).
SPORT_CODE = {"road": "ROAD", "trail": "TRAIL", "tri": "TRI", "bike": "BIKE", "hyrox": "HYROX"}


def short_date(label: str) -> str:
    """Drop the trailing year so the cover shows a compact date (e.g. '28–29 NOV')."""
    return re.sub(r"\s*\d{4}\s*$", "", label).strip()

# In-feed ad after the Nth rendered card (1-based) — matches current layout.
AD_AFTER = [3, 11]
AD_BLOCK = '    <div class="ad infeed"><span class="lbl">Advertisement · โฆษณา</span></div>'

# Grid region anchors in index.html (stable, unique).
GRID_START = '<div class="grid c3" style="margin-top:16px">'
GRID_END = '\n  </div>\n</div></div>\n\n<!-- BY CITY TEASER -->'


def card_html(ev: dict) -> str:
    sport = ev["sport"]
    if sport not in SPORT:
        raise SystemExit(f"Unknown sport '{sport}' for event '{ev['slug']}'")
    code = SPORT_CODE[sport]
    return (
        f'    <a class="evcard" href="{ev["slug"]}.html" data-sport="{sport}">\n'
        f'      <div class="dcover s-{sport}">\n'
        f'        <span class="sp">{code}</span>\n'
        f'        <span class="dd">{short_date(ev["dateLabel"])}</span>\n'
        f'      </div>\n'
        f'      <div class="dbody">\n'
        f'        <h3>{ev["name"]}</h3>\n'
        f'        <div class="desc" data-th="{ev["blurbTh"]}" data-en="{ev["blurbEn"]}">{ev["blurbTh"]}</div>\n'
        f'      </div>\n'
        f'    </a>'
    )


def build_grid(events: list) -> str:
    blocks = []
    rendered = 0
    for ev in events:
        blocks.append(card_html(ev))
        rendered += 1
        if rendered in AD_AFTER:
            blocks.append(AD_BLOCK)
    return "\n\n" + "\n\n".join(blocks) + "\n"


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    events = data["events"]
    html = INDEX.read_text(encoding="utf-8")

    try:
        s = html.index(GRID_START) + len(GRID_START)
        e = html.index(GRID_END)
    except ValueError:
        raise SystemExit("Could not locate the event-grid region in index.html — anchors changed?")
    if e <= s:
        raise SystemExit("Grid anchors out of order in index.html.")

    new_html = html[:s] + build_grid(events) + html[e:]

    # Keep the static event count in sync (JS also recomputes it on load).
    n = len(events)
    new_html = re.sub(r'(id="evcount">)\d+(<)', rf"\g<1>{n}\g<2>", new_html, count=1)

    if new_html != html:
        INDEX.write_text(new_html, encoding="utf-8")
        print(f"✓ index.html rebuilt — {n} events, {len(AD_AFTER)} in-feed ads")
    else:
        print(f"= index.html already up to date — {n} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
