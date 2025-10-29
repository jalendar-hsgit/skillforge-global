from pydantic import BaseModel
from typing import List

class ProgressItem(BaseModel):
    path: str
    module_id: str

class ProgressList(BaseModel):
    path: str
    completed: List[str]
