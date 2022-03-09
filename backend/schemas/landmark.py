from typing import Tuple

from pydantic import BaseModel


class Landmark(BaseModel):
    coordinate: Tuple[str, str]
    name: str
    description: str
    type: str
