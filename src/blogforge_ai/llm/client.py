from langchain_mistralai import ChatMistralAI
from blogforge_ai.core.settings import settings


llm = ChatMistralAI(model_name='ministral-8b-2512',
                    api_key=settings.mistral_api_key)
