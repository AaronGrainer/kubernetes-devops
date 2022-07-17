from pydantic import BaseModel


class Recommender(BaseModel):
    search: str
