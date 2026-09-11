from unittest.mock import patch
from uuid import uuid4
from datetime import datetime

import pytest

from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.research import (
    ResearchExtractionError,
    ResearchGenerationError,
    ResearchSearchError,
)
from blogforge_ai.graph.graphs.research_graph import research_graph
from blogforge_ai.schemas.research_schemas import (
    BlogRequest,
    ResearchPlan,
    ResearchQuery,
    SearchOutput,
    SearchResult,
    SourceSelection,
    SelectedSource,
    SelectedSourceData,
    ExtractionOutput,
    ExtractedContent,
)


def create_blog_request() -> BlogRequest:
    return BlogRequest(
        topic="iPhone 17",
        target_audience="Teenagers",
        content_type="Brief summary",
        desired_length=150,
        tone="professional",
        additional_instructions="Focus on a brief introduction type blog",
    )


def create_research_plan() -> ResearchPlan:
    return ResearchPlan(
        queries=[
            ResearchQuery(
                query="iPhone 17 latest features",
                purpose="Identify the major features of iPhone 17",
            )
        ]
    )


def create_search_output() -> SearchOutput:
    return SearchOutput(
        results=[
            SearchResult(
                title="iPhone 17 Features",
                url="https://example.com/iphone-17",
                content="Information about iPhone 17 features.",
                score=0.95,
                id="source-1",
            )
        ]
    )


def create_source_selection() -> SourceSelection:
    return SourceSelection(
        selected_sources=[
            SelectedSource(
                source_id="source-1",
                reason="Relevant source containing information about iPhone 17.",
            )
        ]
    )


def create_selected_sources() -> list[SelectedSourceData]:
    search_result = SearchResult(
        title="iPhone 17 Features",
        url="https://example.com/iphone-17",
        content="Information about iPhone 17 features.",
        score=0.95,
        id="source-1",
    )

    return [
        SelectedSourceData(
            source=search_result,
            selection_reason="Relevant source containing information about iPhone 17.",
        )
    ]


def create_extracted_sources() -> list[SelectedSourceData]:
    search_result = SearchResult(
        title="iPhone 17 Features",
        url="https://example.com/iphone-17",
        content="Information about iPhone 17 features.",
        score=0.95,
        id="source-1",
    )

    extraction_output = ExtractionOutput(
        content=ExtractedContent(
            url="https://example.com/iphone-17",
            title="iPhone 17 Features",
            content="Detailed extracted information about iPhone 17 features.",
            extracted_at=datetime.now(),
        )
    )

    return [
        SelectedSourceData(
            source=search_result,
            selection_reason="Relevant source containing information about iPhone 17.",
            extracted_content=extraction_output,
        )
    ]


def test_research_workflow_happy_path():

    blog_request = create_blog_request()

    research_plan = create_research_plan()
    search_output = create_search_output()
    source_selection = create_source_selection()
    selected_sources = create_selected_sources()
    extracted_sources = create_extracted_sources()

    research_id = uuid4()

    with (
        patch(
            "blogforge_ai.graph.nodes.research_nodes.research_agent"
        ) as mock_research_agent,
        patch(
            "blogforge_ai.graph.nodes.research_nodes.knowledge_base_service"
        ) as mock_knowledge_base_service,
    ):

        mock_research_agent.plan_research.return_value = research_plan
        mock_research_agent.search_sources.return_value = search_output
        mock_research_agent.select_sources.return_value = source_selection
        mock_research_agent.get_selected_sources.return_value = selected_sources
        mock_research_agent.extract_selected_sources.return_value = extracted_sources

        mock_knowledge_base_service.ingest_research.return_value = research_id

        result = research_graph.invoke(
            {
                "blog_request": blog_request
            }
        )

    assert result["research_plan"] == research_plan
    assert result["search_output"] == search_output
    assert result["source_selection"] == source_selection
    assert result["selected_sources"] == selected_sources
    assert result["extracted_sources"] == extracted_sources
    assert result["research_result"] is not None
    assert result["research_id"] == research_id
    assert result["research_status"] == "Saved"


def test_research_workflow_llm_failure():

    blog_request = create_blog_request()

    generation_error = ResearchGenerationError(
        message="Research generation failed",
        error_code=ErrorCodes.RESEARCH_GENERATION_FAILED,
        workflow="research",
        node="plan_research",
        retryable=False,
    )

    with patch(
        "blogforge_ai.graph.nodes.research_nodes.research_agent"
    ) as mock_research_agent:

        mock_research_agent.plan_research.side_effect = generation_error

        with pytest.raises(ResearchGenerationError) as exc_info:
            research_graph.invoke(
                {
                    "blog_request": blog_request
                }
            )

    error = exc_info.value

    assert error is generation_error
    assert error.error_code == ErrorCodes.RESEARCH_GENERATION_FAILED
    assert error.workflow == "research"
    assert error.node == "plan_research"


def test_research_workflow_tavily_search_failure():

    blog_request = create_blog_request()

    research_plan = create_research_plan()

    search_error = ResearchSearchError(
        message="Research search failed",
        error_code=ErrorCodes.RESEARCH_SEARCH_FAILED,
        workflow="research",
        node="search_sources",
        retryable=False,
    )

    with patch(
        "blogforge_ai.graph.nodes.research_nodes.research_agent"
    ) as mock_research_agent:

        mock_research_agent.plan_research.return_value = research_plan
        mock_research_agent.search_sources.side_effect = search_error

        with pytest.raises(ResearchSearchError) as exc_info:
            research_graph.invoke(
                {
                    "blog_request": blog_request
                }
            )

    error = exc_info.value

    assert error is search_error
    assert error.error_code == ErrorCodes.RESEARCH_SEARCH_FAILED
    assert error.workflow == "research"
    assert error.node == "search_sources"


def test_research_workflow_tavily_extraction_failure():

    blog_request = create_blog_request()

    research_plan = create_research_plan()
    search_output = create_search_output()
    source_selection = create_source_selection()
    selected_sources = create_selected_sources()

    extraction_error = ResearchExtractionError(
        message="Research extraction failed",
        error_code=ErrorCodes.RESEARCH_EXTRACTION_FAILED,
        workflow="research",
        node="extract_selected_sources",
        retryable=False,
    )

    with patch(
        "blogforge_ai.graph.nodes.research_nodes.research_agent"
    ) as mock_research_agent:

        mock_research_agent.plan_research.return_value = research_plan
        mock_research_agent.search_sources.return_value = search_output
        mock_research_agent.select_sources.return_value = source_selection
        mock_research_agent.get_selected_sources.return_value = selected_sources
        mock_research_agent.extract_selected_sources.side_effect = extraction_error

        with pytest.raises(ResearchExtractionError) as exc_info:
            research_graph.invoke(
                {
                    "blog_request": blog_request
                }
            )

    error = exc_info.value

    assert error is extraction_error
    assert error.error_code == ErrorCodes.RESEARCH_EXTRACTION_FAILED
    assert error.workflow == "research"
    assert error.node == "extract_selected_sources"
