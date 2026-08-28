from blogforge_ai.tools.research_tools import web_search_tool, extract_content_tool
from blogforge_ai.schemas.research_schemas import BlogRequest,  ResearchPlan
from blogforge_ai.llm.client import llm
from langchain_core.messages import SystemMessage, HumanMessage
from blogforge_ai.prompts.research_prompts import RESEARCH_PLANNING_PROMPT


class ResearchAgent:
    def __init__(self):
        self.web_search_tool = web_search_tool
        self.extract_content_tool = extract_content_tool
        self.knowledge_base_service = None  # once built will be added here
        self.llm = llm
        self.research_planning_llm = self.llm.with_structured_output(
            ResearchPlan)

    def plan_research(self, blog_request: BlogRequest) -> ResearchPlan:
        messages = [SystemMessage(content=RESEARCH_PLANNING_PROMPT), HumanMessage(
            content=blog_request.model_dump_json(indent=2))]

        return self.research_planning_llm.invoke(messages)
