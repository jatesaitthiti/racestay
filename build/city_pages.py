"""Keep city pages and cities.html in sync with data/events.json.

- Each city-*.html page: the "01 / Events" grid is rebuilt from the events whose
  city maps to that page (soonest first).
- cities.html: each city card's "N events" tag and event-name list are rebuilt.
A city's page is derived from its name: "Nakhon Ratchasima" -> city-nakhon-ratchasima.html.
Events in a city without a page (e.g. Nan) are simply not listed on a city page.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPORT = {"road": ("วิ่งถนน", "Road"), "trail": ("วิ่งเทรล", "Trail"), "tri": ("ไตรกีฬา", "Triathlon"),
         "bike": ("จักรยาน", "Cycling"), "hyrox": ("HYROX", "HYROX")}


def e(s):
    return html.escape(str(s), quote=True)


def city_page(city):
    return f'city-{city.lower().replace(" ", "-")}.html'


def card(ev):
    th, en = SPORT[ev["sport"]]
    return (f'    <a class="card" href="{ev["slug"]}.html" data-sport="{ev["sport"]}">\n'
            f'      <h3>{e(ev["name"])}</h3>\n'
            f'      <div class="when"><span data-th="{th}" data-en="{en}">{th}</span> · {e(ev["dateLabel"])} · {e(ev["city"])}</div>\n'
            f'      <div class="desc" data-th="{e(ev["blurbTh"])}" data-en="{e(ev["blurbEn"])}">{e(ev["blurbTh"])}</div>\n'
            f'      <span class="go" data-th="ดูรายละเอียด →" data-en="View details →">ดูรายละเอียด →</span>\n'
            f'    </a>')


def sync(events, sort_key):
    by_page = {}
    for ev in sorted(events, key=sort_key):
        by_page.setdefault(city_page(ev["city"]), []).append(ev)
    changed = []

    for page in sorted(ROOT.glob("city-*.html")):
        h = page.read_text(encoding="utf-8")
        i = h.find("01 / Events")
        if i < 0:
            continue
        g = h.index('<div class="grid c3"', i)
        g = h.index(">", g) + 1
        end = h.index("\n  </div>\n</div></div>", g)
        evs = by_page.get(page.name, [])
        body = ("\n\n" + "\n\n".join(card(x) for x in evs) + "\n") if evs else "\n"
        new = h[:g] + body + h[end:]
        if new != h:
            page.write_text(new, encoding="utf-8")
            changed.append(page.name)

    cp = ROOT / "cities.html"
    h = cp.read_text(encoding="utf-8")

    def fix_card(m):
        block, href = m.group(0), m.group(1)
        evs = by_page.get(href, [])
        n = len(evs)
        block = re.sub(r'(<span class="tag[^"]*") data-th="[^"]*" data-en="[^"]*">[^<]*</span>',
                       lambda t: f'{t.group(1)} data-th="{n} งาน" data-en="{n} event{"s" if n != 1 else ""}">{n} งาน</span>',
                       block, count=1)
        block = re.sub(r'(<span data-th="งาน:" data-en="Events:">งาน:</span><span><b>)[^<]*(</b>)',
                       lambda t: t.group(1) + e(" · ".join(x["name"] for x in evs)) + t.group(2), block, count=1)
        return block

    new = re.sub(r'    <a class="card" href="(city-[a-z-]+\.html)">.*?\n    </a>', fix_card, h, flags=re.S)
    if new != h:
        cp.write_text(new, encoding="utf-8")
        changed.append("cities.html")
    return changed
