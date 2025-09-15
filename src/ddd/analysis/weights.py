import streamlit as st

from model.performance import Performance
from model.tower import Tower, Bell
from utils import lbs_to_cwt


def within_x_lbs(weight_lbs: int, target_weight_lbs: int, tolerance_lbs: int = 5):
    """TODO: docstring"""
    diff = abs(target_weight_lbs - weight_lbs)
    return diff <= tolerance_lbs

def ignore_extra_bells(true_num: str) -> int:
    nums_only = [c for c in true_num if c.isnumeric()]
    return int("".join(nums_only))

def estimate_weight_lbs(bell_no: int, all_bells: list[int], perf_tenor_weight_lbs: float, tower_bells: list[Bell]) -> float | None:
    """TODO: docstring"""
    # order the bells by weight (if the bell has a weight)
    weighted_bells = [bell for bell in tower_bells if bell.weight_lbs]

    # find biggest bell that matches tenor weight from performance
    matching = [b for b in weighted_bells if within_x_lbs(b.weight_lbs, perf_tenor_weight_lbs)]
    if len(matching) == 0:
        # TODO: log a warning
        return None
    elif len(matching) > 1:
        matching.sort(key= lambda b: b.weight_lbs)
        tenor_no = ignore_extra_bells(matching[-1].true_number)
    else:
        tenor_no = ignore_extra_bells(matching[0].true_number)

    diff_backwards = max([int(x) for x in all_bells]) - int(bell_no)
    actual_bell_no = int(tenor_no) - diff_backwards

    equiv_bell = [b for b in weighted_bells if ignore_extra_bells(b.true_number) == actual_bell_no]
    if len(equiv_bell) == 0:
        # TODO: log a warning
        return None
    elif len(equiv_bell) > 1:
        return None
    else:
        return equiv_bell[0].weight_lbs


def assign_performance_weights(performances: list[Performance], towers: list[Tower], names: list[str]) -> None:
    """TODO: docstrign"""
    for p in performances:
        data = p.get_ringer_bell_data(names)
        ringer_bell_no = data["bell_no"]
        all_bells = data["all_bells"]
        perf_tenor_weight_lbs = data["tenor_weight_lbs"]
        ring_id = data["dove_ring_id"]

        matching_towers = [t for t in towers if t.dove_ring_id == ring_id]
        if len(matching_towers) == 0:
            est_lbs = None
        elif len(matching_towers) > 1:
            est_lbs = None
        else:
            bells = matching_towers[0].bells
            est_lbs = estimate_weight_lbs(
                ringer_bell_no,
                all_bells,
                perf_tenor_weight_lbs,
                bells
            ) 

        p.set_bell_weight(est_lbs)


def get_heaviest_bell_rung(weighted_perfs: list[Performance]) -> str:
    """TODO: docstring"""
    max_lbs = max([p.ringer_bell_weight_lbs for p in weighted_perfs])
    return lbs_to_cwt(max_lbs)

