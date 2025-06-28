# season_watcher.py

import json
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import subprocess  # to trigger the main script

CONFIG_FILE = 'last_seen_season.json'
ANNOUNCE_URL = 'https://simulationhockey.com/forumdisplay.php?fid=24'
OFFSEASON_PATTERN = re.compile(r'S(\d+)\s+Offseason Post', re.IGNORECASE)

def load_last_seen():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"season": 0, "date": ""}

def save_last_seen(season, date_str):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"season": season, "date": date_str}, f)

def fetch_latest_offseason():
    resp = requests.get(ANNOUNCE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Find all thread titles in announcements
    titles = soup.find_all('a', string=OFFSEASON_PATTERN)
    if not titles:
        return None, None

    # Take the first/latest
    title = titles[0].get_text(strip=True)
    match = OFFSEASON_PATTERN.search(title)
    season = int(match.group(1))

    # Extract date from corresponding row
    row = titles[0].find_parent('tr')
    # example date format: "06-02-2025"
    date_span = row.find('td', class_='alt1')
    if date_span:
        date_str = date_span.get_text(strip=True)
    else:
        date_str = datetime.utcnow().strftime('%Y-%m-%d')  # fallback

    return season, date_str

def main():
    last = load_last_seen()
    latest_season, latest_date = fetch_latest_offseason()

    if latest_season is None:
        print("No Offseason Post found.")
        return

    print(f"Last seen season: S{last['season']}, Latest found: S{latest_season} on {latest_date}")

    if latest_season > last['season']:
        print(f"➡️ New season S{latest_season} detected on {latest_date}! Triggering snapshot...")

        # Run the  main snapshot script here
        # Example: python fetch_peak_tpe.py
        subprocess.run(['python', 'fetch_tpe_data.py'], check=True)

        save_last_seen(latest_season, latest_date)
        print("✅ Updated last seen season.")
    else:
        print("ℹ️ No new season since last check.")

if __name__ == '__main__':
    main()
