import streamlit as st
from streamlit_folium import st_folium

from analysis.dove import get_performance_map
from model.performance import Performance

def show_map(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.header("Performance map")
    if st.session_state["performance_type"] in ["hand", "both"]:
        st.text("Handbell performances are not shown on the map.")
    performance_map = get_performance_map(performances)
    st_folium(performance_map, width=725, returned_objects=[])