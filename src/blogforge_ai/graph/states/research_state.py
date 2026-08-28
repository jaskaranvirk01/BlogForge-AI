from typing import TypedDict
from blogforge_ai.schemas.research_schemas import BlogRequest, ResearchQuery, ResearchSource, ResearchFinding


class ResearchState(TypedDict):
    blog_request: BlogRequest
    queries: list[ResearchQuery]
    sources: list[ResearchSource]
    findings: list[ResearchFinding]
    research_complete: bool
