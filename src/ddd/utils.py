import logging
import math
from pathlib import Path
import re

logger = logging.getLogger()

BASE_URL = "https://bb.ringingworld.co.uk/export.php?pagesize={}&ringer={}"

SAINT_REGEX = re.compile("St ([A-Za-z]+)|SS ([A-Za-z]+) and ([A-Za-z]+)|S ([A-Za-z]+)|Saint ([A-Za-z]+)|SS ([A-Za-z]+) & ([A-Za-z]+)")

LBS_IN_CWT = 112
LBS_IN_QUARTER = 28

def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent

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

def extract_saints_from_dedication(dedication: str) -> list[str]:
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

def make_word_camelcase(word: str) -> str:
    """TODO: string"""
    return word[0].upper() + word[1:].lower()

def word_is_valid(w: str) -> bool:
    """TODO: docstring"""
    for char in w:
        if char not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-"]:
            return False
    return True

def cwt_to_lbs(cwt_str: str) -> int | None:
    """Convert a bell weight in x-y-z format to a weight in lbs"""
    # TODO: put try catch on this
    # only keep words that only contain numbers and -
    if " " in cwt_str:
        words = cwt_str.split(" ")
        valid_words = [w for w in words if word_is_valid(w)]
        if len(valid_words) == 0:
            return None
        cwt_str = valid_words[0]

    if "-" in cwt_str:
        (cwt, quarters, lbs) = [int(x) for x in cwt_str.split("-")]
        total_lbs = 0
        total_lbs += cwt * LBS_IN_CWT
        total_lbs += quarters * LBS_IN_QUARTER
        total_lbs += lbs
        return total_lbs
    else:
        return LBS_IN_CWT * int(cwt_str)

def lbs_to_cwt(lbs: float) -> str:
    """TODO: docstring"""
    as_int = round(lbs)

    whole_cwt = math.floor(as_int / LBS_IN_CWT)
    as_int = as_int - (whole_cwt * LBS_IN_CWT)

    whole_quarters = math.floor(as_int / LBS_IN_QUARTER)
    remainder_lbs = as_int - (whole_quarters * LBS_IN_QUARTER)

    return f"{whole_cwt}-{whole_quarters}-{remainder_lbs}"


# TODO: move to dove?
def extract_true_bell_no(bell_no_str: str) -> str | None:
    """TODO: docstring"""
    if "c" in bell_no_str:
        if bell_no_str.startswith("c"):
            return None
        else:
            return bell_no_str.split("c")[0]
    else:
        return bell_no_str
