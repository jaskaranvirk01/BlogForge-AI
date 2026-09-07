from datetime import datetime
from tavily import TavilyClient
from langchain_core.tools import tool
from blogforge_ai.schemas.research_schemas import SearchInput, SearchResult, SearchOutput, ExtractionInput, ExtractionOutput, ExtractedContent
from blogforge_ai.core.settings import settings

tavily_client = TavilyClient(api_key=settings.tavily_api_key)


@tool
def web_search_tool(search_input: SearchInput) -> SearchOutput | None:
    '''This tool uses tavily web search api to search the web and get relevant information'''
    try:
        response = tavily_client.search(
            search_input.query, max_results=search_input.max_results)
        results = []
        for result in response['results']:
            results.append(SearchResult(
                title=result['title'],
                url=result['url'],
                content=result['content'],
                score=result['score'],
                id=result['id']
            ))
        return SearchOutput(
            results=results
        )
    except Exception as e:
        raise e


@tool
def extract_content_tool(source: ExtractionInput) -> ExtractionOutput | None:
    """This tool uses Tavily extract API to extract raw content from the provided source."""

    try:
        response = tavily_client.extract(urls=source.url)

        results = response.get("results", [])

        if not results:
            return None

        result = results[0]

        content = ExtractedContent(
            url=result["url"],
            content=result["raw_content"],
            title=source.title,
            extracted_at=datetime.now()
        )

        return ExtractionOutput(
            content=content
        )

    except Exception as e:
        raise e
