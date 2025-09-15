from typing import Optional

from pydantic import BaseModel, Field

from model.place import Place
from model.method import MethodDetails
from model.ringers import Ringers, Ringer
from model.enums import PerformanceType
from utils import cwt_to_lbs

class RingingEvent(BaseModel):
    """TODO: docstring"""
    dove_tower_id: str
    dove_ring_id: str
    bell_no: int
    tenor_weight: Optional[str] = None # TODO: what units will this be in?


class Performance(BaseModel):
    """TODO: docstring"""
    performance_id: str = Field(alias="@id")
    association: Optional[str] = Field(alias="association", default=None)
    place: Place = Field(alias="place")
    date: str = Field(alias="date")
    duration: Optional[str] = Field(alias="duration", default=None)
    method_details: MethodDetails = Field(alias="title")
    details: Optional[str] = Field(alias="details", default=None)
    ringers: Ringers = Field(alias="ringers")
    footnotes: Optional[str | list[str]] = Field(alias="footnote", default=None)
    ringer_bell_weight_lbs: Optional[float] = None

    def set_bell_weight(self, weight_lbs):
        """TODO: docstring"""
        self.ringer_bell_weight_lbs = weight_lbs

    def get_all_bells_rung(self) -> int:
        """TODO: docstring"""
        bell_nos = []
        if hasattr(self.ringers, "ringers"):
            if isinstance(self.ringers.ringers, list):
                for ringer in self.ringers.ringers:
                    if hasattr(ringer, "bell_no"):
                        bell_nos.append(ringer.bell_no)
        return bell_nos
        

    # TODO: write tests
    def get_ringers(self) -> list[str]:
        """TODO: docstring"""
        if hasattr(self.ringers, "ringers"): # TODO: add a discriminator, this is hacky af
            if isinstance(self.ringers.ringers, list):
                names = []
                for ringer in self.ringers.ringers:
                    if isinstance(ringer, str):
                        names.append(ringer)
                    else:
                        names.append(ringer.name)
                return names
            elif isinstance(self.ringers.ringers, Ringer):
                return [self.ringers.ringers.name]
    
    # TODO: write tests
    def get_bell_rung_by(self, names: list[str]) -> int:
        """TODO: docstring"""
        named_ringers = [r for r in self.ringers.ringers if r.name in names]
        if len(named_ringers):
            return named_ringers[0].bell_no
        else:
            return None
        
    # TODO: write tests
    def get_conductor_names(self) -> list[str]:
        """TODO: docstring"""
        if hasattr(self.ringers, "ringers"):
            if isinstance(self.ringers.ringers, list):
                names = []
                for ringer in self.ringers.ringers:
                    if isinstance(ringer, Ringer):
                        if ringer.conductor:
                            names.append(ringer.name)
                return names
            elif isinstance(self.ringers.ringers, Ringer):
                if self.ringers.ringers.conductor:
                    return [self.ringers.ringers.name]
        return []
    
    def get_ringer_bell_data(self, names: list[str]) -> dict:
        """TODO: docstring"""
        if hasattr(self.ringers, "ringers") and isinstance(self.ringers.ringers, list):
            # find current ringer
            matching_ringers = []
            for ringer_str_or_obj in self.ringers.ringers:
                if hasattr(ringer_str_or_obj, "bell_no") and hasattr(ringer_str_or_obj, "name") and ringer_str_or_obj.name in names:
                    matching_ringers.append({
                        "bell_no": ringer_str_or_obj.bell_no,
                        "all_bells": self.get_all_bells_rung(),
                        "tenor_weight_lbs": cwt_to_lbs(self.place.ring_details.tenor_weight),
                        "dove_ring_id": self.place.ring_details.dove_ring_id
                    })
            return matching_ringers[0] # TODO: is this OK?
        else:
            return {}
                

    # TODO: write tests
    def ringer_is_conductor(self, names: list[str]) -> bool:
        """TODO: Docstring"""
        conductors = self.get_conductor_names()
        matching = [name for name in names if name in conductors]
        return len(matching) > 0
    
    # TODO: write tests
    def determine_performance_type(self) -> PerformanceType:
        """TODO: docstring"""
        num_changes = self.method_details.get_num_changes()
        if not num_changes:
            return PerformanceType.OTHER
        elif num_changes >= 1250 and num_changes <= 2499:
            return PerformanceType.QP
        elif num_changes >= 5000:
            return PerformanceType.PEAL
        else:
            return PerformanceType.OTHER
        
    # TODO: write tests
    def get_ringing_event(self, name: str) -> RingingEvent:
        """TODO: docstring""" # to power tower circling
        return RingingEvent(
            dove_tower_id=self.place.dove_tower_id,
            dove_ring_id=self.place.ring_details.dove_ring_id,
            bell_no=self.get_bell_rung_by(name),
            tenor_weight=self.place.ring_details.tenor_weight
        )
    
    def extract_duration_minutes(self) -> int:
        """TODO: docstring"""
        # TODO: replace with regex
        minutes = 0
        if self.duration:
            if "h " in self.duration:
                (hours, mins) = self.duration.split("h ")
                minutes += 60 * int(hours) + int(mins)
            elif "h" in self.duration:
                (hours, mins) = self.duration.split("h")
                minutes += 60 * int(hours)
                if mins:
                    minutes += int(mins)
            elif "m" in self.duration:
                just_mins = self.duration.split("m")[0]
                minutes += int(just_mins)
        return minutes

    # TODO: write tests
    def pretty_print(self):
        return f"""
            {self.date} - {self.place.pretty_print()}
            {self.method_details.num_changes} {self.method_details.method_name}
        """