from pydantic import BaseModel, Field

from model.performance import Performance
from model.enums import Stage

class Performances(BaseModel):
    """TODO: docstring"""
    performances: list[Performance] = Field(alias="performance")

    # TODO: write tests
    def get_all_associations(self) -> list[str]:
        """TODO: docstring"""
        return sorted(list(set([p.association for p in self.performances if p.association])))
    
    # TODO: write tests
    def get_all_towns(self) -> list[str]:
        """TODO: docstring"""
        return sorted(list(set([p.place.extract_town_name() for p in self.performances])))
    
    # TODO: write tests
    def get_all_counties(self) -> list[str]:
        """TODO: docstring"""
        return sorted(list(set([p.place.extract_county_name() for p in self.performances if p.place.extract_county_name()])))

    # TODO: write tests    
    def get_all_stages(self) -> list[str]:
        """TODO: docstring"""
        all_stages: list[Stage] = []
        for p in self.performances:
            all_stages += p.method_details.extract_stages()
        unique_stages: list[Stage] = list(set(all_stages))

        # Keep only ones with ordinal
        ordinal_stages = [s for s in unique_stages if s is not Stage.UNKNOWN]
        ordinal_stages.sort(key=lambda stage: stage.get_ordinal())
        
        return [stage.value for stage in ordinal_stages]
    
    def remove_ringing_room_performances(self) -> None:
        """TODO: docstring"""
        self.performances = [p for p in self.performances if "ringing room" not in p.place.model_dump_json().lower()]


class RootModel(BaseModel):
    """TODO: docstring"""
    performances: Performances = Field(alias="performances")
