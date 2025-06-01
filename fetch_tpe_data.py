import requests
import csv
import time
from config import API_URL, OUTPUT_FILE

def get_players():
    response = requests.get("https://portal.simulationhockey.com/api/v1/players")
    if response.status_code == 200:
        return response.json()
    print("Error fetching players.")
    return []

def get_peak_tpe(pid):
    url = f"{API_URL}/tpe/timeline?pid={pid}&peak=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return max((entry.get('tpe', 0) for entry in data), default=None)
    print(f"Failed to fetch TPE timeline for pid {pid}, status: {response.status_code}")
    return None

def fetch_and_rank_players():
    players = get_players()
    print(f"Fetched {len(players)} players.")
    ranked_players = []

    for i, player in enumerate(players):
        pid = player['pid']
        name = player['name']
        peak_tpe = get_peak_tpe(pid)
        if peak_tpe:
            print(f"{i+1}/{len(players)}: {name} (pid {pid}) - Peak TPE: {peak_tpe}")
            ranked_players.append({
                'name': name,
                'pid': pid,
                'peakTPE': peak_tpe
            })
        time.sleep(0.1)  # Reduced delay to speed up first run

    ranked_players = sorted(ranked_players, key=lambda x: x['peakTPE'], reverse=True)

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for player in ranked_players:
            writer.writerow(player)

    print(f"Saved {len(ranked_players)} players to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
