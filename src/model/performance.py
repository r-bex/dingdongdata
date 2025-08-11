from typing import Optional

from pydantic import BaseModel, Field

from model.place import Place
from model.method import MethodDetails
from model.ringers import Ringers, Ringer
from model.enums import PerformanceType

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
    ringers: Ringers = Field(alias="ringers")
    footnotes: Optional[str | list[str]] = Field(alias="footnote", default=None)

    # TODO: write tests
    def get_ringers(self) -> list[str]:
        """TODO: docstring"""
        if hasattr(self.ringers, "ringers"): # TODO: add a discriminator, this is hacky af
            if isinstance(self.ringers.ringers, list):
                return [ringer.name for ringer in self.ringers.ringers]
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
        conductors = [r.name for r in self.ringers.ringers if r.conductor and r.name]
        return list(set(conductors))

    # TODO: write tests
    def ringer_is_conductor(self, names: list[str]) -> bool:
        """TODO: Docstring"""
        named_ringers = [r for r in self.ringers.ringers if r.name in names]
        return len(named_ringers) and named_ringers[0].conductor
    
    # TODO: write tests
    def determine_performance_type(self) -> PerformanceType:
        """TODO: docstring"""
        num_changes = self.method_details.num_changes
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

    # TODO: write tests
    def pretty_print(self):
        return f"""
            {self.date} - {self.place.pretty_print()}
            {self.method_details.num_changes} {self.method_details.method_name}
        """