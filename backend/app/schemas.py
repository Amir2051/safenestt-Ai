from datetime import datetime
from pydantic import BaseModel, Field

class AuthRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)

class CaseCreate(BaseModel):
    case_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=10000)
    title: str | None = Field(default=None, max_length=200)

class EvidenceCreate(BaseModel):
    kind: str = Field(min_length=2, max_length=80)
    label: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)

class CaseOut(BaseModel):
    id: int
    title: str
    case_type: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class FindingOut(BaseModel):
    category: str
    title: str
    detail: str
    confidence: str
    source: str
    class Config:
        from_attributes = True
