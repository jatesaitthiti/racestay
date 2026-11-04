"""Thai names for values stored in English (places, cities, distance names): data/th-names.json."""
import json
from pathlib import Path

_DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "th-names.json").read_text(encoding="utf-8"))


def place_th(en):
    try:
        return _DATA["places"][en]
    except KeyError:
        raise SystemExit(f"No Thai name for place '{en}': add it to data/th-names.json")


def distance_th(en):
    try:
        return _DATA["distances"][en]
    except KeyError:
        raise SystemExit(f"No Thai name for distance '{en}': add it to data/th-names.json")
