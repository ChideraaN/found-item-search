import math
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, field_validator

type BagForm = Literal["suitcase", "backpack", "duffel"]
type BagShell = Literal["hard", "soft"]


def is_blank(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def clean(value):
    return value.strip() if isinstance(value, str) else value


class BagBase(BaseModel):
    colour: str
    bag_form: BagForm
    shell: BagShell | None = None
    brand: str | None = None
    weight_kg: float | None = None

    @field_validator("colour", "bag_form", mode="before")
    @classmethod
    def required_not_empty(cls, value):
        if is_blank(value):
            raise ValueError("Field is Empty")
        return clean(value)

    @field_validator("shell", "brand", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        return None if is_blank(value) else clean(value)

    @field_validator("weight_kg", mode="before")
    @classmethod
    def check_weight(cls, value):
        if is_blank(value):
            return None
        try:
            weight = float(value)
        except (TypeError, ValueError):
            raise ValueError("Weight is not a number")
        if math.isnan(weight):
            raise ValueError("Weight is not a number")
        if weight <= 0 or weight > 32:
            raise ValueError("Weight must be above 0 and at most 32")
        return weight


class MiniBag(BagBase):
    pass


class Bag(BagBase):
    report_id: str

    @field_validator("report_id", mode="before")
    @classmethod
    def report_id_not_empty(
        cls, value
    ):  # different name, so it no longer replaces the parent's
        if is_blank(value):
            raise ValueError("Field is Empty")
        return clean(value)


@dataclass
class ExtractionResult:
    bag: MiniBag | None
    failure_reason: str | None
    input_tokens: int
    output_tokens: int
    cost: float

class NotABagError(Exception):
    pass

class MultipleBagsError(Exception):
    pass