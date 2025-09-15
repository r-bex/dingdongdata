from collections import defaultdict
import logging
import math
import pandas as pd
import folium
import branca
import streamlit as st

from model.performance import Performance
from model.tower import Tower, Bell, Coordinates
from utils import extract_saints_from_dedication, extract_true_bell_no, get_project_root

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
@st.cache_data
def load_tower_data() -> pd.DataFrame:
    """
    Fetch the merged tower & bell data from Doves
    :return: a pandas DataFrame of the merged data
    """
    df = pd.read_csv(MERGED_DATA_PATH)
    return df

# TODO: write tests
@st.cache_data
def load_modelled_towers(df: pd.DataFrame) -> list[Tower]:
    """Load modelled towers from merged Dove df."""
    # Replace empty fields with None, e.g. unknown bell weight, miniring dedication
    df = df.replace({float('nan'): None})

    towers = []
    ring_ids = list(df["RingID"].drop_duplicates())
    for ring_id in ring_ids:
        sub_df = df[df.RingID == ring_id]
        first_row = sub_df.iloc[0]

        ring_size = str(first_row.RingSize)
        bells = [
            Bell(true_number=extract_true_bell_no(r.BellRole), weight_lbs=r.WeightLbs)
            for r in sub_df.itertuples() if extract_true_bell_no(r.BellRole)
        ]
        tenor_weight = [b for b in bells if str(b.true_number) == ring_size][0].weight_lbs

        if first_row.Lat:
            coordinates = Coordinates(latitude=first_row.Lat, longitude=first_row.Long)
        else:
            coordinates = None

        towers.append(
            Tower(
                dove_tower_id=str(first_row.TowerID),
                dove_ring_id=str(ring_id),
                place=first_row.Place,
                county=first_row.County,
                dedication=first_row.Dedicn,
                location=coordinates,
                bells=bells,
                tenor_weight_lbs=tenor_weight,
                num_bells=ring_size
            )
        )
    
    return towers

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

    #Initialise map
    m = folium.Map(location=[avg_lat, avg_lng])

    # Create colourmap
    colormap = branca.colormap.LinearColormap(
        #colors=["blue", "red"],
        colors=["#0033FC", "#FC0054"],
        index=[1, math.log(max(perf_counts))]
    )

    for row in merged_df.sort_values(by="PerformanceCount", axis=0, ascending=True).itertuples():
        folium.CircleMarker(
            [row.Lat, row.Long],
            color=colormap(math.log(row.PerformanceCount)),
            fillColor=colormap(math.log(row.PerformanceCount)),
            opacity=0.8,
            radius=7,
            tooltip=f"{row.Place} ({row.Dedicn})\n{row.PerformanceCount} performances"
        ).add_to(m)

    # Calculate bounds to show all features in initial view
    sw = merged_df[['Lat', 'Long']].min().values.tolist()
    ne = merged_df[['Lat', 'Long']].max().values.tolist()
    m.fit_bounds([sw, ne]) 

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
        for saint in extract_saints_from_dedication(dedication):
            if saint not in saints:
                saints.append(saint)
    return saints

def get_all_counties() -> list[str]:
    """TODO: docstring"""
    df = load_tower_data()
    counties = list(df["County"].drop_duplicates().dropna())
    return counties
