from pydantic import BaseModel, Field
from typing import Optional

class School(BaseModel):
    id: str = Field(..., alias="NCESSCH", description="Unique School ID")
    name: str = Field(..., alias="SCHNAM05", description="School Name")
    city: str = Field(..., alias="LCITY05", description="City")
    state: str = Field(..., alias="LSTATE05", description="State")
    
    class Config:
        populate_by_name = True
        from_attributes = True

class SchoolCreate(School):
    pass

class SearchResult(BaseModel):
    school: School
    score: float
