import datetime
from pydantic import BaseModel, Field, field_validator

class Movie(BaseModel):
    id: int
    title: str
    overview: str
    year: int
    rating: float
    category: str

class Movie_create(BaseModel):
    id: int
    title: str
    overview: str = Field(min_length=15, max_length=50, default="Esta película trata de...")
    year: int = Field(le=datetime.date.today().year, ge= 1900)
    rating: float = Field(ge=0, le=10)
    category: str = Field(min_length=5, max_length=20)

@field_validator('title')
def validate_title(cls,value: str) -> str:
    if len(value) < 5:
        raise ValueError('Title Field must hava a minimun length of 5 characters')
    if len(value) > 5:
        raise ValueError('Title Field must hava a maximun  length of 5 characters')
    return value

class Movie_update(BaseModel):
    title: str
    overview: str
    year: int
    rating: float
    category: str