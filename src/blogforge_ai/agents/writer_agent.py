from blogforge_ai.llm.client import llm
from blogforge_ai.rag.knowledge_base_service import knowledge_base_service
from blogforge_ai.database.models.fact_check import FactCheck
from uuid import UUID


class WriterAgent:
    def __init__(self):
        self.llm = llm
        self.knowledge_base_service = knowledge_base_service

    def retrieve_fact_check(self, fact_check_id: UUID) -> FactCheck:
        fact_check = self.knowledge_base_service.retrieve_fact_check_by_id(
            fact_check_id=fact_check_id)
        return fact_check

    def prepare_verified_claims(self, fact_check: FactCheck):

        claims = []

        for claim in fact_check.claims:
            claims.append(claim)

        return claims
