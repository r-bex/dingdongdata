from pydantic import BaseModel, Field

from model.performance import Performance

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
        identifiable_stages = list(set([
            p.method_details.extract_stage() for p in self.performances
            if p.method_details.extract_stage().get_ordinal()
        ]))
        identifiable_stages.sort(key=lambda stage: stage.get_ordinal())
        return [stage.value for stage in identifiable_stages]


class RootModel(BaseModel):
    """TODO: docstring"""
    performances: Performances = Field(alias="performances")
