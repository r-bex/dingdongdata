import json
import logging

import requests
import streamlit as st
import xmltodict

from model.performance import Performance
from model.performance_set import RootModel
from utils import format_bellboard_url, get_project_root

DEFAULT_PAGE_SIZE = 10000 # BellBoard max

PROJECT_ROOT = get_project_root()
TXT_DATA_PATH = f"{PROJECT_ROOT}/data/user/raw_data.txt"
JSON_DATA_PATH = f"{PROJECT_ROOT}/data/user/data.json"

logger = logging.getLogger()

# TODO: write tests
def fetch_raw_data(name: str, page_size: int = DEFAULT_PAGE_SIZE) -> None:
    """
    Fetch & save the raw XML data export from BellBoard
    :param name: the name provided by the user to search for
    :param page_size: the max number of results to fetch from BellBoard
    :return: None
    """
    try:
        url = format_bellboard_url(name, page_size)
        response = requests.get(url, headers={"Accept": "application/xml"})
        response.raise_for_status()

        with open(TXT_DATA_PATH, "w") as f:
            f.writelines(response.text)
        logger.info("Raw data written to text file.")
    except Exception as exc:
        logger.exception("Could not fetch raw data.", exc_info=exc)
        raise

# TODO: write tests
def load_performances_from_json(file: str = "data.json") -> list[Performance]:
    """
    Load the JSON data of all performances and validate into Root model
    :param file: name of the JSON file in the data directory containing to load
    :return: a list of Performance objects
    """
    # TODO: handle non-existent or empty JSON
    path = f"{PROJECT_ROOT}/data/user/{file}"
    with open(path, "r") as f: # TODO: switch back to JSON_DATA_PATH
        dct = json.load(f)

    model = RootModel.model_validate(dct)
    return model.performances.performances

# TODO: write tests
def convert_text_to_json() -> None:
    """
    Convert the raw XML text data into pydantic-ready JSON
    :return: None
    """
    # TODO: handle non-existent, empty or invalid data
    # Convert the txt to XML file
    with open(TXT_DATA_PATH, "r") as f:
        xml_string = f.read()

    dct = xmltodict.parse(xml_string)
    
    with open(JSON_DATA_PATH, "w") as f:
        json.dump(dct, f)
    logger.info("XML converted to JSON.")


@st.cache_data
def load_data(from_file: bool, name: str = None) -> list[Performance]:
    """
    Fetch up to 10k records from BellBoard
    :param from_file: if True, don't load new data and reload data.json
    :param name: the name to use in the BellBoard search API call
    :return: a list of Performance objects
    """
    if from_file:
        return load_performances_from_json(file="data.json")
    else:
        if not name:
            raise ValueError("Please provide a name to load data for")
        fetch_raw_data(name)
        convert_text_to_json()
        return load_performances_from_json()