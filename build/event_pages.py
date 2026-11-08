"""Generate event detail pages ({slug}.html) for events that carry a `detail` block.

Hand-written pages (events without `detail`) are left alone, except the marked hotel
regions of atm-2026.html (see fill_handwritten_hotels). The page chrome
(nav, newsletter, footer) is borrowed from an existing detail page so every page
stays consistent. Prices and availability come live from the Stay22 map; under
it, an event may list team-curated hotel cards from data/hotels/{slug}.json
(text only: name, area, distance, phone-confirmed facilities, a Stay22 link).
"""
import html
import json
import math
import re
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlencode

from th_names import distance_th, place_th

ROOT = Path(__file__).resolve().parent.parent
CHROME_SRC = ROOT / "buriram-marathon.html"
HOTELS_DIR = ROOT / "data" / "hotels"
CSS_V, JS_V = "85", "24"
STAY22_AID = "affiliateid"  # placeholder until the real Stay22 partner ID is issued

# athlete facilities the team confirms by phone; a card shows only those confirmed "yes"
FACIL = {
    "earlyBreakfast": ("อาหารเช้าก่อนปล่อยตัว", "Breakfast before the start"),
    "breakfastBox": ("กล่องอาหารเช้า", "Breakfast box"),
    "lateCheckout": ("เช็กเอาต์สายหลังแข่ง", "Late checkout after the race"),
    "luggage": ("ฝากกระเป๋า", "Luggage storage"),
    "showerAfterCheckout": ("อาบน้ำหลังเช็กเอาต์", "Shower after checkout"),
    "bikeStorage": ("ที่เก็บจักรยาน", "Bike storage"),
    "shuttle": ("รถรับส่งไปจุดสตาร์ท", "Shuttle to the start"),
}
# chip icons: Dazzle Line Icons (svgrepo, CC0) path data on a 24px grid; the set has no bicycle, so bike storage uses garage
FACIL_ICON = {
    "earlyBreakfast": '<path d="M8 21V3M15 21V3C17.2091 3 19 4.79086 19 7V9C19 11.2091 17.2091 13 15 13M11 3V8C11 9.65685 9.65685 11 8 11C6.34315 11 5 9.65685 5 8V3"/>',  # fork-knife
    "breakfastBox": '<path d="M9 11V6C9 4.34315 10.3431 3 12 3C13.6569 3 15 4.34315 15 6V10.9673M10.4 21H13.6C15.8402 21 16.9603 21 17.816 20.564C18.5686 20.1805 19.1805 19.5686 19.564 18.816C20 17.9603 20 16.8402 20 14.6V12.2C20 11.0799 20 10.5198 19.782 10.092C19.5903 9.71569 19.2843 9.40973 18.908 9.21799C18.4802 9 17.9201 9 16.8 9H7.2C6.0799 9 5.51984 9 5.09202 9.21799C4.71569 9.40973 4.40973 9.71569 4.21799 10.092C4 10.5198 4 11.0799 4 12.2V14.6C4 16.8402 4 17.9603 4.43597 18.816C4.81947 19.5686 5.43139 20.1805 6.18404 20.564C7.03968 21 8.15979 21 10.4 21Z"/>',  # bag-shopping
    "lateCheckout": '<path d="M12 16.5V8.5M16 12.5L8 12.5008M3 5.5L5 3.5M21 5.5L19 3.5M20 12.5C20 16.9183 16.4183 20.5 12 20.5C7.58172 20.5 4 16.9183 4 12.5C4 8.08172 7.58172 4.5 12 4.5C16.4183 4.5 20 8.08172 20 12.5Z"/>',  # clock-plus
    "luggage": '<path d="M8 7V6.2C8 5.0799 8 4.51984 8.21799 4.09202C8.40973 3.71569 8.71569 3.40973 9.09202 3.21799C9.51984 3 10.0799 3 11.2 3H12.8C13.9201 3 14.4802 3 14.908 3.21799C15.2843 3.40973 15.5903 3.71569 15.782 4.09202C16 4.51984 16 5.0799 16 6.2V7M7 21V7.00169M17 21V7M7 7.00169C7.24373 7 7.50929 7 7.8 7H16M7 7.00169C5.83507 7.00979 5.16873 7.05658 4.63803 7.32698C4.07354 7.6146 3.6146 8.07354 3.32698 8.63803C3 9.27976 3 10.1198 3 11.8V16.2C3 17.8802 3 18.7202 3.32698 19.362C3.6146 19.9265 4.07354 20.3854 4.63803 20.673C5.27976 21 6.11984 21 7.8 21H16.2C17.8802 21 18.7202 21 19.362 20.673C19.9265 20.3854 20.3854 19.9265 20.673 19.362C21 18.7202 21 17.8802 21 16.2V11.8C21 10.1198 21 9.27976 20.673 8.63803C20.3854 8.07354 19.9265 7.6146 19.362 7.32698C18.7202 7 17.8802 7 16.2 7H17M17 7H16"/>',  # suitcase
    "showerAfterCheckout": '<path d="M21 14.7C21 18.1794 19.0438 21 15.5 21C11.9562 21 10 18.1794 10 14.7C10 11.2206 15.5 3 15.5 3C15.5 3 21 11.2206 21 14.7Z"/><path d="M8 8.2C8 9.7464 7.11083 11 5.5 11C3.88917 11 3 9.7464 3 8.2C3 6.6536 5.5 3 5.5 3C5.5 3 8 6.6536 8 8.2Z"/>',  # droplets
    "bikeStorage": '<path d="M7 20H4.6C4.03995 20 3.75992 20 3.54601 19.891C3.35785 19.7951 3.20487 19.6422 3.10899 19.454C3 19.2401 3 18.9601 3 18.4V9.0398C3 8.66343 3 8.47524 3.05919 8.31095C3.1115 8.16573 3.19673 8.03458 3.30819 7.9278C3.43428 7.80699 3.60625 7.73056 3.95018 7.5777L12 4L20.0498 7.5777C20.3938 7.73056 20.5657 7.80699 20.6918 7.9278C20.8033 8.03458 20.8885 8.16573 20.9408 8.31095C21 8.47524 21 8.66343 21 9.0398V18.4C21 18.9601 21 19.2401 20.891 19.454C20.7951 19.6422 20.6422 19.7951 20.454 19.891C20.2401 20 19.9601 20 19.4 20H17M7 20H17M7 20V14M17 20V14M7 14V10H17V14M7 14H17"/>',  # garage
    "shuttle": '<path d="M5 6V15.8C5 16.9201 5 17.4802 5.21799 17.908C5.40973 18.2843 5.71569 18.5903 6.09202 18.782C6.51984 19 7.07989 19 8.2 19H15.8C16.9201 19 17.4802 19 17.908 18.782C18.2843 18.5903 18.5903 18.2843 18.782 17.908C19 17.4802 19 16.9201 19 15.8V6M5 6C5 6 5 3 12 3C19 3 19 6 19 6M5 6H19M5 13H19M17 21V19M7 21V19M8 16H8.01M16 16H16.01"/>',  # bus
}
FACIL_MAX_AGE_DAYS = 365  # an older phone check is hidden until the team calls again

SPORT = {
    "road": ("วิ่งถนน", "Road"), "trail": ("วิ่งเทรล", "Trail"), "tri": ("ไตรกีฬา", "Triathlon"),
    "bike": ("จักรยาน", "Cycling"), "hyrox": ("ไฮรอกซ์", "HYROX"),
}
# the start-point word per sport (docs/BRIEF.md §10); cross-sport copy uses จุดสตาร์ท
SPOT = {"road": "จุดปล่อยตัว", "trail": "จุดปล่อยตัว", "bike": "จุดสตาร์ท", "tri": "จุดทรานซิชัน", "hyrox": "เวนิว"}
TH_MONTH = {"JAN": "ม.ค.", "FEB": "ก.พ.", "MAR": "มี.ค.", "APR": "เม.ย.", "MAY": "พ.ค.", "JUN": "มิ.ย.",
            "JUL": "ก.ค.", "AUG": "ส.ค.", "SEP": "ก.ย.", "OCT": "ต.ค.", "NOV": "พ.ย.", "DEC": "ธ.ค."}

WHY = {
    "road": ("งานวิ่งถนนส่วนใหญ่ปล่อยตัวเช้ามืดและปิดถนน พักใกล้จุดปล่อยตัวช่วยให้ไม่ต้องลุ้นรถ และกลับไปพักได้ไวหลังเข้าเส้นชัย",
             "Most road races start before dawn with roads closed — staying near the start removes the transport gamble and gets you back to rest sooner."),
    "trail": ("งานเทรลมักสตาร์ทในพื้นที่ห่างไกล รถสาธารณะน้อย และปล่อยตัวตั้งแต่ก่อนสว่าง พักใกล้จุดปล่อยตัวหรือในอำเภอเดียวกันช่วยให้ได้นอนเต็มอิ่ม",
              "Trail races usually start somewhere remote with little transport and pre-dawn gun times — staying close to the start (or in the same district) buys you sleep."),
}
WHY["hyrox"] = ("ไฮรอกซ์ แข่งเป็นรอบตามเวลาที่ได้ทั้งวัน หลายวันติดกัน และมีคนดูมาเชียร์ด้วย ที่พักใกล้ฮอลล์จะเดินมาวอร์มอัปและกลับไปพักระหว่างวันได้สะดวก",
                 "HYROX runs in timed heats all day over several days, with spectators too — a stay near the hall lets you walk over to warm up and rest between sessions.")
WHY["tri"] = ("ไตรกีฬาต้องเอาจักรยานไปเช็กอินที่จุดทรานซิชันก่อนวันแข่ง และปล่อยตัวว่ายน้ำตั้งแต่เช้า พักใกล้จุดทรานซิชันช่วยให้ขนอุปกรณ์ง่ายและไม่ต้องรีบ",
               "Triathlons need bike check-in at transition the day before and an early swim start — staying near transition makes the gear run easy and unhurried.")
WHY["bike"] = ("งานปั่นปล่อยตัวเช้าและต้องขนจักรยานไปจุดสตาร์ท พักใกล้ๆ ในที่ที่มีที่เก็บจักรยานช่วยให้เช้าวันแข่งไม่วุ่น",
               "Rides start early and you need to get your bike to the line — a stay near the start with secure bike storage keeps race morning calm.")
TIP = {
    "road": ("เช็กวันรับบิบ ก่อนจอง แล้วเลือกที่พักในระยะเดินถึงจุดปล่อยตัว",
             "Check the BIB pickup day before you book, then pick a stay within walking distance of the start."),
    "hyrox": ("ดูเวลารอบปล่อยตัวของตัวเองก่อนจอง แล้วเลือกวันพักให้ตรงกับรอบนั้น",
              "Check your heat time before booking, then match your nights to that day."),
    "tri": ("ถามที่พักว่าเอาจักรยานเข้าห้องหรือมีที่เก็บไหม และเช็กเวลาเช็กอินจักรยานที่จุดทรานซิชัน",
            "Ask whether bikes can go in the room or into storage, and check the transition bike check-in times."),
    "bike": ("เลือกที่พักที่มีที่เก็บจักรยานปลอดภัย และเผื่อเวลาประกอบรถก่อนวันแข่ง",
             "Pick a stay with secure bike storage and leave time to build your bike before race day."),
    "trail": ("ระยะไกลมักปล่อยตัวกลางดึก เลือกที่พักที่ออกเดินทางได้ตอนตีสาม-ตีสี่ และเผื่อคืนหลังแข่งไว้พักฟื้น",
              "Long distances often start in the middle of the night — pick a stay you can leave at 3–4 am and keep a recovery night after."),
}


# ---- section headlines: answers built from verified data, generic only when data is missing ----
TH_MON = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
EN_MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TH_DAY = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
EN_DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

OLD_HEAD = [("ทำไมทำเลที่พักสำคัญ", "Why location matters"),
       ("รายละเอียดการแข่ง — ทุกระยะ", "Race details — every distance"),
       ("ที่พักใกล้จุดปล่อยตัว", "Where to stay"),
       ("การเดินทางไปจุดปล่อยตัว", "Getting to the start"),
       ("ตารางสุดสัปดาห์แข่ง", "Race weekend schedule"),
       ("คำถามที่นักกีฬาถามบ่อย", "Answers to athletes’ questions")]

# second half of the 01 headline: what the early start means for where you sleep, per sport
WHY_TAIL = {"road": ("พักให้เดินถึงจุดปล่อยตัว", "stay within walking distance of the start"),
            "trail": ("พักให้ใกล้จุดปล่อยตัวที่สุด", "sleep as close to the start as you can"),
            "tri": ("พักใกล้จุดทรานซิชัน", "stay near transition"),
            "bike": ("พักที่มีที่เก็บจักรยาน ใกล้จุดสตาร์ท", "stay near the start with bike storage")}


def mins(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def parse(entry):
    """'13 JUN · 03:00' -> ('13 JUN', ['03:00']); '02:30 / 02:45 / 03:00' -> (None, [3 waves]); '29 NOV' -> ('29 NOV', [])"""
    m = re.match(r"(\d{1,2}(?:–\d{1,2})? [A-Z]{3})", entry or "")
    return (m.group(1) if m else None), re.findall(r"\d{2}:\d{2}", entry or "")


def daymonths(prefix):
    """'5–6 DEC' -> [(12, 5), (12, 6)]"""
    days, mon = prefix.split(" ")
    m = [x.upper() for x in EN_MONTH].index(mon) + 1
    return [(m, int(x)) for x in days.split("–")]


def headlines(ev):
    d = ev["detail"]
    dist = d["distances"]
    n = len(dist)
    parsed = [parse(x.get("time")) for x in dist]
    days = {p[0] for p in parsed if p[0]}
    firsts = [p[1][0] for p in parsed if p[1]]
    every = [t for p in parsed for t in p[1]]
    out = []

    # 01 why
    if ev["sport"] == "hyrox":
        out.append(("แข่งเป็นรอบทั้งวัน พักใกล้ฮอลล์", "Heats run all day, stay near the hall"))
    elif len(days) > 1:
        out.append(("จองคืนให้ตรงกับวันแข่งของระยะที่ลง", "Book your nights around your distance's race day"))
    elif firsts:
        first = min(firsts, key=mins)
        th, en = WHY_TAIL[ev["sport"]]
        word_th, word_en = ("ปล่อยตัวแรก", "First start") if n > 1 else ("ปล่อยตัว", "Start")
        out.append((f"{word_th} {first} {th}", f"{word_en} {first}, {en}"))
    else:
        th, en = WHY_TAIL[ev["sport"]]
        out.append((th, en[0].upper() + en[1:]))

    # 02 distances
    if ev["sport"] == "hyrox":
        out.append((f"{n} รุ่น แข่งเป็นรอบ", f"{n} divisions, timed heats"))
    elif len(days) > 1:
        when_th, when_en = "ปล่อยตัวคนละวัน", "on different days"
    elif every and len(firsts) == n:
        lo, hi = min(every, key=mins), max(every, key=mins)
        waves = n == 1 and len(every) > 1
        if lo == hi:
            when_th, when_en = f"ปล่อยตัว {lo}", f"start {lo}"
        elif waves:
            when_th, when_en = f"ปล่อยตัวเป็นรอบ {lo}–{hi}", f"waves {lo}–{hi}"
        else:
            when_th, when_en = f"ปล่อยตัว {lo}–{hi}", f"starts {lo}–{hi}"
    elif firsts:
        when_th, when_en = "บางระยะรอยืนยันเวลา", "some start times TBA"
    else:
        when_th, when_en = "เวลาปล่อยตัวรอยืนยัน", "start times TBA"
    if ev["sport"] == "hyrox":
        pass
    elif n == 1:
        what_th = dist[0].get("name") or f"{dist[0]['km']} กม."
        what_en = dist[0].get("name") or f"{dist[0]['km']} km"
        out.append((f"{what_th} {when_th}", f"{what_en}, {when_en}"))
    else:
        out.append((f"{n} ระยะ {when_th}", f"{n} races, {when_en}".replace(", on ", " on ")))

    # 03 stay: the recommended zone is the answer
    out.append((d["zoneTh"], d["zoneEn"]))

    # 04 transit: where the trip home starts
    finish = d.get("finish")
    if finish is None and d.get("finishTbc"):
        out.append(("จุดเส้นชัยรอผู้จัดยืนยัน", "Finish point still to be confirmed"))
    elif not finish or finish == d["start"]:
        out.append(("สตาร์ทและเข้าเส้นชัยที่เดียวกัน", "Start and finish at the same spot"))
    else:
        out.append((f"ขากลับออกจากเส้นชัยที่{place_th(finish)}", f"The trip back starts at {finish}"))

    # 05 schedule
    if ev.get("dateTba"):
        out.append(("วันแข่งรอยืนยัน", "Race date to be announced"))
    elif len(days) > 1:
        y = int(ev["date"][:4])
        span = sorted(dm for p in days for dm in daymonths(p))
        (m1, d1), (m2, d2) = span[0], span[-1]
        if m1 == m2:
            th_s, en_s = f"{d1}–{d2} {TH_MON[m1-1]}", f"{d1}–{d2} {EN_MONTH[m1-1]}"
        else:
            th_s, en_s = f"{d1} {TH_MON[m1-1]}–{d2} {TH_MON[m2-1]}", f"{d1} {EN_MONTH[m1-1]}–{d2} {EN_MONTH[m2-1]}"
        out.append((f"แข่ง {th_s} {y}", f"Racing {en_s} {y}"))
    else:
        y, m, dd = (int(v) for v in ev["date"].split("-"))
        wd = date(y, m, dd).weekday()
        out.append((f"วันแข่ง {TH_DAY[wd]} {dd} {TH_MON[m-1]} {y}", f"Race day {EN_DAY[wd]} {dd} {EN_MONTH[m-1]} {y}"))

    # 06 faq: the four questions are the same on every page
    out.append(("4 เรื่องที่นักกีฬาถามก่อนจองที่พัก", "4 things athletes ask before booking"))
    return out


def e(s):
    return html.escape(str(s), quote=True)


def bi(tag, th, en, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}{extra} data-th="{e(th)}" data-en="{e(en)}">{e(th)}</{tag}>'


def statpanel(ev, d, start, finish, same, finish_tbc, zone_th, zone_en, date_th):
    """Race stats panel: start times on charcoal + 2x2 facts. Verified data only — nothing estimated."""
    from datetime import date as _date
    tba = bool(ev.get("dateTba"))
    rows = ""
    for x in d["distances"]:
        pre_th = (distance_th(x["name"]) + " · ") if x.get("name") else ""
        pre_en = (x["name"] + " · ") if x.get("name") else ""
        rows += bi("span", f'{pre_th}{x["km"]} กม.', f'{pre_en}{x["km"]} km', "km")
        rows += f'<span class="tm">{e(x["time"])}</span>' if x.get("time") else bi("span", "รอยืนยัน", "TBA", "tm")

    def fact(lth, len_, value, sub):
        return f'<div>{bi("div", lth, len_, "l")}{value}{sub}</div>'

    day = bi("div", "รอยืนยัน", "TBA", "v txt") if tba else f'<div class="v txt">{e(date_th)}</div>'
    if finish_tbc:
        fin = bi("div", "เส้นชัยรอยืนยัน", "Finish to be confirmed", "sub")
    elif same:
        fin = bi("div", "เข้าเส้นชัยที่จุดเดียวกัน", "Finishes at the same spot", "sub")
    else:
        fin = bi("div", f"เส้นชัย: {place_th(finish)}", f"Finish: {finish}", "sub")
    if tba:
        left = bi("div", "รอยืนยัน", "TBA", "v") + bi("div", "ผู้จัดยังไม่ประกาศวันแข่ง", "The organizer hasn't announced the date", "sub")
    else:
        y, m, dd = (int(v) for v in ev["date"].split("-"))
        days = max((_date(y, m, dd) - _date.today()).days, 0)
        left = (f'<div class="v" data-countdown="{e(ev["date"])}">{days}<small> วัน</small></div>'
                + bi("div", "ถึงวันแข่ง", "to race day", "sub"))
    city_sub = bi("div", place_th(ev["city"]), ev["city"], "sub")
    start_v = bi("div", place_th(start), start, "v txt")
    zone_v = bi("div", zone_th, zone_en, "v txt")
    zone_sub = bi("div", "ดูที่พักจริงบนแผนที่ Stay22 ด้านล่าง", "Live hotels on the Stay22 map below", "sub")
    facts = [fact("วันแข่ง", "Race day", day, city_sub),
             fact(SPOT.get(ev["sport"], "จุดสตาร์ท"), "Start", start_v, fin),
             fact("ย่านที่พักแนะนำ", "Where to stay", zone_v, zone_sub),
             fact("เหลืออีก", "Countdown", left, "")]
    times_l = bi("div", "เวลาปล่อยตัว", "Start times", "l")
    return ('<div class="band"><div class="in"><div class="statpanel">\n'
            '  <div class="times">' + times_l + '<div class="list">' + rows + '</div></div>\n'
            '  <div class="facts">\n' + "".join("    " + x + "\n" for x in facts) + '  </div>\n'
            '</div></div></div>\n')


def metres(lat1, lng1, lat2, lng2):
    """Straight-line (haversine) distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(a))


def dist_text(m):
    v = max(50, int(round(m / 50.0)) * 50)
    if v < 1000:
        return f"{v} ม.", f"{v} m"
    k = f"{m / 1000:.1f}"
    return f"{k} กม.", f"{k} km"


def hotel_block(slug, hotels, lat, lng, label, to, race, extra_cap=None):
    """Cards for one venue, nearest first. Facilities show only when phone-confirmed and recent."""
    to_th, to_en = to
    today = date.today()
    stay = {}
    if race and date.fromisoformat(race) >= today:  # a finished race gets no pre-filled dates
        stay = {"checkin": (date.fromisoformat(race) - timedelta(days=1)).isoformat(), "checkout": race}
    cards = ""
    for h in sorted(hotels, key=lambda h: metres(lat, lng, h["lat"], h["lng"])):
        dt_th, dt_en = dist_text(metres(lat, lng, h["lat"], h["lng"]))
        ok, last = set(), None
        for key, f in (h.get("facilities") or {}).items():
            on = f.get("checkedOn")
            if key in FACIL and f.get("status") == "yes" and on and (today - date.fromisoformat(on)).days <= FACIL_MAX_AGE_DAYS:
                ok.add(key)
                last = max(last or on, on)
        shown = [k for k in FACIL if k in ok]  # same order on every card, whatever order the team typed
        sample = [k for k in FACIL if k in (h.get("sampleFacilities") or [])] if not shown else []  # mockup only, never a phone check
        facil = ""
        if shown or sample:
            chips = "".join(
                '<span><svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{FACIL_ICON[k]}</svg>{bi("span", *FACIL[k])}</span>'
                for k in shown or sample)
            if shown:
                y, m, dd = (int(v) for v in last.split("-"))
                note = bi("p", f"ตรวจสอบโดยทีมงาน · โทรเช็ก {dd} {TH_MON[m - 1]} {y}",
                          f"Checked by our team · phoned {dd} {EN_MONTH[m - 1]} {y}", "checked")
            else:
                note = bi("p", "ข้อมูลตัวอย่าง · ยังไม่ได้โทรเช็กกับโรงแรม", "Sample data · not yet checked with the hotel", "checked sample")
            facil = f'<div class="hfac"><div class="facil">{chips}</div>{note}</div>'
        q = {"aid": STAY22_AID, "hotelname": h["name"], "lat": h["lat"], "lng": h["lng"], **stay,
             "currency": "THB", "campaign": f'ev_{slug.replace("-", "_")}_hotel'}
        link = "https://www.stay22.com/allez/roam?" + urlencode(q)
        # header row (name, distance · zone, button) over a full-width facility strip
        cards += (f'    <article class="hotelcard"><div class="hmain"><h3>{e(h["name"])}</h3>'
                  f'<p class="hd"><b>{bi("span", dt_th, dt_en)}</b> {bi("span", to_th, to_en)}<span class="sep" aria-hidden="true">·</span>{bi("span", h["zoneTh"], h["zoneEn"], "hz")}</p></div>'
                  f'<a class="go btn ghost" href="{e(link)}" target="_blank" rel="noopener sponsored">{bi("span", "ดูห้องว่าง", "See rooms")}'
                  f'<span class="vh">: {e(h["name"])}</span></a>{facil}</article>\n')
    cap_th = "ระยะวัดเป็นเส้นตรงจากพิกัด OpenStreetMap ระยะเดินจริงอาจไกลกว่า · ราคาและห้องว่างดูได้ที่ Stay22"
    cap_en = "Straight-line distance from OpenStreetMap coordinates; the walk may be longer · prices and availability on Stay22"
    if extra_cap:
        cap_th, cap_en = f"{extra_cap[0]} · {cap_th}", f"{extra_cap[1]} · {cap_en}"
    return (f'  <div class="hotels">{bi("div", label[0], label[1], "l")}\n'
            f'  <div class="hotelgrid">\n{cards}  </div>\n  <p class="staycap">{bi("span", cap_th, cap_en)}</p></div>\n')


def hotel_cards(ev, d, same):
    """Team-curated hotels under the map; a file's `near` block overrides the venue on multi-venue events."""
    path = HOTELS_DIR / f'{ev["slug"]}.json'
    if not path.exists():
        return ""
    data = json.loads(path.read_text(encoding="utf-8"))
    hotels = data.get("hotels", [])
    if not hotels:
        return ""
    near = data.get("near")
    if near:
        return hotel_block(ev["slug"], hotels, near["lat"], near["lng"], (near["labelTh"], near["labelEn"]),
                           (near["toTh"], near["toEn"]), near.get("race"), (near["capTh"], near["capEn"]))
    spot = SPOT.get(ev["sport"], "จุดสตาร์ท")
    spot_en = {"tri": "transition", "hyrox": "the venue"}.get(ev["sport"], "the start")
    # HYROX races inside one hall, so "and the finish" would read oddly there
    both = same and ev["sport"] != "hyrox"
    to = (f"จาก{spot}และเส้นชัย", f"from {spot_en} and finish") if both else (f"จาก{spot}", f"from {spot_en}")
    return hotel_block(ev["slug"], hotels, d["lat"], d["lng"], (f"โรงแรมใกล้{spot}", f"Hotels near {spot_en}"), to,
                       None if ev.get("dateTba") else ev["date"])


def fill_handwritten_hotels():
    """atm-2026.html is hand-written: fill only its <!-- HOTELS:key --> regions from data/hotels/atm-2026.json."""
    page = ROOT / "atm-2026.html"
    html_text = page.read_text(encoding="utf-8")
    for key, g in json.loads((HOTELS_DIR / "atm-2026.json").read_text(encoding="utf-8"))["groups"].items():
        block = hotel_block("atm-2026", g["hotels"], g["lat"], g["lng"], (g["labelTh"], g["labelEn"]),
                            (g["toTh"], g["toEn"]), g["race"])
        html_text, n = re.subn(rf"(<!-- HOTELS:{key} -->\n).*?(\s*<!-- /HOTELS:{key} -->)",
                               lambda m: m.group(1) + block.rstrip("\n") + m.group(2), html_text, flags=re.S)
        assert n == 1, key
    page.write_text(html_text, encoding="utf-8")


def staycard(ev, d, start, finish, same, finish_tbc, sf_same, city):
    """Stay layout A: card (status + route | area note) then the map(s) and a one-line caption."""
    if same:
        route = bi("span", "สตาร์ทและเส้นชัย", "Start and finish", "to") + bi("span", place_th(start), start)
    elif finish_tbc:
        route = bi("span", place_th(start), start) + '<span class="to">→</span>' + bi("span", "เส้นชัยรอยืนยัน", "Finish TBC")
    else:
        route = bi("span", place_th(start), start) + '<span class="to">→</span>' + bi("span", place_th(finish), finish)
    card = (f'  <div class="staycard">\n    <div>{sf_same}<div class="route">{route}</div></div>\n'
            f'    <div>{bi("div", "เตรียมตัวเรื่องที่พัก", "Before you book", "l")}{bi("p", d["zoneNoteTh"], d["zoneNoteEn"], "note")}</div>\n  </div>\n')
    maps = d.get("maps") or [{"labelTh": "", "labelEn": "", "lat": d["lat"], "lng": d["lng"], "venue": d.get("startMap", start)}]
    out = card
    for i, m in enumerate(maps):
        vq = quote(f'{m["venue"]}, {city}')
        mid = "map-a" if i == 0 else f"map-{chr(98 + i - 1)}"
        label = bi("div", m["labelTh"], m["labelEn"], "l") if m["labelTh"] else ""
        out += (f'  <div class="staymap">{label}<iframe class="mapframe" id="{mid}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="ที่พักใกล้{e(place_th(m["venue"]))}" data-th-title="ที่พักใกล้{e(place_th(m["venue"]))}" data-en-title="hotels near {e(m["venue"])}" '
                f'src="https://www.stay22.com/embed/gm?aid={STAY22_AID}&amp;lat={m["lat"]}&amp;lng={m["lng"]}&amp;venue={vq}&amp;maincolor=72f1ba&amp;currency=THB&amp;priceper=nightly&amp;campaign=ev-{e(ev["slug"])}"></iframe></div>\n')
    near = d.get("startMap", start)
    cap_th = f"ราคาและห้องว่างจริงจาก Stay22 · รอบ{place_th(near)}"
    cap_en = f"Live prices and availability from Stay22 · around {near}"
    link = (f' · <a href="{e(d["cityPage"])}" data-th="ดูที่พักทั้งหมดใน{e(place_th(city))} →" data-en="See all stays in {e(city)} →">ดูที่พักทั้งหมดใน{e(place_th(city))} →</a>'
            if d.get("cityPage") else "")
    out += f'  <p class="staycap">{bi("span", cap_th, cap_en)}{link}</p>\n'
    return out + hotel_cards(ev, d, same)


def chrome():
    src = CHROME_SRC.read_text(encoding="utf-8")
    crumb = re.search(r'<div class="band[^"]*"><div class="in"><div class="crumb">', src).start()
    nav = src[src.index("<body>") + len("<body>\n"): crumb]
    foot = src[src.index("<!-- AD: end of content -->"):]
    return nav, foot


def render(ev, nav, foot):
    d = ev["detail"]
    s_th, s_en = SPORT[ev["sport"]]
    kind = ev["sport"] if ev["sport"] in ("trail", "hyrox", "tri", "bike") else "road"
    spot = SPOT.get(ev["sport"], "จุดสตาร์ท")
    start_col = "จุดปล่อยตัว" if kind in ("road", "trail") else "จุดสตาร์ท"
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
        f'    <tr><td>{bi("span", distance_th(x["name"]) + " · ", x["name"] + " · ") if x.get("name") else ""}<span class="d" data-th="{e(x["km"])} กม." data-en="{e(x["km"])} km">{e(x["km"])} กม.</span></td>'
        f'<td class="num">{e(x.get("time") or "—")}</td>{bi("td", place_th(x.get("start") or start), x.get("start") or start)}{bi("td", place_th(x.get("finish") or finish), x.get("finish") or finish)}</tr>'
        for x in d["distances"])

    sched = "\n".join(
        f'    <tr><td class="num">{e(r["when"])}</td>{bi("td", r["th"], r["en"])}{bi("td", r["stayTh"], r["stayEn"])}</tr>'
        for r in d.get("schedule", []))
    if not sched:
        sched = (f'    <tr>{bi("td", "ก่อนวันแข่ง", "Before", "num")}{bi("td", "รับบิบ", "BIB pickup")}{bi("td", "พักตั้งแต่คืนก่อนแข่ง", "Stay the night before")}</tr>\n'
                 f'    <tr><td class="num">{e(d["dayLabel"])}</td>{bi("td", "ปล่อยตัว + เข้าเส้นชัย", "Start + finish")}{bi("td", f"พักใกล้{spot}", "Stay near the start")}</tr>\n'
                 f'    <tr>{bi("td", "หลังแข่ง", "After", "num")}{bi("td", "พักฟื้น / เดินทางกลับ", "Recover / travel home")}{bi("td", "เลือกเช็กเอาต์สายถ้ามี", "Late checkout if available")}</tr>')

    if finish_tbc:
        sf_same = bi("span", "รอผู้จัดยืนยันจุดเส้นชัย", "Finish point to be confirmed by the organizer", "status tbc")
    elif same:
        sf_same = bi("span", "จุดเดียวกัน · พักที่เดียวจบ", "Same spot · one base", "status same")
    else:
        sf_same = bi("span", "คนละที่ · ระวังเรื่องการเดินทาง", "Different spots · plan your transport", "status diff")
    city_link = (f'  <div class="allrow"><a href="{e(d["cityPage"])}" data-th="ดูที่พักทั้งหมดใน{e(place_th(city))} →" data-en="See all stays in {e(city)} →">ดูที่พักทั้งหมดใน{e(place_th(city))} →</a></div>\n'
                 if d.get("cityPage") else "")
    official = (f'  <div class="mapfoot" style="margin-top:12px"><span data-th="ข้อมูลจากเว็บไซต์ทางการ · ตรวจล่าสุด {e(checked)}" data-en="From the official website · last checked {e(checked)}">ข้อมูลจากเว็บไซต์ทางการ · ตรวจล่าสุด {e(checked)}</span> · '
                f'<a href="{e(d["officialUrl"])}" target="_blank" rel="noopener">{e(d["officialUrl"].split("//")[-1].rstrip("/"))}</a></div>\n'
                if d.get("officialUrl") else "")

    maps = d.get("maps") or [{"labelTh": f"แผนที่ · {place_th(city)}", "labelEn": f"Map · {city}", "lat": d["lat"], "lng": d["lng"], "venue": d.get("startMap", start)}]
    maps_html = ""
    for i, m in enumerate(maps):
        vq = quote(f'{m["venue"]}, {city}')
        mid = "map-a" if i == 0 else f"map-{chr(98 + i - 1)}"
        maps_html += (f'  <div class="maplabel"><span data-th="{e(m["labelTh"])}" data-en="{e(m["labelEn"])}">{e(m["labelTh"])}</span><span>Stay22</span></div>\n'
                      f'  <iframe class="mapframe" id="{mid}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="ที่พักใกล้{e(place_th(m["venue"]))}" data-th-title="ที่พักใกล้{e(place_th(m["venue"]))}" data-en-title="hotels near {e(m["venue"])}" '
                      f'src="https://www.stay22.com/embed/gm?aid={STAY22_AID}&amp;lat={m["lat"]}&amp;lng={m["lng"]}&amp;venue={vq}&amp;maincolor=72f1ba&amp;currency=THB&amp;priceper=nightly&amp;campaign=ev-{e(ev["slug"])}"></iframe>\n')
    title_th = f"{name} — ที่พักใกล้{spot} | RaceStay"
    title_en = f"{name} — Hotels Near the Start | RaceStay"
    head = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title data-th="{e(title_th)}" data-en="{e(title_en)}">{e(name)} — RaceStay</title>
<link rel="icon" href="logo.svg" type="image/svg+xml">
<meta name="description" content="{e(name)} — ที่พักใกล้{spot} {e(place_th(start))} · {e(place_th(city))} · ระยะ {e(km_list[:-3])} กม.">
<link rel="stylesheet" href="assets/style.css?v={CSS_V}">
<script src="assets/app.js?v={JS_V}" defer></script>
</head>
<body>
"""
    panel = statpanel(ev, d, start, finish, same, finish_tbc, zone_th, zone_en, date_th)
    H = headlines(ev)
    stay_html = staycard(ev, d, start, finish, same, finish_tbc, sf_same, city)
    body = f"""<div class="band herodark"><div class="in"><div class="crumb"><a href="index.html" data-th="← งานกีฬาทั้งหมด" data-en="← All events">← งานกีฬาทั้งหมด</a></div></div></div>

<div class="band herodark"><div class="in phero">
  {bi("div", s_th + " · " + place_th(city), s_en + " · " + city, "kick")}
  <h1>{e(name)}</h1>
  {bi("p", ev["blurbTh"], ev["blurbEn"], "sub")}
</div></div>

<div class="band databand"><div class="in">
  <span><b>{e(d["dayLabel"])}</b></span>{bi("span", place_th(start), start)}{bi("span", place_th(city), city)}{bi("span", km_list[:-3] + " กม.", km_list, "times")}
</div></div>

{panel}
<div class="band tone-paper"><div class="in sec banded">
  <div class="seclabel"><span class="num">01</span><span class="n" data-th="ทำไม" data-en="Why">ทำไม</span>{bi("h2", *H[0])}</div>
  {bi("p", d.get("whyTh", WHY[kind][0]), d.get("whyEn", WHY[kind][1]), "lead")}
  <div class="callout"><span class="h" data-th="เคล็ดลับ" data-en="Insight · tip">เคล็ดลับ</span>{bi("span", d.get("tipTh", TIP[kind][0]), d.get("tipEn", TIP[kind][1]))}</div>
</div></div>

<div class="band tone-white"><div class="in sec banded">
  <div class="seclabel"><span class="num">02</span><span class="n" data-th="ทุกระยะ" data-en="Distances">ทุกระยะ</span>{bi("h2", *H[1])}</div>
  <div class="table-wrap"><table>
    <tr><th data-th="ระยะ" data-en="Distance">ระยะ</th><th data-th="เวลาปล่อยตัว" data-en="Start time">เวลาปล่อยตัว</th><th data-th="{start_col}" data-en="Start">{start_col}</th><th data-th="เส้นชัย" data-en="Finish">เส้นชัย</th></tr>
{rows}
  </table></div>
{official}</div></div>

<div class="band stay tone-mint"><div class="in sec banded">
  <div class="seclabel"><span class="num">03</span><span class="n" data-th="ที่พัก" data-en="Stay">ที่พัก</span>{bi("h2", *H[2])}</div>
{stay_html}</div></div>

<div class="band tone-paper2"><div class="in sec banded">
  <div class="seclabel"><span class="num">04</span><span class="n" data-th="การเดินทาง" data-en="Transit">การเดินทาง</span>{bi("h2", *H[3])}</div>
  <div class="table-wrap"><table>
    <tr><th data-th="วิธี" data-en="Option">วิธี</th><th data-th="รายละเอียด" data-en="Details">รายละเอียด</th><th data-th="เหมาะกับ" data-en="Best for">เหมาะกับ</th></tr>
    <tr>{bi("td", "เดินจากที่พัก", "Walk", "d")}{bi("td", "ชัวร์สุด ไม่ลุ้นจราจรหรือถนนปิด", "Surest — no traffic or closures")}{bi("td", "พักย่าน " + zone_th, zone_en + " stays")}</tr>
    <tr><td class="d">Grab / <span data-th="แท็กซี่" data-en="Taxi">แท็กซี่</span></td>{bi("td", "เผื่อเวลาช่วงเช้ามืด · รถอาจหายาก", "Allow extra time pre-dawn · cars can be scarce")}{bi("td", "คนพักไกล", "Farther stays")}</tr>
    <tr>{bi("td", "รถรับส่งของงาน", "Event shuttle", "d")}{bi("td", "เช็กประกาศผู้จัดว่ามีรถรับส่งหรือไม่", "Check the organizer’s notices for shuttles")}{bi("td", "คนไม่มีรถ", "No car")}</tr>
  </table></div>
</div></div>

<div class="band tone-dark"><div class="in sec banded">
  <div class="seclabel"><span class="num">05</span><span class="n" data-th="ตารางแข่ง" data-en="Schedule">ตารางแข่ง</span>{bi("h2", *H[4])}</div>
  <div class="table-wrap"><table>
    <tr><th data-th="ช่วง" data-en="When">ช่วง</th><th data-th="รายการ" data-en="What">รายการ</th><th data-th="คำแนะนำที่พัก" data-en="Stay tip">คำแนะนำที่พัก</th></tr>
{sched}
  </table></div>
</div></div>

<div class="band tone-white"><div class="in sec banded" id="faq">
  <div class="seclabel"><span class="num">06</span><span class="n" data-th="คำถามบ่อย" data-en="FAQ">คำถามบ่อย</span>{bi("h2", *H[5])}</div>
  <div class="faq2" style="margin-top:16px">
    <details open>{bi("summary", "ควรจองที่พักกี่คืน?", "How many nights should I book?")}{bi("p", "อย่างน้อยคืนก่อนแข่ง (เผื่อรับบิบ) ถ้าวิ่งระยะไกลเผื่ออีกคืนหลังแข่งไว้พักฟื้น", "At least the night before (for BIB pickup); for long distances add a recovery night.")}</details>
    <details>{bi("summary", "ควรพักย่านไหน?", "Where should I stay?")}{bi("p", "แนะนำย่าน " + zone_th + " ที่เดินทางสะดวกถึง" + spot, "We recommend " + zone_en + " — easy to reach the start.")}</details>
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
    fill_handwritten_hotels()
    return made
