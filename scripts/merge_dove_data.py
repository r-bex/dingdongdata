# This script assumes as a starting point that you have downloaded a CSV of all ringable rings from Doves
# to data/dove/dove_towers.csv and a CSV of bells from Doves to data/dove/dove_bells.csv. The links are below.
# Rings - https://dove.cccbr.org.uk/dove?ringable=1
# Bells - https://dove.cccbr.org.uk/bells?bells=3%2B&ringable=1&ring_type=all+english
# This script will take the relevant columns from each and do a join to produce a file "dove_merged.csv"
# containing just the data needed for this app.

from pathlib import Path

import pandas as pd

from utils import get_project_root

PROJECT_ROOT = get_project_root()
TOWER_PATH = f"{PROJECT_ROOT}/data/dove/dove_towers.csv"
BELL_PATH = f"{PROJECT_ROOT}/data/dove/dove_bells.csv"
SUMMARY_PATH = f"{PROJECT_ROOT}/data/dove/dove_merged.csv"

def generate_summary_table():
    """Merge towers and bells dataframes to get required data for app"""
    tower_df = pd.read_csv(TOWER_PATH).reset_index()
    tower_df = tower_df[["TowerID", "RingID", "Place", "Dedicn", "County", "Lat", "Long"]]
    print(f"Towers file loaded: {len(tower_df)} towers.")

    bell_df = pd.read_csv(BELL_PATH).reset_index()
    bell_df = bell_df[["Tower ID", "Ring ID", "Ring Size", "Bell Role", "Weight (lbs)"]]
    bell_df.columns = ["TowerID", "RingID", "RingSize", "BellRole", "WeightLbs"]
    print(f"Bells file loaded: {len(bell_df)} bells.")

    df = tower_df.merge(right=bell_df, how="inner", on=["TowerID", "RingID"])
    df.to_csv(f"{PROJECT_ROOT}/data/dove/dove_merged.csv", index=False)
    print(f"Merged table of {len(df)} rows written to {SUMMARY_PATH}")

if __name__ == "__main__":
    generate_summary_table()