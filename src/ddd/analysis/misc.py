from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from model.performance import Performance
from model.enums import RingType, PerformanceType, Stage

# TODO: rename
def basic_filter(all_performances: list[Performance]) -> list[Performance]:
    """TODO:docstring"""
    if not all_performances:
        return []
    
    perfs = acceptable_ring_types = ["hand", "tower"] if st.session_state["ring_type"] == "both" else [st.session_state["ring_type"]]
    perfs = [p for p in all_performances if p.place.ring_details.ring_type in acceptable_ring_types]

    acceptable_performance_types = ["qp", "peal"] if st.session_state["performance_type"] == "both" else [st.session_state["performance_type"]]
    perfs = [p for p in perfs if p.determine_performance_type() in acceptable_performance_types]
    
    if st.session_state["conductor_only"]:
        perfs = [p for p in perfs if p.ringer_is_conductor(st.session_state["accepted_names"])]

    return perfs

# TODO: write tests
def advanced_filter(all_performances: list[Performance]) -> list[Performance]:
    """TODO: Docstring"""
    if not all_performances:
        return []
    
    perfs = all_performances

    if st.session_state["association_filter"] != "All":
        perfs = [p for p in perfs if p.association == st.session_state["association_filter"]]

    if st.session_state["town_filter"] != "All":
        perfs = [p for p in perfs if p.place.extract_town_name() == st.session_state["town_filter"]]

    if st.session_state["county_filter"] != "All":
        perfs = [p for p in perfs if p.place.extract_county_name() == st.session_state["county_filter"]]

    if st.session_state["stage_filter"] != "All":
        perfs = [p for p in perfs if p.method_details.extract_stage() == st.session_state["stage_filter"]]
    
    return perfs

    
# TODO: write tests
def generate_pandas_dataframe(performances: list[Performance]) -> pd.DataFrame:
    """TODO: docstring"""
    for p in performances:
        try:
            p.place.pretty_print()
        except:
            st.header(p)
    dct_data = [{
        "date": p.date,
        "place": p.place.pretty_print(),
        "method": p.method_details.pretty_print()
    } for p in performances]
    return pd.DataFrame(dct_data)

# TODO: write tests
def get_leading_coringers(performances: list[Performance], names: list[str], min_performances: int = 5) -> pd.DataFrame:
    """TODO: docstring"""
    dd = defaultdict(int)
    for performance in performances:
        for ringer in performance.get_ringers():
            if ringer not in names:
                dd[ringer] += 1

    df = pd.DataFrame([{"ringer": k, "count": v} for k, v in dd.items()])
    # Filter by min_performances
    df = df[df["count"] >= min_performances]
    # Sort by count descending
    return df.sort_values(by="count", ascending=False)

# TODO: write tests
def get_leading_conductors(performances: list[Performance], names: list[str]) -> pd.DataFrame:
    """TODO: docstring"""
    dd = defaultdict(int)
    for performance in performances:
        for conductor in performance.get_conductor_names():
            if conductor not in names:
                dd[conductor] += 1

    df = pd.DataFrame([{"conductor": k, "count": v} for k, v in dd.items()])
    return df.sort_values(by="count", ascending=False)

# TODO: move to be on performances object
# TODO: write tests
def get_top_associations(performances: list[Performance]) -> pd.DataFrame:
    """TODO: docstring"""
    dd = defaultdict(int)
    for performance in performances:
        if performance.association:
            dd[performance.association] += 1

    df = pd.DataFrame([{"association": k, "count": v} for k, v in dd.items()])
    return df.sort_values(by="count", ascending=False)

# TODO: move to be on performances object
# TODO: write tests
def get_all_stages_rung(performances: list[Performance]) -> list[Stage]:
    """TODO: docstring"""
    stages = []
    for performance in performances:
        stages.append(performance.method_details.extract_stage())
    return list(set(stages))

# TODO: move to be on performances object
# TODO: write tests
def get_top_methods_by_stage(performances: list[Performance], stage: str | None) -> pd.DataFrame:
    """TODO: docstring"""
    df = pd.DataFrame([{
        "Stage": p.method_details.extract_stage(),
        "Method": p.method_details.method_name
    } for p in performances])
    if stage is not None:
        df = df[df["Stage"] == stage]
    # Group by stage and method to get count
    grouped = df.groupby(by=["Method"]).count().reset_index()
    grouped.columns = ["Method", "Count"]
    return grouped.sort_values(by="Count", ascending=False)

# TODO: write tests
def generate_timeline(performances: list[Performance], agg_level: str) -> pd.DataFrame:
    """TODO: docstring"""
    date_generators = {
        "Day": lambda day: day,
        "Year": lambda day: day.year,
        "Month": lambda day: day.strftime("%Y-%m"),
        "Week": lambda day: (day - timedelta(day.weekday())).isoformat()
    }

    dicts = []
    for p in performances:
        day = date.fromisoformat(p.date)
        dicts.append({
            agg_level: date_generators[agg_level](day),
            "Stage": p.method_details.extract_stage()
        })
    df = pd.DataFrame(dicts)

    df = df[[agg_level, "Stage"]]

    grouped_df = df.groupby(by=[agg_level, "Stage"]).size().reset_index()
    grouped_df.columns = [agg_level, "Stage", "Count"]
    return grouped_df
