import requests
import json
import gzip
from datetime import datetime

# Step 1: Download Scryfall bulk index
bulk_index_url = "https://api.scryfall.com/bulk-data"
bulk_index = requests.get(bulk_index_url).json()

# Step 2: Locate default_cards file
default_cards_info = next(entry for entry in bulk_index['data'] if entry['type'] == 'default_cards')
download_url = default_cards_info['download_uri']

# Step 3: Download full card dataset
response = requests.get(download_url)
all_cards = response.json()

# Step 4: Filter to latest commander-legal version per card name
latest_cards = {}
for card in all_cards:
    if card.get("legalities", {}).get("commander") == "legal":
        name = card.get("name")
        released_at = card.get("released_at", "0000-00-00")
        if name not in latest_cards or released_at > latest_cards[name].get("released_at", "0000-00-00"):
            latest_cards[name] = card

# Step 5: Write to compressed .json.gz
with gzip.open("commander_legal.json.gz", "wt", encoding="utf-8") as f:
    json.dump(list(latest_cards.values()), f, indent=2, ensure_ascii=False)

print(f"Wrote {len(latest_cards)} commander-legal cards to commander_legal.json.gz")
