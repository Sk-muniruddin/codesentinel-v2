from pydantic import BaseModel
from typing import List


class ReviewFinding(BaseModel):
    severity: str
    category: str
    file: str
    line: int
    problem: str
    impact: str
    recommendation: str


class CodeReview(BaseModel):
    summary: str
    findings: List[ReviewFinding]