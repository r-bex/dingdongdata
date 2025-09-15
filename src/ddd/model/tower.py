from typing import Optional

import pandas as pd
from pydantic import BaseModel

from utils import extract_true_bell_no

class Bell(BaseModel):
    # e.g. 6b or 0
    true_number: str
    weight_lbs: Optional[float] = None # might not be known

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Tower(BaseModel):
    dove_tower_id: str
    dove_ring_id: str
    place: Optional[str] = None
    county: Optional[str] = None
    dedication: Optional[str] = None
    location: Optional[Coordinates]
    bells: list[Bell]
    tenor_weight_lbs: float
    num_bells: int
