from collections import defaultdict
import logging
import pandas as pd
import streamlit as st
import random
import folium
import branca

from model.performance import Performance
from utils import extract_saints, get_project_root

logger = logging.getLogger()

# What do I need to know?
# - has someone circled the tower (can only know if tenor weight provided)
# - heaviest bell rung
# - location

# dove_towers.csv has
# - TowerID
# - RingID
# - Lat
# - Long
# - Bells (number of bells)

# dove_bells.csv has
# - BellID
# - TowerID
# - RingID
# - Ring Size
# - Bell Role
# - Weight (lbs)

PROJECT_ROOT = get_project_root()
MERGED_DATA_PATH = f"{PROJECT_ROOT}/data/dove/dove_merged.csv"

# TODO: write tests
def load_tower_data() -> pd.DataFrame:
    """
    Fetch the merged tower & bell data from Doves
    :return: a pandas DataFrame of the merged data
    """
    df = pd.read_csv(MERGED_DATA_PATH)
    return df

# TODO: write tests
def get_performance_map(performances: list[Performance]) -> folium.Map:
    """
    Generates a mapping between tower ID and number of performances there
    :param performances: a list of Performance objects
    :return: a folium Map displaying performance locations
    """
    perfs = defaultdict(int)
    for performance in performances:
        tower_id = performance.place.dove_tower_id
        if tower_id:
            perfs[tower_id] += 1
    
    wide_df = pd.DataFrame([{
        "TowerID": int(k),
        "PerformanceCount": v
    } for k, v in perfs.items()])

    tower_df = load_tower_data()
    tower_df = tower_df[["TowerID", "Place", "Dedicn", "Lat", "Long"]]

    merged_df = wide_df.merge(
        tower_df, how="inner", on="TowerID"
    ).dropna().drop_duplicates().sort_values(by="PerformanceCount", ascending=True)

    avg_lat = merged_df["Lat"].mean()
    avg_lng = merged_df["Long"].mean()

    perf_counts = list(merged_df["PerformanceCount"])
    total_perf_count = sum(perf_counts)

    #Initialise map
    m = folium.Map(location=[avg_lat, avg_lng], zoom_start=6)

    # Create colourmap
    colormap = branca.colormap.LinearColormap(
        colors=["blue", "red"],
        index=[0, max(perf_counts)/total_perf_count]
    )
    # colormap.caption = 'Performance count'
    # colormap.add_to(m)

    for row in merged_df.itertuples():
        folium.CircleMarker(
            [row.Lat, row.Long],
            color=colormap(row.PerformanceCount/total_perf_count),
            fillColor=colormap(row.PerformanceCount/total_perf_count),
            opacity=0.8,
            radius=5,
            tooltip=f"{row.Place} ({row.Dedicn})\n{row.PerformanceCount} performances"
        ).add_to(m)
    return m

# TODO: write tests
def get_tower_progress_bars(performances: list[Performance]) -> dict[int, (int, int)]:
    """
    Calculate 'completion' stats of towers by number of bells
    :param performances: a list of Performance objects
    :return: a mapping between number of bells and a tuple (num_rung_at, total_num)
    """
    perf_tower_ids = [perf.place.dove_tower_id for perf in performances]
    tower_df = load_tower_data()[["TowerID", "RingSize"]].drop_duplicates()
    tower_df["RungAt"] = tower_df["TowerID"].apply(lambda tower_id: str(tower_id) in perf_tower_ids)
    grpd = tower_df.groupby(["RingSize", "RungAt"]).size().reset_index()
    grpd.columns = ["RingSize", "RungAt", "Count"]

    results = {}
    for ring_size in [6, 8, 10, 12, 16]:
        rung_at_df = grpd[grpd.RingSize == ring_size][grpd.RungAt == True]
        if len(rung_at_df):
            rung_at = rung_at_df["Count"].values[0]
        else:
            rung_at = 0
        total = grpd[grpd.RingSize == ring_size]["Count"].sum()
        results[ring_size] = (int(rung_at), int(total))

    return results

def get_all_saints() -> list[str]:
    """TODO: docstring"""
    # Dedicn
    df = load_tower_data()
    dedications = list(df["Dedicn"].drop_duplicates())
    saints = []
    for dedication in dedications:
        for saint in extract_saints(dedication):
            if saint not in saints:
                saints.append(saint)
    return saints

def get_all_counties() -> list[str]:
    """TODO: docstring"""
    df = load_tower_data()
    counties = list(df["County"].drop_duplicates().dropna())
    return counties