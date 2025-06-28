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
        tpe_values = [entry['tpe'] for entry in data if isinstance(entry.get('tpe'), int)]
        return max(tpe_values) if tpe_values else None
    else:
        print(f"Failed to fetch TPE timeline for pid {pid}, status: {response.status_code}")
        return None

def fetch_and_rank_players():
    players = get_players()
    print(f"Fetched {len(players)} players.")

    ranked_players = []
    for player in players:
        pid = player.get('pid')
        name = player.get('name', 'Unknown')
        draft_season = player.get('draftSeason', 'Unknown')

        if not pid:
            continue

        peak_tpe = get_peak_tpe(pid)
        if peak_tpe is not None:
            ranked_players.append({
                'name': name,
                'pid': pid,
                'draftSeason': draft_season,
                'peakTPE': peak_tpe
            })
        else:
            print(f"No valid TPE data for {name} (pid {pid})")

        time.sleep(0.5)  # To avoid hitting API too hard

    # Sort players by peak TPE descending
    ranked_players.sort(key=lambda x: x['peakTPE'], reverse=True)

    # Write to CSV
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'draftSeason', 'peakTPE'])
        writer.writeheader()
        for p in ranked_players:
            writer.writerow(p)

    print(f"Saved {len(ranked_players)} ranked players to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
