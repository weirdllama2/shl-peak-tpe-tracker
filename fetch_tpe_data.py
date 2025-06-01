import requests
import csv
import time
from config import OUTPUT_FILE, API_URL

def get_all_tpeevents():
    """Fetch all TPE events, returns list of events."""
    url = f"{API_URL}/tpeevents"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch TPE events: {response.status_code}")
        return []

def get_peak_tpe(pid):
    """Fetch peak TPE timeline for a player by pid."""
    url = f"{API_URL}/tpeevents/timeline?pid={pid}&peak=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract max 'tpe' from timeline entries
            return max(entry.get('tpe', 0) for entry in data)
    return None

def fetch_and_rank_players():
    """Process TPE events to find players with TPE >= 1800 and get their peak TPE."""
    events = get_all_tpeevents()
    
    # Aggregate player info from events: {pid: {'name': playerName, 'max_tpe': max_tpe}}
    players = {}
    for event in events:
        pid = event.get('pid')
        name = event.get('playerName')
        # taskDescription might have TPE? If not, skip or add other logic here.
        # Since original used totalTPE ≥ 1800, we need a way to get TPE from event:
        # But the example JSON doesn’t show TPE field in event.
        # So we will fetch timeline for each unique pid, then filter later.
        if pid and name:
            players[pid] = {'name': name}

    ranked_players = []
    for pid, info in players.items():
        peak_tpe = get_peak_tpe(pid)
        if peak_tpe is not None and peak_tpe >= 1800:
            ranked_players.append({
                'name': info['name'],
                'pid': pid,
                'peakTPE': peak_tpe
            })
        time.sleep(1)  # Respect API rate limits
    
    # Sort descending by peakTPE
    ranked_players.sort(key=lambda x: x['peakTPE'], reverse=True)
    
    # Write CSV
    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for player in ranked_players:
            writer.writerow(player)
    
    print(f"Saved rankings to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
