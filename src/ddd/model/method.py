from typing import Optional

from pydantic import BaseModel, Field

from model.enums import Stage
from utils import make_word_camelcase

class RecordLength(BaseModel):
    """TODO: docstring"""
    record_length: bool = Field(alias="@record", default=False)
    num_changes: int = Field(alias="#text")


class MethodDetails(BaseModel):
    """Information about what was rung"""
    changes: Optional[int | RecordLength] = Field(alias="changes", default=None)
    method_name: str = Field(alias="method")

    def get_num_changes(self) -> int | None:
        """Extract the number of changes in the performance, if provided."""
        if self.changes:
            if isinstance(self.changes, int):
                return self.changes
            else:
                return self.changes.num_changes
        return None

    # TODO: write tests
    def pretty_print(self):
        """Return a nice string representation for performance listings."""
        if self.get_num_changes():
            changes = self.get_num_changes()
            return f"{changes} {self.method_name}"
        else:
            return self.method_name

    # TODO: write tests
    def extract_stages(self) -> list[Stage]:
        """Extract the performance's stage(s), for filtering & granular displays."""
        if "spliced" in self.method_name.lower():
            # extract all stages
            stages = []
            for word in self.method_name.split(" "):
                try:
                    stage = Stage(make_word_camelcase(word))
                    stages.append(stage)
                except:
                    pass
            return stages
        else:
            # just use last term
            last_method_word = self.method_name.split(" ")[-1]
            camel_case = last_method_word[0].upper() + "".join(last_method_word[1:]).lower()
            try:
                return [Stage(camel_case)]
            except:
                return [Stage.UNKNOWN]
