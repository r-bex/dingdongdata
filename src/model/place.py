from typing import Optional

from pydantic import BaseModel, Field

class PlaceDetail(BaseModel):
    """TODO: docstring"""
    place_detail_type: Optional[str] = Field(alias="@type") # TODO: could be enum
    place_detail_text: str = Field(alias="#text")

class RingDetails(BaseModel):
    """TODO: docstring"""
    ring_type: str = Field(alias="@type") # TODO: could be enum
    dove_ring_id: Optional[str] = Field(alias="@dove-ring-id", default=None)
    tenor_weight: Optional[str] = Field(alias="@tenor", default=None)

class Place(BaseModel):
    """TODO: docstring"""
    tower_base_id: Optional[str] = Field(alias="@towerbase-id", default=None)
    dove_tower_id: Optional[str] = Field(alias="@dove-tower-id", default=None)
    place_details: list[PlaceDetail] | PlaceDetail = Field(alias="place-name")
    ring_details: Optional[RingDetails] = Field(alias="ring", default=None)

    # TODO: write tests
    def extract_town_name(self) -> str:
        """TODO: docstring"""
        matching_detail = [d for d in self.place_details if d.place_detail_type == "place"]
        if matching_detail:
            return matching_detail[0].place_detail_text
        return None
    
    def extract_county_name(self) -> str:
        """TODO: docstring"""
        matching_detail = [d for d in self.place_details if d.place_detail_type == "county"]
        if matching_detail:
            return matching_detail[0].place_detail_text
        return None

    # TODO: write tests
    def get_specific_detail_type(self, detail_type: str) -> str:
        """TODO: docstring"""
        if isinstance(self.place_details, list):
            detail = [pd.place_detail_text for pd in self.place_details if pd.place_detail_type == detail_type]
            if len(detail):
                return detail[0]
            return "Unknown"
        elif isinstance(self.place_details, dict) and self.place_details.place_detail_type == detail_type:
            return self.place_details.place_detail_text
        else:
            return "Unknown"

    # TODO: write tests
    def pretty_print(self):
        """TODO: docstring"""
        place_name = self.get_specific_detail_type("place")
        dedication = self.get_specific_detail_type("dedication")
        county = self.get_specific_detail_type("county")
        return f"{place_name} ({dedication}), {county}"