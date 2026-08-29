from datetime import datetime
from pydantic import BaseModel, Field


# The input to our overall workflow
class BlogRequest(BaseModel):
    topic: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    desired_length: int = Field(gt=0)
    tone: str = Field(min_length=1)
    additional_instructions: str | None = None


# Records what the Research Agent searched for and why
class ResearchQuery(BaseModel):
    query: str = Field(min_length=1)
    purpose: str = Field(min_length=1)


# Research Plan
class ResearchPlan(BaseModel):
    queries: list[ResearchQuery]

# Represents a discovered source:


class ResearchSource(BaseModel):
    source_id: str
    title: str
    url: str
    domain: str
    snippet: str | None = None
    content: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime


# Represents information extracted from sources:
class ResearchFinding(BaseModel):
    finding_id: str
    topic: str
    finding: str
    source_ids: list[str]


# The complete output of the Research Agent:
class ResearchOutput(BaseModel):
    research_summary: str
    queries: list[ResearchQuery]
    sources: list[ResearchSource]
    findings: list[ResearchFinding]


# Web Search tool input
class SearchInput(BaseModel):
    query: str
    max_results: int


# Web Search Results
class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float
    id: str


# Web Search Output
class SearchOutput(BaseModel):
    results: list[SearchResult]


# Extraction input
class ExtractionInput(BaseModel):
    url: str
    title: str


# Extracted Content
class ExtractedContent(BaseModel):
    url: str
    title: str
    content: str
    extracted_at: datetime


# Extraction Output
class ExtractionOutput(BaseModel):
    content: ExtractedContent


# Selected Source
class SelectedSource(BaseModel):
    source_id: str
    reason: str


# List of selected sources
class SourceSelection(BaseModel):
    selected_sources: list[SelectedSource]


# Input Schema for LLM to select sources
class SourceSelectionInput(BaseModel):
    research_plan: ResearchPlan
    search_output: SearchOutput


# Selected Source Data
class SelectedSourceData(BaseModel):
    source: SearchResult
    selection_reason: str = Field(min_length=1)
    extracted_content: ExtractionOutput | None = None


# Research Result
class ResearchResult(BaseModel):
    research_plan: ResearchPlan
    selected_sources: list[SelectedSourceData]
