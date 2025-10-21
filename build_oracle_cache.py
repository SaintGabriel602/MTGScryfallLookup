#!/usr/bin/env python3
import csv, json, gzip, hashlib, sys, re
from datetime import datetime
from pathlib import Path

OWNED_CSV   = "Collection102125.csv"
ORACLE_GZ   = "oracle-cards.json.gz"   # already in your repo

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def sha256(txt: str) -> str:
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()

def load_owned_names(csv_path: str) -> list:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.strip() for h in reader.fieldnames]
        name_col = next((h for h in headers if h.lower() in {
            "name","card","card name","card_name","cardname","cardtitle"
        }), headers[0])
        seen, out = set(), []
        for row in reader:
            nm = norm(row.get(name_col, ""))
            if nm and nm not in seen:
                seen.add(nm); out.append(nm)
        return out

def load_oracle_list() -> list:
    if not Path(ORACLE_GZ).exists():
        print(f"ERROR: {ORACLE_GZ} not found.", file=sys.stderr)
        sys.exit(1)
    with gzip.open(ORACLE_GZ, "rt", encoding="utf-8") as f:
        return json.load(f)

def to_cache_entry(card: dict) -> dict:
    oracle_text = card.get("oracle_text") or ""
    type_line   = card.get("type_line") or ""
    if "card_faces" in card and isinstance(card["card_faces"], list):
        texts = [ (face.get("oracle_text") or "") for face in card["card_faces"] ]
        types = [ (face.get("type_line") or "") for face in card["card_faces"] ]
        oracle_text = "\n//\n".join(texts).strip()
        type_line   = " // ".join(types).strip()
    return {
        "name": card.get("name",""),
        "oracle_id": card.get("oracle_id"),
        "scryfall_id": card.get("id"),
        "set_code": card.get("set"),
        "collector_number": card.get("collector_number"),
        "type_line": type_line,
        "oracle_text": oracle_text,
        "mana_cost": card.get("mana_cost"),
        "mana_value": card.get("cmc"),
        "colors": card.get("colors"),
        "color_identity": card.get("color_identity"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "produced_mana": card.get("produced_mana"),
        "legalities": card.get("legalities",{}),
        "rarity": card.get("rarity"),
        "last_updated_utc": datetime.utcnow().isoformat()+"Z",
        "oracle_hash": sha256(oracle_text)
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: build_oracle_cache.py <out_json>", file=sys.stderr)
        sys.exit(1)
    out_json = sys.argv[1]

    owned_names = set(load_owned_names(OWNED_CSV))
    oracle_cards = load_oracle_list()

    # fast join by name
    name_to_card = {}
    for c in oracle_cards:
        nm = norm(c.get("name",""))
        if nm and nm not in name_to_card:
            name_to_card[nm] = c

    cache_cards, missing = [], []
    for nm in owned_names:
        c = name_to_card.get(norm(nm))
        if c is None:
            missing.append(nm); continue
        cache_cards.append(to_cache_entry(c))

    cache = {
        "_meta": {
            "description": "Owned-only Oracle Text Cache (full Oracle text, no deck filtering).",
            "version": "1.0.0",
            "created_utc": datetime.utcnow().isoformat()+"Z",
            "source": ORACLE_GZ,
            "owned_names_count": len(owned_names),
            "cached_cards_count": len(cache_cards),
            "missing_count": len(missing),
        },
        "cards": cache_cards,
        "missing_names": sorted(missing)
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_json} with {len(cache_cards)} cards; missing {len(missing)}.")

if __name__ == "__main__":
    main()
