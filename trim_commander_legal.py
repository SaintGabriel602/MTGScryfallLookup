import gzip
import json

INPUT_FILE = "commander_legal.json.gz"
OUTPUT_FILE = "commander_legal_trimmed.json.gz"

def trim_card(card):
    trimmed = {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text"),
        "color_identity": card.get("color_identity"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "legal_in_commander": card.get("legalities", {}).get("commander"),
    }

    # If the card has multiple faces, trim both
    if "card_faces" in card:
        trimmed["card_faces"] = [
            {
                "name": face.get("name"),
                "mana_cost": face.get("mana_cost"),
                "type_line": face.get("type_line"),
                "oracle_text": face.get("oracle_text"),
                "power": face.get("power"),
                "toughness": face.get("toughness"),
                "colors": face.get("colors"),
            }
            for face in card["card_faces"]
        ]
    
    return trimmed

def main():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        all_cards = json.load(f)

    trimmed_cards = [trim_card(card) for card in all_cards]

    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as f:
        json.dump(trimmed_cards, f, indent=2, ensure_ascii=False)

    print(f"✅ Trimmed {len(trimmed_cards)} cards to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
