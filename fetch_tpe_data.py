import requests
import csv
import time
import os

API_BASE = "https://portal.simulationhockey.com/api/v1"

def fetch_all_players():
    url = f"{API_BASE}/player"
    print("Fetching player list...")
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def get_peak_tpe(pid):
    url = f"{API_BASE}/player/peak-tpe?pid={pid}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json().get("peakTpe")

def load_previous_data(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['pid']: int(row['peakTPE']) for row in reader}

def save_current_data(players, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "pid", "peakTPE", "change"])
        writer.writeheader()
        for player in players:
            writer.writerow(player)

def main():
    previous_file = "peak_tpe_rankings_previous.csv"
    output_file = "peak_tpe_rankings.csv"

    players = fetch_all_players()
    peak_data = []

    print(f"Checking {len(players)} players...")
    for i, player in enumerate(players):
        pid = str(player["pid"])
        name = player["name"]
        peak = get_peak_tpe(pid)
        if peak and peak >= 2000:
            peak_data.append({"name": name, "pid": pid, "peakTPE": peak})
        time.sleep(0.2)  # Prevent hammering API
        if i % 100 == 0 and i != 0:
            print(f"...{i} players processed")

    print(f"Found {len(peak_data)} players with ≥2000 peak TPE")

    # Sort new data by peakTPE descending
    peak_data.sort(key=lambda x: -x["peakTPE"])

    # Load previous data
    previous = load_previous_data(previous_file)
    prev_ranks = {pid: rank for rank, (pid, _) in enumerate(
        sorted(previous.items(), key=lambda x: -x[1]), start=1)}

    # Add change info
    for rank, player in enumerate(peak_data, start=1):
        pid = player["pid"]
        if pid not in previous:
            player["change"] = "NEW"
        else:
            prev_rank = prev_ranks.get(pid)
            if prev_rank and prev_rank > rank:
                player["change"] = f"↑{prev_rank - rank}"
            else:
                player["change"] = ""

    # Save updated data
    save_current_data(peak_data, output_file)
    print(f"✅ Saved {len(peak_data)} players to {output_file}")
    print("📌 Previous file management is handled automatically by CI.")

if __name__ == "__main__":
    main()
