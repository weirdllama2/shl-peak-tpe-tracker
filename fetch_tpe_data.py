import requests
import csv
import time
from config import API_URL, OUTPUT_FILE

def get_players():
    """Fetch all players from /player endpoint."""
    players_url = f"{API_URL}/player"
    response = requests.get(players_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching players: Status {response.status_code}")
        return []

def get_peak_tpe(pid):
    """Fetch the TPE timeline for a player and return peak TPE."""
    url = f"{API_URL}/tpeevents/timeline?pid={pid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Find max 'tpe' in the timeline entries
            return max(entry.get('tpe', 0) for entry in data)
        else:
            return None
    else:
        print(f"Failed to fetch TPE timeline for pid {pid}, status: {response.status_code}")
        return None

def fetch_and_rank_players():
    players = get_players()
    print(f"Fetched {len(players)} players.")

    ranked_players = []
    for player in players:
        tpe = player.get('totalTPE', 0)
        pid = player.get('pid')
        if tpe >= 1800 and pid:
            peak_tpe = get_peak_tpe(pid)
            if peak_tpe is not None:
                ranked_players.append({
                    'name': player.get('name', 'Unknown'),
                    'pid': pid,
                    'peakTPE': peak_tpe
                })
            else:
                print(f"No timeline data for pid {pid}")
            time.sleep(0.5)  # reduce rate to be polite
    ranked_players.sort(key=lambda x: x['peakTPE'], reverse=True)

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for p in ranked_players:
            writer.writerow(p)

    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
