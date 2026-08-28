from langchain_mistralai import ChatMistralAI
from blogforge_ai.core.settings import settings


llm = ChatMistralAI(model_name='voxtral-mini-2602',
                    api_key=settings.mistral_api_key)
