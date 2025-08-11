import logging
from pathlib import Path
import re

import streamlit as st

logger = logging.getLogger()

BASE_URL = "https://bb.ringingworld.co.uk/export.php?pagesize={}&ringer={}"

SAINT_REGEX = re.compile("St ([A-Za-z]+)|SS ([A-Za-z]+) and ([A-Za-z]+)|S ([A-Za-z]+)|Saint ([A-Za-z]+)|SS ([A-Za-z]+) & ([A-Za-z]+)")

def get_project_root() -> Path:
    return Path(__file__).parent.parent

# TODO: write tests
def format_bellboard_url(name: str, page_size: int) -> str: # TODO: rename this function
    """
    Take a name and format the bellboard URL
    :param name: the name provided by the user to search for
    :param page_size: the max number of results to fetch from BellBoard
    :return: the BellBoard URL to make the request to
    """
    # Remove dots
    name = name.replace(".", "")
    # Replace spaces with URL-safe version
    name = name.replace(" ", "%20")
    return BASE_URL.format(page_size, name)

def extract_saints(dedication: str) -> list[str]:
    """TODO: docstring"""
    # TODO: strip trailing commas
    saints = []
    try:
        dedication = dedication.replace("-", " ").replace("'", " ").replace(",", " ")
        re_match = re.match(SAINT_REGEX, dedication)
        if re_match:
            saints = [g for g in re_match.groups() if g]
    except:
        pass
    return saints

def format_total_mins(mins: int, sig_figs: int = 3) -> str:
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
