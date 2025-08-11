from typing import Optional

from pydantic import BaseModel, Field

from model.enums import Stage

class MethodDetails(BaseModel):
    """TODO: docstring"""
    num_changes: Optional[int] = Field(alias="changes", default=None)
    method_name: str = Field(alias="method")

    # TODO: write tests
    def pretty_print(self):
        """TODO: docstring"""
        if self.num_changes:
            return f"{self.num_changes} {self.method_name}"
        else:
            return self.method_name
    
    # TODO: write tests
    def extract_stage(self) -> Stage:
        """TODO: docstring"""
        # TODO: this currently doesn't handle combinations e.g. Cinques & Maximus
        last_method_word = self.method_name.split(" ")[-1]
        camel_case = last_method_word[0].upper() + "".join(last_method_word[1:]).lower()
        try:
            return Stage(camel_case)
        except:
            return Stage.UNKNOWN