from collections import defaultdict
import streamlit as st

from analysis.dove import get_all_saints, get_all_counties
from model.performance import Performance
from utils import extract_saints

# TODO: why isn't Eanswythe in all saints?

# TODO: write tests
def saint_bingo(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.subheader("Saint bingo")

    all_saints = get_all_saints()
    user_dedications = list(set([p.place.get_specific_detail_type("dedication") for p in performances]))
    user_saints = []
    for dedication in user_dedications:
        extracted_saints = extract_saints(dedication)
        for extracted_saint in extracted_saints:
            if extracted_saint not in user_saints:
                user_saints.append(extracted_saint)

    generic_bingo("saint_bingo_state", all_saints, user_saints)


def county_bingo(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.subheader("County bingo")

    all_counties = get_all_counties()
    user_counties = list(set([p.place.extract_county_name() for p in performances]))

    generic_bingo("county_bingo_state", all_counties, user_counties)


def day_of_the_year_bingo(performances: list[Performance]) -> None:
    """TODO: docstring"""
    def transform_date_format(iso_format_date: str) -> str:
        """TODO: docstring"""
        (_, month, day) = iso_format_date.split("-")
        return f"{day}/{month}"
    def left_pad(value: int) -> str:
        """TODO: docstring"""
        return f"0{str(value)}" if value < 10 else str(value)
    st.subheader("Date bingo")
    dates = set([transform_date_format(p.date) for p in performances])
    data = [
        ("Jan", 31), ("Feb", 29), ("Mar", 31), ("Apr", 30), ("May", 31), ("Jun", 30),
        ("Jul", 31), ("Aug", 31), ("Sep", 30), ("Oct", 31), ("Nov", 30), ("Dec", 31)
    ]
    for month_index, (month_str, num_days) in enumerate(data):
        display_str = f"{month_str} - "
        for date in range(1, num_days+1):
            formatted = f"{left_pad(date)}/{left_pad(month_index+1)}"
            colour = "green" if formatted in dates else "red"
            display_str += f":{colour}[{date}] "
        st.write(display_str)



def generic_bingo(state_name: str, possible_values: list[str], collected_values: list[str], display_details: bool = True) -> None:
    """TODO: docstring"""
    # group possible by letter
    possible_by_letter = defaultdict(set)
    for possible_value in possible_values:
        possible_by_letter[possible_value[0]].add(possible_value)

    letters = sorted(list(possible_by_letter.keys()))

    def set_state(letter_clicked, collected, possible) -> None:
        """TODO: docstring"""
        st.dialog(f"Clicking {letter_clicked} with possible = {possible} and collected = {collected}")
        if letter_clicked == st.session_state[state_name]["letter_clicked"]:
            st.session_state[state_name]["letter_clicked"] = None
        else:
            st.session_state[state_name]["letter_clicked"] = letter_clicked
            st.session_state[state_name]["possible"] = possible
            st.session_state[state_name]["collected"] = collected

    # create buttons
    cols = st.columns(len(letters))
    for i in range(0, len(letters)):
        with cols[i]:
            letter_possible_values = possible_by_letter[letters[i]]
            letter_collected_values = [v for v in letter_possible_values if v in collected_values]
            if len(letter_collected_values) == 0:
                colour = "red"
            elif len(letter_collected_values) == len(letter_possible_values):
                colour = "green"
            else:
                colour = "blue"
            button_key = f"{state_name}-{letters[i]}"
            st.button(f":{colour}[{letters[i]}]", key=button_key, on_click=set_state, args=[letters[i], letter_collected_values, letter_possible_values])

    # display details
    if display_details and st.session_state[state_name]["letter_clicked"]:
        possible = st.session_state[state_name]["possible"]
        collected = st.session_state[state_name]["collected"]
        building_str = ""
        for possible_val in sorted(possible):
            colour = "green" if possible_val in collected else "red"
            building_str += f":{colour}[{possible_val}] - "
        st.markdown(building_str[:-2])

def show_bingo(performances: list[Performance]) -> None:
    """TODO: docstring"""
    st.header("Bingo")
    saint_bingo(performances)
    #county_bingo(performances)
    day_of_the_year_bingo(performances)
