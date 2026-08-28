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
                score=result['score']
            ))
        return SearchOutput(
            results=results
        )
    except Exception as e:
        raise e


@tool
def extract_content_tool(source: ExtractionInput) -> ExtractionOutput | None:
    '''This tool uses tavily extract api to extract raw content from the provided sources'''
    try:
        response = tavily_client.extract(urls=source.url)
        content = ExtractedContent(
            url=response['results'][0]['url'],
            content=response['results'][0]['raw_content'],
            title=source.title,
            extracted_at=datetime.now()
        )
        return ExtractionOutput(
            content=content
        )
    except Exception as e:
        raise e


source = ExtractionInput(
    url='https://en.wikipedia.org/wiki/Elon_Musk',
    title='Elon Musk'
)

res = extract_content_tool.invoke({
    'source': source
})

print(res)
