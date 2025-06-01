import requests
import csv
import time
from config import API_URL, OUTPUT_FILE

def get_players():
    """Fetch unique players from TPE events."""
    url = f"{API_URL}/tpeevents"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        players = {}
        for event in data:
            pid = event.get("pid")
            name = event.get("playerName")
            if pid and name:
                players[pid] = name  # avoid duplicates
        print(f"Fetched {len(players)} players.")
        return [{'pid': pid, 'name': name} for pid, name in players.items()]
    else:
        print("Error fetching TPE events.")
        return []

def get_peak_tpe(pid):
    """Fetch the peak TPE for a player by their ID."""
    url = f"{API_URL}/tpe/timeline?pid={pid}&peak=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            try:
                return max(entry.get('tpe', 0) for entry in data if isinstance(entry, dict))
            except Exception as e:
                print(f"Error parsing peak TPE for pid {pid}: {e}")
    else:
        print(f"Failed to fetch TPE timeline for pid {pid}, status: {response.status_code}")
    return None

def fetch_and_rank_players():
    """Fetch player data, calculate peak TPE, and write rankings to a CSV file."""
    players = get_players()
    ranked_players = []

    for player in players:
        pid = player['pid']
        name = player['name']
        peak_tpe = get_peak_tpe(pid)
        if peak_tpe and peak_tpe >= 1800:
            ranked_players.append({
                'name': name,
                'pid': pid,
                'peakTPE': peak_tpe
            })
        time.sleep(0.5)  # To reduce server load

    # Sort players by peak TPE in descending order
    ranked_players = sorted(ranked_players, key=lambda x: x['peakTPE'], reverse=True)

    # Save to CSV
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for player in ranked_players:
            writer.writerow(player)

    print(f"Saved {len(ranked_players)} players to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
