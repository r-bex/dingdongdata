import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

from model.performance import Performance
from utils import format_total_mins

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

        if p.duration:
            if "h" in p.duration:
                (hours, mins) = p.duration.split("h ")
                total_mins += 60 * int(hours) + int(mins)
            elif "m" in p.duration:
                mins = int(p.duration[:-1])
                total_mins += mins

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric(label="Performances", value=len(performances))
    col2.metric(label="Towers", value=len(set(tower_ids)))
    col3.metric(label="Counties", value=len(set(counties)))
    col4.metric(label="Ringers", value=len(set(ringers)))
    col5.metric(label="Methods", value=len(set(methods)))
    col6.metric(label="Time ringing", value=format_total_mins(total_mins, sig_figs=1))


    style_metric_cards()