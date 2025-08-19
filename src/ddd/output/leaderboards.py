import streamlit as st

from analysis.misc import get_all_stages_rung, get_leading_conductors, get_leading_coringers, get_top_associations, get_top_methods_by_stage
from model.performance import Performance

def show_leaderboards(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.header("Leaderboards")

    # Top methods by stage
    st.subheader("Top methods by stage")
    possible_stages = [
        "Singles", "Minimus", "Doubles", "Minor", "Triples", "Major", "Caters",
        "Royal", "Cinques", "Maximus", "Fourteen", "Sixteen"
    ]
    stages_rung = [stage.value for stage in get_all_stages_rung(performances)]
    selected_stage = st.selectbox(
        "Select stage:",
        ["All stages"] + [stage for stage in possible_stages if stage in stages_rung],
        placeholder="All stages"
    )
    parsed_stage = None if selected_stage == "All stages" else selected_stage
    df = get_top_methods_by_stage(performances, parsed_stage)
    st.dataframe(df, hide_index=True)

    # Top associations
    st.subheader("Your top associations")
    st.dataframe(get_top_associations(performances), hide_index=True)

    # Leading co-ringers
    st.subheader("Leading co-ringers")
    #min_performances_coringer = st.slider("Minimum shared performances", min_value=1, max_value=100, value=10)
    st.dataframe(get_leading_coringers(performances, st.session_state["accepted_names"], min_performances=1), hide_index=True)

    # Top conductors (or co-conductors)
    if not st.session_state["conductor_only"]:
        st.subheader("Your top conductors")
        st.dataframe(get_leading_conductors(performances, st.session_state["accepted_names"]), hide_index=True)