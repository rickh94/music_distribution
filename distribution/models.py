import datetime
from enum import Enum
from typing import List

from odetam import DetaModel
from pydantic import BaseModel, Field


class Piece(BaseModel):
    composer: str
    title: str


class DistributionMethod(str, Enum):
    mail = "Mail"
    in_person = "In Person"
    dropped_off = "Dropped Off"
    email = "Email"
    other = "Other"


class MusicDistribution(DetaModel):
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "student": "Michael Burnham",
                "pieces": [
                    {"title": "Serenade for Strings", "composer": "P. Tchaikovsky"},
                    {"title": "St. Paul's Suite", "composer": "G. Holst"},
                ],
                "distribution_method": "Mail",
                "date": str(datetime.date.today()),
                "parts": ["Violin 1", "Violin 2"],
            }
        }

    student: str = Field(
        ..., title="Student Name", description="Student the music was delivered to"
    )
    pieces: List[Piece] = Field(
        ..., title="Pieces", description="Pieces that were delivered"
    )
    distribution_method: DistributionMethod = Field(
        ..., title="Distribution Method", description="How the music was given out"
    )
    date: datetime.date = Field(
        None, title="Date", description="The date the music was send out"
    )
    parts: List[str] = Field(
        ..., title="Parts", description="Instrument parts given out"
    )
