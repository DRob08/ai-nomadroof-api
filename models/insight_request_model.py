from pydantic import BaseModel
from models.property_model import PropertyModel
from typing import List

class InsightRequest(BaseModel):
    question: str
    properties: List[PropertyModel]