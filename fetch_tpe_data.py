import requests
import csv
import time
from config import API_URL, OUTPUT_FILE

def get_players():
    """Fetch all players, return player IDs."""
    players_url = "https://portal.simulationhockey.com/api/v1/players"  # Replace this with the actual endpoint for player list
    response = requests.get(players_url)
    if response.status_code == 200:
        return response.json()  # Assuming the player list is returned as JSON
    else:
        print("Error fetching players.")
        return []

def get_peak_tpe(pid):
    """Fetch the peak TPE for a player by their ID."""
    url = f"{API_URL}/tpe/timeline?pid={pid}&peak=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return max([entry['tpe'] for entry in data])  # Get the peak TPE from the timeline
    return None

def fetch_and_rank_players():
    """Fetch player data, calculate peak TPE, and write rankings to a CSV file."""
    players = get_players()
    ranked_players = []
    
    for player in players:
        if player['totalTPE'] >= 1800:  # Only include players with TPE >= 1800
            peak_tpe = get_peak_tpe(player['pid'])
            if peak_tpe:
                ranked_players.append({
                    'name': player['name'],
                    'pid': player['pid'],
                    'peakTPE': peak_tpe
                })
            time.sleep(1)  # Be respectful to the API (avoid hitting rate limits)
    
    # Sort players by peak TPE in descending order
    ranked_players = sorted(ranked_players, key=lambda x: x['peakTPE'], reverse=True)
    
    # Save the data to a CSV file
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'pid', 'peakTPE'])
        writer.writeheader()
        for player in ranked_players:
            writer.writerow(player)
    
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    fetch_and_rank_players()
