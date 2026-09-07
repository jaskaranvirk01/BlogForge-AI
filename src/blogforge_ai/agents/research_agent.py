from blogforge_ai.tools.research_tools import web_search_tool, extract_content_tool
from blogforge_ai.schemas.research_schemas import BlogRequest,  ResearchPlan, SearchInput, SearchOutput, SourceSelection, SourceSelectionInput,  SelectedSourceData, ExtractionInput
from blogforge_ai.llm.client import llm
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.prompts.research_prompts import RESEARCH_PLANNING_PROMPT, RESEARCH_SOURCE_SELECTION_PROMPT


class ResearchAgent:
    def __init__(self):
        self.web_search_tool = web_search_tool
        self.extract_content_tool = extract_content_tool
        self.llm = llm
        self.research_planning_llm = self.llm.with_structured_output(
            ResearchPlan)
        self.source_selection_llm = self.llm.with_structured_output(
            SourceSelection)

    def plan_research(self, blog_request: BlogRequest) -> ResearchPlan:

        messages = [SystemMessage(content=RESEARCH_PLANNING_PROMPT), HumanMessage(
            content=blog_request.model_dump_json(indent=2))]

        return self.research_planning_llm.invoke(messages)

    def search_sources(self, research_plan: ResearchPlan, max_results: int) -> SearchOutput:
        queries = research_plan.queries

        search_results = []
        seen_source_ids = set()
        for research_query in queries:
            search_input = SearchInput(
                query=research_query.query, max_results=max_results)
            response = self.web_search_tool.invoke(
                {'search_input': search_input})

            for result in response.results:
                if result.id not in seen_source_ids:
                    search_results.append(result)
                    seen_source_ids.add(result.id)

        return SearchOutput(results=search_results)

    def select_sources(self, research_plan: ResearchPlan, search_output: SearchOutput) -> SourceSelection:

        source_selection_input = SourceSelectionInput(
            research_plan=research_plan, search_output=search_output)

        messages = [SystemMessage(
            content=RESEARCH_SOURCE_SELECTION_PROMPT),
            HumanMessage(
            content=source_selection_input.model_dump_json(indent=1))]

        return self.source_selection_llm.invoke(messages)

    def get_selected_sources(self, source_selection: SourceSelection, search_output: SearchOutput) -> list[SelectedSourceData]:

        results_by_id = {
            result.id: result
            for result in search_output.results
        }

        selected_sources = []

        for selected_source in source_selection.selected_sources:
            result = results_by_id.get(selected_source.source_id)

            if result:
                selected_sources.append(
                    SelectedSourceData(
                        source=result, selection_reason=selected_source.reason)
                )

        return selected_sources

    def extract_selected_sources(self, selected_sources: list[SelectedSourceData]) -> list[SelectedSourceData]:
        extracted_sources = []

        for selected_source in selected_sources:
            extraction_input = ExtractionInput(
                url=selected_source.source.url, title=selected_source.source.title)

            extracted_output = self.extract_content_tool.invoke(
                {'source': extraction_input})

            if not extracted_output:
                continue

            extracted_sources.append(
                SelectedSourceData(source=selected_source.source, selection_reason=selected_source.selection_reason,
                                   extracted_content=extracted_output)
            )

        return extracted_sources


research_agent = ResearchAgent()
