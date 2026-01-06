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
    paper_id: Optional[int] = None
    case_id: Optional[int] = None
    title: str
    court: Optional[str] = None
    holding: Optional[str] = None
    status: str = Field(..., description="'verified' or 'unverified'")
    reason: Optional[str] = None

class VerifierOutput(BaseModel):
    citations: List[VerifiedCitation]

class DocAnalysis(BaseModel):
    doc_id: int
    title: str
    summary: str
    key_findings: str
    implications: str
    verified_via: Optional[str] = None

class DocAnalyzerOutput(BaseModel):
    documents: List[DocAnalysis]

class Source(BaseModel):
    title: str
    url: Optional[str] = None
    year: Optional[int] = None
    authors: Optional[str] = None
    court: Optional[str] = None
    snippet: Optional[str] = None

class ExplainerOutput(BaseModel):
    explanation: str
    caveats: str
    sources: List[Source]

class MarketDefOutput(BaseModel):
    market_definition: str
    evidence_evaluation: str
    conclusion: str
    sources: List[Source]
