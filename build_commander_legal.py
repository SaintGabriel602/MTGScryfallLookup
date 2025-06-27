import requests
import json
from datetime import datetime

# Download the bulk data index
bulk_index_url = "https://api.scryfall.com/bulk-data"
bulk_index = requests.get(bulk_index_url).json()

# Find the default cards file
default_cards_info = next(entry for entry in bulk_index['data'] if entry['type'] == 'default_cards')
download_url = default_cards_info['download_uri']

# Download the full card list
response = requests.get(download_url)
all_cards = response.json()

# Filter to commander-legal and keep only latest printing per card name
latest_cards = {}
for card in all_cards:
    if card.get("legalities", {}).get("commander") == "legal":
        name = card.get("name")
        released_at = card.get("released_at", "0000-00-00")
        if name not in latest_cards or released_at > latest_cards[name].get("released_at", "0000-00-00"):
            latest_cards[name] = card

# Write filtered data to file
with open("commander_legal.json", "w", encoding="utf-8") as f:
    json.dump(list(latest_cards.values()), f, indent=2, ensure_ascii=False)

print(f"Wrote {len(latest_cards)} commander-legal cards.")
