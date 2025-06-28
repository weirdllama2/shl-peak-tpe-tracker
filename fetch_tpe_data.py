import json
import os
import time
import requests
from config import API_URL, OUTPUT_FILE

CACHE_FILE = 'peak_tpe_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_players():
    players_url = f"{API_URL}/player"
    response = requests.get(players_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching players: Status {response.status_code}")
        return []

def get_peak_tpe(pid):
    url = f"{API_URL}/tpeevents/timeline?pid={pid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return max(entry.get('tpe', 0) for entry in data)
    print(f"No valid TPE data for pid {pid}")
    return None

def fetch_and_rank_players():
    cache = load_cache()
    players = get_players()
    print(f"Fetched {len(players)} players.")

    ranked_players = []
    for player in players:
        pid = str(player.get('pid'))
        tpe = player.get('totalTPE', 0)
        if tpe >= 1800:
            if pid in cache:
                peak_tpe = cache[pid]
            else:
                peak_tpe = get_peak_tpe(pid)
                if peak_tpe is not None:
                    cache[pid] = peak_tpe
                else:
                    continue
            ranked_players.append({
                'name': player.get('name', 'Unknown'),
                'pid': pid,
                'peakTPE': peak_tpe
            })
            time.sleep(0.5)  # polite delay

    ranked_players.sort(key=lambda x: x['peakTPE'], reverse=True)

    with open(OUTPUT_FILE, 'w', newline='') as file:
        import csv
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for p in ranked_players:
            writer.writerow(p)

    save_cache(cache)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
