import requests
import csv
import time
import os
from config import API_URL, OUTPUT_FILE

def get_players():
    url = f"{API_URL}/players"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching players.")
        return []

def load_existing_data():
    if not os.path.exists(OUTPUT_FILE):
        return {}
    
    existing = {}
    with open(OUTPUT_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            pid = int(row['pid'])
            existing[pid] = {
                'name': row['name'],
                'peakTPE': int(row['peakTPE'])
            }
    return existing

def get_peak_tpe(pid):
    url = f"{API_URL}/tpe/timeline?pid={pid}&peak=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            return max(entry.get('tpe', 0) for entry in data if isinstance(entry, dict))
    else:
        print(f"Failed to fetch TPE timeline for pid {pid}, status: {response.status_code}")
    return None

def fetch_and_rank_players():
    print("Fetching player list...")
    players = get_players()
    existing_data = load_existing_data()
    updated_data = {}

    for player in players:
        pid = player.get('pid')
        name = player.get('name')
        total_tpe = player.get('totalTPE', 0)

        if total_tpe < 1800:
            continue

        # Reuse existing data if available
        if pid in existing_data:
            updated_data[pid] = {
                'name': name,
                'peakTPE': existing_data[pid]['peakTPE']
            }
            continue

        # Otherwise fetch fresh peak TPE
        peak_tpe = get_peak_tpe(pid)
        if peak_tpe:
            updated_data[pid] = {
                'name': name,
                'peakTPE': peak_tpe
            }

        time.sleep(0.5)  # Respect the API

    # Sort by peak TPE descending
    ranked_players = sorted(updated_data.items(), key=lambda x: x[1]['peakTPE'], reverse=True)

    # Write to CSV
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for pid, data in ranked_players:
            writer.writerow({
                'name': data['name'],
                'pid': pid,
                'peakTPE': data['peakTPE']
            })

    print(f"Updated {len(ranked_players)} players and saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
