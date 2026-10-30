"""Generate event detail pages ({slug}.html) for events that carry a `detail` block.

Hand-written pages (events without `detail`) are never touched. The page chrome
(nav, newsletter, footer) is borrowed from an existing detail page so every page
stays consistent. No hotel cards are generated — hotels come live from the
Stay22 map, per the RaceStay concept (aggregate, don't curate).
"""
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
CHROME_SRC = ROOT / "buriram-marathon.html"
CSS_V, JS_V = "54", "16"

SPORT = {
    "road": ("วิ่งถนน", "Road"), "trail": ("วิ่งเทรล", "Trail"), "tri": ("ไตรกีฬา", "Triathlon"),
    "bike": ("จักรยาน", "Cycling"), "hyrox": ("HYROX", "HYROX"),
}
TH_MONTH = {"JAN": "ม.ค.", "FEB": "ก.พ.", "MAR": "มี.ค.", "APR": "เม.ย.", "MAY": "พ.ค.", "JUN": "มิ.ย.",
            "JUL": "ก.ค.", "AUG": "ส.ค.", "SEP": "ก.ย.", "OCT": "ต.ค.", "NOV": "พ.ย.", "DEC": "ธ.ค."}

WHY = {
    "road": ("งานวิ่งถนนส่วนใหญ่ปล่อยตัวเช้ามืดและปิดถนน พักใกล้จุดปล่อยตัวช่วยให้ไม่ต้องลุ้นรถ และกลับไปพักได้ไวหลังเข้าเส้นชัย",
             "Most road races start before dawn with roads closed — staying near the start removes the transport gamble and gets you back to rest sooner."),
    "trail": ("งานเทรลมักสตาร์ทในพื้นที่ห่างไกล รถสาธารณะน้อย และปล่อยตัวตั้งแต่ก่อนสว่าง พักใกล้จุดสตาร์ทหรือในอำเภอเดียวกันช่วยให้ได้นอนเต็มอิ่ม",
              "Trail races usually start somewhere remote with little transport and pre-dawn gun times — staying close to the start (or in the same district) buys you sleep."),
}
WHY["hyrox"] = ("HYROX แข่งเป็นรอบตามเวลาที่ได้ทั้งวัน หลายวันติดกัน และมีคนดูมาเชียร์ด้วย ที่พักใกล้ฮอลล์จะเดินมาวอร์มอัปและกลับไปพักระหว่างวันได้สะดวก",
                 "HYROX runs in timed heats all day over several days, with spectators too — a stay near the hall lets you walk over to warm up and rest between sessions.")
WHY["tri"] = ("ไตรกีฬาต้องเอาจักรยานไปเช็กอินที่ transition ก่อนวันแข่ง และปล่อยตัวว่ายน้ำตั้งแต่เช้า พักใกล้ transition ช่วยให้ขนอุปกรณ์ง่ายและไม่ต้องรีบ",
               "Triathlons need bike check-in at transition the day before and an early swim start — staying near transition makes the gear run easy and unhurried.")
WHY["bike"] = ("งานปั่นปล่อยตัวเช้าและต้องขนจักรยานไปจุดสตาร์ท พักใกล้จุดปล่อยตัวที่มีที่เก็บจักรยานช่วยให้เช้าวันแข่งไม่วุ่น",
               "Rides start early and you need to get your bike to the line — a stay near the start with secure bike storage keeps race morning calm.")
TIP = {
    "road": ("เช็กวันรับ BIB ก่อนจอง แล้วเลือกที่พักในระยะเดินถึงจุดปล่อยตัว",
             "Check the BIB pickup day before you book, then pick a stay within walking distance of the start."),
    "hyrox": ("ดูเวลารอบปล่อยตัว (heat) ของตัวเองก่อนจอง แล้วเลือกวันพักให้ตรงกับรอบนั้น",
              "Check your heat time before booking, then match your nights to that day."),
    "tri": ("ถามที่พักว่าเอาจักรยานเข้าห้องหรือมีที่เก็บไหม และเช็กเวลาเช็กอินจักรยานที่ transition",
            "Ask whether bikes can go in the room or into storage, and check the transition bike check-in times."),
    "bike": ("เลือกที่พักที่มีที่เก็บจักรยานปลอดภัย และเผื่อเวลาประกอบรถก่อนวันแข่ง",
             "Pick a stay with secure bike storage and leave time to build your bike before race day."),
    "trail": ("ระยะไกลมักปล่อยตัวกลางดึก เลือกที่พักที่ออกเดินทางได้ตอนตีสาม-ตีสี่ และเผื่อคืนหลังแข่งไว้พักฟื้น",
              "Long distances often start in the middle of the night — pick a stay you can leave at 3–4 am and keep a recovery night after."),
}


def e(s):
    return html.escape(str(s), quote=True)


def bi(tag, th, en, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}{extra} data-th="{e(th)}" data-en="{e(en)}">{e(th)}</{tag}>'


def chrome():
    src = CHROME_SRC.read_text(encoding="utf-8")
    nav = src[src.index("<body>") + len("<body>\n"): src.index('<div class="band"><div class="in"><div class="crumb">')]
    foot = src[src.index("<!-- AD: end of content -->"):]
    return nav, foot


def render(ev, nav, foot):
    d = ev["detail"]
    s_th, s_en = SPORT[ev["sport"]]
    kind = ev["sport"] if ev["sport"] in ("trail", "hyrox", "tri", "bike") else "road"
    name, city = ev["name"], ev["city"]
    start = d["start"]
    finish_tbc = d.get("finish") is None and d.get("finishTbc")
    finish = "TBC" if finish_tbc else (d.get("finish") or start)
    same = finish == start
    zone_th, zone_en = d["zoneTh"], d["zoneEn"]
    km_list = " / ".join(x["km"] for x in d["distances"]) + " km"
    venue_q = quote(f'{d.get("startMap", start)}, {city}')
    checked = ev.get("checkedOn", "")
    date_th = d["dayLabel"]
    for k, v in TH_MONTH.items():
        date_th = date_th.replace(k, v)

    rows = "\n".join(
        f'    <tr><td>{(e(x["name"]) + " · ") if x.get("name") else ""}<span class="d" data-th="{e(x["km"])} กม." data-en="{e(x["km"])} km">{e(x["km"])} กม.</span></td>'
        f'<td class="num">{e(x.get("time") or "—")}</td><td>{e(x.get("start") or start)}</td><td>{e(x.get("finish") or finish)}</td></tr>'
        for x in d["distances"])

    sched = "\n".join(
        f'    <tr><td class="num">{e(r["when"])}</td>{bi("td", r["th"], r["en"])}{bi("td", r["stayTh"], r["stayEn"])}</tr>'
        for r in d.get("schedule", []))
    if not sched:
        sched = (f'    <tr>{bi("td", "ก่อนวันแข่ง", "Before", "num")}{bi("td", "รับ BIB", "BIB pickup")}{bi("td", "พักตั้งแต่คืนก่อนแข่ง", "Stay the night before")}</tr>\n'
                 f'    <tr><td class="num">{e(d["dayLabel"])}</td>{bi("td", "ปล่อยตัว + เข้าเส้นชัย", "Start + finish")}{bi("td", "พักใกล้จุดปล่อยตัว", "Stay near the start")}</tr>\n'
                 f'    <tr>{bi("td", "หลังแข่ง", "After", "num")}{bi("td", "พักฟื้น / เดินทางกลับ", "Recover / travel home")}{bi("td", "เลือกเช็กเอาต์สายถ้ามี", "Late checkout if available")}</tr>')

    if finish_tbc:
        sf_same = bi("span", "รอผู้จัดยืนยันจุดเส้นชัย", "Finish point to be confirmed by the organizer", "status tbc")
    elif same:
        sf_same = bi("span", "จุดเดียวกัน · พักที่เดียวจบ", "Same spot · one base", "status same")
    else:
        sf_same = bi("span", "คนละที่ · ระวังเรื่องการเดินทาง", "Different spots · plan your transport", "status diff")
    city_link = (f'  <div class="allrow"><a href="{e(d["cityPage"])}" data-th="ดูที่พักทั้งหมดใน {e(city)} →" data-en="See all stays in {e(city)} →">ดูที่พักทั้งหมดใน {e(city)} →</a></div>\n'
                 if d.get("cityPage") else "")
    official = (f'  <div class="mapfoot" style="margin-top:12px"><span data-th="ข้อมูลจากเว็บไซต์ทางการ · ตรวจล่าสุด {e(checked)}" data-en="From the official website · last checked {e(checked)}">ข้อมูลจากเว็บไซต์ทางการ · ตรวจล่าสุด {e(checked)}</span> · '
                f'<a href="{e(d["officialUrl"])}" target="_blank" rel="noopener">{e(d["officialUrl"].split("//")[-1].rstrip("/"))}</a></div>\n'
                if d.get("officialUrl") else "")

    maps = d.get("maps") or [{"labelTh": f"Map · {city}", "labelEn": f"Map · {city}", "lat": d["lat"], "lng": d["lng"], "venue": d.get("startMap", start)}]
    maps_html = ""
    for i, m in enumerate(maps):
        vq = quote(f'{m["venue"]}, {city}')
        mid = "map-a" if i == 0 else f"map-{chr(98 + i - 1)}"
        maps_html += (f'  <div class="maplabel"><span data-th="{e(m["labelTh"])}" data-en="{e(m["labelEn"])}">{e(m["labelTh"])}</span><span>Stay22</span></div>\n'
                      f'  <iframe class="mapframe" id="{mid}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="hotels near {e(m["venue"])}" '
                      f'src="https://www.stay22.com/embed/gm?aid=affiliateid&amp;lat={m["lat"]}&amp;lng={m["lng"]}&amp;venue={vq}&amp;maincolor=d9ef2f&amp;currency=THB&amp;priceper=nightly&amp;campaign=ev-{e(ev["slug"])}"></iframe>\n')
    title_th = f"{name} — ที่พักใกล้จุดปล่อยตัว | RaceStay"
    title_en = f"{name} — Hotels Near the Start | RaceStay"
    head = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title data-th="{e(title_th)}" data-en="{e(title_en)}">{e(name)} — RaceStay</title>
<link rel="icon" href="logo.svg" type="image/svg+xml">
<meta name="description" content="{e(name)} — ที่พักใกล้จุดปล่อยตัว {e(start)} · {e(city)} · ระยะ {e(km_list)}">
<link rel="stylesheet" href="assets/style.css?v={CSS_V}">
<script src="assets/app.js?v={JS_V}" defer></script>
</head>
<body>
"""
    body = f"""<div class="band"><div class="in"><div class="crumb"><a href="index.html" data-th="← งานกีฬาทั้งหมด" data-en="← All events">← งานกีฬาทั้งหมด</a></div></div></div>

<div class="band"><div class="in phero">
  <div class="kick">{e(s_en)} · {e(city)}</div>
  <h1>{e(name)}</h1>
  {bi("p", ev["blurbTh"], ev["blurbEn"], "sub")}
</div></div>

<div class="band databand"><div class="in">
  <span><b>{e(d["dayLabel"])}</b></span><span>{e(start)}</span><span>{e(city)}</span><span class="times">{e(km_list)}</span>
</div></div>

<div class="band"><div class="in sec">
  <div class="seclabel"><span class="n">01 / Why</span><h2 data-th="ทำไมทำเลที่พักสำคัญ" data-en="Why location matters">ทำไมทำเลที่พักสำคัญ</h2></div>
  {bi("p", d.get("whyTh", WHY[kind][0]), d.get("whyEn", WHY[kind][1]), "lead")}
  <div class="callout"><span class="h" data-th="Insight · เคล็ดลับ" data-en="Insight · tip">Insight · เคล็ดลับ</span>{bi("span", d.get("tipTh", TIP[kind][0]), d.get("tipEn", TIP[kind][1]))}</div>
</div></div>

<div class="band"><div class="in sec">
  <div class="seclabel"><span class="n">02 / Distances</span><h2 data-th="รายละเอียดการแข่ง — ทุกระยะ" data-en="Race details — every distance">รายละเอียดการแข่ง — ทุกระยะ</h2></div>
  <div class="table-wrap"><table>
    <tr><th data-th="ระยะ" data-en="Distance">ระยะ</th><th data-th="เวลาปล่อยตัว" data-en="Start time">เวลาปล่อยตัว</th><th data-th="จุดสตาร์ท" data-en="Start">จุดสตาร์ท</th><th data-th="เส้นชัย" data-en="Finish">เส้นชัย</th></tr>
{rows}
  </table></div>
{official}</div></div>

<div class="band stay"><div class="in sec">
  <div class="seclabel"><span class="n">03 / Stay</span><h2 data-th="ที่พักใกล้จุดปล่อยตัว" data-en="Where to stay">ที่พักใกล้จุดปล่อยตัว</h2></div>
  <div class="sf">
    {sf_same}
    <span class="lb ls">Start</span><span class="lb lf">Finish</span>
    <span class="v vs">{e(start)}</span><span class="arrow" aria-hidden="true">→</span><span class="v vf">{e(finish)}</span>
  </div>
  <div class="zone"><div class="zonelabel">Stay zone</div>{bi("h3", zone_th, zone_en)}{bi("p", d["zoneNoteTh"], d["zoneNoteEn"])}</div>
{maps_html}  <div class="mapfoot" data-th="วิดเจ็ต Stay22 จริง · โรงแรมและราคาจริงรอบจุดปล่อยตัว เลือกและจองได้เลย" data-en="Live Stay22 widget · real hotels and prices around the start — browse and book">วิดเจ็ต Stay22 จริง · โรงแรมและราคาจริงรอบจุดปล่อยตัว เลือกและจองได้เลย</div>
{city_link}</div></div>

<div class="band"><div class="in sec">
  <div class="seclabel"><span class="n">04 / Transit</span><h2 data-th="การเดินทางไปจุดปล่อยตัว" data-en="Getting to the start">การเดินทางไปจุดปล่อยตัว</h2></div>
  <div class="table-wrap"><table>
    <tr><th data-th="วิธี" data-en="Option">วิธี</th><th data-th="รายละเอียด" data-en="Details">รายละเอียด</th><th data-th="เหมาะกับ" data-en="Best for">เหมาะกับ</th></tr>
    <tr>{bi("td", "เดินจากที่พัก", "Walk", "d")}{bi("td", "ชัวร์สุด ไม่ลุ้นจราจรหรือถนนปิด", "Surest — no traffic or closures")}{bi("td", "พักย่าน " + zone_th, zone_en + " stays")}</tr>
    <tr><td class="d">Grab / <span data-th="แท็กซี่" data-en="Taxi">แท็กซี่</span></td>{bi("td", "เผื่อเวลาช่วงเช้ามืด · รถอาจหายาก", "Allow extra time pre-dawn · cars can be scarce")}{bi("td", "คนพักไกล", "Farther stays")}</tr>
    <tr>{bi("td", "รถรับส่งของงาน", "Event shuttle", "d")}{bi("td", "เช็กประกาศผู้จัดว่ามีรถรับส่งหรือไม่", "Check the organizer’s notices for shuttles")}{bi("td", "คนไม่มีรถ", "No car")}</tr>
  </table></div>
</div></div>

<div class="band"><div class="in sec">
  <div class="seclabel"><span class="n">05 / Schedule</span><h2 data-th="ตารางสุดสัปดาห์แข่ง" data-en="Race weekend schedule">ตารางสุดสัปดาห์แข่ง</h2></div>
  <div class="table-wrap"><table>
    <tr><th data-th="ช่วง" data-en="When">ช่วง</th><th data-th="รายการ" data-en="What">รายการ</th><th data-th="ผลต่อการจอง" data-en="Impact on stay">ผลต่อการจอง</th></tr>
{sched}
  </table></div>
</div></div>

<div class="band"><div class="in sec" id="faq">
  <div class="seclabel"><span class="n">06 / FAQ</span><h2 data-th="คำถามที่นักกีฬาถามบ่อย" data-en="Answers to athletes’ questions">คำถามที่นักกีฬาถามบ่อย</h2></div>
  <div class="faq2" style="margin-top:16px">
    <details open>{bi("summary", "ควรจองที่พักกี่คืน?", "How many nights should I book?")}{bi("p", "อย่างน้อยคืนก่อนแข่ง (เผื่อรับ BIB) ถ้าวิ่งระยะไกลเผื่ออีกคืนหลังแข่งไว้พักฟื้น", "At least the night before (for BIB pickup); for long distances add a recovery night.")}</details>
    <details>{bi("summary", "ควรพักย่านไหน?", "Where should I stay?")}{bi("p", "แนะนำย่าน " + zone_th + " ที่เดินทางสะดวกถึงจุดปล่อยตัว", "We recommend " + zone_en + " — easy to reach the start.")}</details>
    <details>{bi("summary", "ปล่อยตัวเช้ามืด อาหารเช้าทำยังไง?", "Early start — what about breakfast?")}{bi("p", "ถามที่พักว่าขอกล่องอาหารเช้าล่วงหน้าได้ไหม หรือเตรียมของกินเบา ๆ ไว้เอง", "Ask your stay for a pre-arranged breakfast box, or bring light snacks.")}</details>
    <details>{bi("summary", "ฝากกระเป๋าหลังเช็กเอาต์ได้ไหม?", "Can I store luggage after checkout?")}{bi("p", "ได้เกือบทุกที่ · ถ้าเลือกที่เช็กเอาต์สายได้ จะอาบน้ำหลังแข่งได้สบาย", "Almost everywhere · a late checkout lets you shower after finishing.")}</details>
  </div>
</div></div>

"""
    return head + nav + body + foot


def render_all(events):
    nav, foot = chrome()
    made = []
    for ev in events:
        if "detail" not in ev:
            continue
        (ROOT / f'{ev["slug"]}.html').write_text(render(ev, nav, foot), encoding="utf-8")
        made.append(ev["slug"])
    return made
