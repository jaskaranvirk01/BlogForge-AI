from blogforge_ai.tools.research_tools import web_search_tool, extract_content_tool
from blogforge_ai.schemas.research_schemas import BlogRequest,  ResearchPlan, SearchInput, SearchOutput, SourceSelection, SourceSelectionInput
from blogforge_ai.llm.client import llm
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.prompts.research_prompts import RESEARCH_PLANNING_PROMPT, RESEARCH_SOURCE_SELECTION_PROMPT


class ResearchAgent:
    def __init__(self):
        self.web_search_tool = web_search_tool
        self.extract_content_tool = extract_content_tool
        self.knowledge_base_service = None  # once built will be added here
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

        for research_query in queries:
            search_input = SearchInput(
                query=research_query.query, max_results=max_results)
            response = self.web_search_tool.invoke(
                {'search_input': search_input})

            for result in response.results:
                search_results.append(result)

        return SearchOutput(results=search_results)

    def select_sources(self, research_plan: ResearchPlan, search_output: SearchOutput) -> SourceSelection:
        source_selection_input = SourceSelectionInput(
            research_plan=research_plan, search_output=search_output)
        messages = [SystemMessage(
            content=RESEARCH_SOURCE_SELECTION_PROMPT),
            HumanMessage(
            content=source_selection_input.model_dump_json(indent=1))]

        return self.source_selection_llm.invoke(messages)


# =============================================================================
blog_request = BlogRequest(
    topic="Impact of Artificial Intelligence on Software Development",
    target_audience="Software developers",
    content_type="technical blog",
    desired_length=1500,
    tone="professional",
    additional_instructions="Focus on practical benefits, risks, and current trends",
)

RA = ResearchAgent()
research_plan = RA.plan_research(blog_request=blog_request)
search_output = RA.search_sources(research_plan=research_plan, max_results=3)
source_selection = RA.select_sources(
    research_plan=research_plan, search_output=search_output)
print('Research Plan')
print()
print(research_plan)
print()
print('Search Output')
print()
print(search_output)
print()
print('Selected Sources')
print()
print(source_selection)
print()


print()

for selected_source in source_selection.selected_sources:
    for search_result in search_output.results:
        if selected_source.source_id == search_result.id:
            print(f"id : {selected_source.source_id}")
            print(selected_source.reason)
