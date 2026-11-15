"""Fill data/walks.json with on-foot routes from each curated hotel to its venue.

Run by hand when hotels change (the page build never touches the network):
    python3 build/fetch_walks.py
Routes come from the FOSSGIS OSRM foot profile (OpenStreetMap data,
https://routing.openstreetmap.de). Only coordinates are sent. Cached pairs are
skipped, one request per second, so a full refresh of ~40 hotels takes under a minute.
"""
import json
import subprocess
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "walks.json"
HOTELS_DIR = ROOT / "data" / "hotels"
URL = "https://routing.openstreetmap.de/routed-foot/route/v1/driving/{},{};{},{}?overview=false"
UA = "static-site-build/1.0 (walking-distance cache; few requests)"


def key(h_lat, h_lng, v_lat, v_lng):
    return f"{h_lat:.6f},{h_lng:.6f}|{v_lat:.6f},{v_lng:.6f}"


def pairs():
    events = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
    events = events if isinstance(events, list) else events["events"]
    by_slug = {e["slug"]: e for e in events}
    for f in sorted(HOTELS_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if "groups" in data:  # hand-written atm-2026 page: one venue per group
            for g in data["groups"].values():
                for h in g["hotels"]:
                    yield h, g["lat"], g["lng"]
            continue
        ev = by_slug.get(data.get("event", f.stem))
        venue = data.get("near") or (ev or {}).get("detail")
        if not venue:
            continue
        for h in data.get("hotels", []):
            yield h, venue["lat"], venue["lng"]


def main():
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    routes = cache.setdefault("routes", {})
    cache["_comment"] = ("Walking routes hotel -> venue from the FOSSGIS OSRM foot profile (OpenStreetMap). "
                         "m = metres, s = seconds, on = fetch date. Filled by build/fetch_walks.py.")
    added = 0
    for h, v_lat, v_lng in pairs():
        k = key(h["lat"], h["lng"], v_lat, v_lng)
        if k in routes:
            continue
        # curl, not urllib: the macOS system Python's old SSL fails the server's TLS handshake
        out = subprocess.run(["curl", "-sS", "-m", "20", "-A", UA, URL.format(h["lng"], h["lat"], v_lng, v_lat)],
                             capture_output=True, text=True, check=True).stdout
        res = json.loads(out)
        if res.get("code") != "Ok" or not res.get("routes"):
            print("no route:", h["name"], res.get("code"))
            continue
        rt = res["routes"][0]
        routes[k] = {"m": round(rt["distance"]), "s": round(rt["duration"]), "on": date.today().isoformat(), "name": h["name"]}
        added += 1
        print(f'{h["name"]}: {routes[k]["m"]} m, {routes[k]["s"] // 60} min')
        time.sleep(1)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added {added}, cached {len(routes)}")


if __name__ == "__main__":
    main()
