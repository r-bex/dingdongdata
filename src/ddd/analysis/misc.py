from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from model.performance import Performance
from model.enums import RingType, PerformanceType, Stage

def strip_label_counts(label: str) -> str:
    """TODO: docstring"""
    return label.split(" ")[0]

# TODO: rename
def basic_filter(all_performances: list[Performance]) -> list[Performance]:
    """TODO:docstring"""
    if not all_performances:
        return []

    sanitised_ring_type = strip_label_counts(st.session_state["ring_type"])
    acceptable_ring_types = ["hand", "tower"] if sanitised_ring_type == "both" else [sanitised_ring_type]
    perfs = [p for p in all_performances if p.place.ring_details.ring_type in acceptable_ring_types]

    sanitised_perf_type = strip_label_counts(st.session_state["performance_type"])
    acceptable_performance_types = ["qp", "peal"] if sanitised_perf_type == "both" else [sanitised_perf_type]
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
        perfs = [p for p in perfs if st.session_state["stage_filter"] in p.method_details.extract_stages()]
    
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
        stages += performance.method_details.extract_stages()
    return list(set(stages))

# TODO: move to be on performances object
# TODO: write tests
def get_top_methods_by_stage(performances: list[Performance], stage: str | None) -> pd.DataFrame:
    """TODO: docstring"""
    all_methods = []
    for p in performances:
        for perf_stage in p.method_details.extract_stages():
            all_methods.append({
                "Stage": perf_stage,
                "Method": p.method_details.method_name
            })
    df = pd.DataFrame(all_methods)

    if stage is not None:
        df = df[df["Stage"] == stage]
    # Group by stage and method to get count
    grouped = df.groupby(by=["Method"]).count().reset_index()
    grouped.columns = ["Method", "Count"]
    return grouped.sort_values(by="Count", ascending=False)

# TODO: write tests
def generate_timeline(performances: list[Performance], agg_level: str, hide_gaps: bool) -> pd.DataFrame:
    """TODO: docstring"""
    sorted_perfs = sorted(performances, key=lambda p: p.date)
    
    date_generators = {
        "Day": lambda day: day,
        "Year": lambda day: day.year,
        "Month": lambda day: day.strftime("%Y-%m"),
        "Week": lambda day: (day - timedelta(day.weekday())).isoformat()
    }

    dicts = []
    aggs_added = []
    for p in performances:
        day = date.fromisoformat(p.date)
        stages = p.method_details.extract_stages()
        # TODO: choose a stage if multiple?
        for stage in p.method_details.extract_stages():
            agg_date = date_generators[agg_level](day)
            aggs_added.append(agg_date)
            dicts.append({
                agg_level: agg_date,
                "Stage": str(stage.get_ordinal())
            })

    df = pd.DataFrame(dicts)
    df = df[[agg_level, "Stage"]]

    grouped_df = df.groupby(by=[agg_level, "Stage"]).size().reset_index()
    grouped_df.columns = [agg_level, "Stage", "Count"]

    if not hide_gaps:
        gap_df_dicts = []

        earliest_perf_date = date.fromisoformat(sorted_perfs[0].date)
        latest_perf_date = date.fromisoformat(sorted_perfs[-1].date)

        # Generate all times between first perf and last perf
        all_days = pd.date_range(earliest_perf_date , latest_perf_date - timedelta(days=1),freq='d').tolist()
        at_agg_level = list(set([date_generators[agg_level](day) for day in all_days]))

        # Add a zero count entry to the df if it's not in there already
        for possible_agg_level in at_agg_level:
            if possible_agg_level not in aggs_added:
                gap_df_dicts.append({
                    agg_level: possible_agg_level,
                    "Count": 0
                })
    
        gap_df = pd.DataFrame(gap_df_dicts)
        grouped_df = pd.concat([grouped_df, gap_df])
                
    return grouped_df
