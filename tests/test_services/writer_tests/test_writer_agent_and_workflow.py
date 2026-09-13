from blogforge_ai.schemas.writer_schemas import (
    BlogRequest,
    BlogSection,
    FactCheckContent,
    WriterLLMInput,
    WriterLLMResult,
    WriterResult,
)
from blogforge_ai.schemas.fact_checker_schemas import Evidence, Reference
from blogforge_ai.graph.graphs.writer_graph import writer_graph
from blogforge_ai.exceptions.writer import (
    WriterGenerationError,
    WriterPersistenceError,
)
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from blogforge_ai.agents.writer_agent import writer_agent
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.writer import WriterGenerationError
from blogforge_ai.schemas.fact_checker_schemas import (
    Evidence,
    Reference,
    VerificationVerdict,
)
from blogforge_ai.schemas.writer_schemas import BlogRequest, BlogSection


def test_retrieve_fact_check_success():
    fact_check_id = uuid4()
    fact_check = MagicMock()

    with patch.object(
        writer_agent.knowledge_base_service,
        "retrieve_fact_check_by_id",
        return_value=fact_check,
    ) as mock_retrieve:
        with patch(
            "blogforge_ai.agents.writer_agent.FactCheckContent.model_validate",
            return_value="validated_fact_check",
        ) as mock_validate:
            result = writer_agent.retrieve_fact_check(
                fact_check_id=fact_check_id
            )

    assert result == "validated_fact_check"

    mock_retrieve.assert_called_once_with(
        fact_check_id=fact_check_id
    )

    mock_validate.assert_called_once_with(fact_check)


def test_prepare_writer_input_success():
    fact_check = MagicMock()

    fact_check.title = "AI in Software Development"
    fact_check.overview = "Overview of AI's impact."

    supported_evidence = Evidence(
        source_id=uuid4(),
        chunk_id=uuid4(),
    )

    unsupported_evidence = Evidence(
        source_id=uuid4(),
        chunk_id=uuid4(),
    )

    supported_claim = MagicMock()
    supported_claim.claim = "AI improves productivity."
    supported_claim.explanation = "AI automates repetitive tasks."
    supported_claim.verdict = VerificationVerdict.SUPPORTED
    supported_claim.evidence = [supported_evidence]

    unsupported_claim = MagicMock()
    unsupported_claim.claim = "AI eliminates all developers."
    unsupported_claim.explanation = "Unsupported claim."
    unsupported_claim.verdict = VerificationVerdict.CONTRADICTED
    unsupported_claim.evidence = [unsupported_evidence]

    reference_1 = MagicMock()
    reference_1.source_id = uuid4()
    reference_1.title = "Source One"
    reference_1.url = "https://example.com/one"

    reference_2 = MagicMock()
    reference_2.source_id = uuid4()
    reference_2.title = "Source Two"
    reference_2.url = "https://example.com/two"

    fact_check.claims = [
        supported_claim,
        unsupported_claim,
    ]

    fact_check.references = [
        reference_1,
        reference_2,
    ]

    blog_request = BlogRequest(
        topic="AI impact on software development",
        target_audience="Software developers",
        content_type="Technical blog",
        desired_length=1500,
        tone="Professional",
        additional_instructions=(
            "Focus on practical benefits, risks, and current trends."
        ),
    )

    human_feedback = "Make the practical implications clearer."

    result, evidence_map, reference_map = (
        writer_agent.prepare_writer_input(
            fact_check=fact_check,
            blog_request=blog_request,
            human_feedback=human_feedback,
        )
    )

    # Blog request / feedback
    assert result.blog_request is blog_request
    assert result.human_feedback == human_feedback

    # Fact-check context
    assert result.fact_check_title == fact_check.title
    assert result.fact_check_overview == fact_check.overview

    # Only SUPPORTED claims should be sent to the writer
    assert len(result.verified_claims) == 1

    llm_claim = result.verified_claims[0]

    assert llm_claim.claim == supported_claim.claim
    assert llm_claim.explanation == supported_claim.explanation

    assert len(llm_claim.evidence) == 1
    assert llm_claim.evidence[0].evidence_id == "E1"

    # Evidence mapping
    assert evidence_map["E1"].source_id == supported_evidence.source_id
    assert evidence_map["E1"].chunk_id == supported_evidence.chunk_id

    # References
    assert len(result.references) == 2

    assert result.references[0].source_id == "S1"
    assert result.references[0].title == reference_1.title
    assert result.references[0].url == reference_1.url

    assert result.references[1].source_id == "S2"
    assert result.references[1].title == reference_2.title
    assert result.references[1].url == reference_2.url

    # Reference mapping
    assert reference_map["S1"].source_id == reference_1.source_id
    assert reference_map["S1"].title == reference_1.title
    assert reference_map["S1"].url == reference_1.url

    assert reference_map["S2"].source_id == reference_2.source_id
    assert reference_map["S2"].title == reference_2.title
    assert reference_map["S2"].url == reference_2.url


def test_write_blog_success():
    llm_input = MagicMock()
    llm_result = MagicMock()

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = llm_result

    writer_agent.blog_writing_llm = mock_llm

    result = writer_agent.write_blog(
        llm_input=llm_input
    )

    assert result is llm_result

    mock_llm.invoke.assert_called_once()

    messages = mock_llm.invoke.call_args.args[0]

    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)


def test_write_blog_generation_failure():
    llm_input = MagicMock()

    llm_error = Exception("simulated LLM failure")

    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = llm_error

    writer_agent.blog_writing_llm = mock_llm

    with pytest.raises(WriterGenerationError) as exc_info:
        writer_agent.write_blog(
            llm_input=llm_input
        )

    error = exc_info.value

    assert error.error_code == ErrorCodes.WRITER_GENERATION_FAILED
    assert error.workflow == "writing"
    assert error.node == "write_blog"
    assert error.retryable is False
    assert error.cause is llm_error

    mock_llm.invoke.assert_called_once()


def test_create_writer_result_success():
    source_id = uuid4()

    reference_map = {
        "S1": Reference(
            source_id=source_id,
            title="AI Research",
            url="https://example.com/ai",
        )
    }

    llm_reference = MagicMock()
    llm_reference.source_id = "S1"

    llm_result = MagicMock()

    llm_result.blog_title = "AI in Software Development"

    llm_result.blog_introduction = (
        "AI is changing software development."
    )

    llm_result.sections = [
        BlogSection(
            heading="Benefits of AI",
            content=(
                "AI can automate repetitive development tasks."
            ),
        ),
        BlogSection(
            heading="Risks of AI",
            content=(
                "AI-generated code still requires human review."
            ),
        ),
    ]

    llm_result.conclusion = (
        "AI will continue to evolve."
    )

    llm_result.references = [
        llm_reference
    ]

    result = writer_agent.create_writer_result(
        llm_result=llm_result,
        reference_map=reference_map,
    )

    assert result.blog_title == llm_result.blog_title

    assert (
        result.blog_introduction
        == llm_result.blog_introduction
    )

    assert result.sections == llm_result.sections

    assert result.conclusion == llm_result.conclusion

    assert len(result.references) == 1

    reference = result.references[0]

    assert reference.source_id == source_id
    assert reference.title == "AI Research"
    assert reference.url == "https://example.com/ai"


def test_writer_workflow_success():
    fact_check_id = uuid4()
    draft_id = uuid4()

    blog_request = BlogRequest(
        topic="iPhone 17",
        target_audience="Teenagers",
        content_type="Brief summary",
        desired_length=150,
        tone="professional",
        additional_instructions=(
            "Focus on a brief introduction type blog."
        ),
    )

    fact_check = FactCheckContent(
        id=fact_check_id,
        analysis_id=uuid4(),
        title="iPhone 17",
        overview="Overview of iPhone 17.",
        claims=[],
        references=[],
    )

    llm_input = WriterLLMInput(
        blog_request=blog_request,
        human_feedback=None,
        fact_check_title="iPhone 17",
        fact_check_overview="Overview of iPhone 17.",
        verified_claims=[],
        references=[],
    )

    llm_result = WriterLLMResult(
        blog_title="iPhone 17: What Teenagers Should Know",
        blog_introduction="A brief introduction to the iPhone 17.",
        sections=[
            BlogSection(
                heading="Key Highlights",
                content="The iPhone 17 introduces several new features.",
            ),
        ],
        conclusion="The iPhone 17 offers several notable improvements.",
        references=[],
    )

    writer_result = WriterResult(
        blog_title="iPhone 17: What Teenagers Should Know",
        blog_introduction="A brief introduction to the iPhone 17.",
        sections=[
            BlogSection(
                heading="Key Highlights",
                content="The iPhone 17 introduces several new features.",
            ),
        ],
        conclusion="The iPhone 17 offers several notable improvements.",
        references=[],
    )

    evidence_map = {
        "E1": Evidence(
            source_id=uuid4(),
            chunk_id=uuid4(),
        )
    }

    reference_map = {
        "S1": Reference(
            source_id=uuid4(),
            title="Apple",
            url="https://example.com/apple",
        )
    }

    initial_state = {
        "fact_check_id": fact_check_id,
        "blog_request": blog_request,
        "human_feedback": None,
        "writer_status": "Writer Started",
    }

    with patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.retrieve_fact_check",
        return_value=fact_check,
    ) as mock_retrieve_fact_check, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.prepare_writer_input",
        return_value=(llm_input, evidence_map, reference_map),
    ) as mock_prepare_input, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.write_blog",
        return_value=llm_result,
    ) as mock_write_blog, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.create_writer_result",
        return_value=writer_result,
    ) as mock_create_result, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.knowledge_base_service.ingest_blog_draft",
        return_value=draft_id,
    ) as mock_save_draft:

        result = writer_graph.invoke(initial_state)

    # Final state
    assert result["fact_check_id"] == fact_check_id
    assert result["blog_request"] == blog_request
    assert result["human_feedback"] is None

    assert result["fact_check"] is fact_check

    assert result["llm_input"] is llm_input
    assert result["evidence_map"] is evidence_map
    assert result["reference_map"] is reference_map

    assert result["llm_result"] is llm_result
    assert result["writer_result"] is writer_result

    assert result["draft_id"] == draft_id
    assert result["writer_status"] == "Blog Draft Saved"

    # Fact-check retrieval
    mock_retrieve_fact_check.assert_called_once_with(
        fact_check_id=fact_check_id
    )

    # Writer input preparation
    mock_prepare_input.assert_called_once_with(
        fact_check=fact_check,
        blog_request=blog_request,
        human_feedback=None,
    )

    # Blog generation
    mock_write_blog.assert_called_once_with(
        llm_input=llm_input
    )

    # Writer result creation
    mock_create_result.assert_called_once_with(
        llm_result=llm_result,
        reference_map=reference_map,
    )

    # Persistence
    mock_save_draft.assert_called_once_with(
        fact_check_id=fact_check_id,
        writer_result=writer_result,
    )


def test_writer_workflow_fact_check_retrieval_failure():
    fact_check_id = uuid4()

    blog_request = BlogRequest(
        topic="iPhone 17",
        target_audience="Teenagers",
        content_type="Brief summary",
        desired_length=150,
        tone="professional",
        additional_instructions=None,
    )

    retrieval_error = Exception(
        "simulated fact-check retrieval failure"
    )

    initial_state = {
        "fact_check_id": fact_check_id,
        "blog_request": blog_request,
        "human_feedback": None,
        "writer_status": "Writer Started",
    }

    with patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.retrieve_fact_check",
        side_effect=retrieval_error,
    ) as mock_retrieve_fact_check:

        with pytest.raises(Exception) as exc_info:
            writer_graph.invoke(initial_state)

    error = exc_info.value

    assert error is retrieval_error

    mock_retrieve_fact_check.assert_called_once_with(
        fact_check_id=fact_check_id
    )


def test_writer_workflow_generation_failure():
    fact_check_id = uuid4()

    blog_request = BlogRequest(
        topic="iPhone 17",
        target_audience="Teenagers",
        content_type="Brief summary",
        desired_length=150,
        tone="professional",
        additional_instructions=None,
    )

    fact_check = MagicMock()
    llm_input = MagicMock()

    generation_error = WriterGenerationError(
        message="Blog Draft Generation failed",
        error_code="WRITER_GENERATION_FAILED",
        workflow="writing",
        node="write_blog",
        retryable=False,
        cause=Exception("simulated LLM failure"),
    )

    initial_state = {
        "fact_check_id": fact_check_id,
        "blog_request": blog_request,
        "human_feedback": None,
        "writer_status": "Writer Started",
    }

    with patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.retrieve_fact_check",
        return_value=fact_check,
    ) as mock_retrieve_fact_check, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.prepare_writer_input",
        return_value=(
            llm_input,
            {},
            {},
        ),
    ) as mock_prepare_input, patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.write_blog",
        side_effect=generation_error,
    ) as mock_write_blog:

        with pytest.raises(WriterGenerationError) as exc_info:
            writer_graph.invoke(initial_state)

    error = exc_info.value

    # Workflow should preserve the domain error from the agent.
    assert error is generation_error

    mock_retrieve_fact_check.assert_called_once_with(
        fact_check_id=fact_check_id
    )

    mock_prepare_input.assert_called_once_with(
        fact_check=fact_check,
        blog_request=blog_request,
        human_feedback=None,
    )

    mock_write_blog.assert_called_once_with(
        llm_input=llm_input
    )


def test_writer_workflow_persistence_failure():
    fact_check_id = uuid4()

    blog_request = BlogRequest(
        topic="iPhone 17",
        target_audience="Teenagers",
        content_type="Brief summary",
        desired_length=150,
        tone="professional",
        additional_instructions=None,
    )

    fact_check = MagicMock()
    llm_input = MagicMock()
    llm_result = MagicMock()
    writer_result = MagicMock()

    persistence_error = WriterPersistenceError(
        message="Blog Draft Persistence Failed",
        error_code="WRITER_PERSISTENCE_FAILED",
        workflow="writing",
        node="ingest_blog_draft",
        retryable=False,
        cause=Exception("simulated database failure"),
    )

    initial_state = {
        "fact_check_id": fact_check_id,
        "blog_request": blog_request,
        "human_feedback": None,
        "writer_status": "Writer Started",
    }

    with patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.retrieve_fact_check",
        return_value=fact_check,
    ), patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.prepare_writer_input",
        return_value=(
            llm_input,
            {},
            {},
        ),
    ), patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.write_blog",
        return_value=llm_result,
    ), patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.writer_agent.create_writer_result",
        return_value=writer_result,
    ), patch(
        "blogforge_ai.graph.nodes.writer_agent_nodes.knowledge_base_service.ingest_blog_draft",
        side_effect=persistence_error,
    ) as mock_save_draft:

        with pytest.raises(WriterPersistenceError) as exc_info:
            writer_graph.invoke(initial_state)

    error = exc_info.value

    # Workflow should preserve the domain error from the service.
    assert error is persistence_error

    mock_save_draft.assert_called_once_with(
        fact_check_id=fact_check_id,
        writer_result=writer_result,
    )
