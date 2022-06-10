from typing import Literal, Annotated

from pydantic import BaseModel, Field


class SearchTextOption(BaseModel):
    query: str
    name: str
    type: Literal["text"] = "text"
    placeholder: str


class SearchSliderOption(BaseModel):
    query: str
    name: str
    type: Literal["slider"] = "slider"
    default: float = Field(alias="def")
    min: float
    max: float
    step: float
    display: Literal["number", "percentage"]

    class Config:
        allow_population_by_field_name = True


class SearchToggleOption(BaseModel):
    query: str
    name: str
    type: Literal["toggle"] = "toggle"
    default: Literal[0, 1] = Field(alias="def")

    class Config:
        allow_population_by_field_name = True


class SearchSelectOption(BaseModel):
    query: str
    name: str
    type: Literal["select"] = "select"
    default: int = Field(alias="def")
    values: list[str]

    class Config:
        allow_population_by_field_name = True


SearchOption = Annotated[
    SearchTextOption | SearchSliderOption | SearchToggleOption | SearchSelectOption,
    Field(discriminator="type"),
]


class Search(BaseModel):
    options: list[SearchOption]
