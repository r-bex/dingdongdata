from typing import Optional, Annotated

from pydantic import BaseModel, Field, AfterValidator

class Ringer(BaseModel):
    """TODO: docstring"""
    bell_no: Optional[str] = Field(alias="@bell", default=None)
    name: str = Field(alias="#text")
    conductor: Optional[bool] = Field(alias="@conductor", default=False)

    @classmethod
    def from_name(cls, name: str) -> "Ringer":
        return cls(bell_no=None, name=name, conductor=False)

def handle_flat_ringers(ringers):
    """TODO: docstring"""
    if isinstance(ringers, str):
        return [Ringer(bell_no=None, name=ringers, conductor=False)]
    if isinstance(ringers, dict):
        return [Ringer.model_validate(ringers)]
    if isinstance(ringers, list):
        new_ringers = []
        for ringer in ringers:
            if isinstance(ringer, str):
                new_ringers.append(Ringer(bell_no=None, name=ringer, conductor=False))
            elif isinstance(ringer, dict):
                new_ringers.append(Ringer.model_validate(ringer))
        return new_ringers

class Ringers(BaseModel):
    """TODO: docstring"""
    # Need to account for single ringer in case of e.g. tolling
    ringers: list[Ringer | str] | Ringer = Field(alias="ringer")
    #ringers: Annotated[list[Ringer | str] | Ringer, AfterValidator(handle_flat_ringers)]

    #def handle_flat_ringers
