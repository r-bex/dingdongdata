import streamlit as st

from analysis.misc import generate_timeline
from model.performance import Performance

def show_trends(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.header("Trends")
    timeline_agg = st.selectbox("Group by:", options=["Day", "Week", "Month", "Year"], index=2)
    timeline_df = generate_timeline(performances, timeline_agg)
    # TODO: move this to altair to get full zooming/panning
    st.bar_chart(timeline_df, x=timeline_agg, y=["Count"], color="Stage")