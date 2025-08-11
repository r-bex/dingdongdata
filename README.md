# DingDongData

## Caveats

* Circling doesn't factor in bells being rehung or tuned or changed in anyway
* It only includes performances on BellBoard
* Some performances that couldn't be parsed might be excluded from analysis
* Handbells basically don't work right now
* Nothing is well-tested. This is currently just a fun side project.

## Running the app locally

1. Install the dependencies into a Python 3.11 environment using `pip install -r requirements.txt`. Other versions might work but haven't been tested.

2. Run `streamlit run src/main.py` to run the app.

## Features to add

Requires no new data:
* hosting
* method alphabet completion
* tower alphabet completion

Extra filtering:
* by method

Uses Dove dataset:
* tower circling stats
* heaviest bell rung (overall and turned in)

## Dev features to add
* unit tests for analysis & logic
* linting & formatting
* better documentation
* use uv for dependency management
* script for pulling up-to-date Dove data

## General improvements to make
* try using fuzzywuzzy for name matching on all ringers
* toggle on/off gaps in timeline
* show agg totals in timeline
* fix timeline stacking order to stage increasing
* fix map hover formatting
* show performance details on hover in perf table
* why does the map load so vertically long sometimes?
* improve map icons
* map struggles with handbell locations due to lack of tower ID
* switch pandas for polars
