# SHL Peak TPE Tracker

This project fetches the peak TPE for SHL players using the Simulation Hockey League API (https://portal.simulationhockey.com/api#tag/TPE-Events/operation/getTPETimeline) and ranks them. This only works for players with portal data available.

## How to run

1. Install the required libraries:
    ```
    pip install -r requirements.txt
    ```

2. Run the tracker script:
    ```
    python peak_tpe_tracker.py
    ```

Output is saved in `/data/peak_tpe_records.csv`.

