# SHL Peak TPE Tracker

This project automatically fetches and ranks the **peak TPE** for Simulation Hockey League players using the [SHL API](https://portal.simulationhockey.com/api#tag/TPE-Events/operation/getTPETimeline).  
It only includes players who have data available on the SHL portal.

---

## How It Works

- **Data Source:** SHL Player Portal API  
- **Automation:** GitHub Actions run the script manually or when a new season begins  
- **Filtering:** Only players with ≥2000 peak TPE are included  
- **Comparison:** Latest ranking is compared against the previous snapshot

---

## Output Files

- `peak_tpe_rankings.csv`: Most recent peak TPE rankings  
- `peak_tpe_rankings_previous.csv`: Snapshot of rankings from the last run  

Each run:
- Renames the current output file to `_previous.csv`
- Generates a fresh ranking
- Commits and pushes both files automatically

---

## Running Locally

1. Install the required libraries:
    ```bash
    pip install requests beautifulsoup4
    ```

2. Run the main script:
    ```bash
    python fetch_tpe_data.py
    ```

3. To check for a new SHL season and trigger the tracker:
    ```bash
    python season_watcher.py
    ```

---

## Dependencies

The Python scripts use:

- `requests` – for API calls  
- `beautifulsoup4` – for parsing HTML content  
- `datetime`, `json`, `re`, `os`, `subprocess`, `csv`, `time` – standard library

---

## Automation

This repository uses GitHub Actions to:
- Detect a new SHL season via `season_watcher.py`
- Run the tracker via `fetch_tpe_data.py`
- Rename files and commit updated rankings

You can also trigger the workflow manually via the **Actions** tab in GitHub.
