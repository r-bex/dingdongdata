import streamlit as st

from analysis.misc import advanced_filter, basic_filter, generate_pandas_dataframe
from analysis.names import find_similar_names
from data import load_data
from model.performance_set import Performances
from output.bingo import show_bingo
from output.leaderboards import show_leaderboards
from output.map import show_map
from output.progress import show_progress_stats
from output.stats import show_headline_stats
from output.trends import show_trends

basic_subset = None
all_performances = []
subset_performances = []

def generate_new_bingo_vars() -> dict:
    return {
        "letter_clicked": None,
        "possible": [],
        "collected": []
    }

# initialise filter vars
initial_values = {
    "ring_type": "tower",
    "performance_type": "qp",
    "conductor_only": False,
    "association_filter": "All",
    "town_filter": "All",
    "county_filter": "All",
    "stage_filter": "All",
    "saint_bingo_state": generate_new_bingo_vars(),
    "county_bingo_state": generate_new_bingo_vars()
}
for key, init_value in initial_values.items():
    if key not in st.session_state:
        st.session_state[key] = init_value

st.title(":bell: DingDongData")

with st.expander("About this app"):
    st.write("This is a work in progress with lots of limitations and caveats.")

# TODO: allow entry of multiple name variations
st.session_state["primary_name"] = st.text_input("Enter your name as it appears on Bellboard: ")

if st.session_state["primary_name"] and not all_performances:
    st.spinner(text="Loading all performances...", show_time=False)
    all_performances = load_data(from_file=False, name=st.session_state["primary_name"])

if st.session_state["primary_name"] and len(all_performances):
    st.text(f"Loaded {len(all_performances)} performances from BellBoard.")

    # Identify synonyms
    candidate_synonyms = find_similar_names(all_performances, st.session_state["primary_name"])
    if len(candidate_synonyms):
        st.subheader("Name deduplication")
        selected_synonyms = st.pills("Are any of these you?", options=candidate_synonyms, selection_mode="multi")
        st.session_state["accepted_names"] = [st.session_state["primary_name"]] + selected_synonyms

    ## -- Basic filters --

    st.subheader("Filter performances")

    # Filter - tower bells vs handbells
    st.session_state["ring_type"] = st.segmented_control(
        label="Select performance type",
        options=["tower", "hand", "both"],
        selection_mode="single",
        default="tower"
    )

    # Filter - peal vs QP
    st.session_state["performance_type"] = st.segmented_control(
        label="Select other performance type",
        options=["qp", "peal", "both"],
        selection_mode="single",
        default="qp"
    )

    # Filter - only show performances as conductor
    st.session_state["conductor_only"] = st.toggle("Conductor only", value=False)

    basic_subset = basic_filter(all_performances)
    basic_subset_obj = Performances(performance=basic_subset)

# TODO: fix this.
if basic_subset and len(basic_subset) == 0:
    st.text("No performances found.")
    if st.session_state["conductor_only"]:
        st.info("It looks like you haven't conducted anything yet. Why not visit https://callingitround.cccbr.org.uk/ for tips on getting into calling as a beginner?")
elif basic_subset:
    with st.expander("View additional filters"):
        all_perf_object = Performances(performance=all_performances)
        # Filter by association rung for
        st.session_state["association_filter"] = st.selectbox(
            label="Filter by association",
            options=["All", *basic_subset_obj.get_all_associations()]
        )

        # Filter by town/place
        st.session_state["town_filter"] = st.selectbox(
            label="Filter by town/place",
            options=["All", *basic_subset_obj.get_all_towns()]
        )

        # Filter by town/place
        st.session_state["county_filter"] = st.selectbox(
            label="Filter by county",
            options=["All", *basic_subset_obj.get_all_counties()],
        )

        # Filter by stage
        st.session_state["stage_filter"] = st.selectbox(
            label="Filter by stage",
            options=["All", *basic_subset_obj.get_all_stages()]
        )
        
        # filter by method
        # TODO: implement. But how does it interact with the stage filter?
        #st.text("Filter by method")

        subset_performances = advanced_filter(basic_subset)
        subset = Performances(performance=subset_performances)

## -- Performance analysis --

if subset_performances and len(subset_performances):
    # Side bar for navigating between sections
    st.sidebar.markdown('''
        # Sections
        - [Vital statistics](#vital-statistics)
        - [Trends](#trends)
        - [Performance map](#performance-map)
        - [Leaderboards](#leaderboards)
        - [Proportion of X-bell towers rung at](#proportion-of-x-bell-towers-rung-at)
        - [Bingo](#bingo)
        ''',
        unsafe_allow_html=True
    )
        
    # View all performances (collapsed)
    with st.expander("View all matching performances"):
        st.table(generate_pandas_dataframe(subset_performances))

    # Headline stats
    show_headline_stats(subset_performances)

    # Timeline plot
    show_trends(subset_performances)

    # TODO: don't show map if filtered by location?
    # Performance map
    if st.session_state["ring_type"] != "hand":
        show_map(subset_performances)

    ## Leaderboards
    show_leaderboards(subset_performances)

    ## Progress stats
    show_progress_stats(subset_performances)

    ## Bingo
    show_bingo(subset_performances)