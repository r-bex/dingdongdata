import streamlit as st

from analysis.dove import load_tower_data, load_modelled_towers
from analysis.misc import advanced_filter, basic_filter, generate_pandas_dataframe
from analysis.names import find_similar_names
from analysis.weights import assign_performance_weights
from data import load_data
from model.performance import Performance
from model.performance_set import Performances
from output.bingo import show_bingo
from output.leaderboards import show_leaderboards
from output.map import show_map
from output.progress import show_progress_stats
from output.stats import show_headline_stats
from output.trends import show_trends

basic_subset = None
all_entries = []
subset_performances = []

def generate_new_bingo_vars() -> dict:
    return {
        "letter_clicked": None,
        "possible": [],
        "collected": []
    }

# TODO: move this somewhere else
def get_toggle_labels(performances: list[Performance]) -> dict[str, str]:
    """TODO: docstring"""
    num_tower = len([p for p in performances if p.place.ring_details.ring_type == "tower"])
    num_hand = len([p for p in performances if p.place.ring_details.ring_type == "hand"])
    num_peal = len([p for p in performances if p.determine_performance_type() == "peal"])
    num_qp = len([p for p in performances if p.determine_performance_type() == "qp"])

    return {
        "all_ring_types": [f"tower ({num_tower})", f"hand ({num_hand})", f"both ({num_tower + num_hand})"],
        "default_ring_type": f"both ({num_tower + num_hand})",
        "all_perf_types": [f"qp ({num_qp})", f"peal ({num_peal})", f"both ({num_qp + num_peal})"],
        "default_perf_type": f"both ({num_qp + num_peal})"
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

# Load tower data for later? TODO: move this later?
# raw_tower_df = load_tower_data()
# modelled_towers = load_modelled_towers(raw_tower_df)

# TODO: allow entry of multiple name variations
st.session_state["primary_name"] = st.text_input("Enter your name as it appears on Bellboard: ")

if st.session_state["primary_name"] and not all_entries:
    st.spinner(text="Loading all performances...", show_time=False)
    all_entries = load_data(filename=None, name=st.session_state["primary_name"])

if st.session_state["primary_name"] and len(all_entries):
    all_performances = [p for p in all_entries if p.determine_performance_type() in ["qp", "peal"] and p.place.ring_details.ring_type in ["tower", "hand"]]
    st.text(f"Loaded {len(all_entries)} entries from BellBoard, filtered down to {len(all_performances)} performances.")

    # BellBoard entries that will not be shown
    excluded = [p for p in all_entries if p not in all_performances]
    with st.expander("Excluded BellBoard entries"):
        st.table(generate_pandas_dataframe(excluded))

    # Identify synonyms
    candidate_synonyms = find_similar_names(all_performances, st.session_state["primary_name"])
    selected_synonyms = []
    if len(candidate_synonyms):
        st.subheader("Name deduplication")
        selected_synonyms = st.pills(
            "Are any of these you?",
            options=candidate_synonyms,
            default=candidate_synonyms,
            selection_mode="multi"
        )
    st.session_state["accepted_names"] = [st.session_state["primary_name"]] + selected_synonyms
    

    # Match locations
    #assign_performance_weights(all_performances, modelled_towers, st.session_state["accepted_names"])

    ## -- Basic filters --

    st.subheader("Filter performances")
    toggle_labels = get_toggle_labels(all_performances)

    # Filter - tower bells vs handbells
    st.session_state["ring_type"] = st.segmented_control(
        label="Select performance type",
        options=toggle_labels["all_ring_types"],
        selection_mode="single",
        default=toggle_labels["default_ring_type"]
    )

    # Filter - peal vs QP
    st.session_state["performance_type"] = st.segmented_control(
        label="Select other performance type",
        options=toggle_labels["all_perf_types"],
        selection_mode="single",
        default=toggle_labels["default_perf_type"]
    )

    # Filter - only show performances as conductor
    st.session_state["conductor_only"] = st.toggle("Conductor only", value=False)

    basic_subset = basic_filter(all_performances)
    basic_subset_obj = Performances(performance=basic_subset)

    # Remove Ringing Room performances
    basic_subset_obj.remove_ringing_room_performances()

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
        - [Settings](#name-deduplication)
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