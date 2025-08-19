import streamlit as st

from analysis.dove import get_tower_progress_bars
from model.performance import Performance

def show_progress_stats(performances: list[Performance]) -> None:
    """TODO: docstring"""
    if st.session_state["ring_type"] != "hand":
        st.header("Proportion of X-bell towers rung at")
        performance_type_word = "quarter peals" if st.session_state["performance_type"] == "qp" else "peals"
        st.text(f"You've rung {performance_type_word} at...")
        tower_progress_stats = get_tower_progress_bars(performances)
        for ring_size in [6, 8, 10, 12, 16]:
            (rung_at, total) = tower_progress_stats[ring_size]
            progress_text = f"{rung_at} out of {total} ringable {ring_size}-bell towers."
            st.progress(rung_at/total, text=progress_text)