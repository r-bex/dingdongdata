import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

from analysis.weights import get_heaviest_bell_rung
from model.performance import Performance

def _format_total_mins(mins: int, sig_figs: int = 3) -> str:
    """TODO: docstring"""
    if mins < 60:
        return f"{mins} minutes"
    if mins < 24*60:
        hours = round(mins/60, sig_figs)
        return f"{hours} hours"
    if mins < 7*24*60:
        days = round(mins/(60*24), sig_figs)
        return f"{days} days"
    if mins < 52*7*24*60:
        weeks = round(mins/(60*24*7), sig_figs)
        return f"{weeks} weeks"
    years = round(mins/(52*7*24*60), sig_figs)
    return f"{years} years"

def show_headline_stats(performances: list[Performance]) -> None:
    """TODO: docstring"""
    # You have rung X performances in Y towers with Z ringers.
    # Your heaviest bell is X and you have spent approx X hours ringing.
    # TODO: account for handbell locations
    st.header("Vital statistics")
    tower_ids = []
    ringers = []
    counties = []
    methods = []
    total_mins = 0

    for p in performances:
        if p.place.dove_tower_id:
            tower_ids.append(p.place.dove_tower_id)

        ringers += p.get_ringers()

        county = p.place.extract_county_name()
        counties.append(county)

        methods.append(p.method_details.method_name)

        total_mins += p.extract_duration_minutes()

    # heaviest_bell = get_heaviest_bell_rung(performances)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    # col7, col8, col9 = st.columns(3)

    col1.metric(label="Performances", value=len(performances))
    col2.metric(label="Towers", value=len(set(tower_ids)))
    col3.metric(label="Counties", value=len(set(counties)))
    col4.metric(label="Ringers", value=len(set(ringers)))
    col5.metric(label="Methods", value=len(set(methods)))
    col6.metric(label="Time ringing", value=_format_total_mins(total_mins, sig_figs=1))
    #col7.metric(label="Heaviest bell rung", value=heaviest_bell)


    style_metric_cards()