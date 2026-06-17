from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RawReview(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(..., alias="text")
    rating: int = Field(..., alias="score")
    published_at: datetime = Field(..., alias="date")
    reviewId: Optional[str] = Field(None, alias="id")
    userName: Optional[str] = Field(None, alias="userName")




class Review(BaseModel):
    text: str
    rating: int
