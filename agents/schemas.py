from pydantic import BaseModel, Field
from typing import List, Optional

class Paper(BaseModel):
    paper_id: int
    title: str
    authors: str
    outlet: str
    year: int
    doi: Optional[str] = None
    url: Optional[str] = None
    snippet: str
    verified_via: Optional[str] = None

class EconPaperOutput(BaseModel):
    papers: List[Paper]

class Case(BaseModel):
    case_id: int
    title: str
    court: str
    year: int
    url: Optional[str] = None
    snippet: str
    verified_via: Optional[str] = None

class CaseLawOutput(BaseModel):
    cases: List[Case]

class VerifiedCitation(BaseModel):
    paper_id: int
    title: str
    status: str = Field(..., description="'verified' or 'unverified'")
    reason: Optional[str] = None

class VerifierOutput(BaseModel):
    citations: List[VerifiedCitation]
